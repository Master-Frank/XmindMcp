from pathlib import Path
from .base import BaseParser
from .markdown import MarkdownParser
from .text import TextOutlineParser
from .html import HtmlParser
from .word import WordParser
from .excel import ExcelParser


DEFAULT_PARSERS = {
    '.md': MarkdownParser,
    '.markdown': MarkdownParser,
    '.txt': TextOutlineParser,
    '.text': TextOutlineParser,
    '.html': HtmlParser,
    '.htm': HtmlParser,
    '.docx': WordParser,
    '.xlsx': ExcelParser,
    '.xls': ExcelParser,
}


def detect_file_type(file_path):
    """检测文件类型（通过扩展名和内容）"""
    ext = Path(file_path).suffix.lower()

    # 如果有扩展名，优先使用扩展名
    if ext:
        return ext

    # 没有扩展名时，通过内容检测
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # 读取前1000字符

            # HTML检测
            if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
                return '.html'

            # Markdown检测
            if any(line.strip().startswith('#') for line in content.split('\n')[:10]):
                return '.md'

            # OPML检测
            if '<opml' in content.lower():
                return '.opml'

            # 文本大纲检测（有缩进结构）
            lines = content.split('\n')[:20]
            indent_chars = ['  ', '\t', '·', '•', '-']
            if any(any(line.startswith(char) for char in indent_chars) for line in lines if line.strip()):
                return '.txt'

            # 默认文本
            return '.txt'

    except Exception:
        return '.txt'


class ParserRegistry:
    """Instance-local extensions, preventing one server from changing another."""
    def __init__(self, parsers=None):
        self.parsers = dict(DEFAULT_PARSERS if parsers is None else parsers)

    def register(self, extension, parser):
        if not extension.startswith('.') or not issubclass(parser, BaseParser):
            raise ValueError("解析器必须继承BaseParser，扩展名必须以点开头")
        self.parsers[extension.lower()] = parser

    def get_parser(self, file_path):
        extension = detect_file_type(file_path)
        if extension not in self.parsers:
            raise ValueError(f"不支持的文件格式: {extension}")
        return self.parsers[extension](file_path)

    def get_supported_formats(self):
        return list(self.parsers)
