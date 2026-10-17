"""Application use cases. No MCP imports, process globals or CLI dependencies."""
import json
from pathlib import Path

from .analysis import analyze_document
from .errors import XMindError, result_boundary
from .filesystem import list_files
from .models import Document, Topic, normalize_topics, topic_structure
from .parsers.registry import ParserRegistry
from .settings import Settings, sanitize_filename
from .translation import default_translator, translate_archive
from .xmind_io.reader import XMindReader
from .xmind_io.writer import create_xmind_file


class XMindService:
    def __init__(self, settings: Settings, *, parser_factory=None,
                 translator_factory=default_translator):
        self.settings = settings
        self.parser_factory = ParserRegistry() if parser_factory is None else parser_factory
        self.translator_factory = translator_factory

    def _read(self, path):
        limits = self.settings.read_limits
        return XMindReader(path, max_content_bytes=limits.max_content_bytes,
                           max_nodes=limits.max_nodes, max_depth=limits.max_depth).read()

    @result_boundary
    def read_xmind_file(self, file_path):
        path = self.settings.input_path(file_path)
        if not path.exists():
            raise XMindError(f"文件不存在: {file_path}", "file_not_found")
        if path.stat().st_size == 0:
            raise XMindError("文件为空", "empty_file")
        loaded = self._read(path)
        message = "读取成功"
        if loaded.truncation_reasons:
            message = "读取完成（触发降级：" + ",".join(loaded.truncation_reasons) + "）"
        return {"status": "success", "message": message,
                "data": {"format": "xmind", "source_format": loaded.source_format,
                         "structure": topic_structure(loaded.document.root),
                         "file_path": str(path), "file_size": path.stat().st_size},
                "stats": loaded.stats.as_dict()}

    @result_boundary
    def create_mind_map(self, title, topics_json, output_path=None):
        # Text fallback and aliases are the same for CLI, library and MCP callers.
        if isinstance(topics_json, str):
            try:
                topics = json.loads(topics_json)
            except json.JSONDecodeError:
                topics = [{"title": topics_json}]
        else:
            topics = topics_json
        normalized = normalize_topics(topics) if topics else []
        document = Document(Topic(title, normalized))
        path = self.settings.output_path(output_path, f"{sanitize_filename(title)}.xmind")
        create_xmind_file(document, path)
        return {"status": "success", "message": "思维导图已创建",
                "data": {"filename": path.name, "title": title, "topics_count": len(normalized),
                         "absolute_path": str(path), "output_path": str(path), "file_size": path.stat().st_size}}

    @result_boundary
    def analyze_mind_map(self, file_path):
        path = self.settings.input_path(file_path)
        loaded = self._read(path)
        analysis, stats = analyze_document(loaded.document)
        output_stats = stats.as_dict(analysis=True)
        output_stats.pop('titles_count')
        return {"status": "success", "message": "分析完成",
                "data": {"filename": path.name, "structure_analysis": analysis}, "stats": output_stats}

    @result_boundary
    def convert_to_xmind(self, source_filepath=None, output_filepath=None, source_file=None, output_file=None):
        source = source_filepath or source_file
        if not source:
            raise XMindError("必须提供源文件路径：source_filepath 或 source_file")
        path = self.settings.input_path(source, require_absolute=True)
        if not path.is_file():
            raise XMindError(f"源文件不存在: {source}", "file_not_found")
        output = self.settings.output_path(output_filepath or output_file, f"{path.stem}.xmind")
        document = self.parser_factory.get_parser(path).parse()
        if not isinstance(document, Document):
            raise XMindError("解析器必须返回Document", "invalid_parser_result")
        create_xmind_file(document, output)
        return {"status": "success", "message": "文件转换成功",
                "data": {"source_file": str(path), "output_file": str(output)}}

    @result_boundary
    def list_xmind_files(self, directory=None, recursive=True, pattern=None, max_depth=None):
        if directory is None:
            path = self.settings.default_output_dir
            path.mkdir(parents=True, exist_ok=True)
        else:
            path = self.settings.input_path(directory, require_absolute=True)
        if not path.exists():
            raise XMindError(f"目录不存在: {path}", "file_not_found")
        if not path.is_dir():
            raise XMindError(f"路径不是目录: {path}")
        files = list_files(path, recursive, pattern, max_depth)
        return {"status": "success", "message": "列出XMind文件完成",
                "data": {"directory": str(path), "recursive": recursive, "pattern": pattern,
                         "max_depth": max_depth, "file_count": len(files), "files": files}}

    @result_boundary
    def translate_xmind_titles(self, source_filepath, output_filepath=None, target_lang="en", overwrite=False):
        source = self.settings.input_path(source_filepath)
        if not source.is_file():
            raise XMindError(f"源文件不存在: {source_filepath}", "file_not_found")
        output = self.settings.output_path(output_filepath, f"{source.stem}_{target_lang}.xmind")
        result = translate_archive(source, output, target_lang, overwrite, self.translator_factory)
        return {"status": "success", "message": "翻译完成", "translated_titles": result.translated_titles,
                "data": {"source_file": str(source), "output_file": str(output)}}
