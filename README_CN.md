# XMind MCP

将 Markdown、文本大纲、HTML、Word、Excel 转为 XMind，并通过 MCP 提供创建、读取、结构分析、文件列举及标题翻译。

[English](README.md) · [文档导航](docs/README.md)

## 快速开始

需要 UV 和 Python 3.11+。在仓库根目录运行当前源码：

```bash
uvx --python 3.12 --from . xmind-mcp --stdio
```

客户端通过标准输入/输出连接；服务在终端等待输入是正常现象。使用 `uvx xmind-mcp` 会安装已发布包，不包含尚未发布的本地修改。

本项目使用 MCP Python SDK v2，支持 `2026-07-28` 协议以及旧客户端握手。`--mode fastmcp`、`--mode stdio`、`--stdio` 保留为兼容参数，使用相同 STDIO 入口。

完整 MCP 配置和路径规则见 [使用指南](docs/USAGE_GUIDE.md)。

## Agent 接入教程

以下配置使用 PyPI 版本 `2.0.1`，不需要克隆本仓库。先安装 [UV](https://docs.astral.sh/uv/getting-started/installation/)，确认 `uvx --version` 可执行。首次下载依赖需要网络，可先运行以下命令完成安装并检查版本：

```bash
uvx --python 3.12 --from xmind-mcp==2.0.1 xmind-mcp --version
```

### Codex

将 [TOML 示例](configs/mcp_config.toml) 合并到 `~/.codex/config.toml`，或受信任项目的 `.codex/config.toml`：

```toml
[mcp_servers.xmind]
command = "uvx"
args = ["--python", "3.12", "--from", "xmind-mcp==2.0.1", "xmind-mcp", "--stdio"]
startup_timeout_sec = 120
tool_timeout_sec = 120
```

保留其他配置；如果已有 `[mcp_servers.xmind]`，修改原表，不要重复添加。保存后重启客户端并新建会话。也可通过 CLI 注册同一服务：

```bash
codex mcp add xmind -- uvx --python 3.12 --from xmind-mcp==2.0.1 xmind-mcp --stdio
codex mcp list
```

CLI 注册后若首次启动超时，在配置中设置上面的 `startup_timeout_sec`。桌面端、CLI 和 IDE 扩展共用同一主机的配置；CLI 交互界面可用 `/mcp` 查看连接状态。[Codex 官方文档](https://developers.openai.com/codex/mcp#connect-codex-to-an-mcp-server)

### Claude Code

在终端注册为用户级服务，使其在各项目中可用：

```bash
claude mcp add --transport stdio --scope user xmind -- uvx --python 3.12 --from xmind-mcp==2.0.1 xmind-mcp --stdio
claude mcp get xmind
```

重新打开 Claude Code，在会话中运行 `/mcp` 检查连接。若只想对团队项目生效，将 `--scope user` 换成 `--scope project`，命令会写入项目根目录的 `.mcp.json`；也可将 [JSON 示例](configs/mcp_config.json) 合并到该文件。项目级配置需要按客户端提示批准。[Claude Code 官方文档](https://code.claude.com/docs/en/mcp)

### Cursor

将以下 [JSON 示例](configs/mcp_config.json) 合并到 `~/.cursor/mcp.json`，或项目目录的 `.cursor/mcp.json`：

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

保留已有 `mcpServers` 中的其他服务，保存后重新加载客户端，在 MCP 设置中检查 `xmind` 状态，然后在 Agent 对话中使用。同名配置以项目级配置优先。[Cursor 官方文档](https://cursor.com/docs/mcp)

### 验证与常见设置

连接成功后应有六个工具。可以在 Agent 对话中发送：

> 使用 xmind 创建项目开发计划思维导图，包含需求分析、开发、测试和发布，保存到默认目录，并返回文件链接。

默认输出到用户主目录下的 `Documents/XmindOutput`，例如 macOS 的 `/Users/用户名/Documents/XmindOutput`，Windows 的 `C:/Users/用户名/Documents/XmindOutput`；不存在时自动创建。创建、转换和翻译的成功结果包含 `data.absolute_path`。

无需 `env`，MCP 通信使用 UTF-8。找不到 `uvx` 时，macOS/Linux 执行 `command -v uvx`、Windows 执行 `where.exe uvx`，将配置中的 `command` 改为查到的绝对路径。`~` 在本文配置位置中表示用户主目录，Windows 通常为 `%USERPROFILE%`。

如需自定义输出位置，在 `args` 末尾追加 `"--default-output-dir", "/绝对路径/输出目录"`；Windows JSON/TOML 字符串建议用 `D:/XmindOutput` 这样的正斜杠路径。连接本地开发代码时，将 `--from` 后的包名版本替换为仓库绝对路径。其他支持 STDIO 及 `mcpServers` 格式的客户端可复用 JSON 示例，具体配置文件位置以客户端文档为准。

## 六个 MCP 工具

| 工具 | 用途 |
| --- | --- |
| `create_mind_map` | 根据 JSON 主题结构创建导图 |
| `read_xmind_file` | 读取首个画布的主题结构与统计 |
| `analyze_mind_map` | 分析节点、层级和结构 |
| `convert_to_xmind` | 转换支持的文件格式 |
| `list_xmind_files` | 按目录、通配模式和深度列举文件 |
| `translate_xmind_titles` | 调用外部翻译服务处理标题 |

创建主题推荐使用 `title` + `children`，兼容旧字段别名。从 2.0.1 起，默认输出到当前用户主目录下的 `Documents/XmindOutput`，目录不存在时自动创建。可用 `--default-output-dir`、`XMIND_MCP_DEFAULT_OUTPUT_DIR` 或工具的绝对输出路径覆盖。创建、转换及翻译成功后均返回 `data.absolute_path`。标题翻译需要网络；可选 AI 扩展没有作为额外 MCP 工具注册。

## 独立转换

```bash
uv run xmind-convert examples/test_markdown.md output/markdown.xmind
```

安装本项目后也可使用 `xmind-convert input.md output/result.xmind`。目前支持 Markdown、TXT、HTML、`.docx`、`.xlsx`；详细格式规则见 [使用指南](docs/USAGE_GUIDE.md)。

## 开发

```bash
uv venv --python 3.12
uv pip install -e '.[test]'
.venv/bin/python tests/run_all_tests.py -q
```

Windows 将 `.venv/bin/python` 替换为 `.venv/Scripts/python.exe`。

推送分支或提交 PR 会自动运行测试；`main` 的全部检查通过后自动递增补丁版本并发布 PyPI。首次需配置 `PYPI_API_TOKEN`，详见 [开发与发布](docs/DEVELOPMENT.md)。

## 文档

- [使用指南](docs/USAGE_GUIDE.md)：安装、MCP 客户端配置、工具参数、转换与排错。
- [架构说明](docs/ARCHITECTURE.md)：统一模型、服务边界、配置隔离与扩展。
- [开发与发布](docs/DEVELOPMENT.md)：环境、测试、分发验证、版本管理与 PyPI 发布。

实现和 MCP 启动入口均位于 `xmind_mcp/`；根目录旧脚本和导入接口已移除。文档合并去向见 [文档导航](docs/README.md)。

## 许可证

[MIT](LICENSE)
