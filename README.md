# XMind MCP

Convert Markdown, text outlines, HTML, Word, and Excel to XMind. MCP tools provide mind map creation, reading, structural analysis, conversion, file listing, and title translation.

[中文](README_CN.md) · [Documentation index](docs/README.md) (Chinese)

## Quick start

Requires UV and Python 3.11+. From the repository root, run the current source and replace the output directory with an absolute path on your machine:

```bash
uvx --python 3.12 --from . xmind-mcp --stdio --default-output-dir /absolute/path/to/output
```

Clients communicate through standard input/output. Waiting for input in a terminal is normal. `uvx xmind-mcp` installs the published package and does not include unpublished local changes.

The project uses MCP Python SDK v2, supporting the `2026-07-28` protocol revision and legacy initialization. `--mode fastmcp`, `--mode stdio`, and `--stdio` remain aliases for the same STDIO entry point.

See the [usage guide](docs/USAGE_GUIDE.md) for MCP client configuration and path rules.

## Six MCP tools

| Tool | Purpose |
| --- | --- |
| `create_mind_map` | Create a mind map from JSON topics |
| `read_xmind_file` | Read the first sheet's topic tree and statistics |
| `analyze_mind_map` | Analyze nodes, depth, and structure |
| `convert_to_xmind` | Convert a supported input file |
| `list_xmind_files` | List files by directory, pattern, and depth |
| `translate_xmind_titles` | Translate titles through an external provider |

Topic input uses `title` and `children`, with legacy aliases supported. Output tools need an absolute default output directory or explicit absolute output path. Translation requires network access; optional AI helpers are separate from the six registered tools.

## Standalone conversion

```bash
uv run xmind-convert examples/test_markdown.md output/markdown.xmind
```

After installation, `xmind-convert input.md output/result.xmind` is also available. Supported inputs are Markdown, TXT, HTML, `.docx`, and `.xlsx`; see the [usage guide](docs/USAGE_GUIDE.md) for parsing rules.

## Development

```bash
uv venv --python 3.12
uv pip install -e '.[test]'
.venv/bin/python tests/run_all_tests.py -q
```

On Windows, use `.venv/Scripts/python.exe` instead of `.venv/bin/python`.

Branch pushes and pull requests run automated checks. Successful checks on `main` automatically increment the patch version and publish to PyPI. Configure `PYPI_API_TOKEN` once; see the [development guide](docs/DEVELOPMENT.md).

## Documentation

- [Usage guide](docs/USAGE_GUIDE.md): setup, MCP configuration, arguments, conversion, and troubleshooting.
- [Architecture](docs/ARCHITECTURE.md): models, service boundaries, configuration isolation and extensions.
- [Development and publishing](docs/DEVELOPMENT.md): environments, tests, distribution checks, versions, and PyPI releases.

Implementation and MCP entry points live in `xmind_mcp/`; root-level scripts and their import APIs have been removed. See the [documentation index](docs/README.md) for the consolidation map.

## License

[MIT](LICENSE)
