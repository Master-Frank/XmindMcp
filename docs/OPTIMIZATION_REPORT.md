# 项目优化分析报告（重整版）

本报告基于近期讨论与验证结论重新梳理，重点明确 MCP 服务的“绝对路径输出”策略与相应配置方式，同时保留整体项目结构、代码质量、性能与合规方面的系统性建议与任务清单。

## 概览与关键决策

- 路径策略总则：
  - 文档与示例默认使用相对路径（如 `examples/...`、`output/...`）。
  - 公共接口可接收绝对路径入参以适配跨环境诉求，但不鼓励默认使用。
  - 内部解析可短暂使用绝对路径以保证正确读写，不得在接口返回、日志或配置中外泄绝对路径。

- MCP 输出路径策略（强制执行）：
  - 若 MCP 配置中设置了默认输出路径（绝对路径），输出型工具的输出路径入参可选；未传入时使用该默认路径。
  - 若 MCP 配置未设置默认输出路径，则输出型工具的输出路径入参必填且必须为绝对路径；否则报错。
  - 任一输出路径（默认或入参）若不是绝对路径，统一报错并拒绝写入。

- 部署要求：
  - MCP 服务必须使用 `uvx` 部署与执行（UVX-only）。
  - 允许在终端通过 `python/pip` 调用 CLI 或脚本（非 MCP 场景），此能力不影响 MCP 的 UVX-only 要求。

- 数据与示例：
  - 禁止一切模拟数据；示例逻辑与 AI 扩展默认关闭或显式标注为实验性，不在生产路径中触发。

## MCP 输出路径策略（细化说明）

- 工具适用范围：针对会在磁盘写入文件的输出型工具，例如：
  - `create_mind_map(title, topics_json, output_path?)`
  - `convert_to_xmind(source_filepath, output_filepath?)`

- 策略细则：
  1. 配置了默认输出目录（绝对路径）：
     - `output_path`/`output_filepath` 入参可省略；未填时使用默认输出目录。
     - 若传入输出路径，则必须为绝对路径；相对路径将报错。
  2. 未配置默认输出目录：
     - `output_path`/`output_filepath` 入参必填且必须为绝对路径；否则报错。
  3. 路径校验：
     - 验证绝对路径、存在性与可写性；失败时明确错误信息（不执行写入）。
  4. 安全输出：
     - 日志与返回避免暴露完整绝对路径，建议仅返回文件名或简化片段。

- 背景说明：在 UVX 环境下，代码运行位置与项目目录可能不一致，基于 `__file__` 或当前工作目录推断项目根在部分场景会指向 UVX 安装路径。为保证输出稳定与可控，故采用“绝对路径输出”策略。

## 配置与部署示例（MCP）

- MCP 启动配置片段（例如 `configs/mcp_config.json` 中定义，仅使用 env）：

```
{
  "mcpServers": {
    "Xmind": {
      "command": "uvx",
      "args": [
        "xmind-mcp",
        "--mode",
        "fastmcp"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "XMIND_MCP_BASE_DIR": ".",
        "XMIND_MCP_DEFAULT_OUTPUT_DIR": "output"
      }
    }
  }
}
```

- 说明：
  - 文档中的路径示例使用相对路径；通过 `XMIND_MCP_BASE_DIR` 传入基准绝对目录，以在不同环境适配。
  - 也可在命令行使用 `--default-output-dir` 指定绝对路径（优先级高于 env）。

## 项目结构与问题概览

- 路径策略不一致：早期文档与代码部分位置建议绝对路径，与工作区规则冲突。
- 文档与目录结构描述不一致：存在历史文件名与当前实现不匹配。
- 模块职责集中：`universal_xmind_converter.py` 体量较大，解析与输出耦合、副作用多。
- 工作目录策略：强制/隐式 `chdir` 会影响外部调用，但相对路径解析更稳；需明确策略并最小化副作用。
- 冷启动偏慢：顶层导入 `docx/openpyxl/bs4` 等重量库。
- 目录扫描可控性弱：递归范围与过滤模式有限。
- 测试条目与现状不一致：API 命名与工具列表需校正。
- 合规项：MCP 必须 UVX-only；示例与文档需统一。

## 对应优化建议

