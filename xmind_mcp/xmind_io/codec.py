"""Conversions at the XMind JSON boundary; no wire format leaks into parsers."""
from copy import deepcopy
from ..models import Document, Topic
from .style import create_json_structure as default_sheet


def topic_to_mapping(topic: Topic) -> dict:
    result = deepcopy(topic.extra)
    result.update(id=topic.id, title=topic.title)
    groups = {}
    for child in topic.children:
        groups.setdefault(child.group, []).append(topic_to_mapping(child))
    if groups:
        result["children"] = groups
    return result


def document_to_sheet(document: Document) -> dict:
    # Preserve a loaded document's presentation; only new documents use the default theme.
    result = deepcopy(document.extra) if document.extra else default_sheet(document.root.title, [])
    root = topic_to_mapping(document.root)
    if not document.extra:
        root = {**result.get("rootTopic", {}), **root}
    result.update(id=document.id, title=document.sheet_title, rootTopic=root)
    return result

