#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind 写入器模块
负责将解析后的 JSON 结构打包为 .xmind 文件（ZIP），并生成必要的 content.xml、metadata.json、manifest.json 以及缩略图目录。

此模块与解析器模块（universal_xmind_converter.py 内的各 Parser 类）解耦，减少单文件体量和职责耦合。
"""

import json
import zipfile


def escape_xml_text(text):
    """安全转义 XML 文本内容"""
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_content_xml(json_structure):
    """生成 XMind 的 content.xml 内容"""
    sheet_id = json_structure.get("id", "default-sheet-id")
    sheet_title = json_structure.get("title", "Sheet 1")
    root_topic = json_structure.get("rootTopic", {})

    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" '
        'xmlns:fo="http://www.w3.org/1999/XSL/Format" '
        'xmlns:svg="http://www.w3.org/2000/svg" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'modified-by="Vana" timestamp="1503058545540" version="2.0">',
        f'<sheet id="{sheet_id}" modified-by="Vana" theme="0kdeemiijde6nuk97e4t0vpp54" timestamp="1503058545540">'
    ]

    if root_topic:
        topic_id = root_topic.get("id", "default-topic-id")
        topic_title = root_topic.get("title", "Root Topic")

        xml_parts.append(
            f'<topic id="{topic_id}" modified-by="Vana" timestamp="1503058545484">'
            f'<title>{escape_xml_text(topic_title)}</title>'
        )

        def generate_topics(topics):
            if not topics:
                return []

            result = []
            result.append('<children><topics type="attached">')

            for topic in topics:
                topic_id = topic.get('id', f'topic-{hash(str(topic))}')
                title = topic.get('title', 'Topic')
                children = topic.get('children', {}).get('attached', [])

                result.append(f'<topic id="{topic_id}" modified-by="Vana" timestamp="1503058545484">')
                result.append(f'<title svg:width="500">{escape_xml_text(title)}</title>')

                if children:
                    result.extend(generate_topics(children))

                result.append('</topic>')

            result.append('</topics></children>')
            return result

        attached_topics = root_topic.get('children', {}).get('attached', [])
        if attached_topics:
            xml_parts.extend(generate_topics(attached_topics))

        xml_parts.append('</topic>')

    xml_parts.extend([
        '<extensions><extension provider="org.xmind.ui.map.unbalanced">',
        '<content><right-number>-1</right-number></content>',
        '</extension></extensions>',
        f'<title>{escape_xml_text(sheet_title)}</title>',
        '</sheet>',
        '</xmap-content>'
    ])

    return '\n'.join(xml_parts)


def create_metadata():
    """生成 metadata.json"""
    return {
        "dataStructureVersion": "2",
        "layoutEngineVersion": "3",
        "creator": {
            "name": "Vana",
            "version": "23.05.2004"
        }
    }


def create_manifest():
    """生成 manifest.json"""
    return {
        "file-entries": {
            "content.json": {},
            "content.xml": {},
            "metadata.json": {},
            "Thumbnails/thumbnail.png": {}
        }
    }


def create_xmind_file(json_structure, output_file):
    """根据解析后的 JSON 结构创建 .xmind 文件"""
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # content.json：正常文件使用数组格式
        zip_file.writestr('content.json', json.dumps([json_structure], ensure_ascii=False, indent=2))

        # content.xml
        content_xml = generate_content_xml(json_structure)
        zip_file.writestr('content.xml', content_xml)

        # metadata.json
        zip_file.writestr('metadata.json', json.dumps(create_metadata(), ensure_ascii=False, indent=2))

        # manifest.json
        zip_file.writestr('manifest.json', json.dumps(create_manifest(), ensure_ascii=False, indent=2))

        # 缩略图目录与默认缩略图
        zip_file.writestr('Thumbnails/', b'')
        thumbnail_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd4c\x00\x00\x00\x00IEND\xaeB`\x82'
        zip_file.writestr('Thumbnails/thumbnail.png', thumbnail_data)