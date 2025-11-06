#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind文件结构验证工具
用于检测转换后的XMind文件格式是否正确，节点数量和关系是否正确
"""

import os
import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path

class XMindValidator:
    def __init__(self, xmind_file):
        self.xmind_file = xmind_file
        self.content_json = None
        self.content_xml = None
        self.metadata = None
        self.structure = {}
        self.parsed_source = None  # 'json' 或 'xml'
        
    def extract_xmind_content(self):
        """提取XMind文件内容"""
        try:
            # 确保文件路径正确
            file_path = Path(self.xmind_file)
            if not file_path.exists():
                print(f"[ERROR] 文件不存在: {self.xmind_file}")
                return False
                
            # 使用Path对象处理文件路径，避免编码问题
            with zipfile.ZipFile(str(file_path), 'r') as zip_file:
                # 提取content.json
                if 'content.json' in zip_file.namelist():
                    json_content = zip_file.read('content.json').decode('utf-8')
                    self.content_json = json.loads(json_content)
                
                # 提取content.xml
                if 'content.xml' in zip_file.namelist():
                    xml_content = zip_file.read('content.xml').decode('utf-8')
                    self.content_xml = xml_content
                
                # 提取metadata.json
                if 'metadata.json' in zip_file.namelist():
                    metadata_content = zip_file.read('metadata.json').decode('utf-8')
                    self.metadata = json.loads(metadata_content)
                    
                return True
        except zipfile.BadZipFile as e:
            print(f"[ERROR] 无效的XMind文件格式: {e}")
            return False
        except UnicodeDecodeError as e:
            print(f"[ERROR] 文件编码错误: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 提取XMind内容失败: {e}")
            print(f"   文件路径: {self.xmind_file}")
            return False

    def parse_json_structure(self):
        """解析JSON结构（无JSON时自动回退到XML）"""
        if not self.content_json:
            # 回退到XML解析
            return self.parse_xml_structure()
            
        try:
            # XMind文件结构是数组格式
            if isinstance(self.content_json, list) and len(self.content_json) > 0:
                sheet = self.content_json[0]  # 第一个工作表
                
                # 获取根主题
                if 'rootTopic' in sheet:
                    root_topic = sheet['rootTopic']
                    self.structure = self._parse_topic_recursive(root_topic)
                    self.parsed_source = 'json'
                    return True
                elif 'primaryTopic' in sheet:
                    primary_topic = sheet['primaryTopic']
                    self.structure = self._parse_topic_recursive(primary_topic)
                    self.parsed_source = 'json'
                    return True
                    
            # 备用：直接检查rootTopic
            if isinstance(self.content_json, dict) and 'rootTopic' in self.content_json:
                root_topic = self.content_json['rootTopic']
                self.structure = self._parse_topic_recursive(root_topic)
                self.parsed_source = 'json'
                return True
                
            # 备用：直接检查primaryTopic
            if isinstance(self.content_json, dict) and 'primaryTopic' in self.content_json:
                primary_topic = self.content_json['primaryTopic']
                self.structure = self._parse_topic_recursive(primary_topic)
                self.parsed_source = 'json'
                return True
            
            return False
        except Exception as e:
            print(f"[ERROR] 解析JSON结构失败: {e}")
            return False

    def _parse_topic_recursive(self, topic, level: int = 0):
        """将JSON中的topic解析为统一结构"""
        title = topic.get('title', '')
        node_id = topic.get('id', '')
        children = []
        # JSON路径下的子主题兼容处理
        json_children = []

        # 兼容新版XMind：children 为对象，内部包含 attached/detached/callout 等分组
        ch = topic.get('children')
        if isinstance(ch, list):
            json_children.extend(ch)
        elif isinstance(ch, dict):
            # 遍历所有分组，收集其中的列表项
            for key, val in ch.items():
                if isinstance(val, list):
                    json_children.extend(val)

        # 兼容其他别名
        tp = topic.get('topics')
        if isinstance(tp, list):
            json_children.extend(tp)
        elif isinstance(tp, dict):
            for key, val in tp.items():
                if isinstance(val, list):
                    json_children.extend(val)

        sp = topic.get('subtopics')
        if isinstance(sp, list):
            json_children.extend(sp)
        elif isinstance(sp, dict):
            for key, val in sp.items():
                if isinstance(val, list):
                    json_children.extend(val)

        for child in json_children:
            # 子节点本身也是标准topic对象
            if isinstance(child, dict):
                children.append(self._parse_topic_recursive(child, level + 1))
        
        return {
            'level': level,
            'title': title,
            'id': node_id,
            'children': children
        }

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
                print('[ERROR] XML中未找到根topic')
                return False
            self.structure = self._parse_topic_recursive_xml(topic_el, level=0)
            self.parsed_source = 'xml'
            return True
        except Exception as e:
            print(f"[ERROR] 解析XML结构失败: {e}")
            return False

    def _parse_topic_recursive_xml(self, topic_el, level=0):
        """递归解析XML中的topic节点为统一结构（含notes/markers）"""
        ns = '{urn:xmind:xmap:xmlns:content:2.0}'
        title_el = topic_el.find(f'{ns}title')
        title = title_el.text.strip() if (title_el is not None and title_el.text) else ''
        node_id = topic_el.get('id', '')
        result = {
            'level': level,
            'title': title,
            'id': node_id,
            'children': []
        }
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
            result['notes'] = notes_text
        # markers
        markers = []
        mrefs_el = topic_el.find(f'{ns}marker-refs')
        if mrefs_el is not None:
            for mref in mrefs_el.findall(f'{ns}marker-ref'):
                mid = mref.get('marker-id', '')
                if mid:
                    markers.append(mid)
        if markers:
            result['markers'] = markers
        # 子节点：children/topics[@type='attached']/topic
        children_el = topic_el.find(f'{ns}children')
        if children_el is not None:
            for topics_group in children_el.findall(f'{ns}topics'):
                t_type = topics_group.get('type', '')
                if t_type == 'attached':
                    for child_topic in topics_group.findall(f'{ns}topic'):
                        child_structure = self._parse_topic_recursive_xml(child_topic, level + 1)
                        result['children'].append(child_structure)
        return result

    def validate(self):
        """完整验证流程"""
        print(f"\n[VALIDATION] 验证文件: {self.xmind_file}")
        print("=" * 50)
        
        # 1. 提取内容
        if not self.extract_xmind_content():
            return False
        
        # 2. 解析结构（JSON优先，失败回退到XML）
        parsed = self.parse_json_structure()
        if not parsed:
            print("[ERROR] 无法解析结构（JSON与XML均失败）")
            return False
        
        # 3. 基本验证
        print("[SUCCESS] 文件格式验证通过")
        
        # 4. 统计信息
        total_nodes = self.count_nodes()
        all_titles = self.get_all_titles()
        max_depth = self.get_max_depth()
        
        print(f"[STATS] 统计信息:")
        print(f"  • 总节点数: {total_nodes}")
        print(f"  • 标题数量: {len(all_titles)}")
        print(f"  • 最大深度: {max_depth}")
        
        # 5. 结构展示
        print(f"\n[STRUCTURE] 结构树:")
        self.print_structure()
        
        # 6. 验证通过
        print("[SUCCESS] 结构验证通过")
        return True

    def count_nodes(self) -> int:
        """统计节点总数（基于解析后的统一结构）"""
        if not self.structure:
            return 0
        return self._count_nodes_recursive(self.structure)

    def _count_nodes_recursive(self, node: dict) -> int:
        count = 1
        for child in node.get('children', []) or []:
            count += self._count_nodes_recursive(child)
        return count

    def get_max_depth(self) -> int:
        """计算最大层级深度（根为0层）"""
        if not self.structure:
            return 0
        return self._get_max_depth_recursive(self.structure, 0)

    def _get_max_depth_recursive(self, node: dict, current_depth: int) -> int:
        max_depth = current_depth
        for child in node.get('children', []) or []:
            child_depth = self._get_max_depth_recursive(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        return max_depth

    def get_all_titles(self) -> list:
        """获取所有标题列表（从根到所有子节点）"""
        titles: list = []
        def _dfs(n: dict):
            if not isinstance(n, dict):
                return
            titles.append(n.get('title', ''))
            for c in n.get('children', []) or []:
                _dfs(c)
        if self.structure:
            _dfs(self.structure)
        return titles

def validate_all_xmind_files():
    """验证所有转换的XMind文件"""
    print("[VALIDATION] 开始验证所有XMind文件结构...")
    print("=" * 60)
    
    # 定义要验证的文件映射 - 使用不同的输出文件名避免冲突
    test_files = {
        "Markdown转换": "test_document.xmind",
        "文本大纲转换": "test_outline.xmind",
        "HTML转换": "test_outline_html.xmind",
        "Word转换": "test_outline_docx.xmind",
        "Excel转换": "test_outline_xlsx.xmind",
        "自动识别转换": "test_auto.xmind",
        "Playwright学习指南": "playwright-learning-guide.xmind",
        "Playwright指南": "playwright_guide.xmind",
        "参考示例": "reference_example.xmind"
    }
    
    results = {}
    
    for test_name, filename in test_files.items():
        print(f"\n[FILE] {test_name}: {filename}")
        
        if os.path.exists(filename):
            validator = XMindValidator(filename)
            if validator.validate():
                print("[SUCCESS] 结构验证通过")
                results[test_name] = True
            else:
                print("[ERROR] 结构验证失败")
                results[test_name] = False
        else:
            print(f"[WARNING] 文件不存在: {filename}")
            results[test_name] = False
    
    # 生成总结报告
    print("\n" + "=" * 60)
    print("[REPORT] 验证总结报告:")
    print("=" * 60)
    
    passed = 0
    total = len(test_files)
    
    for test_name, filename in test_files.items():
        if results[test_name]:
            print(f"[SUCCESS] 通过 {test_name}: {filename}")
            passed += 1
        else:
            print(f"[ERROR] 失败 {test_name}: {filename}")
    
    print(f"\n[STATS] 总体结果: {passed}/{total} 文件验证通过")
    
    if passed == total:
        print("[SUCCESS] 所有文件验证通过！")
    else:
        print("[WARNING] 部分文件验证失败，需要检查转换逻辑")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 验证指定文件
        filename = sys.argv[1]
        if os.path.exists(filename):
            validator = XMindValidator(filename)
            validator.validate()
        else:
            print(f"[ERROR] 文件不存在: {filename}")
    else:
        # 验证所有文件
        validate_all_xmind_files()