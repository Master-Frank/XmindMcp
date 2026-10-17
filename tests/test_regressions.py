"""Regression coverage for data integrity, hierarchy, resource budgets and release checks."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from xmind_mcp.models import Document, Topic, ReadLimits
from xmind_mcp.parsers.html import HtmlParser
from xmind_mcp.parsers.markdown import MarkdownParser
from xmind_mcp.service import XMindService
from xmind_mcp.settings import Settings
from xmind_mcp.xmind_io.codec import document_to_sheet
from xmind_mcp.xmind_io import writer


def load_root(path):
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read("content.json"))[0]["rootTopic"]


def children(node):
    return node.get("children", {}).get("attached", [])


def test_concurrent_same_title_preserves_each_tree(tmp_path):
    import threading
    barrier = threading.Barrier(2)
    engine = XMindService(Settings(tmp_path))

    def create(index):
        path = tmp_path / f"{index}.xmind"
        title = f"Unique {index} *\nsecond line"
        barrier.wait(timeout=5)
        response = engine.create_mind_map("Same title", json.dumps([
            {"title": title, "topics": [{"title": "grandchild"}]},
        ]), str(path))
        assert response["status"] == "success", response
        node = children(load_root(path))[0]
        assert node["title"] == title
        assert children(node)[0]["title"] == "grandchild"

    with ThreadPoolExecutor(2) as pool:
        list(pool.map(create, [1, 2]))
    assert sorted(p.name for p in tmp_path.iterdir()) == ["1.xmind", "2.xmind"]


@pytest.mark.parametrize("failure", ["serialize", "replace"])
def test_failed_write_preserves_original_and_cleans_temporary(tmp_path, monkeypatch, failure):
    target = tmp_path / "original.xmind"
    target.write_bytes(b"original data")

    def fail(*args):
        raise OSError("simulated write failure")

    if failure == "serialize":
        monkeypatch.setattr(writer, "generate_content_xml", fail)
    else:
        monkeypatch.setattr(writer.os, "replace", fail)
    with pytest.raises(OSError, match="simulated"):
        writer.create_xmind_file(Document(Topic("New")), target)
    assert target.read_bytes() == b"original data"
    assert list(tmp_path.iterdir()) == [target]


def test_successful_replacement_contains_valid_json_and_xml(tmp_path):
    import xml.etree.ElementTree as ET
    target = tmp_path / "map.xmind"
    target.write_bytes(b"old data")
    writer.create_xmind_file(Document(Topic("中文<&", [Topic("child")])), target)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        ET.fromstring(archive.read("content.xml"))
    assert load_root(target)["title"] == "中文<&"
    assert list(tmp_path.iterdir()) == [target]


def test_invalid_translated_archive_preserves_original(tmp_path):
    target = tmp_path / "translated.xmind"
    target.write_bytes(b"old data")
    with pytest.raises(zipfile.BadZipFile):
        writer.write_xmind_bytes(b"not a zip", target)
    assert target.read_bytes() == b"old data"
    assert list(tmp_path.iterdir()) == [target]


def test_html_heading_order_and_skipped_levels(tmp_path):
    source = tmp_path / "headings.html"
    source.write_text("<h1>A</h1><h2>A child</h2><h1>B</h1><h3>B child</h3>", encoding="utf-8")
    a, b = children(document_to_sheet(HtmlParser(source).parse())["rootTopic"])
    assert [node["title"] for node in children(a)] == ["A child"]
    assert [node["title"] for node in children(b)] == ["B child"]


def test_html_without_h1_keeps_headings(tmp_path):
    source = tmp_path / "headings.html"
    source.write_text("<h2>A</h2><h4>A child</h4><h2>B</h2>")
    a, b = children(document_to_sheet(HtmlParser(source).parse())["rootTopic"])
    assert a["title"] == "A" and b["title"] == "B"
    assert children(a)[0]["title"] == "A child"


def test_markdown_new_branch_cannot_use_old_parent(tmp_path):
    source = tmp_path / "headings.md"
    source.write_text("# Root\n## A\n### A1\n## B\n#### B deep\n###### B deeper\n# C\n## C child\n")
    a, b, c = children(document_to_sheet(MarkdownParser(source).parse())["rootTopic"])
    assert children(children(a)[0]) == []
    assert children(b)[0]["title"] == "B deep"
    assert children(children(b)[0])[0]["title"] == "B deeper"
    assert children(c)[0]["title"] == "C child"


def xml_document(topic):
    return '<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"><sheet>' + topic + '</sheet></xmap-content>'


def write_archive(path, **members):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)


@pytest.mark.parametrize("damaged", ["{bad JSON", "[]", '{"rootTopic":null}', b"\xff"])
def test_bad_json_falls_back_to_xml_even_with_bad_metadata(tmp_path, damaged):
    path = tmp_path / "fallback.xmind"
    write_archive(path, **{
        "content.json": damaged, "metadata.json": "not json",
        "content.xml": xml_document('<topic id="root"><title>Valid XML</title></topic>'),
    })
    result = XMindService(Settings()).read_xmind_file(str(path))
    assert result["status"] == "success", result
    assert result["data"]["source_format"] == "xml"
    assert result["data"]["structure"]["title"] == "Valid XML"


def test_valid_json_does_not_require_valid_xml(tmp_path):
    path = tmp_path / "json.xmind"
    write_archive(path, **{"content.json": json.dumps([document_to_sheet(Document(Topic("JSON")))]),
                           "content.xml": "<broken", "metadata.json": "broken"})
    result = XMindService(Settings()).read_xmind_file(str(path))
    assert result["status"] == "success"
    assert result["data"]["source_format"] == "json"


@pytest.mark.parametrize("source_format", ["json", "xml"])
@pytest.mark.parametrize("budget", ["nodes", "depth", "exact"])
def test_read_enforces_budgets_and_stats(tmp_path, source_format, budget):
    path = tmp_path / "limited.xmind"
    if budget == "depth":
        node = {"title": "leaf"}
        for _ in range(100):
            node = {"title": "parent", "children": {"attached": [node]}}
        topic_xml = '<topic><title>leaf</title></topic>'
        for _ in range(100):
            topic_xml = '<topic><title>parent</title><children><topics type="attached">' + topic_xml + '</topics></children></topic>'
    else:
        node = {"title": "root", "children": {"attached": [{"title": str(i)} for i in range(20)]}}
        topic_xml = '<topic><title>root</title><children><topics type="attached">' + ''.join(
            f'<topic><title>{i}</title></topic>' for i in range(20)) + '</topics></children></topic>'
    if source_format == "json":
        write_archive(path, **{"content.json": json.dumps([{"rootTopic": node}])})
    else:
        write_archive(path, **{"content.xml": xml_document(topic_xml)})
    nodes = {"nodes": 2, "depth": 1000, "exact": 21}[budget]
    depth = {"nodes": 30, "depth": 2, "exact": 1}[budget]
    engine = XMindService(Settings(tmp_path, read_limits=ReadLimits(max_nodes=nodes, max_depth=depth)))
    result = engine.read_xmind_file(str(path))
    assert result["status"] == "success", result
    assert result["stats"]["total_nodes"] == {"nodes": 2, "depth": 3, "exact": 21}[budget]
    assert result["stats"]["titles_count"] == result["stats"]["total_nodes"]
    assert result["stats"]["max_depth"] == (2 if budget == "depth" else 1)
    assert ("降级" in result["message"]) == (budget != "exact")


def test_zip_uncompressed_budget_checked_before_read(tmp_path, monkeypatch):
    path = tmp_path / "compressed.xmind"
    write_archive(path, **{"content.json": '"' + "x" * (1024 * 1024) + '"'})
    assert path.stat().st_size < 1024 * 1024
    engine = XMindService(Settings(tmp_path, read_limits=ReadLimits(max_content_bytes=1024 * 1024)))

    def no_read(*args, **kwargs):
        pytest.fail("Oversized member must be rejected before decompression")

    monkeypatch.setattr(zipfile.ZipFile, "open", no_read)
    result = engine.read_xmind_file(str(path))
    assert result["status"] == "error"
    assert "解压内容大小超限" in result["message"]


def test_archive_file_budget_checked_before_open(tmp_path, monkeypatch):
    path = tmp_path / "large.xmind"
    path.write_bytes(b"x" * (1024 * 1024 + 1))
    engine = XMindService(Settings(tmp_path, read_limits=ReadLimits(max_content_bytes=1024 * 1024)))

    def no_open(*args, **kwargs):
        pytest.fail("Oversized file must be rejected before opening ZIP")

    monkeypatch.setattr(zipfile, "ZipFile", no_open)
    assert "文件大小超限" in engine.read_xmind_file(str(path))["message"]


@pytest.mark.parametrize("passing", [True, False])
def test_test_runner_uses_exit_status_and_writes_report(tmp_path, passing):
    source = tmp_path / "test_sample.py"
    source.write_text(f'def test_result():\n    print("通过率: 100.0%")\n    assert {passing}\n', encoding="utf-8")
    report = tmp_path / "report.json"
    result = subprocess.run([sys.executable, str(ROOT / "tests/run_all_tests.py"),
                             str(source), "-q", "--report-file", str(report)],
                            cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert result.returncode == (0 if passing else 1), result.stdout + result.stderr
    data = json.loads(report.read_text())
    assert data["exit_code"] == result.returncode
    assert data["summary"]["passed" if passing else "failed"] == 1