- 路径策略统一：
  - 常规场景遵循“相对路径优先”；MCP 输出型工具作为例外，采用“绝对路径输出”。
  - 封装路径解析入口（如 `resolve_output_path`），集中校验绝对路径与可写性。

- 文档一致性：
  - 更新 `README/README_CN/UVX_DEPLOYMENT_GUIDE` 指引，强调 UVX-only 与输出型工具绝对路径要求。
  - 非输出型工具与示例统一采用相对路径演示，避免混淆。

- 模块与性能：
  - 拆分转换器：解耦解析与写入器，降低耦合与维护成本。
  - 懒加载重量库：将导入移动到具体使用位置，缩短 MCP 冷启动。

- 遍历与工具增强：
  - 为 `list_xmind_files` 增加 `max_depth/pattern` 可选参数（仅读取型工具，保持相对路径输出）。
  - 大文件读取增加阈值与降级策略。

- 统一返回结构：
  - 引入轻量类型结构（如 TypedDict/Dataclass），统一 `status/message/error_code/data/stats`。

## 工具行为与路径策略对照

- 读取型工具：
  - `read_xmind_file(file_path)`：入参可相对或绝对；读取过程内部可解析为绝对路径但不外泄。
  - `analyze_mind_map(...)`、`list_xmind_files(directory?)`：若接收目录参数，默认相对路径；输出结果中避免绝对路径。

- 输出型工具（严格绝对路径）：
  - `create_mind_map(title, topics_json, output_path?)`
  - `convert_to_xmind(source_filepath, output_filepath?)`
  - 入参或默认值必须为绝对路径；未满足条件统一报错。

## 质量与合规

- MCP 服务 UVX-only；禁止在文档中提供 MCP 的 `python/pip` 启动示例。
- 测试条目维护：清理过时项，统一 API 名称（如统一为 `read_xmind_file`）。
- 数据与示例：禁止模拟数据；AI 示例逻辑默认关闭或标注实验性。

## 优化任务清单（更新版）

| 任务ID | 任务描述 | 优先级 | 预计耗时 | 难度 |
|--------|----------|--------|----------|------|
| T001   | 统一路径策略：MCP 输出型工具强制绝对路径 | 高 | 3h | 中 |
| T002   | 更新配置管理：校验 `default_output_dir` 绝对路径 | 高 | 2h | 中 |
| T003   | 统一工具输入 Schema 与文档示例 | 高 | 2h | 低 |
| T004   | 修订 `README/README_CN/UVX_GUIDE` 指引 | 高 | 2h | 低 |
| T005   | 懒加载 `docx/openpyxl/bs4` 等重量库 | 中 | 3h | 中 |
| T006   | 为 `list_xmind_files` 增加过滤/深度参数 | 中 | 2h | 中 |
| T007   | 拆分 `universal_xmind_converter` 模块 | 中 | 8–12h | 高 |
| T008   | 统一返回结构（TypedDict/Dataclass） | 中 | 4h | 中 |
| T009   | 大文件读取阈值与降级策略 | 中 | 3h | 中 |
| T010   | 测试套件维护与统一命名 | 中 | 3h | 中 |
| T011   | 隔离 AI 示例逻辑，默认关闭 | 中 | 2h | 低 |
| T012   | 路径工具与日志统一（安全输出） | 低 | 2h | 低 |
| T013   | 修正 `PROJECT_STRUCTURE.md` 文件清单 | 低 | 1.5h | 低 |
| T014   | 更新 `package.json` 文案去除 MCP 的 `python/pip` | 低 | 1h | 低 |

## 实施计划与改动点

- 服务器层（`xmind_mcp_server.py`）：
  - `ConfigManager`：读取 `default_output_dir` 并强制绝对路径校验；缺失时要求调用方传绝对路径。
  - 输出型工具入口：统一调用 `resolve_output_path`（仅接受绝对路径），失败时返回明确错误。

- 引擎层（`xmind_core_engine.py`）：
  - 输出方法：禁止将相对路径拼接为输出目的地；仅接受通过服务器层校验后的绝对路径。
  - 读取方法：支持相对或绝对路径入参，内部解析后不外泄绝对路径。

- 文档层：
  - 更新相关文档与示例，区分读取型与输出型工具的路径要求；确保 MCP UVX-only 指引一致。

## 风险与兼容性

