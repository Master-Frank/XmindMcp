# AI 调用 XMind MCP 入参规范与容错指南

本指南帮助 AI（或任何客户端）在第一次调用就成功生成完整的 XMind 文件。我们对 `create_mind_map` 入参做了容错优化，并提供清晰示例与反例。

## 1. 工具与入参
- 工具：`create_mind_map`
- 必填：`title`（字符串）
- 必填：`topics_json`（JSON 字符串）

## 2. 主题结构规范（支持别名，已自动归一化）
- 每个节点至少包含：`title`
- 子节点使用：`children`（推荐），也兼容 `topics`/`subtopics`/`nodes`/`items`（服务器会自动归一化为 `children`）

示例（推荐结构）：
```json
[
  {
    "title": "测试用例",
    "children": [
      {"title": "前置条件"},
      {"title": "步骤"},
      {"title": "预期结果"}
    ]
  }
]
```

示例（使用别名：topics，服务器会自动处理）：
```json
[
  {
    "title": "测试用例",
    "topics": [
      {"title": "前置条件"},
      {"title": "步骤"},
      {"title": "预期结果"}
    ]
  }
]
```

## 3. 反例（会导致内容缺失或解析失败）
- 反例1：把 JSON 当作 Markdown/纯文本传给 `convert_to_xmind`
  - 错误输入：包含 `"title"`/`"children"` 字段的纯文本或 Markdown
  - 结果：解析为字面字符串，出现很多 `title`/`children` 文本节点
  - 正确做法：对 JSON 结构使用 `create_mind_map`，不要用 `convert_to_xmind`

- 反例2：非 JSON 字符串传给 `topics_json`
  - 错误输入：`topics_json` 传的是对象的字符串表现（例如再次包裹引号或转义错误）
  - 结果：解析失败或被当作“简单字符串”处理，仅生成一个根节点
  - 正确做法：确保 `topics_json` 是合法 JSON 字符串（例如使用 `JSON.stringify` 或 `json.dumps`）

## 4. 输出路径与工作目录
- 建议显式传入绝对路径 `output_path`（例如 `D:/project/XmindMcp/output/xxx.xmind`）
- 若未传入，服务器使用配置文件中的 `default_output_dir`（见 `configs/xmind_mcp_config.json`）并自动创建目录

## 5. 快速自检与验证
- 生成后调用 `analyze_mind_map(filepath)` 或 `read_xmind_file(filepath)`
  - 检查 `total_nodes`、`max_depth` 与标题列表，确认节点完整
- 若节点明显少于输入：基本是结构字段不匹配（已支持别名）；请检查是否传入了合法 JSON

## 6. 给 AI 的调用建议
- 优先使用规范字段：`title` + `children`
- 若来源结构使用其他名称（如 `topics`/`subtopics`）：可以直接传，服务器会自动归一化
- 保证 `topics_json` 是有效 JSON 字符串，不要夹杂注释或多余转义
- 对 JSON 结构使用 `create_mind_map`；对 Markdown/纯文本大纲使用 `convert_to_xmind`

## 7. 兼容性说明
- 服务器在传入后会统一将所有子节点别名归一化为 `children`
- 引擎递归同时兼容 `children`/`topics`/`subtopics`，双重保障避免内容丢失

有任何结构扩展需求（如新增别名）可在服务器的归一化列表中添加即可。