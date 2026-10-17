# 使用指南

[返回文档导航](README.md)

本项目通过 MCP 提供 XMind 创建、读取、分析、格式转换、文件列举及标题翻译，也提供独立转换命令。需要 Python 3.11+；以下环境示例使用 Python 3.12。

## 安装与启动

### 从当前源码启动 MCP

在仓库根目录执行：

```bash
uvx --python 3.12 --from . xmind-mcp --stdio --default-output-dir /absolute/path/to/output
```

MCP 客户端通常负责启动此进程并连接其标准输入/输出。在终端单独运行后等待输入属于正常行为。

本地开发环境的安装与测试见 [开发与发布](DEVELOPMENT.md)。已有虚拟环境也可通过 `python -m xmind_mcp` 启动同一个入口。

### 从已发布包启动

```bash
uvx --python 3.12 xmind-mcp --stdio --default-output-dir /absolute/path/to/output
```

此命令使用 PyPI 已发布版本；本地尚未发布的修改必须用 `--from .` 或指定源码目录。

| 参数 | 作用 |
| --- | --- |
| `--version` | 显示应用版本 |
| `--help` | 显示帮助 |
| `--debug` | 开启调试日志，写入 stderr |
| `--stdio` | STDIO 兼容别名 |
| `--mode fastmcp` / `--mode stdio` | 历史兼容参数，均使用同一 STDIO 传输 |
| `--default-output-dir` | 默认输出目录，优先于环境变量 |

当前使用 MCP Python SDK v2，支持 `2026-07-28` 协议及旧客户端的 `initialize` 握手。当前入口是 STDIO 服务，不提供旧文档中的 `/health`、`/tools/*` REST 接口。

## MCP 客户端配置

在 Trae 等支持 STDIO MCP 的客户端中添加以下配置，并将两处 `/absolute/path/...` 替换为本机绝对路径。客户端配置文件的保存位置由客户端决定。

```json
{
  "mcpServers": {
    "xmind": {
      "command": "uvx",
      "args": [
        "--python", "3.12",
        "--from", "/absolute/path/to/XmindMcp",
        "xmind-mcp", "--stdio"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "XMIND_MCP_DEFAULT_OUTPUT_DIR": "/absolute/path/to/output"
      }
    }
  }
}
```

Windows 可使用 `D:/project/XmindMcp`、`D:/project/XmindMcp/output` 等路径；JSON 中反斜杠需要转义。仓库 [配置示例](../configs/mcp_config.json) 也需要按本机目录修改。源码目录使用绝对路径，避免客户端启动位置不同导致找不到项目。

若要连接已发布包，删除 `--from` 和其后的源码目录参数即可。客户端启动后应能列出下面六个工具。

## 路径与读取预算

| 场景 | 规则 |
| --- | --- |
| MCP 转换源文件 | `source_filepath` 或旧别名 `source_file` 必须为绝对路径 |
| 显式输出文件 | `output_path` / `output_filepath` / `output_file` 必须为绝对路径 |
| 省略输出文件 | 使用默认输出目录；未配置则返回错误 |
| 文件列举 | 显式 `directory` 必须为绝对路径；省略时使用默认输出目录 |
| 读取、分析、翻译源文件 | 建议使用绝对路径；相对路径按配置创建时捕获的基准目录解析 |
| 独立转换 CLI | 可以输入相对路径，CLI 会先解析为绝对路径 |

默认输出目录优先级为：CLI `--default-output-dir`，然后是 `XMIND_MCP_DEFAULT_OUTPUT_DIR`。相对默认目录仅在设置了绝对 `XMIND_MCP_BASE_DIR` 时有效；例如基准目录 `/work/project` 加默认目录 `output`，得到 `/work/project/output`。

XMind 读取与分析可设置以下环境变量：

| 环境变量 | 默认值 | 含义 |
| --- | --- | --- |
| `XMIND_MAX_FILE_SIZE_MB` | `200` | 压缩文件大小，以及所读取内容成员的解压总大小上限 |
| `XMIND_MAX_NODE_COUNT` | `50000` | 返回主题树的节点上限，包含根节点 |
| `XMIND_MAX_PARSE_DEPTH` | `30` | 返回主题树的深度上限，根节点深度为 0 |

体积超限会在读取内容前报错。节点或深度超限时，返回裁剪后的树及相应统计，并在消息中注明降级；这些配置不代表对所有输入格式的转换或翻译都采用相同预算。

## MCP 工具与主题结构

下列示例均为对应工具的 **arguments 对象**，应通过 MCP 客户端调用，而不是向 HTTP 地址提交。

### 创建导图

工具：`create_mind_map(title, topics_json, output_path?)`。

```json
{
  "title": "项目计划",
  "topics_json": "[{\"title\":\"开发\",\"children\":[{\"title\":\"实现\"},{\"title\":\"测试\"}]},{\"title\":\"发布\"}]",
  "output_path": "/absolute/path/to/output/plan.xmind"
}
```

`title` 是根节点标题；`topics_json` 是其子主题结构的 JSON 字符串。推荐每个节点使用 `title` 和 `children`；兼容子节点别名 `topics`、`subtopics`、`nodes`、`items`，标题别名 `name`、`text`。

