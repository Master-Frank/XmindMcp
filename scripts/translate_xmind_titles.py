#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate XMind titles to English while preserving structure.

Usage:
  python scripts/translate_xmind_titles.py <input_xmind_path> [output_xmind_path]

- Extracts all unique <title> texts from content.xml inside the .xmind file
- Saves extracted titles to output/<basename>_titles.json
- If output_xmind_path is provided, attempts translation using deep-translator (preferred)
  and falls back to googletrans if available, then writes a new .xmind with only titles replaced.

Requirements:
  pip install deep-translator==1.11.4 (preferred)
  or
  pip install googletrans==4.0.0-rc1 (fallback)
"""

import sys
import os
import json
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

NAMESPACE = {
    'xmap': 'urn:xmind:xmap:xmlns:content:2.0',
    'fo': 'http://www.w3.org/1999/XSL/Format',
    'svg': 'http://www.w3.org/2000/svg',
    'xhtml': 'http://www.w3.org/1999/xhtml',
    'xlink': 'http://www.w3.org/1999/xlink',
}

ET.register_namespace('', NAMESPACE['xmap'])
ET.register_namespace('fo', NAMESPACE['fo'])
ET.register_namespace('svg', NAMESPACE['svg'])
ET.register_namespace('xhtml', NAMESPACE['xhtml'])
ET.register_namespace('xlink', NAMESPACE['xlink'])


def extract_titles_from_content_xml(xml_text: str):
    """Return a sorted list of unique titles from content.xml."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise RuntimeError(f"XML parse error: {e}")

    titles = []
    for title_el in root.findall('.//{urn:xmind:xmap:xmlns:content:2.0}title'):
        if title_el.text is not None:
            t = title_el.text.strip()
            if t:
                titles.append(t)
    # unique and sorted for easier human translation review
    uniq = sorted(list(set(titles)))
    return uniq


def read_content_xml(xmind_path: Path) -> str:
    with zipfile.ZipFile(str(xmind_path), 'r') as zf:
        names = zf.namelist()
        if 'content.xml' not in names:
            raise FileNotFoundError('content.xml not found in XMind archive')
        return zf.read('content.xml').decode('utf-8')


def write_translated_xmind(original_xmind: Path, output_xmind: Path, translated_xml: bytes):
    """Copy all entries from original .xmind, replacing content.xml with translated_xml."""
    output_xmind.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(original_xmind), 'r') as src:
        with zipfile.ZipFile(str(output_xmind), 'w', compression=zipfile.ZIP_DEFLATED) as dst:
            for item in src.infolist():
                if item.filename == 'content.xml':
                    dst.writestr('content.xml', translated_xml)
                else:
                    data = src.read(item.filename)
                    dst.writestr(item, data)


def _translate_text(translator, text: str) -> str:
    """Translate text to English using provided translator, handling different APIs."""
    try:
        # deep-translator: GoogleTranslator(source='auto', target='en').translate(text)
        return translator.translate(text)
    except TypeError:
        # googletrans: Translator().translate(text, src='zh-CN', dest='en').text
        try:
            res = translator.translate(text, src='zh-CN', dest='en')
            return getattr(res, 'text', res)
        except Exception:
            return text
    except Exception:
        return text


def apply_translation_to_titles(xml_text: str, translator) -> bytes:
    """Translate all <title> element texts and return updated XML bytes with declaration."""
    root = ET.fromstring(xml_text)
    for title_el in root.findall('.//{urn:xmind:xmap:xmlns:content:2.0}title'):
        if title_el.text and title_el.text.strip():
            src_text = title_el.text.strip()
            try:
                # Avoid translating already-English-like strings (without any CJK characters)
                if any(ch.isalpha() for ch in src_text) and not any('\u4e00' <= ch <= '\u9fff' for ch in src_text):
                    new_text = src_text
                else:
                    new_text = _translate_text(translator, src_text)
            except Exception:
                new_text = src_text  # fallback
            title_el.text = new_text
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/translate_xmind_titles.py <input_xmind_path> [output_xmind_path]")
        sys.exit(1)

    # Use relative paths per project rule: no absolute paths
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(2)

    # Read content.xml and extract titles
    xml_text = read_content_xml(input_path)
    titles = extract_titles_from_content_xml(xml_text)

    # Keep output directory relative to project root
    out_dir = Path('output')
    out_dir.mkdir(parents=True, exist_ok=True)
    titles_json_path = out_dir / f"{input_path.stem}_titles.json"
    with open(titles_json_path, 'w', encoding='utf-8') as f:
        json.dump({"count": len(titles), "titles": titles}, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Extracted {len(titles)} unique titles -> {titles_json_path}")

    # If output path provided, perform translation using deep-translator or googletrans
    if len(sys.argv) >= 3:
        # Output path should remain relative
        output_path = Path(sys.argv[2])
        translator = None
        try:
            from deep_translator import GoogleTranslator  # type: ignore
            translator = GoogleTranslator(source='auto', target='en')
            print("[INFO] Using deep-translator (GoogleTranslator)")
        except Exception:
            try:
                from googletrans import Translator  # type: ignore
                translator = Translator()
                print("[INFO] Using googletrans (Translator)")
            except Exception:
                print("[WARN] No translator available. Install deep-translator or googletrans.")
                sys.exit(0)

        translated_xml = apply_translation_to_titles(xml_text, translator)
        write_translated_xmind(input_path, output_path, translated_xml)
        print(f"[SUCCESS] Wrote translated XMind: {output_path}")
        print("[NOTE] Only titles were translated; other metadata preserved.")


if __name__ == '__main__':
    main()