"""Application composition and command-line entry points."""
import argparse
import logging
from pathlib import Path
import sys

from . import __version__
from .service import XMindService
from .settings import Settings


def main(argv=None):
    parser = argparse.ArgumentParser(description='XMind MCP服务器')
    parser.add_argument('--version', action='version', version=f'XMind MCP Server {__version__}')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--mode', choices=['fastmcp', 'stdio'], help='兼容旧配置；均使用SDK v2 STDIO传输')
    parser.add_argument('--stdio', action='store_true', help='STDIO模式兼容别名')
    parser.add_argument('--default-output-dir', help='默认输出目录（绝对路径或相对已配置的基准目录）')
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stderr)
    from .server import create_server
    settings = Settings.from_env(args.default_output_dir)
    create_server(settings).run(transport='stdio')


def convert_main(argv=None):
    parser = argparse.ArgumentParser(description='将Markdown、TXT、HTML、Word、Excel转换为XMind')
    parser.add_argument('input_file')
    parser.add_argument('output_file', nargs='?')
    args = parser.parse_args(argv)
    source = Path(args.input_file).resolve()
    output = Path(args.output_file).resolve() if args.output_file else Path.cwd() / 'output' / f'{source.stem}.xmind'
    service = XMindService(Settings.from_env())
    result = service.convert_to_xmind(str(source), str(output))
    print(result['message'])
    if result['status'] == 'success':
        print(f'输出文件: {output}')
    return 0 if result['status'] == 'success' else 1
