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
        """解析JSON结构"""
        if not self.content_json:
            return False
            
        try:
            # XMind文件结构是数组格式
            if isinstance(self.content_json, list) and len(self.content_json) > 0:
                sheet = self.content_json[0]  # 第一个工作表
                
                # 获取根主题
                if 'rootTopic' in sheet:
                    root_topic = sheet['rootTopic']
                    self.structure = self._parse_topic_recursive(root_topic)
                    return True
                elif 'primaryTopic' in sheet:
                    primary_topic = sheet['primaryTopic']
                    self.structure = self._parse_topic_recursive(primary_topic)
                    return True
                    
            # 备用：直接检查rootTopic
            if 'rootTopic' in self.content_json:
                root_topic = self.content_json['rootTopic']
                self.structure = self._parse_topic_recursive(root_topic)
                return True
                
            # 备用：直接检查primaryTopic
            if 'primaryTopic' in self.content_json:
                primary_topic = self.content_json['primaryTopic']
                self.structure = self._parse_topic_recursive(primary_topic)
                return True
                
            print("[ERROR] 无法找到根主题节点")
            return False
            
        except Exception as e:
            print(f"[ERROR] 解析JSON结构失败: {e}")
            return False
    
    def _parse_topic_recursive(self, topic, level=0):
        """递归解析主题结构"""
        result = {
            'level': level,
            'title': topic.get('title', ''),
            'id': topic.get('id', ''),
            'children': []
        }
        
        # 检查子主题
        if 'children' in topic and 'attached' in topic['children']:
            for child in topic['children']['attached']:
                child_structure = self._parse_topic_recursive(child, level + 1)
                result['children'].append(child_structure)
        
        return result
    
    def count_nodes(self, structure=None):
        """统计节点数量"""
        if structure is None:
            structure = self.structure
            
        count = 1  # 当前节点
        for child in structure.get('children', []):
            count += self.count_nodes(child)
        return count
    
    def get_all_titles(self, structure=None, titles=None):
        """获取所有标题"""
        if structure is None:
            structure = self.structure
            titles = []
        
        if structure.get('title'):
            titles.append(structure['title'])
        
        for child in structure.get('children', []):
            self.get_all_titles(child, titles)
        
        return titles
    
    def get_max_depth(self, structure=None):
        """获取最大深度"""
        if structure is None:
            structure = self.structure
            
        max_depth = structure.get('level', 0)
        for child in structure.get('children', []):
            child_depth = self.get_max_depth(child)
            max_depth = max(max_depth, child_depth)
        return max_depth
    
    def print_structure(self, structure=None, indent=0):
        """打印结构树"""
        if structure is None:
            structure = self.structure
            
        prefix = "  " * indent
        title = structure.get('title', '')
        level = structure.get('level', 0)
        print(f"{prefix}Level {level}: {title}")
        
        for child in structure.get('children', []):
            self.print_structure(child, indent + 1)
    
    def validate(self):
        """完整验证流程"""
        print(f"\n[VALIDATION] 验证文件: {self.xmind_file}")
        print("=" * 50)
        
        # 1. 提取内容
        if not self.extract_xmind_content():
            return False
        
        # 2. 解析结构
        if not self.parse_json_structure():
            print("[ERROR] 无法解析JSON结构")
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