"""Automatic version planning uses PyPI stable history and never writes the source checkout."""
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tomllib
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.github/scripts/release_version.py'
MODULE = runpy.run_path(str(SCRIPT))


@pytest.mark.parametrize('source, releases, expected', [
    ('1.3.9', ['1.3.8', '1.3.9'], '1.3.10'),
    ('1.3.9', ['1.3.10', '1.3.9'], '1.3.11'),
    ('1.3.9', ['1.4.9', '2.0.0rc1', 'invalid'], '1.4.10'),
    ('2.0.0', ['1.3.9'], '2.0.0'),
    ('1.3.9', [], '1.3.9'),
    ('1.3.9', ['1.3.9.post1'], '1.3.10'),
    ('1.0.0', ['2.1'], '2.1.1'),
    ('1.0.0', ['2.0.0.dev1', '2.0.0rc1'], '1.0.0'),
])
def test_select_next_patch_or_explicit_new_baseline(source, releases, expected):
    assert MODULE['select_version'](source, releases) == expected


@pytest.mark.parametrize('source', ['1.0', '1.0.0rc1', '1.0.0.dev1', '1.0.0.post1', '1.0.0+local', '1!1.0.0'])
def test_reject_ambiguous_source_version(source):
    with pytest.raises(ValueError):
        MODULE['select_version'](source, [])


def test_apply_changes_only_project_version_and_non_release_plan_does_not_write(tmp_path):
    path = tmp_path / 'pyproject.toml'
    original = '[project]\nname = "xmind-mcp"\nversion = "1.3.9"\n\n[tool.example]\nversion = "unchanged"\n'
    path.write_text(original)
    output = tmp_path / 'outputs'
    planned = subprocess.run([sys.executable, str(SCRIPT), 'plan', '--pyproject', str(path)],
                             capture_output=True, text=True, cwd=tmp_path,
                             env={**os.environ, 'GITHUB_OUTPUT': str(output)}, timeout=10)
    assert planned.returncode == 0, planned.stderr
    assert output.read_text() == 'version=1.3.9\n'
    assert path.read_text() == original
    MODULE['apply_version'](path, '1.3.10')
    assert path.read_text() == original.replace('version = "1.3.9"', 'version = "1.3.10"')
    assert tomllib.loads(path.read_text())['tool']['example']['version'] == 'unchanged'


def test_pypi_missing_project_is_distinct_from_network_failure():
    fn = MODULE['fetch_versions']
    original = fn.__globals__['urlopen']
    try:
        def missing(*args, **kwargs):
            raise HTTPError('https://pypi.org/', 404, 'missing', {}, None)
        fn.__globals__['urlopen'] = missing
        assert fn('new-project') == []
        def offline(*args, **kwargs):
            raise TimeoutError('network unavailable')
        fn.__globals__['urlopen'] = offline
        with pytest.raises(TimeoutError):
            fn('existing-project')
    finally:
        fn.__globals__['urlopen'] = original


def test_plan_release_exports_selected_version_without_modifying_source(tmp_path, monkeypatch, capsys):
    main = MODULE['main']
    path = tmp_path / 'pyproject.toml'
    original = '[project]\nname = "xmind-mcp"\nversion = "1.3.9"\n'
    path.write_text(original)
    output = tmp_path / 'outputs'
    monkeypatch.setenv('GITHUB_OUTPUT', str(output))
    monkeypatch.setitem(main.__globals__, 'fetch_versions', lambda project: ['1.3.9'])
    assert main(['plan', '--release', '--pyproject', str(path)]) == 0
    assert output.read_text() == 'version=1.3.10\n'
    assert path.read_text() == original
    assert capsys.readouterr().out == '1.3.10\n'
