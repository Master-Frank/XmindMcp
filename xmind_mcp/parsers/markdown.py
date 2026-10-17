from pathlib import Path
import re
from .base import BaseParser, create_document
from ..models import Document, build_heading_tree


class MarkdownParser(BaseParser):
    """Markdown文件解析器"""

    def parse(self) -> Document:
        """解析Markdown文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        title = self.extract_title_from_content(lines)

        headings = []
        title_extracted = False
        for line in lines:
            match = re.match(r"^\s*(#{1,6})\s+(.+)$", line)
            if not match:
                continue
            level, text = len(match[1]), match[2].strip()
            if level == 1 and not title_extracted:
                title_extracted = True
                continue
            headings.append((level, text))
        return create_document(title, build_heading_tree(headings))

    def extract_title_from_content(self, lines):
        """从内容中提取标题"""
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return Path(self.file_path).stem

