#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind文件结构验证工具
用于检测转换后的XMind文件格式是否正确，节点数量和关系是否正确
"""

import os
import zipfile
import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass
from ..models import Document, Topic, Stats
from ..errors import XMindError

logger = logging.getLogger(__name__)


class XMindReader:
    def __init__(self, xmind_file, *, max_content_bytes=200 * 1024 * 1024,
                 max_nodes=50000, max_depth=30):
        self.xmind_file = xmind_file
        self.content_json = None
        self.content_xml = None
        self.metadata = None
        self.topic = None
        self.sheet_data = {}
        self.parsed_source = None  # 'json' 或 'xml'
        self.max_content_bytes = max(1, max_content_bytes)
        self.max_nodes = max(1, max_nodes)
        self.max_depth = max(0, max_depth)
        self.stats = {}
        self.truncation_reasons = []
        self.error = None

    def extract_xmind_content(self):
        """解压前检查体积；各成员独立解码，允许JSON损坏后使用XML。"""
        self.content_json = self.content_xml = self.metadata = None
        self.error = None
        try:
            file_path = Path(self.xmind_file)
            if file_path.stat().st_size > self.max_content_bytes:
                raise ValueError("XMind文件大小超限")
            with zipfile.ZipFile(file_path) as archive:
                names = ("content.json", "content.xml", "metadata.json")
                members = [info for info in archive.infolist() if info.filename in names]
                if sum(info.file_size for info in members) > self.max_content_bytes:
                    raise ValueError("XMind解压内容大小超限")
                remaining = self.max_content_bytes
                for info in members:
                    with archive.open(info) as member:
                        data = member.read(remaining + 1)
                    if len(data) > remaining:
                        raise ValueError("XMind解压内容大小超限")
                    remaining -= len(data)
                    try:
                        text = data.decode("utf-8")
                        if info.filename == "content.xml":
                            self.content_xml = text
                        elif info.filename == "content.json":
                            self.content_json = json.loads(text)
                        else:
                            self.metadata = json.loads(text)
                    except (UnicodeError, ValueError, RecursionError) as exc:
                        logger.warning("无法解析 %s: %s", info.filename, exc)
                return self.content_json is not None or self.content_xml is not None
        except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
            self.error = str(exc)
            logger.warning("提取XMind内容失败: %s", exc)
            return False

    def parse_json_structure(self):
        """JSON优先；结构无效时由调用方尝试XML。"""
        sheet = self.content_json
        if isinstance(sheet, list):
            sheet = sheet[0] if sheet else None
        if not isinstance(sheet, dict):
            return False
        root = sheet.get("rootTopic") or sheet.get("primaryTopic")
        if not isinstance(root, dict):
            return False
        self.sheet_data = {k: v for k, v in sheet.items() if k not in ("rootTopic", "primaryTopic")}
        self.topic = self._parse_topic_recursive(root)
        self.parsed_source = "json"
        return True

    @staticmethod
    def _json_children(topic):
        for key in ("children", "topics", "subtopics"):
            children = topic.get(key)
            groups = children.items() if isinstance(children, dict) else (("attached", children),)
            for name, group in groups:
                if isinstance(group, list):
                    yield from ((child, name) for child in group if isinstance(child, dict))

    def _bounded_tree(self, root, node_data, children, level=0):
        """迭代遍历，同时执行预算并收集统计；不构造超限子树。"""
        self.truncation_reasons = []
        result = node_data(root, level)
        self.stats = {"total_nodes": 1, "max_depth": level, "titles_count": 1}
        stack = [(result, iter(children(root)), level)]
        while stack:
            parent, iterator, depth = stack[-1]
            try:
                source = next(iterator)
            except StopIteration:
                stack.pop()
                continue
            if depth >= self.max_depth:
                reason = f"层级过深(>{self.max_depth})"
                if reason not in self.truncation_reasons:
                    self.truncation_reasons.append(reason)
                stack.pop()
                continue
            if self.stats["total_nodes"] >= self.max_nodes:
                self.truncation_reasons.append(f"节点数超限(>{self.max_nodes})")
                break
            source, group = source if isinstance(source, tuple) else (source, "attached")
            child = node_data(source, depth + 1)
            child.group = group
            parent.children.append(child)
            self.stats["total_nodes"] += 1
            self.stats["titles_count"] += 1
            self.stats["max_depth"] = max(self.stats["max_depth"], depth + 1)
            stack.append((child, iter(children(source)), depth + 1))
        return result

    def _parse_topic_recursive(self, topic, level=0):
        def node_data(node, depth):
            return Topic(str(node.get("title", "")), id=str(node.get("id", "")),
                         extra={k: v for k, v in node.items() if k not in ("children", "topics", "subtopics", "title", "id")})
        return self._bounded_tree(topic, node_data, self._json_children, level)

    def parse_xml_structure(self):
        """解析XML结构（content.xml）"""
        if not self.content_xml:
            return False
        try:
            ns = '{urn:xmind:xmap:xmlns:content:2.0}'
            root = ET.fromstring(self.content_xml)
            # 优先定位到sheet下的根topic
            sheet = root.find(f'.//{ns}sheet')
            if sheet is not None:
                topic_el = sheet.find(f'.//{ns}topic')
            else:
                topic_el = root.find(f'.//{ns}topic')
            if topic_el is None:
                logger.warning('XML中未找到根topic')
                return False
            self.topic = self._parse_topic_recursive_xml(topic_el, level=0)
            self.parsed_source = 'xml'
            return True
        except Exception as e:
            logger.warning("解析XML结构失败: %s", e)
            return False

    def _parse_topic_recursive_xml(self, topic_el, level=0):
        ns = '{urn:xmind:xmap:xmlns:content:2.0}'

        def node_data(topic_el, depth):
            ns = '{urn:xmind:xmap:xmlns:content:2.0}'
            title_el = topic_el.find(f'{ns}title')
            title = title_el.text.strip() if (title_el is not None and title_el.text) else ''
            node_id = topic_el.get('id', '')
            result = Topic(title, id=node_id)
            # notes
            notes_text = ''
            notes_el = topic_el.find(f'{ns}notes')
            if notes_el is not None:
                # plain/text
                plain_el = notes_el.find(f'{ns}plain')
                if plain_el is not None:
                    text_el = plain_el.find(f'{ns}text')
                    if text_el is not None and text_el.text:
                        notes_text = (text_el.text or '').strip()
                # html/text（作为备用）
                if not notes_text:
                    html_el = notes_el.find(f'{ns}html')
                    if html_el is not None:
                        text_el2 = html_el.find(f'{ns}text')
                        if text_el2 is not None and text_el2.text:
                            notes_text = (text_el2.text or '').strip()
            if notes_text:
                result.extra['notes'] = notes_text
            # markers
            markers = []
            mrefs_el = topic_el.find(f'{ns}marker-refs')
            if mrefs_el is not None:
                for mref in mrefs_el.findall(f'{ns}marker-ref'):
                    mid = mref.get('marker-id', '')
                    if mid:
                        markers.append(mid)
            if markers:
                result.extra['markers'] = markers
            return result

        def children(node):
            container = node.find(f'{ns}children')
            if container is not None:
                for group in container.findall(f'{ns}topics'):
                    if group.get('type') == 'attached':
                        yield from group.iterfind(f'{ns}topic')

        return self._bounded_tree(topic_el, node_data, children, level)

    def read(self):
        if not self.extract_xmind_content():
            raise XMindError(self.error or "无法提取XMind内容", "read_error")
        if not (self.parse_json_structure() or self.parse_xml_structure()):
            raise XMindError("无法解析XMind结构（JSON与XML均失败）", "invalid_format")
        extra = {k: v for k, v in self.sheet_data.items() if k not in ("title", "id")}
        document = Document(self.topic, self.sheet_data.get("title", "画布 1"),
                            self.sheet_data.get("id", ""), extra)
        return ReadDocument(document, Stats(**self.stats), self.parsed_source,
                            tuple(self.truncation_reasons))


@dataclass
class ReadDocument:
    document: Document
    stats: Stats
    source_format: str
    truncation_reasons: tuple[str, ...] = ()
