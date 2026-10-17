from pathlib import Path
from .base import BaseParser, create_document
from ..models import Document, build_heading_tree


def _lazy_import_openpyxl():
    try:
        import importlib
        return importlib.import_module('openpyxl')
    except Exception as e:
        raise ImportError("需要安装openpyxl: pip install openpyxl") from e


class ExcelParser(BaseParser):
    """Excel文件解析器"""

    def __init__(self, file_path):
        super().__init__(file_path)

    def parse(self) -> Document:
        """解析Excel文件"""
        openpyxl = _lazy_import_openpyxl()
        wb = openpyxl.load_workbook(self.file_path)

        try:
            # 使用第一个工作表
            ws = wb.active
            title = self.extract_title(ws)

            # 按层级组织数据
            headings = []

            for row in ws.iter_rows(min_row=1, values_only=True):
                if not row or not row[0]:
                    continue

                # 尝试不同的解析策略
                level, text = self.parse_row(row)
                if text:
                    headings.append((level, text))

            return create_document(title, build_heading_tree(headings))
        finally:
            wb.close()

    def extract_title(self, worksheet):
        """提取标题"""
        # 使用工作表名称
        title = worksheet.title

        # 或者使用第一个非空单元格
        if not title or title == 'Sheet1':
            for row in worksheet.iter_rows(min_row=1, max_row=1, values_only=True):
                for cell in row:
                    if cell:
                        title = str(cell)
                        break

        return title or Path(self.file_path).stem

    def parse_row(self, row):
        """解析行数据"""
        # 策略1: 第一列是层级，第二列是内容
        if len(row) >= 2:
            try:
                level = int(row[0]) if isinstance(row[0], (int, float)) else 0
                text = str(row[1]) if row[1] else ""
                return level, text.strip()
            except (ValueError, TypeError):
                pass

        # 策略2: 按缩进或特殊字符判断
        text = str(row[0]) if row[0] else ""
        level = 0

        # 计算前导空格或特殊字符
        stripped = text.lstrip()
        if stripped != text:
            indent = len(text) - len(stripped)
            level = indent // 2  # 每2个空格一级
            text = stripped.strip('-*•→')

        return level, text.strip()