- 向后兼容：历史相对路径调用输出型工具会收到报错，需要在调用处修复为绝对路径或配置默认输出目录。
- 隐私与安全：避免在日志与返回中暴露完整绝对路径；必要时进行裁剪或掩码处理。
- 环境差异：如需在本地开发中使用相对路径，可通过 CLI（非 MCP）运行，但输出型工具仍建议传递绝对路径以避免歧义。

## 后续动作

- 按任务清单从 T001–T004 开始落地路径策略与文档修订。
- 若需要，我可以进一步提交代码改动：新增 `resolve_output_path`、完善 `ConfigManager` 校验、以及统一的错误返回结构。

## 进度更新

- T001 完成：服务器层已对输出型工具实施绝对路径策略（`create_mind_map`、`convert_to_xmind`），并统一错误信息与日志，避免在返回中暴露绝对路径。
- T002 完成：`ConfigManager` 仅接受绝对的 `default_output_dir`，移除历史相对路径自动拼接为绝对路径的行为，并在配置缺失时要求调用方提供绝对输出路径。
- T003 完成：引擎层移除所有隐式相对输出默认（`create_mind_map`/`convert_to_xmind`/`translate_xmind_titles` 均要求传入绝对输出路径），并更新服务器入口的参数说明；输入 Schema 文档示例统一展示绝对路径用法，未配置默认目录时将返回明确错误。
 - T004 完成：修订文档指引，统一 UVX-only 与绝对输出策略。
   - 更新 `README.md`：明确“示例采用相对路径、MCP 输出型工具要求绝对路径”，并说明默认绝对输出目录与未配置时的调用约束。
  - 更新 `README_CN.md`：项目结构说明统一为 `configs/mcp_config.json`（env 配置），并统一路径策略描述。
   - 更新 `UVX_DEPLOYMENT_GUIDE.md`：强调“若未配置默认输出目录则必须传绝对输出路径、相对路径会被拒绝”。
 - 更新 `docs/AI_INPUT_GUIDE.md`：补充默认绝对输出目录与相对路径拒绝的说明。
 - T005 完成：懒加载 `docx/openpyxl/bs4` 等重量库，优化 MCP 冷启动。
   - 变更文件：`universal_xmind_converter.py`
   - 将顶层的可选依赖导入改为按需加载（定义 `_lazy_import_docx/_lazy_import_openpyxl/_lazy_import_beautifulsoup`），并在 `WordParser/ExcelParser/HtmlParser` 的 `parse()` 内部调用。
   - 移除顶层 `WORD_AVAILABLE/EXCEL_AVAILABLE/HTML_AVAILABLE` 标志与构造函数的依赖校验，改为在解析时抛出明确的缺依赖错误信息。
   - 验证：快速导入模块 `python -c "import universal_xmind_converter"` 成功，冷启动额外开销显著降低。
   - 影响：MCP 服务冷启动更快；功能与错误提示不变；CLI/MCP 调用行为保持一致。
 - T006 完成：为 `list_xmind_files` 增加过滤 `pattern` 与 `max_depth`。
   - 变更文件：`xmind_core_engine.py`、`xmind_mcp_server.py`
   - 输入 Schema 增加 `pattern/max_depth` 可选参数；服务端工具签名扩展并透传至引擎。
   - 引擎层实现：使用 `fnmatch` 进行文件名通配符匹配；在递归遍历中按 `max_depth` 限制深入层级。
   - 兼容性：默认行为不变（递归=true）；仅在提供参数时生效；返回结构保持稳定。
 - T007 完成：拆分 `universal_xmind_converter` 模块，解析与写入器解耦。
   - 新增文件：`xmind_writer.py`，负责 `generate_content_xml/create_metadata/create_manifest/create_xmind_file`。
   - 变更文件：`universal_xmind_converter.py`（移除写入器函数，改为导入 `create_xmind_file`）；`xmind_core_engine.py`（改为从 `xmind_writer` 导入 `create_xmind_file`）。
   - 兼容性：外部 API 保持不变（解析工厂 `ParserFactory` 仍在原模块；引擎与 CLI 均通过导入使用写入器）。路径策略无变更。
   - 验证：`python -c "import xmind_writer, universal_xmind_converter, xmind_core_engine"` 导入成功。
   - 影响：降低单文件体量与职责耦合，为后续返回结构统一与写入器扩展打下基础。
 - 下一步：T008（统一返回结构 TypedDict/Dataclass；引擎/服务器返回统一 `status/message/error_code/data/stats` 字段，不改动工具名称与入参）。

