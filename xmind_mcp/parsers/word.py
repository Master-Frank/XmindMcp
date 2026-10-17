from pathlib import Path
from .base import BaseParser, create_document
from ..models import Document, build_heading_tree


def _lazy_import_docx():
    try:
        import importlib
        return importlib.import_module('docx')
    except Exception as e:
        raise ImportError("需要安装python-docx: pip install python-docx") from e


class WordParser(BaseParser):
    """Word文档解析器"""

    def __init__(self, file_path):
        super().__init__(file_path)

    def parse(self) -> Document:
        """解析Word文档"""
        docx = _lazy_import_docx()
        doc = docx.Document(self.file_path)
        title = self.extract_title(doc)

        # 按段落解析
        headings = []

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue

            # 根据样式判断层级
            level = self.get_heading_level(paragraph)
            if level is not None:
                headings.append((level, text))

        return create_document(title, build_heading_tree(headings))

    def extract_title(self, doc):
        """提取标题"""
        # 尝试从属性中获取
        if doc.core_properties.title:
            return doc.core_properties.title

        # 查找第一个标题
        for paragraph in doc.paragraphs:
            if paragraph.style and 'Heading' in paragraph.style.name:
                return paragraph.text.strip()

        # 使用文件名
        return Path(self.file_path).stem

    def get_heading_level(self, paragraph):
        """获取段落标题级别"""
        if not paragraph.style:
            return None

        style_name = paragraph.style.name

        # Word标准标题样式
        if style_name.startswith('Heading '):
            try:
                level = int(style_name.split()[-1]) - 1
                return min(level, 5)  # 限制最大层级
            except ValueError:
                pass

        # 自定义标题样式
        heading_patterns = ['标题', 'Heading', 'head', 'title']
        for i, pattern in enumerate(heading_patterns):
            if pattern.lower() in style_name.lower():
                return i

        return None
