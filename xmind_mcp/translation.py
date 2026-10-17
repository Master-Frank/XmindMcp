"""Title translation provider and archive-preserving application operation."""
from dataclasses import dataclass
import io
import json
from pathlib import Path
from typing import Protocol
import xml.etree.ElementTree as ET
import zipfile

from .errors import XMindError
from .xmind_io.writer import write_xmind_bytes


class Translator(Protocol):
    def translate(self, text: str) -> str: ...


def default_translator(target_lang):
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source='auto', target=target_lang)


@dataclass(frozen=True)
class TranslationResult:
    translated_titles: int


def translate_archive(source: Path, output: Path, target_lang="en", overwrite=False,
                      translator_factory=default_translator) -> TranslationResult:
    if output.exists() and not overwrite:
        raise XMindError(f"输出文件已存在: {output}. 需设置 overwrite=True", "output_exists")
    translator = translator_factory(target_lang)
    cache = {}
    count = 0

    def translate(text):
        if not text or not any(ord(char) > 127 for char in text):
            return text
        if text not in cache:
            try:
                cache[text] = translator.translate(text) or text
            except Exception:
                cache[text] = text
        return cache[text]

    replacements = {}
    with zipfile.ZipFile(source) as archive:
        if 'content.json' in archive.namelist():
            data = json.loads(archive.read('content.json').decode('utf-8'))
            stack = [data]
            while stack:
                node = stack.pop()
                if isinstance(node, list):
                    stack.extend(node)
                elif isinstance(node, dict):
                    if isinstance(node.get('title'), str):
                        old = node['title'].strip()
                        new = translate(old)
                        if new != old:
                            node['title'] = new
                            count += 1
                    for segment in node.get('attributedTitle', []) or []:
                        if isinstance(segment, dict) and isinstance(segment.get('text'), str):
                            old = segment['text'].strip()
                            new = translate(old)
                            if new != old:
                                segment['text'] = new
                                count += 1
                    stack.extend(value for value in node.values() if isinstance(value, (dict, list)))
            replacements['content.json'] = json.dumps(data, ensure_ascii=False).encode('utf-8')
        elif 'content.xml' in archive.namelist():
            root = ET.fromstring(archive.read('content.xml'))
            for element in root.findall('.//{urn:xmind:xmap:xmlns:content:2.0}title'):
                old = (element.text or '').strip()
                new = translate(old)
                if new != old:
                    element.text = new
                    count += 1
            replacements['content.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        else:
            raise XMindError("XMind中未找到 content.json 或 content.xml", "invalid_format")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as translated:
            for info in archive.infolist():
                content = replacements[info.filename] if info.filename in replacements else archive.read(info)
                translated.writestr(info, content)
    write_xmind_bytes(buffer.getvalue(), output)
    return TranslationResult(count)
