from pathlib import Path
from .base import BaseParser, create_document
from ..models import Document, build_heading_tree


class TextOutlineParser(BaseParser):
    """文本大纲解析器 - 支持缩进层级"""

    def parse(self) -> Document:
        """解析文本大纲文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        title = self.extract_title(lines)

        # 构建层级结构
        headings = []

        # 跳过标题行（如果标题行存在）
        title_found = False
        for line in lines:
            line = line.rstrip('\n\r')
            if not line.strip():
                continue

            # 检查是否是标题行
            stripped_line = line.lstrip()
            if stripped_line.strip() == title.strip() and not title_found:
                title_found = True
                continue  # 跳过标题行

            # 计算缩进级别
            indent_level = len(line) - len(stripped_line)
            level = self.indent_to_level(indent_level)
            title_text = stripped_line.strip('-*• ')

            if not title_text:
                continue

            headings.append((level, title_text))

        return create_document(title, build_heading_tree(headings))

    def indent_to_level(self, indent):
        """将缩进转换为层级"""
        # 假设每4个空格或1个制表符为一级
        return indent // 4

    def extract_title(self, lines):
        """提取标题"""
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith((' ', '\t', '-', '*', '•')):
                return stripped
        return Path(self.file_path).stem