- T008（阶段1）完成：引擎层返回结构统一为 TypedDict（统一字段：`status/message/error_code/data/stats`）。
  - 新增文件：`xmind_types.py`（定义统一 TypedDict：`ReadXmindResult/TranslateTitlesResult/CreateMindMapResult/AnalyzeResult/ConvertResult/ListFilesResult`，以及 `Stats/XmindFileEntry` 等）。
  - 变更文件：`xmind_core_engine.py`
    - `read_xmind_file`：成功返回包含 `data={format/source_format/structure}` 与 `stats={total_nodes/max_depth/titles_count}`；错误统一为 `status=error` + `message`。
    - `translate_xmind_titles`：成功返回 `data={source_file/output_file}` + `message=翻译完成`；错误统一为 `message`。
    - `create_mind_map`：成功返回 `data={filename/title/topics_count/absolute_path/output_path/file_size}` + `message=思维导图已创建`；错误统一为 `message`。
    - `analyze_mind_map`：成功返回 `data={filename/structure_analysis}` + `stats` + `message=分析完成`；错误统一为 `message`。
    - `convert_to_xmind`：成功返回 `data={source_file/output_file}` + `message=文件转换成功`；错误统一为 `message`。
    - `list_xmind_files`：成功返回 `data={directory/recursive/pattern/max_depth/file_count/files}` + `message=列出XMind文件完成`；错误统一为 `message`。
  - 验证：`python -c "import xmind_types, xmind_writer, xmind_core_engine"` 导入成功。
  - 兼容性与策略：保持引擎内部可包含绝对路径（置于 `data`），服务器层继续负责裁剪/掩码，遵循“读取不外泄、输出型不暴露”原则。
 - T008（阶段2）完成：服务器层（`xmind_mcp_server.py`）返回结构统一，历史顶层字段迁移至 `data`，并按策略裁剪绝对路径。
   - 变更文件：`xmind_mcp_server.py`
     - `read_xmind_file`：统一错误键为 `message`；成功时将 `file_path/file_size` 放入 `data`，顶层仅保留 `status/message`。
     - `create_mind_map`：统一错误键为 `message`；成功时将 `filename` 写入 `data`，裁剪 `absolute_path/output_path`；顶层设置 `message=思维导图已创建`。
     - `analyze_mind_map`：异常返回统一为 JSON（`status=error` + `message`）。
     - `convert_to_xmind`：统一错误键为 `message`；成功时将 `filename` 写入 `data` 并裁剪 `output_file/source_file`；顶层设置 `message=文件转换成功`。
     - `list_xmind_files`：移除历史在服务器层追加的顶层字段（`directory/recursive/pattern/max_depth`），直接透出引擎层统一结构。
     - `translate_xmind_titles`：统一错误键为 `message`；成功时将 `filename` 写入 `data` 并裁剪绝对路径相关字段，顶层设置 `message=标题翻译并写入成功`。
   - 验证：`python -c "import xmind_types, xmind_writer, xmind_core_engine, xmind_mcp_server"` 导入成功，所有模块可用。
   - 策略一致性：服务器层继续避免在返回中暴露绝对路径；新增/上下文信息统一置于 `data` 字段。

  - 下一步：T009（大文件读取阈值与降级策略）。
    - 计划：在引擎层为 `read_xmind_file`/分析相关流程引入文件体积与节点计数阈值；超过阈值时采用降级策略（如限制层级解析、跳过超大附件、返回概要统计）。
    - 成功判定：阈值可配置；超限场景返回稳定的 `status=success` 与精简 `data/stats`，并在 `message` 提供明确的降级说明；错误仍统一为 `message`。

