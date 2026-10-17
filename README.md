# XMind MCP

Convert Markdown, text outlines, HTML, Word, and Excel to XMind. MCP tools provide mind map creation, reading, structural analysis, conversion, file listing, and title translation.

[中文](README_CN.md) · [Documentation index](docs/README.md) (Chinese)

## Quick start

Requires UV and Python 3.11+. From the repository root, run the current source:

```bash
uvx --python 3.12 --from . xmind-mcp --stdio
```

Clients communicate through standard input/output. Waiting for input in a terminal is normal. `uvx xmind-mcp` installs the published package and does not include unpublished local changes.

The project uses MCP Python SDK v2, supporting the `2026-07-28` protocol revision and legacy initialization. `--mode fastmcp`, `--mode stdio`, and `--stdio` remain aliases for the same STDIO entry point.

See the [usage guide](docs/USAGE_GUIDE.md) for MCP client configuration and path rules.

## Agent setup

These examples use PyPI version `2.0.1`; cloning this repository is unnecessary. Install [UV](https://docs.astral.sh/uv/getting-started/installation/) and check that `uvx --version` works. The first run needs network access to download dependencies. You can install them and check the package version first:

```bash
uvx --python 3.12 --from xmind-mcp==2.0.1 xmind-mcp --version
```

### Codex

Merge the [TOML example](configs/mcp_config.toml) into `~/.codex/config.toml`, or `.codex/config.toml` in a trusted project:

```toml
[mcp_servers.xmind]
command = "uvx"
args = ["--python", "3.12", "--from", "xmind-mcp==2.0.1", "xmind-mcp", "--stdio"]
startup_timeout_sec = 120
tool_timeout_sec = 120
```

Keep other settings. Update an existing `[mcp_servers.xmind]` table rather than adding it twice. Restart the client and start a new session. Alternatively, register through the CLI:

```bash
codex mcp add xmind -- uvx --python 3.12 --from xmind-mcp==2.0.1 xmind-mcp --stdio
codex mcp list
```

If the initial startup times out after CLI registration, set `startup_timeout_sec` as shown above. Desktop, CLI, and IDE clients share the same host's configuration. Use `/mcp` in the CLI TUI to inspect connections. [Official Codex documentation](https://developers.openai.com/codex/mcp#connect-codex-to-an-mcp-server)

### Claude Code

Register a user-scoped server for use across projects:

```bash
claude mcp add --transport stdio --scope user xmind -- uvx --python 3.12 --from xmind-mcp==2.0.1 xmind-mcp --stdio
claude mcp get xmind
```

Reopen Claude Code and run `/mcp` in the session to check the connection. For team project configuration, replace `--scope user` with `--scope project`, which writes `.mcp.json` in the project root. You can also merge the [JSON example](configs/mcp_config.json) into that file. Approve project servers when the client prompts. [Official Claude Code documentation](https://code.claude.com/docs/en/mcp)

### Cursor

Merge the [JSON example](configs/mcp_config.json) into `~/.cursor/mcp.json` for all projects, or `.cursor/mcp.json` inside one project:

```json
{
  "mcpServers": {
    "xmind": {
      "command": "uvx",
      "args": ["--python", "3.12", "--from", "xmind-mcp==2.0.1", "xmind-mcp", "--stdio"]
    }
  }
}
```

Keep other entries under `mcpServers`. Save and reload the client, check `xmind` in MCP settings, then use it in Agent chat. A project entry takes priority over a global entry with the same name. [Official Cursor documentation](https://cursor.com/docs/mcp)

### Verify and customize

Once connected, six tools should be available. Try this in your agent:

> Use xmind to create a development plan covering requirements, implementation, testing, and release. Save it to the default directory and return a file link.

Output defaults to `Documents/XmindOutput` inside the process user's home directory, such as `/Users/username/Documents/XmindOutput` on macOS or `C:/Users/username/Documents/XmindOutput` on Windows. Missing directories are created automatically. Successful create, convert, and translate tools return `data.absolute_path`.

No `env` is needed; MCP communication uses UTF-8. If the client cannot find `uvx`, run `command -v uvx` on macOS/Linux or `where.exe uvx` on Windows and use the absolute executable path as `command`. In configuration locations above, `~` means your home directory, typically `%USERPROFILE%` on Windows.

To override output, append `"--default-output-dir", "/absolute/path/to/output"` to `args`. Use forward slashes such as `D:/XmindOutput` in Windows JSON/TOML strings. For local development, replace the package specifier after `--from` with the repository's absolute path. Other STDIO clients using `mcpServers` can reuse the JSON example; consult their documentation for the configuration location.

## Six MCP tools

| Tool | Purpose |
| --- | --- |
| `create_mind_map` | Create a mind map from JSON topics |
| `read_xmind_file` | Read the first sheet's topic tree and statistics |
| `analyze_mind_map` | Analyze nodes, depth, and structure |
| `convert_to_xmind` | Convert a supported input file |
| `list_xmind_files` | List files by directory, pattern, and depth |
| `translate_xmind_titles` | Translate titles through an external provider |

Topic input uses `title` and `children`, with legacy aliases supported. From 2.0.1, output defaults to `Documents/XmindOutput` inside the current user’s home directory, created automatically. Override it with `--default-output-dir` or `XMIND_MCP_DEFAULT_OUTPUT_DIR`, or pass an explicit absolute file path. Successful create, convert, and translate tools return `data.absolute_path`. Translation requires network access; optional AI helpers are separate from the six registered tools.

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
