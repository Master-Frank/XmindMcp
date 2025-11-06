#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind核心引擎
提供XMind文件处理的核心业务逻辑
"""

import json
import os
import sys
import logging
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional
from xmind_types import (
    ReadXmindResult,
    TranslateTitlesResult,
    CreateMindMapResult,
    AnalyzeResult,
    ConvertResult,
    ListFilesResult,
)

# 导入现有的转换器组件
from universal_xmind_converter import ParserFactory
from xmind_writer import create_xmind_file
from validate_xmind_structure import XMindValidator

# 配置日志
logger = logging.getLogger(__name__)


class XMindCoreEngine:
    """XMind核心引擎 - 处理XMind文件的核心业务逻辑"""
    
    def __init__(self):
        self.validator = None  # 将在需要时创建
        self.active_files = {}  # 缓存活跃的XMind文件
        # 高阈值与降级策略（可通过环境变量调整，默认尽可能高）
        try:
            self.max_file_size_mb = int(os.environ.get("XMIND_MAX_FILE_SIZE_MB", "200"))  # 约200MB
        except Exception:
            self.max_file_size_mb = 200
        try:
            self.max_nodes = int(os.environ.get("XMIND_MAX_NODE_COUNT", "50000"))
        except Exception:
            self.max_nodes = 50000
        try:
            self.max_parse_depth = int(os.environ.get("XMIND_MAX_PARSE_DEPTH", "30"))
        except Exception:
            self.max_parse_depth = 30
    
    def get_tools(self):
        """获取可用工具列表 - 兼容MCP服务器"""
        return [
            {
                "name": "read_xmind_file",
                "description": "读取XMind文件内容（返回结构与统计信息）",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "XMind文件路径"}
                    },
                    "required": ["filepath"]
                }
            },
            {
                "name": "create_mind_map",
                "description": "创建新的思维导图（支持 children/topics/subtopics 等别名，服务器自动归一化）",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "思维导图标题（将作为根节点标题）"
                        },
                        "topics_json": {
                            "type": "string",
                            "description": "主题结构的JSON字符串。每个节点至少包含`title`；子节点推荐使用`children`，也兼容`topics`/`subtopics`/`nodes`/`items`（服务器会自动归一化）。必须是合法JSON字符串，不要使用Markdown或纯文本。",
                            "examples": [
                                "[{\"title\":\"根\",\"children\":[{\"title\":\"子1\"},{\"title\":\"子2\",\"children\":[{\"title\":\"孙\"}]}]}]",
                                "[{\"title\":\"根\",\"topics\":[{\"title\":\"子1\"}]}]"
                            ]
                        },
                        "output_path": {
                            "type": "string",
                            "description": "可选。输出文件的绝对路径；未指定时由服务器配置的默认绝对目录决定",
                            "examples": ["D:/project/XmindMcp/output/demo.xmind"]
                        }
                    },
                    "required": ["title", "topics_json"]
                }
            },
            {
                "name": "analyze_mind_map",
                "description": "分析思维导图结构（统计节点数、最大层级等）",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "XMind文件路径"}
                    },
                    "required": ["filepath"]
                }
            },
            {
                "name": "convert_to_xmind",
                "description": "将纯文本、Markdown、HTML、Word、Excel等文件转换为XMind。要求源文件路径为绝对路径；相对路径将被拒绝并返回错误提示。不要传入JSON结构；JSON结构请使用 `create_mind_map`。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source_filepath": {"type": "string", "description": "源文件绝对路径（支持 .txt/.md/.html/.docx/.xlsx 等）", "examples": ["D:/project/XmindMcp/examples/test_outline.md", "D:/project/XmindMcp/examples/test_outline.txt"]},
                        "output_filepath": {"type": "string", "description": "可选。输出XMind文件绝对路径；未指定时由服务器配置的默认绝对目录决定", "examples": ["D:/project/XmindMcp/output/my_outline.xmind"]}
                    },
                    "required": ["source_filepath"]
                }
            },
            {
                "name": "list_xmind_files",
                "description": "列出目录中的XMind文件",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "要遍历的目录，默认当前目录"},
                        "recursive": {"type": "boolean", "description": "是否递归遍历，默认 true"},
                        "pattern": {"type": "string", "description": "可选。文件名过滤模式（如 '*.xmind' 或关键字）"},
                        "max_depth": {"type": "integer", "description": "可选。递归最大深度（0=仅当前目录）"}
                    },
                    "required": []
                }
            }
        ]
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除不安全的字符"""
        import re
        # 移除或替换不安全的字符
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除前导和尾随的空白字符
        safe_filename = safe_filename.strip()
        # 限制长度
        if len(safe_filename) > 100:
            safe_filename = safe_filename[:100]
        # 如果文件名为空，使用默认值
        if not safe_filename:
            safe_filename = "untitled"
        # 替换空格为下划线
        safe_filename = safe_filename.replace(' ', '_')
        return safe_filename
        
    def read_xmind_file(self, file_path: str) -> ReadXmindResult:
        try:
            # 文件体积预判（内部使用绝对路径，不向外暴露）
            file_size_bytes = None
            try:
                file_size_bytes = os.path.getsize(os.path.abspath(file_path))
            except Exception:
                file_size_bytes = None

            validator = XMindValidator(file_path)
            if not validator.extract_xmind_content():
                return {
                    "status": "error",
                    "message": "无法提取XMind内容"
                }
            # JSON优先，失败再尝试XML
            if validator.parse_json_structure():
                structure = validator.structure
            elif validator.parse_xml_structure():
                structure = validator.structure
            else:
                return {
                    "status": "error",
                    "message": "无法解析XMind结构（JSON与XML均失败）"
                }

            # 原始统计
            total_nodes = validator.count_nodes()
            max_depth = validator.get_max_depth()
            titles = validator.get_all_titles()

            # 阈值判定与降级策略（以层级限制为主，保持稳定返回）
            degrade_reasons: List[str] = []
            size_limit_bytes = self.max_file_size_mb * 1024 * 1024
            if file_size_bytes is not None and file_size_bytes > size_limit_bytes:
                degrade_reasons.append(f"文件过大(>{self.max_file_size_mb}MB)")
            if total_nodes > self.max_nodes:
                degrade_reasons.append(f"节点数超限(>{self.max_nodes})")
            if max_depth > self.max_parse_depth:
                degrade_reasons.append(f"层级过深(>{self.max_parse_depth})")

            if degrade_reasons:
                # 按层级限制精简结构
                trimmed = self._limit_depth(structure, self.max_parse_depth)
                # 重新计算概要统计
                trimmed_total = self._count_nodes_simple(trimmed)
                trimmed_max_depth = self._max_depth_simple(trimmed)
                titles_count = self._titles_count_simple(trimmed)
                msg = "读取完成（触发降级：" + ",".join(degrade_reasons) + f"，已限制解析层级至{self.max_parse_depth}）"
                return {
                    "status": "success",
                    "message": msg,
                    "data": {
                        "format": "xmind",
                        "source_format": validator.parsed_source or "unknown",
                        "structure": trimmed,
                    },
                    "stats": {
                        "total_nodes": trimmed_total,
                        "max_depth": trimmed_max_depth,
                        "titles_count": titles_count,
                    },
                }

            # 正常返回
            return {
                "status": "success",
                "message": "读取成功",
                "data": {
                    "format": "xmind",
                    "source_format": validator.parsed_source or "unknown",
                    "structure": structure,
                },
                "stats": {
                    "total_nodes": total_nodes,
                    "max_depth": max_depth,
                    "titles_count": len(titles)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"读取失败: {e}"
            }

    # 新增：翻译XMind标题并输出新文件
    def translate_xmind_titles(self, source_filepath: str, output_filepath: str = None, target_lang: str = "en", overwrite: bool = False) -> TranslateTitlesResult:
        import re
        import io
        import zipfile
        import json
        import xml.etree.ElementTree as ET
        try:
            src_path = Path(source_filepath)
            if not src_path.exists():
                return {"status": "error", "message": f"源文件不存在: {source_filepath}"}
            # 输出路径必须由调用方提供（服务器层负责解析），引擎不再默认到源目录
            if not output_filepath:
                return {"status": "error", "message": "缺少输出路径：请提供绝对输出路径（由服务器层解析）"}
            out_path = Path(output_filepath)
            if out_path.exists() and not overwrite:
                return {"status": "error", "message": f"输出文件已存在: {output_filepath}. 需设置 overwrite=True"}
            # 确保输出目录存在
            try:
                out_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            # 准备翻译器（deep-translator优先，googletrans回退）
            translator = None
            try:
                from deep_translator import GoogleTranslator  # type: ignore
                translator = GoogleTranslator(source='auto', target=target_lang)
            except Exception:
                try:
                    from googletrans import Translator  # type: ignore
                    translator = Translator()
                except Exception as te:
                    return {"status": "error", "message": f"加载翻译器失败: {te}"}
            def _translate_text(text: str) -> str:
                """Translate a single string using the available translator.
                - Prefer deep_translator.GoogleTranslator
                - Fallback to googletrans.Translator
                Returns original text if translation fails.
                """
                try:
                    # deep_translator path
                    return translator.translate(text)
                except TypeError:
                    # googletrans path
                    try:
                        res = translator.translate(text, src='auto', dest=target_lang)
                        return getattr(res, 'text', res)
                    except Exception:
                        return text
                except Exception:
                    return text
            # 文本检测：含非ASCII字符则翻译
            def needs_translate(text: str) -> bool:
                if not text:
                    return False
                return any(ord(c) > 127 for c in text)
            cache = {}
            translated_count = 0
            # 读取并处理XMind内容（JSON优先，回退XML）
            with zipfile.ZipFile(str(src_path), 'r') as zf:
                names = zf.namelist()
                if 'content.json' in names:
                    # 处理 JSON 格式
                    json_text = zf.read('content.json').decode('utf-8')
                    try:
                        data = json.loads(json_text)
                    except Exception as je:
                        return {"status": "error", "message": f"解析 content.json 失败: {je}"}
                    # 递归翻译所有 title
                    def translate_json(node):
                        nonlocal translated_count
                        if isinstance(node, dict):
                            tval = node.get('title')
                            if isinstance(tval, str):
                                raw = tval.strip()
                                if needs_translate(raw):
                                    new_text = cache.get(raw)
                                    if not new_text:
                                        new_text = _translate_text(raw)
                                        cache[raw] = new_text
                                    if new_text and new_text != raw:
                                        node['title'] = new_text
                                        translated_count += 1
                            # also translate attributedTitle text segments if present
                            at_list = node.get('attributedTitle')
                            if isinstance(at_list, list):
                                for it in at_list:
                                    if isinstance(it, dict):
                                        tx = it.get('text')
                                        if isinstance(tx, str):
                                            raw_tx = tx.strip()
                                            if needs_translate(raw_tx):
                                                new_tx = cache.get(raw_tx)
                                                if not new_tx:
                                                    new_tx = _translate_text(raw_tx)
                                                    cache[raw_tx] = new_tx
                                                if new_tx and new_tx != raw_tx:
                                                    it['text'] = new_tx
                                                    translated_count += 1
                            # children 兼容：list 或 dict 分组
                            children_items = []
                            ch = node.get('children')
                            if isinstance(ch, list):
                                children_items.extend(ch)
                            elif isinstance(ch, dict):
                                for val in ch.values():
                                    if isinstance(val, list):
                                        children_items.extend(val)
                            # 其他别名：topics / subtopics（可能是 list 或 dict）
                            for key in ('topics', 'subtopics'):
                                tp = node.get(key)
                                if isinstance(tp, list):
                                    children_items.extend(tp)
                                elif isinstance(tp, dict):
                                    for val in tp.values():
                                        if isinstance(val, list):
                                            children_items.extend(val)
                            # 递归子节点
                            for child in children_items:
                                translate_json(child)
                            # 递归可能的容器（如 sheets）
                            for k, v in node.items():
                                if isinstance(v, (dict, list)) and k not in ('children', 'topics', 'subtopics'):
                                    translate_json(v)
                        elif isinstance(node, list):
                            for item in node:
                                translate_json(item)
                    translate_json(data)
                    # 重新打包，替换 content.json
                    buf = io.BytesIO()
                    new_json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
                    with zipfile.ZipFile(str(src_path), 'r') as zf_in, zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf_out:
                        for name in zf_in.namelist():
                            if name == 'content.json':
                                zf_out.writestr('content.json', new_json_bytes)
                            else:
                                zf_out.writestr(name, zf_in.read(name))
                elif 'content.xml' in names:
                    # 回退处理 XML 格式
                    xml_bytes = zf.read('content.xml')
                    xml_text = xml_bytes.decode('utf-8')
                    ns = '{urn:xmind:xmap:xmlns:content:2.0}'
                    root = ET.fromstring(xml_text)
                    title_els = root.findall(f'.//{ns}title')
                    for t in title_els:
                        if t.text:
                            raw = t.text.strip()
                            if needs_translate(raw):
                                new_text = cache.get(raw)
                                if not new_text:
                                    new_text = _translate_text(raw)
                                    cache[raw] = new_text
                                if new_text and new_text != raw:
                                    t.text = new_text
                                    translated_count += 1
                    buf = io.BytesIO()
                    new_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                    with zipfile.ZipFile(str(src_path), 'r') as zf_in, zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf_out:
                        for name in zf_in.namelist():
                            if name == 'content.xml':
                                zf_out.writestr('content.xml', new_xml)
                            else:
                                zf_out.writestr(name, zf_in.read(name))
                else:
                    return {"status": "error", "message": "XMind中未找到 content.json 或 content.xml"}
            # 写入输出文件
            with open(str(out_path), 'wb') as f:
                f.write(buf.getvalue())
            return {
                "status": "success",
                "message": "翻译完成",
                "translated_titles": translated_count,
                "status": "success",
                "message": "翻译完成",
                "data": {
                    "source_file": str(src_path),
                    "output_file": str(out_path),
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"翻译失败: {e}"}

    def _build_topic_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """构建主题结构"""
        if not structure:
            return {"title": "空主题", "children": []}
        
        # 验证器返回的结构已经是根主题结构，直接转换即可
        return self._convert_topic_to_dict(structure)
    
    def _convert_topic_to_dict(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """转换主题为字典格式"""
        result = {
            "title": topic.get('title', '未命名主题'),
            "children": []
        }
        
        # 添加子主题 - 验证器返回的children已经是列表格式
        children = topic.get('children', [])
        if children and isinstance(children, list):
            for child in children:
                result["children"].append(self._convert_topic_to_dict(child))
        
        return result
    
    def create_mind_map(self, title: str, topics_json: str, output_path: Optional[str] = None) -> CreateMindMapResult:
        """创建新的思维导图"""
        try:
            # 解析JSON格式的主题
            try:
                topics = json.loads(topics_json)
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "message": f"主题JSON格式无效: {str(e)}"
                }
            
            # 构建文本大纲结构
            outline_content = self._build_outline_structure(title, topics)
            
            # 创建临时文件 - 使用安全的文件名
            safe_title = self._sanitize_filename(title)
            
            # 确定临时文件路径 - 使用当前工作目录
            current_dir = os.getcwd()
            temp_file = os.path.join(current_dir, f"temp_{safe_title}.txt")
            
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(outline_content)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"无法创建临时文件: {str(e)}"
                }
            
            # 确定输出文件路径
            if output_path:
                # 如果指定了输出路径，使用指定的路径
                output_file = output_path
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    try:
                        os.makedirs(output_dir)
                    except Exception as e:
                        return {
                            "status": "error",
                            "message": f"无法创建输出目录: {str(e)}"
                        }
            else:
                # 引擎不再默认生成输出路径，缺少输出路径直接报错
                return {
                    "status": "error",
                    "message": "缺少输出路径：请提供绝对输出路径（由服务器层解析）"
                }
            
            # 转换为XMind
            try:
                parser = ParserFactory.get_parser(temp_file)
                json_structure = parser.parse()
                create_xmind_file(json_structure, output_file)
                success = True
            except Exception as e:
                success = False
                error_msg = str(e)
                logger.error(f"XMind转换失败: {error_msg}")
            finally:
                # 清理临时文件
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        logger.warning(f"清理临时文件失败: {str(e)}")
            
            if success:
                # 验证文件是否真的被创建
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    abs_path = os.path.abspath(output_file)
                    return {
                        "status": "success",
                        "message": "思维导图已创建",
                        "data": {
                            "filename": os.path.basename(output_file),
                            "title": title,
                            "topics_count": len(topics),
                            "absolute_path": abs_path,
                            "output_path": output_file,
                            "file_size": file_size,
                        },
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"XMind文件创建失败，文件不存在: {output_file}"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"XMind转换失败: {error_msg}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _build_outline_structure(self, title: str, topics: List[Dict[str, Any]]) -> str:
        """构建文本大纲结构"""
        lines = [title]
        
        def _get_children(topic: Dict[str, Any]):
            return (
                topic.get('children')
                or topic.get('topics')
                or topic.get('subtopics')
                or None
            )

        def add_topics(parent_line: str, topics_list: List[Dict[str, Any]], level: int = 1):
            for topic in topics_list:
                indent = "    " * level  # 使用4个空格作为一级缩进
                line = f"{indent}- {topic.get('title', '未命名主题')}"
                lines.append(line)
                
                # 递归添加子主题（兼容别名）
                children = _get_children(topic)
                if children:
                    add_topics(line, children, level + 1)
        
        add_topics(title, topics)
        return "\n".join(lines)
    
    def analyze_mind_map(self, filepath: str) -> AnalyzeResult:
        """分析思维导图"""
        try:
            # 首先读取文件
            read_result = self.read_xmind_file(filepath)
            if read_result["status"] != "success":
                return read_result
            
            # 获取根主题结构（适配新的read_xmind_file返回结构）
            root_structure = read_result["data"].get("structure", {})
            
            # 构建统计信息（从stats字段获取）
            stats = {
                'total_nodes': read_result.get("stats", {}).get('total_nodes', 0),
                'max_depth': read_result.get("stats", {}).get('max_depth', 0),
                'leaf_nodes': self._count_leaf_nodes(root_structure),
                'branch_count': len(root_structure.get('children', []))
            }
            
            # 分析结构
            analysis = {
                "complexity": self._calculate_complexity(stats),
                "balance": self._calculate_balance(root_structure),
                "completeness": self._calculate_completeness(root_structure),
                "suggestions": self._generate_suggestions(stats, root_structure)
            }
            
            return {
                "status": "success",
                "message": "分析完成",
                "data": {
                    "filename": os.path.basename(filepath),
                    "structure_analysis": analysis,
                },
                "stats": stats,
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _count_leaf_nodes(self, structure: Dict[str, Any]) -> int:
        """计算叶子节点数量"""
        if not structure.get('children'):
            return 1
        
        count = 0
        for child in structure.get('children', []):
            if not child.get('children'):
                count += 1
            else:
                count += self._count_leaf_nodes(child)
        return count
    
    def _calculate_complexity(self, stats: Dict[str, Any]) -> str:
        """计算复杂度"""
        total_nodes = stats.get('total_nodes', 0)
        max_depth = stats.get('max_depth', 0)
        
        if total_nodes < 10:
            return "简单"
        elif total_nodes < 30:
            return "中等"
        elif total_nodes < 60:
            return "复杂"
        else:
            return "非常复杂"
    
    def _calculate_balance(self, root_topic: Dict[str, Any]) -> str:
        """计算平衡性"""
        children = root_topic.get('children', [])
        if len(children) <= 3:
            return "优秀"
        elif len(children) <= 5:
            return "良好"
        else:
            return "一般"
    
    def _calculate_completeness(self, root_topic: Dict[str, Any]) -> str:
        """计算完整性"""
        # 简化的完整性计算
        return "完整"
    
    def _generate_suggestions(self, stats: Dict[str, Any], root_topic: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if stats.get('max_depth', 0) > 4:
            suggestions.append("建议减少层级深度，保持3-4层最佳")
        
        if stats.get('total_nodes', 0) > 50:
            suggestions.append("节点较多，考虑拆分为多个思维导图")
        
        if not suggestions:
            suggestions.append("结构良好，无需优化")
        
        return suggestions

    # ===== 降级辅助：简易统计与层级限制 =====
    def _limit_depth(self, node: Dict[str, Any], max_depth: int, current_depth: int = 1) -> Dict[str, Any]:
        if not isinstance(node, dict):
            return {}
        res: Dict[str, Any] = {k: v for k, v in node.items() if k != 'children'}
        children = node.get('children')
        if isinstance(children, list) and current_depth < max_depth:
            res_children: List[Dict[str, Any]] = []
            for ch in children:
                if isinstance(ch, dict):
                    res_children.append(self._limit_depth(ch, max_depth, current_depth + 1))
            res['children'] = res_children
        # 超过最大层级，移除children以收敛结构
        return res

    def _count_nodes_simple(self, node: Dict[str, Any]) -> int:
        if not isinstance(node, dict) or not node:
            return 0
        cnt = 1
        children = node.get('children')
        if isinstance(children, list):
            for ch in children:
                if isinstance(ch, dict):
                    cnt += self._count_nodes_simple(ch)
        return cnt

    def _max_depth_simple(self, node: Dict[str, Any], current_depth: int = 1) -> int:
        if not isinstance(node, dict) or not node:
            return 0
        children = node.get('children')
        if not isinstance(children, list) or not children:
            return current_depth
        depths = [self._max_depth_simple(ch, current_depth + 1) for ch in children if isinstance(ch, dict)]
        return max(depths) if depths else current_depth

    def _titles_count_simple(self, node: Dict[str, Any]) -> int:
        if not isinstance(node, dict) or not node:
            return 0
        count = 1 if isinstance(node.get('title'), str) and node.get('title') else 0
        children = node.get('children')
        if isinstance(children, list):
            for ch in children:
                if isinstance(ch, dict):
                    count += self._titles_count_simple(ch)
        return count
    
    def convert_to_xmind(self, source_filepath: str, output_filepath: Optional[str] = None) -> ConvertResult:
        """转换文件为XMind"""
        try:
            if not os.path.exists(source_filepath):
                raise Exception(f"源文件不存在: {source_filepath}")
            
            # 输出路径必须由调用方提供（服务器层负责解析），引擎不再默认到相对 output 目录
            if not output_filepath:
                return {
                    "status": "error",
                    "message": "缺少输出路径：请提供绝对输出路径（由服务器层解析）"
                }
            
            # 使用转换器转换
            parser = ParserFactory.get_parser(source_filepath)
            json_structure = parser.parse()
            create_xmind_file(json_structure, output_filepath)
            success = True
            
            if success:
                return {
                    "status": "success",
                    "message": "文件转换成功",
                    "data": {
                        "source_file": source_filepath,
                        "output_file": output_filepath,
                    },
                }
            else:
                return {
                    "status": "error",
                    "message": "转换失败",
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def list_xmind_files(self, directory: str = ".", recursive: bool = True, pattern: Optional[str] = None, max_depth: Optional[int] = None) -> ListFilesResult:
        """列出XMind文件"""
        try:
            # 验证目录路径
            if not directory:
                directory = "."
            
            directory = os.path.abspath(directory)
            
            logger.info(f"开始列出XMind文件，目录: {directory}, 递归: {recursive}")
            
            if not os.path.exists(directory):
                return {
                    "status": "error",
                    "message": f"目录不存在: {directory}"
                }
            
            if not os.path.isdir(directory):
                return {
                    "status": "error",
                    "message": f"路径不是目录: {directory}"
                }
            
            xmind_files = []
            
            if recursive:
                # 递归搜索
                for root, dirs, files in os.walk(directory):
                    # 控制递归深度
                    if max_depth is not None:
                        rel_root = os.path.relpath(root, directory)
                        depth = 0 if rel_root == "." else (rel_root.count(os.sep) + 1)
                        if depth >= max_depth:
                            dirs[:] = []  # 不再深入子目录
                    for file in files:
                        if not file.endswith('.xmind'):
                            continue
                        # 模式匹配（可选）
                        try:
                            if pattern and not fnmatch.fnmatch(file, pattern):
                                continue
                        except Exception:
                            if pattern and (pattern not in file):
                                continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, directory)
                        xmind_files.append({
                            "name": file,
                            "path": full_path,
                            "relative_path": rel_path,
                            "size": os.path.getsize(full_path),
                            "modified": os.path.getmtime(full_path)
                        })
            else:
                # 仅搜索当前目录
                for file in os.listdir(directory):
                    if not file.endswith('.xmind'):
                        continue
                    # 模式匹配（可选）
                    try:
                        if pattern and not fnmatch.fnmatch(file, pattern):
                            continue
                    except Exception:
                        if pattern and (pattern not in file):
                            continue
                    full_path = os.path.join(directory, file)
                    xmind_files.append({
                        "name": file,
                        "path": full_path,
                        "relative_path": file,
                        "size": os.path.getsize(full_path),
                        "modified": os.path.getmtime(full_path)
                    })
            
            return {
                "status": "success",
                "message": "列出XMind文件完成",
                "data": {
                    "directory": directory,
                    "recursive": recursive,
                    "pattern": pattern,
                    "max_depth": max_depth,
                    "file_count": len(xmind_files),
                    "files": xmind_files,
                },
            }
            
        except Exception as e:
            logger.error(f"列出XMind文件失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }


# 全局引擎实例
_engine = None

def get_engine() -> XMindCoreEngine:
    """获取全局引擎实例"""
    global _engine
    if _engine is None:
        _engine = XMindCoreEngine()
    return _engine


# 工具函数
def read_xmind_file(filepath: str) -> Dict[str, Any]:
    """读取XMind文件"""
    return get_engine().read_xmind_file(filepath)

def create_mind_map(title: str, topics_json: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """创建思维导图"""
    return get_engine().create_mind_map(title, topics_json, output_path)

def analyze_mind_map(filepath: str) -> Dict[str, Any]:
    """分析思维导图"""
    return get_engine().analyze_mind_map(filepath)

def convert_to_xmind(source_filepath: str, output_filepath: Optional[str] = None) -> Dict[str, Any]:
    """转换文件为XMind"""
    return get_engine().convert_to_xmind(source_filepath, output_filepath)

def list_xmind_files(directory: str = ".", recursive: bool = True, pattern: Optional[str] = None, max_depth: Optional[int] = None) -> Dict[str, Any]:
    """列出XMind文件"""
    return get_engine().list_xmind_files(directory, recursive, pattern, max_depth)

def get_available_tools() -> List[Dict[str, Any]]:
    """获取可用工具列表"""
    return [
        {
            "name": "read_xmind_file",
            "description": "读取XMind文件内容",
            "parameters": {
                "filepath": {"type": "string", "description": "XMind文件路径"}
            }
        },
        {
            "name": "create_mind_map",
            "description": "创建新的思维导图",
            "parameters": {
                "title": {"type": "string", "description": "思维导图标题"},
                "topics_json": {"type": "string", "description": "主题JSON结构"}
            }
        },
        {
            "name": "analyze_mind_map",
            "description": "分析思维导图结构",
            "parameters": {
                "filepath": {"type": "string", "description": "XMind文件路径"}
            }
        },
        {
            "name": "convert_to_xmind",
            "description": "转换文件为XMind格式（源文件路径必须为绝对路径）",
            "parameters": {
                "source_filepath": {"type": "string", "description": "源文件绝对路径"},
                "output_filepath": {"type": "string", "description": "输出文件路径（可选）"}
            }
        },
        {
            "name": "list_xmind_files",
            "description": "列出XMind文件",
            "parameters": {
                "directory": {"type": "string", "description": "搜索目录"},
                "recursive": {"type": "boolean", "description": "是否递归搜索"}
            }
        }
    ]


if __name__ == "__main__":
    # 测试引擎
    engine = get_engine()
    
    # 测试读取文件
    print("测试读取XMind文件...")
    result = engine.read_xmind_file("test_outline.xmind")
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("\n测试完成！")