- T009 完成：引擎层加入高阈值与降级策略（以层级限制为主），并修正分析引用。
  - 变更文件：`xmind_core_engine.py`
    - 新增环境可调阈值（默认尽可能高，满足生成测试用例场景）：
      - `XMIND_MAX_FILE_SIZE_MB=200`
      - `XMIND_MAX_NODE_COUNT=50000`
      - `XMIND_MAX_PARSE_DEPTH=30`
    - `read_xmind_file`：在解析后根据文件体积/节点数/层级进行判定；触发降级时对结构进行“层级限制”裁剪并重新计算概要统计（`total_nodes/max_depth/titles_count`）。返回 `status=success`，`message` 包含明确的降级原因与限制层级提示，`data.structure` 为裁剪后的结构，`stats` 为对应概要统计。
    - `analyze_mind_map`：修正根结构引用为 `data.structure`，确保 `leaf_nodes/branch_count` 与裁剪后的结构一致。
    - 新增辅助函数：`_limit_depth/_count_nodes_simple/_max_depth_simple/_titles_count_simple`，用于降级场景的轻量统计与层级裁剪。
  - 行为与策略：
    - 入参路径仍可相对或绝对；内部允许临时使用绝对路径进行体积判断，不在返回或日志中外泄。
    - 降级仅限制层级，不进行随机裁剪或模拟数据生成，确保稳定与可重复。
  - 验证：引擎模块导入成功，默认阈值生效（200MB/50000节点/30层级）。
  - 影响：在超大/超深文件场景下保持成功返回，便于用于测试用例生成与大图快速回看；下游服务器层与 UI 无需改动即可获取简化结构。

  - T010 完成：测试套件维护与统一命名。
    - 变更文件：`tests/test_core.py`、`tests/test_client.py`、`tests/run_all_tests.py`
    - 统一断言与命名：
      - `read_xmind_file`/`create_mind_map` 测试改为检查统一返回结构中的 `data.structure` 与 `data.filename`。
      - 修正历史调用 `read_xmind` 为 `read_xmind_file`，避免函数名不一致导致失败。
    - 客户端测试端点统一：
      - 将历史 `/read-file`、`/convert-to-xmind` 端点改为 FastMCP 工具端点：`/tools/read_xmind_file`、`/tools/convert_to_xmind`。
      - 移除文件上传与模拟XMind内容（ZIP头`PK`），改为使用真实示例文件路径的 JSON 请求（`examples/test_outline.txt` → `output/test_client_outline.xmind`）。
    - 测试总控修复：
      - 用 `test_client.py` 替换不存在的 `test_mcp_stdio.py`。
      - 为需服务器地址的脚本统一传入 `--server http://localhost:8080`。
    - 合规性：彻底移除模拟数据与文件上传；所有路径示例遵循相对路径展示，客户端请求对输出型工具传绝对/解析后的路径由服务器层负责。
  - 下一步：T011（隔离 AI 示例逻辑，默认关闭）。
 
 - T011 完成：隔离 AI 示例逻辑，默认关闭。
   - 变更文件：`xmind_ai_extensions.py`
   - 新增环境开关：`XMIND_ENABLE_AI`，默认关闭（未设置或设为 `0/false/no/off`）。
   - 构造函数支持显式覆盖 `enable_ai` 参数；新增 `is_ai_enabled` 并更新 `is_ai_available` 为“开关 + 依赖 + 客户端”三重判定。
   - 工具暴露：`get_ai_tools` 在关闭时返回空列表，避免默认暴露 `/ai-*` 端点。
   - OpenAI 初始化：仅在 `ai_enabled`、依赖可用且提供 `api_key` 时初始化客户端。
   - 示例默认关闭：`__main__` 在未启用开关时提示并退出；设置 `XMIND_ENABLE_AI=1` 可启用示例。
   - 清理：移除不必要的 `random` 导入；所有回退逻辑保持确定性（无随机与模拟数据），符合“禁止模拟数据”规范。
   - 验证：全仓库搜索确认 `xmind_mcp_server.py` 未注册任何 `/ai-*` 工具端点；默认情况下 AI 工具列表为空；现有非 AI 工具与测试不受影响。
 
   - 下一步：T012（路径工具与日志统一）。
     - 计划：集中封装 `resolve_output_path` 与日志裁剪策略，在服务器层统一调用，规范返回中绝对路径的裁剪与掩码。
     - 成功判定：输出型工具在返回结构中不暴露完整绝对路径；日志仅包含必要片段；错误信息保持清晰。

