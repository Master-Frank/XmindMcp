"""Smoke-test a built wheel without importing source-tree modules.

Usage: python tests/check_distribution.py path/to/package.whl
Dependencies are taken from the current interpreter; the package itself is loaded
only from the wheel in an isolated process outside the repository.
"""
from email.parser import Parser
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def main():
    wheel = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix='xmind-wheel-') as temporary:
        target = Path(temporary)
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(target)
            metadata = Parser().parsestr(archive.read(next(name for name in archive.namelist() if name.endswith('.dist-info/METADATA'))).decode())
            expected_version = metadata['Version']
            entry_points = archive.read(next(name for name in archive.namelist() if name.endswith('entry_points.txt'))).decode()
            assert 'xmind-mcp = xmind_mcp.cli:main' in entry_points
        code = '''
import asyncio, importlib.util, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
from mcp import Client
from xmind_mcp.models import Document, Topic
from xmind_mcp.settings import Settings
from xmind_mcp.server import create_server
import xmind_mcp
assert pathlib.Path(xmind_mcp.__file__).is_relative_to(sys.argv[1])
assert xmind_mcp.__version__ == sys.argv[2], (xmind_mcp.__version__, sys.argv[2])
async def run():
    settings = Settings(pathlib.Path.cwd(), pathlib.Path.cwd() / 'output')
    for mode in ('auto', 'legacy'):
        async with Client(create_server(settings), mode=mode) as client:
            assert len((await client.list_tools()).tools) == 6
            response = await client.call_tool('create_mind_map', {'title':'wheel', 'topics_json':'[]'})
            assert json.loads(response.content[0].text)['status'] == 'success'
            response = await client.call_tool('read_xmind_file', {'file_path':str(settings.default_output_dir / 'wheel.xmind')})
            assert json.loads(response.content[0].text)['status'] == 'success'
asyncio.run(run())
for name in ('xmind_core_engine', 'xmind_mcp_server', 'xmind_writer', 'universal_xmind_converter', 'validate_xmind_structure', 'xmind_types', 'xmind_ai_extensions'):
    assert not (pathlib.Path(sys.argv[1]) / (name + '.py')).exists(), name
print('Package-only wheel and modern/legacy MCP smoke tests passed')
'''
        result = subprocess.run([sys.executable, '-I', '-c', code, str(target), expected_version],
                                cwd=target, text=True, timeout=30)
        if result.returncode:
            return result.returncode
        stdio_code = "import runpy, sys; sys.path.insert(0, sys.argv.pop(1)); runpy.run_module('xmind_mcp', run_name='__main__')"
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"_meta": {
            "io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientInfo": {"name": "wheel-check", "version": "1.0"},
            "io.modelcontextprotocol/clientCapabilities": {}}}}
        import json
        stdio = subprocess.run([sys.executable, '-I', '-c', stdio_code, str(target), '--stdio'],
                               input=json.dumps(request) + '\n', capture_output=True, text=True,
                               cwd=target, timeout=20)
        assert stdio.returncode == 0, stdio.stderr
        messages = [json.loads(line) for line in stdio.stdout.splitlines()]
        response = next(message for message in messages if message.get('id') == 1)
        assert len(response['result']['tools']) == 6
        print('Packaged python -m xmind_mcp STDIO entry point passed')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
