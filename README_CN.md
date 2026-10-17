# XMind MCP

将 Markdown、文本大纲、HTML、Word、Excel 转为 XMind，并通过 MCP 提供创建、读取、结构分析、文件列举及标题翻译。

[English](README.md) · [文档导航](docs/README.md)

## 快速开始

需要 UV 和 Python 3.11+。在仓库根目录运行当前源码，并将输出目录替换为本机绝对路径：

```bash
uvx --python 3.12 --from . xmind-mcp --stdio --default-output-dir /absolute/path/to/output
```

客户端通过标准输入/输出连接；服务在终端等待输入是正常现象。使用 `uvx xmind-mcp` 会安装已发布包，不包含尚未发布的本地修改。

本项目使用 MCP Python SDK v2，支持 `2026-07-28` 协议以及旧客户端握手。`--mode fastmcp`、`--mode stdio`、`--stdio` 保留为兼容参数，使用相同 STDIO 入口。

完整 MCP 配置和路径规则见 [使用指南](docs/USAGE_GUIDE.md)。

## 六个 MCP 工具

| 工具 | 用途 |
| --- | --- |
| `create_mind_map` | 根据 JSON 主题结构创建导图 |
| `read_xmind_file` | 读取首个画布的主题结构与统计 |
| `analyze_mind_map` | 分析节点、层级和结构 |
| `convert_to_xmind` | 转换支持的文件格式 |
| `list_xmind_files` | 按目录、通配模式和深度列举文件 |
| `translate_xmind_titles` | 调用外部翻译服务处理标题 |

创建主题推荐使用 `title` + `children`，兼容旧字段别名。输出型工具需要默认绝对输出目录或显式绝对输出路径。标题翻译需要网络；可选 AI 扩展没有作为额外 MCP 工具注册。

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
