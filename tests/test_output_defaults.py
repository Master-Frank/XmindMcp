"""Default directories and the public paths returned by file-producing MCP tools."""
import asyncio
import json
from pathlib import Path
import os
import subprocess
import sys

import pytest

from xmind_mcp.service import XMindService
from xmind_mcp.settings import Settings


def test_unconfigured_startup_creates_user_documents_output(tmp_path, monkeypatch):
    home = tmp_path / '用户'
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: home))
    output = home / 'Documents' / 'XmindOutput'
    assert not output.exists()
    settings = Settings.from_env(environ={})
    assert settings.default_output_dir == output
    assert output.is_dir()
    assert Settings.from_env(environ={}).default_output_dir == output
    assert XMindService(settings).list_xmind_files()['data']['files'] == []


@pytest.mark.parametrize('cli_override', [False, True])
def test_custom_directory_overrides_home_default_and_is_created(tmp_path, monkeypatch, cli_override):
    home = tmp_path / 'unused-home'
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: home))
    env_output, cli_output = tmp_path / 'env', tmp_path / 'cli'
    settings = Settings.from_env(str(cli_output) if cli_override else None,
                                 {'XMIND_MCP_DEFAULT_OUTPUT_DIR': str(env_output)})
    expected = cli_output if cli_override else env_output
    assert settings.default_output_dir == expected
    assert expected.is_dir()
    assert not home.exists()


def test_library_settings_create_default_directory_on_first_use(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: tmp_path))
    service = XMindService(Settings())
    assert service.list_xmind_files()['status'] == 'success'
    assert (tmp_path / 'Documents' / 'XmindOutput').is_dir()
    assert service.list_xmind_files(str(tmp_path / 'missing'))['error_code'] == 'file_not_found'


@pytest.mark.parametrize('mode', ['auto', 'legacy'])
def test_all_file_producing_mcp_tools_return_absolute_paths(tmp_path, monkeypatch, mode):
    from mcp import Client
    from xmind_mcp.server import create_server

    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: tmp_path / 'home'))
    settings = Settings.from_env(environ={})

    class Translator:
        def translate(self, text):
            return 'Translated'

    service = XMindService(settings, translator_factory=lambda language: Translator())
    source = tmp_path / 'outline.md'
    source.write_text('# 文档\n## 内容\n', encoding='utf-8')
    output = settings.default_output_dir

    async def run():
        async with Client(create_server(service=service), mode=mode) as client:
            for tool, args, filename in [
                ('create_mind_map', {'title': '中文标题', 'topics_json': '[]'}, '中文标题.xmind'),
                ('convert_to_xmind', {'source_filepath': str(source)}, 'outline.xmind'),
                ('translate_xmind_titles', {'source_filepath': str(output / '中文标题.xmind')}, '中文标题_en.xmind'),
            ]:
                response = await client.call_tool(tool, args)
                result = json.loads(response.content[0].text)
                assert result['status'] == 'success', result
                path = Path(result['data']['absolute_path'])
                assert path == output / filename
                assert path.is_absolute() and path.is_file()
                assert result['data']['filename'] == filename
    asyncio.run(run())


def test_standalone_conversion_uses_configured_default(tmp_path):
    source = tmp_path / 'source.md'
    source.write_text('# Root\n', encoding='utf-8')
    output = tmp_path / 'new-output'
    env = dict(os.environ, XMIND_MCP_DEFAULT_OUTPUT_DIR=str(output))
    result = subprocess.run([sys.executable, '-c',
                             'from xmind_mcp.cli import convert_main; raise SystemExit(convert_main())',
                             str(source)], env=env, cwd=tmp_path, text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert str(output / 'source.xmind') in result.stdout
    assert (output / 'source.xmind').is_file()
