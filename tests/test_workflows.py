"""Release gates must wait for tests and use their exact validated artifact."""
import os
from pathlib import Path
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def publish_condition(workflow):
    return workflow['jobs']['publish']['if']


@pytest.fixture
def workflow():
    # BaseLoader retains the Actions `on` key rather than treating it as YAML 1.1 boolean.
    return yaml.load((ROOT / '.github/workflows/publish-pypi.yml').read_text(), Loader=yaml.BaseLoader)


def test_publish_is_gated_by_all_tests_and_main_branch(workflow):
    assert set(workflow['on']) == {'push', 'pull_request', 'workflow_dispatch'}
    assert workflow['on']['push']['branches'] == ['**']
    assert workflow['jobs']['test']['strategy']['matrix']['python-version'] == ['3.11', '3.12', '3.13']
    publish = workflow['jobs']['publish']
    assert publish['needs'] == ['prepare', 'test']
    assert workflow['jobs']['test']['needs'] == 'prepare'
    assert workflow['concurrency']['cancel-in-progress'] == 'false'
    assert publish['if'] == (
        "github.repository == 'Master-Frank/XmindMcp' && "
        "github.ref == 'refs/heads/main' && "
        "(github.event_name == 'push' || github.event_name == 'workflow_dispatch')"
    )
    assert workflow['permissions'] == {'contents': 'read'}
    assert len(list((ROOT / '.github/workflows').glob('*.yml'))) == 1


def test_published_files_are_the_validated_artifact(workflow):
    steps = workflow['jobs']['test']['steps']
    unit = next(i for i, step in enumerate(steps) if step.get('run') == 'python tests/run_all_tests.py -q')
    build = next(i for i, step in enumerate(steps) if step.get('run') == 'python -m build')
    verify = next(i for i, step in enumerate(steps) if step.get('run') == 'python tests/check_distribution.py dist/*.whl')
    upload = next(i for i, step in enumerate(steps) if step.get('uses', '').startswith('actions/upload-artifact@'))
    apply = next(i for i, step in enumerate(steps) if '.github/scripts/release_version.py apply' in step.get('run', ''))
    assert apply < unit < build < verify < upload
    assert steps[apply]['env']['PACKAGE_VERSION'] == '${{ needs.prepare.outputs.version }}'
    prepare = workflow['jobs']['prepare']
    assert prepare['outputs']['version'] == '${{ steps.version.outputs.version }}'
    plan = next(step for step in prepare['steps'] if step.get('id') == 'version')
    assert 'plan --release' in plan['run']
    assert publish_condition(workflow) in plan['env']['RELEASE_BUILD']
    assert steps[upload]['if'] == "matrix.python-version == '3.12'"
    assert steps[upload]['with']['path'] == 'dist/'
    publishing = workflow['jobs']['publish']['steps']
    download = next(step for step in publishing if step.get('uses', '').startswith('actions/download-artifact@'))
    assert download['with']['name'] == steps[upload]['with']['name']
    action = publishing[-1]
    assert action['uses'] == 'pypa/gh-action-pypi-publish@release/v1'
    assert download['with']['path'] == action['with']['packages-dir']
    assert action['with']['password'] == '${{ secrets.PYPI_API_TOKEN }}'
    assert action['with']['skip-existing'] == 'true'
    assert not any('python -m build' in step.get('run', '') for step in publishing)


@pytest.mark.parametrize('token, status', [('', 1), ('placeholder-test-token', 0)])
def test_missing_credentials_fail_with_an_actionable_message(workflow, token, status):
    check = workflow['jobs']['publish']['steps'][0]
    assert check['env']['PYPI_API_TOKEN'] == '${{ secrets.PYPI_API_TOKEN }}'
    result = subprocess.run(['bash', '-e', '-c', check['run']], capture_output=True, text=True,
                            env={**os.environ, 'PYPI_API_TOKEN': token}, timeout=10)
    assert result.returncode == status
    if status:
        assert 'Set repository secret PYPI_API_TOKEN' in result.stdout
    else:
        assert token not in result.stdout + result.stderr