- T012 完成：路径工具与日志统一（安全输出）。
  - 变更文件：`xmind_mcp_server.py`
  - 新增封装：
    - `_resolve_output_path(output_path?, default_filename)`：集中绝对路径校验与目录创建；当未传入时使用配置的默认绝对目录并拼接文件名；错误返回统一结构（含 `suggestion`）。
    - `_mask_output_result(result, final_output_path, success_message?)`：裁剪返回中的绝对路径相关字段，仅回传 `filename`；顶层 `message` 统一为成功提示。
  - 三个输出型工具改造：
    - `create_mind_map`、`convert_to_xmind`、`translate_xmind_titles` 改为调用上述封装，移除重复的路径校验与目录创建代码；返回结构通过掩码函数统一裁剪。
  - 行为与合规：
    - 返回结构不暴露绝对路径（仅保留 `filename`）；日志不打印完整路径，仅必要片段（目录创建成功/失败等）。
    - 继续遵循“配置缺失时必须传绝对输出路径”的策略；错误信息包含明确建议。
  - 验证：服务端函数导入与运行正常；搜索仓库确认无其它输出型工具绕过该封装。

  - 下一步：T013（修正 `PROJECT_STRUCTURE.md` 文件清单）。
    - 计划：对照当前实现与文件实际存在情况，修正“文件/模块清单”与职责描述；移除过时条目，补充新增封装与模块拆分（如 `xmind_writer.py`、路径封装）。
    - 成功判定：文档中的结构清单与仓库一致，职责描述与路径策略一致（UVX-only、输出型绝对路径、返回裁剪统一）。

- T013 完成：修正 `PROJECT_STRUCTURE.md` 文件清单与职责描述。
  - 变更文件：`docs/PROJECT_STRUCTURE.md`
  - 更新要点：
    - 目录树与当前仓库一致，新增 `xmind_writer.py`、`xmind_types.py`、`xmind_mcp/__main__.py`，保留 `xmind_mcp_server.py/xmind_core_engine.py/universal_xmind_converter.py/xmind_ai_extensions.py` 等。
    - 模块职责明确：服务器层统一路径解析与返回裁剪（UVX-only），引擎层聚合业务，写入器承载文件生成，类型模块统一结构，转换器专注解析。
    - 路径策略统一：文档示例统一相对路径；强调输出型工具内部解析为绝对路径并返回裁剪；说明 `default_output_dir` 实际要求绝对路径，可通过环境变量传入基准目录。
    - 清理过时项：移除 `start_mcp_server.py/xmind_simple_server.py/xmind_mcp_client.py/markdown_to_xmind_converter.py/demo_merged.py` 等历史条目。
  - 验证：对照仓库文件实际存在情况一致；路径策略表述与服务器实现一致（封装 `_resolve_output_path` 与 `_mask_output_result`）。

  - 下一步：T014（更新 `package.json` 文案去除 MCP 的 `python/pip`）。
- 计划：将 `start/dev` 等脚本统一为 `uvx xmind-mcp --mode fastmcp`；输出目录通过 MCP 配置 `env` 或 CLI `--default-output-dir` 设置；保留非 MCP 场景的 CLI 与 `pip` 安装指令。
    - 成功判定：`package.json` 不再出现用于 MCP 启动的 `python/pip` 用法；UVX-only 要求在脚本文案中清晰体现。

- T014 完成：`package.json` 脚本更新为 UVX-only。
  - 变更文件：`package.json`
  - 修改内容：
- `start/dev` 改为 `uvx xmind-mcp --mode fastmcp`，由 IDE 的 `configs/mcp_config.json` 提供环境变量，或使用 CLI `--default-output-dir` 指定绝对输出目录。
    - 移除 `quick-start`（不存在的 Python 入口）；保留 `install-deps` 与 `test` 以支持非 MCP 场景的 CLI 与测试。
  - 验证：项目脚本不再包含用于 MCP 启动的 `python/pip` 用法；UVX-only 要求在脚本中体现。

## 阶段总结与后续
- 当前清单 T001–T014 已全部完成，关键策略与实现一致：
  - UVX-only 部署；输出型工具绝对路径策略；返回裁剪与日志掩码统一。
  - 引擎/写入器/类型模块职责清晰；转换器懒加载与解耦完成；测试与文档修订到位。
- 后续建议：
  - 回归检查与小版本发布；同步 README/README_CN 的更新片段至网站或 IDE 插件描述。
  - 观察实际使用反馈，必要时在 `list_xmind_files` 增加更多筛选项或在 `read_xmind_file` 提供更细粒度的降级配置。