# XMind MCP 项目结构

本文件反映当前仓库结构与模块职责，并统一路径与部署约束（UVX-only、输出型绝对路径、返回裁剪）。示例路径均使用相对路径。

## 目录结构

```
XmindMcp/
├── configs/                      # 配置文件目录
│   └── mcp_config.json           # MCP 服务配置（示例使用相对路径）
├── docs/                         # 文档目录
│   ├── AI_INPUT_GUIDE.md
│   ├── OPTIMIZATION_REPORT.md
│   ├── PROJECT_STRUCTURE.md
│   ├── TRAE_MCP_SETUP.md
│   ├── UNIVERSAL_CONVERTER_USAGE.md
│   ├── USAGE_GUIDE.md
│   └── xmind_ai_mcp_design.md
├── examples/                     # 示例输入目录（相对路径示例）
│   ├── test_auto/
│   ├── test_excel.xlsx
│   ├── test_html.html
│   ├── test_markdown.md
│   ├── test_txt.txt
│   └── test_word.docx
├── output/                       # 输出结果目录（示例路径）
├── scripts/
│   └── translate_xmind_titles.py # 非 MCP 场景的转换脚本
├── tests/                        # 测试与演示
│   ├── alias_validate.py
│   ├── run_all_tests.py
│   ├── test_batch.py
│   ├── test_client.py
│   ├── test_core.py
│   └── test_setup.py
├── xmind_mcp/                    # 包入口（uvx 执行）
│   ├── __init__.py
│   └── __main__.py
├── universal_xmind_converter.py
├── validate_xmind_structure.py
├── xmind_ai_extensions.py
├── xmind_core_engine.py
├── xmind_mcp_server.py
├── xmind_types.py
├── xmind_writer.py
├── README.md
├── README_CN.md
├── SECURITY.md
├── UVX_DEPLOYMENT_GUIDE.md
├── package.json
├── pyproject.toml
├── requirements.txt
└── configs/mcp_config.json        # MCP 服务配置（通过 env 设置输出目录）
```

## 模块职责

### 服务器层：`xmind_mcp_server.py`
- FastMCP 服务端与工具注册（读取、创建、分析、转换、列出文件、翻译标题）。
- 统一输出路径解析（绝对路径校验与目录创建）与返回结果裁剪（不暴露绝对路径）。
- UVX-only 部署约束：MCP 服务必须通过 `uvx xmind-mcp` 启动。

### 核心引擎：`xmind_core_engine.py`
- 业务逻辑聚合：读取与分析 XMind、创建与写入、类型化返回。
- 与 `xmind_writer.py` 协作完成文件写入，统一结构化类型在 `xmind_types.py`。
- 与 `universal_xmind_converter.py` 对接实现多格式解析。

### 写入器：`xmind_writer.py`
- 承担写入与文件生成的底层实现，提供稳定接口供服务层与引擎调用。

### 类型定义：`xmind_types.py`
- 提供数据类与类型约束，确保工具返回结构一致、可序列化。

### 通用转换器：`universal_xmind_converter.py`
- 负责源文件格式解析与结构提取（TXT/HTML/Word/Excel/Markdown）。
- 采用懒加载依赖与容错解析，不使用任何模拟数据。

### AI 扩展：`xmind_ai_extensions.py`
- 可选模块，默认关闭；通过环境变量 `XMIND_ENABLE_AI=1` 显式启用。
- 当未启用或没有密钥时不暴露任何 AI 工具；`get_ai_tools()` 返回空列表。

### 包入口：`xmind_mcp/__main__.py`
- 提供 `uvx xmind-mcp` 的执行入口；遵循 UVX-only 部署规范。

### 脚本与测试
- `scripts/translate_xmind_titles.py`：非 MCP 场景下的标题翻译脚本。
- `tests/`：保留测试与演示能力（不用于 MCP 部署路径）。

## 运行与路径策略
- 文档中的路径示例统一使用相对路径（如 `examples/...`、`output/...`）。
- MCP 服务启动示例：
  - `uvx xmind-mcp --mode fastmcp`
  - 默认输出目录通过 IDE 的 `configs/mcp_config.json` 中 `env` 设置，如：
    - `XMIND_MCP_BASE_DIR`: 基准绝对目录（例如工作区根）
    - `XMIND_MCP_DEFAULT_OUTPUT_DIR`: 默认输出目录（建议相对，如 `output/`，将与基准目录拼接）
- 输出型工具（创建/转换/翻译）在内部统一解析为绝对路径；返回结果裁剪为文件名或相对形式，避免外泄绝对路径。
- 配置项 `default_output_dir` 在实际运行中要求绝对路径；文档示例以相对路径展示，可通过环境变量传入基准目录（如 `XMIND_MCP_BASE_DIR`）以适配不同环境。

## 维护说明
- 已移除过时条目：`start_mcp_server.py`、`xmind_simple_server.py`、`xmind_mcp_client.py`、`markdown_to_xmind_converter.py`、`demo_merged.py` 等。
- 文档与实现保持一致：UVX-only、输出型绝对路径策略、返回裁剪统一。