"""Plan an automatic release version and apply it only to the CI workspace."""
import argparse
import json
import os
from pathlib import Path
import re
import tomllib
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen

from packaging.version import InvalidVersion, Version


def select_version(source_version, published_versions):
    """Use an explicit newer source version, otherwise bump the latest stable patch."""
    source = Version(source_version)
    if source.epoch or source.is_prerelease or source.is_devrelease or source.is_postrelease or source.local or len(source.release) != 3:
        raise ValueError('Automatic releases require a stable MAJOR.MINOR.PATCH source version')
    stable = []
    for raw in published_versions:
        try:
            candidate = Version(raw)
        except InvalidVersion:
            continue
        if not candidate.is_prerelease and not candidate.is_devrelease and not candidate.local:
            stable.append(candidate)
    latest = max(stable, default=None)
    if latest is None or source > latest:
        return str(source)
    if latest.epoch or len(latest.release) > 3:
        raise ValueError('Published version cannot be automatically incremented as MAJOR.MINOR.PATCH')
    major, minor, patch = (*latest.release, 0, 0)[:3]
    return f'{major}.{minor}.{patch + 1}'


def fetch_versions(project):
    try:
        with urlopen(f'https://pypi.org/pypi/{quote(project, safe="")}/json', timeout=20) as response:
            return list(json.load(response)['releases'])
    except HTTPError as exc:
        if exc.code == 404:
            return []
        raise


def apply_version(pyproject, version):
    """Replace exactly one [project].version without rewriting unrelated TOML."""
    Version(version)
    path = Path(pyproject)
    text = path.read_text(encoding='utf-8')
    tomllib.loads(text)  # Fail before mutation if the source is invalid.
    section = re.search(r'^\[project\]\s*\n(?P<body>.*?)(?=^\[|\Z)', text, flags=re.M | re.S)
    if section is None:
        raise ValueError('Missing [project] section')
    body, count = re.subn(r'^(version\s*=\s*)[\'\"][^\'\"]+[\'\"]',
                          lambda match: f'{match[1]}"{version}"', section['body'], flags=re.M)
    if count != 1:
        raise ValueError('Expected exactly one static [project].version')
    result = text[:section.start('body')] + body + text[section.end('body'):]
    assert tomllib.loads(result)['project']['version'] == version
    path.write_text(result, encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['plan', 'apply'])
    parser.add_argument('--pyproject', default='pyproject.toml')
    parser.add_argument('--release', action='store_true', help='Read PyPI and increment for a real release')
    parser.add_argument('--version', help='Planned version to apply in the build workspace')
    args = parser.parse_args(argv)
    project = tomllib.loads(Path(args.pyproject).read_text(encoding='utf-8'))['project']
    if args.operation == 'apply':
        if not args.version:
            parser.error('apply requires --version')
        apply_version(args.pyproject, args.version)
        selected = args.version
    else:
        selected = select_version(project['version'], fetch_versions(project['name'])) if args.release else project['version']
        if output := os.environ.get('GITHUB_OUTPUT'):
            with open(output, 'a', encoding='utf-8') as stream:
                stream.write(f'version={selected}\n')
    print(selected)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
