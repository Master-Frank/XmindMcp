"""MCP adapter. Server instances and their dependencies are created explicitly."""
import json

from . import __version__
from .presentation import public_result
from .service import XMindService
from .settings import Settings


def tool_handlers(service):
    def encode(result, **options):
        return json.dumps(public_result(result, **options), ensure_ascii=False)

    def read_xmind_file(file_path: str) -> str:
        """读取XMind文件内容（返回结构与统计信息）。file_path 为XMind文件路径。"""
        return encode(service.read_xmind_file(file_path))

    def create_mind_map(title: str, topics_json: str, output_path: str = None) -> str:
        """创建思维导图。topics_json 为主题JSON字符串，支持 children/topics/subtopics/nodes/items 别名；output_path 为可选绝对输出路径。"""
        return encode(service.create_mind_map(title, topics_json, output_path), output=True)

    def analyze_mind_map(file_path: str) -> str:
        """分析思维导图结构，返回节点数量、层级及结构建议。"""
        return encode(service.analyze_mind_map(file_path))

    def convert_to_xmind(source_filepath: str = None, output_filepath: str = None,
                         source_file: str = None, output_file: str = None) -> str:
        """将TXT、Markdown、HTML、Word、Excel转换为XMind。源路径必须为绝对路径；source_file/output_file 是旧参数别名。JSON主题请用 create_mind_map。"""
        return encode(service.convert_to_xmind(source_filepath, output_filepath, source_file, output_file), output=True)

    def list_xmind_files(directory: str = None, recursive: bool = True,
                         pattern: str = None, max_depth: int = None) -> str:
        """列出XMind文件。directory 为绝对目录，省略时使用默认输出目录；支持递归、文件名模式和最大搜索深度。"""
        return encode(service.list_xmind_files(directory, recursive, pattern, max_depth))

    def translate_xmind_titles(source_filepath: str, output_filepath: str = None,
                               target_lang: str = 'en', overwrite: bool = False) -> str:
        """翻译XMind标题并输出新文件。output_filepath 为可选绝对输出路径；target_lang 默认为 en，覆盖已有文件需 overwrite=True。"""
        return encode(service.translate_xmind_titles(source_filepath, output_filepath, target_lang, overwrite),
                      output=True, success_message='标题翻译并写入成功')

    return [read_xmind_file, create_mind_map, analyze_mind_map,
            convert_to_xmind, list_xmind_files, translate_xmind_titles]


def create_server(settings: Settings | None = None, service: XMindService | None = None):
    from mcp.server.mcpserver import MCPServer
    if service is None:
        service = XMindService(settings if settings is not None else Settings.from_env())
    elif settings is not None and settings != service.settings:
        raise ValueError('服务器配置与注入的服务配置不一致')
    server = MCPServer('XMindMCP', version=__version__)
    for handler in tool_handlers(service):
        server.add_tool(handler)
    return server

