from pathlib import Path
from .base import BaseParser, create_topic, create_document
from ..models import Document, build_heading_tree


def _lazy_import_beautifulsoup():
    try:
        from bs4 import BeautifulSoup
        return BeautifulSoup
    except Exception as e:
        raise ImportError("需要安装BeautifulSoup4: pip install beautifulsoup4") from e


class HtmlParser(BaseParser):
    """HTML文件解析器"""

    def __init__(self, file_path):
        super().__init__(file_path)

    def parse(self) -> Document:
        """解析HTML文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        BeautifulSoup = _lazy_import_beautifulsoup()
        soup = BeautifulSoup(content, 'html.parser')
        title = self.extract_title(soup)

        headings = ((int(heading.name[1]), heading.get_text().strip())
                    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
        root_children = build_heading_tree(headings)

        # 如果没有找到标题，尝试列表结构
        if not root_children:
            root_children = self.parse_lists(soup)

        return create_document(title, root_children)

    def extract_title(self, soup):
        """提取标题"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()

        return Path(self.file_path).stem

    def parse_lists(self, soup):
        """解析列表结构"""
        def parse_list_items(items, level=0):
            topics = []
            for item in items:
                text = item.get_text().strip()
                if text:
                    topic = create_topic(text)

                    # 查找子列表
                    sublist = item.find(['ul', 'ol'])
                    if sublist:
                        sub_items = sublist.find_all('li', recursive=False)
                        if sub_items:
                            sub_topics = parse_list_items(sub_items, level + 1)
                            if sub_topics:
                                topic.children = sub_topics

                    topics.append(topic)
            return topics

        # 查找顶级列表
        root_topics = []
        for list_tag in soup.find_all(['ul', 'ol']):
            # 只处理顶级列表（不在其他列表内的）
            if not list_tag.find_parent(['ul', 'ol']):
                items = list_tag.find_all('li', recursive=False)
                if items:
                    root_topics.extend(parse_list_items(items))

        return root_topics