Python 调用应用服务时可用 `json.dumps(topics, ensure_ascii=False)` 生成字符串，避免手工转义。MCP 参数 schema 要求字符串，不要把 Python 字典的字符串表示或带注释的文本当作 JSON。非 JSON 文本虽有简单标题回退，无法表达预期的复杂主题树。

内存中已有 JSON 主题结构时使用此工具；`convert_to_xmind` 用于解析实际文件，不会把 JSON 文件自动当作主题树。

### 读取与分析

`read_xmind_file(file_path)` 与 `analyze_mind_map(file_path)` 使用相同参数：

```json
{
  "file_path": "/absolute/path/to/output/plan.xmind"
}
```

读取返回 `data.structure` 和 `stats`；分析返回 `data.structure_analysis` 和 `stats`。`total_nodes` 包含根节点，`max_depth` 从根节点的 0 开始计数。当前读取和分析处理首个画布。

### 转换文件

工具：`convert_to_xmind(source_filepath?, output_filepath?, source_file?, output_file?)`。

```json
{
  "source_filepath": "/absolute/path/to/XmindMcp/examples/test_markdown.md",
  "output_filepath": "/absolute/path/to/output/converted.xmind"
}
```

`source_file` / `output_file` 是旧参数别名；新调用建议使用 `source_filepath` / `output_filepath`。

### 列举导图

工具：`list_xmind_files(directory?, recursive?, pattern?, max_depth?)`。

```json
{
  "directory": "/absolute/path/to/output",
  "recursive": true,
  "pattern": "*.xmind",
  "max_depth": 2
}
```

`pattern` 是文件名通配模式；`max_depth: 0` 仅搜索当前目录。

### 翻译标题

工具：`translate_xmind_titles(source_filepath, output_filepath?, target_lang?, overwrite?)`。

```json
{
  "source_filepath": "/absolute/path/to/output/plan.xmind",
  "output_filepath": "/absolute/path/to/output/plan_en.xmind",
  "target_lang": "en",
  "overwrite": false
}
```

默认目标语言为 `en`。此操作通过外部翻译服务处理标题，需要网络连接；其他五个核心工具不依赖该翻译服务。翻译会复制原压缩包并替换选定内容成员的标题，保留其他压缩包成员；不会将简化主题树当作整个原文件重新生成。

### 返回结果

工具返回包含 JSON 的文本。成功结果使用 `status: "success"`，失败使用 `status: "error"`，并包含 `message`；错误可附带 `error_code`。统计在顶层 `stats`，业务数据在 `data`。

MCP 写入型工具的成功结果展示文件名；读取和列举结果可能包含完整路径。创建、转换及翻译采用同目录临时文件，ZIP 校验成功后原子替换目标，写入失败时保留已有文件。

## 独立文件转换

在仓库根目录运行，输出路径是第二个位置参数：

```bash
uv run xmind-convert examples/test_markdown.md output/markdown.xmind
uv run xmind-convert examples/test_word.docx output/word.xmind
uv run xmind-convert examples/test_excel.xlsx output/excel.xmind
```

安装本项目后也可用：

```bash
xmind-convert input.md output/result.xmind
```

省略第二个参数时，输出到执行命令时工作目录下的 `output/<源文件名>.xmind`。此 CLI 没有 `--output`、`--batch` 或 `--format` 参数；批量转换可用 shell 循环或应用服务循环调用。

| 格式 | 扩展名 | 当前转换方式 |
| --- | --- | --- |
| Markdown | `.md`、`.markdown` | 识别一至六级标题，首个一级标题用作文档标题 |
| 文本 | `.txt`、`.text` | 读取缩进大纲；建议每层使用四个空格 |
| HTML | `.html`、`.htm` | 按文档顺序处理标题；无标题时尝试列表 |
| Word | `.docx` | 根据标题样式组织层级 |
| Excel | `.xlsx` | 读取活动工作表；建议第一列使用 1、2、3 等数字层级，第二列放标题 |

文本输入使用 UTF-8。当前不提供 CSV、JSON、XML、YAML、OPML 文件转换，也不支持旧版二进制 `.xls`。文件转换针对标题和大纲，不承诺保留原文全部排版、段落、图片及链接。

## 常见问题

| 现象 | 检查方式 |
| --- | --- |
| 客户端启动不了进程 | 在相同环境确认 `uv` / `uvx` 可用；检查源码目录、Python 版本和客户端配置 |
| 找不到新修改或工具 | 确认连接的是 `--from` 指定的当前源码，而不是旧的已发布包；重启该 MCP 连接 |
| 缺少输出路径 | 设置默认绝对输出目录，或在调用中传入绝对输出路径 |
| 转换找不到源文件 | MCP 使用源文件绝对路径；确认文件存在且进程有读取权限 |
| 生成树的层级不对 | 检查源文件标题/缩进；直接生成主题时检查 `topics_json` 是否为有效 JSON |
| 节点数少于预期 | 检查是否只读取首个画布、是否触发预算裁剪，以及输入格式是否以标题为结构 |
| 翻译没有变化 | 检查目标语言、网络及翻译服务；当前实现只尝试含非 ASCII 字符的标题，失败时可保留原文 |
| 需要调试日志 | 启动时加 `--debug`，查看客户端收集的 stderr 日志 |

MCP 版本迁移和扩展方式见 [架构说明](ARCHITECTURE.md)，测试及构建见 [开发与发布](DEVELOPMENT.md)。
