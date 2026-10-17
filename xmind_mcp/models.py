"""Transport- and file-format-independent document model and tree operations."""
from dataclasses import dataclass, field, asdict
from typing import Any, Iterator
from uuid import uuid4

from .errors import XMindError


def generate_id() -> str:
    return uuid4().hex


@dataclass
class Topic:
    title: str
    children: list["Topic"] = field(default_factory=list)
    id: str = field(default_factory=generate_id)
    extra: dict[str, Any] = field(default_factory=dict)
    group: str = "attached"


@dataclass
class Document:
    root: Topic
    sheet_title: str = "画布 1"
    id: str = field(default_factory=generate_id)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReadLimits:
    max_content_bytes: int = 200 * 1024 * 1024
    max_nodes: int = 50000
    max_depth: int = 30

    def __post_init__(self):
        if self.max_content_bytes < 1 or self.max_nodes < 1 or self.max_depth < 0:
            raise ValueError("读取预算要求：大小和节点数大于0，深度不小于0")


@dataclass
class Stats:
    total_nodes: int = 0
    max_depth: int = 0
    titles_count: int = 0
    leaf_nodes: int = 0
    branch_count: int = 0

    def as_dict(self, *, analysis=False):
        result = asdict(self)
        if not analysis:
            result.pop("leaf_nodes")
            result.pop("branch_count")
        return result


def walk_topics(root: Topic) -> Iterator[tuple[Topic, int]]:
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        yield node, depth
        stack.extend((child, depth + 1) for child in reversed(node.children))


def collect_stats(root: Topic) -> Stats:
    stats = Stats(branch_count=len(root.children))
    for node, depth in walk_topics(root):
        stats.total_nodes += 1
        stats.titles_count += 1
        stats.max_depth = max(stats.max_depth, depth)
        stats.leaf_nodes += not node.children
    return stats


def build_heading_tree(headings) -> list[Topic]:
    roots, stack = [], []
    for level, title in headings:
        if not title:
            continue
        node = Topic(title)
        while stack and stack[-1][0] >= level:
            stack.pop()
        (stack[-1][1].children if stack else roots).append(node)
        stack.append((level, node))
    return roots


ALIASES = ("children", "topics", "subtopics", "nodes", "items")


def normalize_topics(value) -> list[Topic]:
    """Normalize public input aliases once, preserving non-structural fields."""
    if not isinstance(value, list):
        value = [value]
    result = []
    for item in value:
        if not isinstance(item, dict):
            result.append(Topic(str(item)))
            continue
        title = item.get("title") or item.get("name") or item.get("text") or ""
        node = Topic(str(title), id=str(item.get("id") or generate_id()),
                     extra={k: v for k, v in item.items() if k not in (*ALIASES, "title", "name", "text", "id", "level")})
        raw_children = next((item[key] for key in ALIASES if item.get(key)), [])
        groups = raw_children.items() if isinstance(raw_children, dict) else [("attached", raw_children)]
        for group, children in groups:
            if not isinstance(children, list):
                raise XMindError("子主题必须为数组")
            normalized = normalize_topics(children)
            for child in normalized:
                child.group = group
            node.children.extend(normalized)
        result.append(node)
    return result


def topic_structure(root: Topic) -> dict:
    """Existing read response format, serialized only at the public boundary."""
    result = {"level": 0, "title": root.title, "id": root.id, "children": []}
    stack = [(root, result, 0)]
    while stack:
        node, target, depth = stack.pop()
        for key in ("notes", "markers"):
            if key in node.extra:
                target[key] = node.extra[key]
        for child in node.children:
            output = {"level": depth + 1, "title": child.title, "id": child.id, "children": []}
            target["children"].append(output)
            stack.append((child, output, depth + 1))
    return result
