# XMind AI MCP 项目结构

本项目已经重新整理，文件按功能分类存放在不同目录中。

## 目录结构

```
XmindMcp/
├── configs/                    # 配置文件目录
│   ├── trae_mcp_config.json           # Trae MCP配置
│   ├── trae_mcp_npx_config.json       # Trae MCP (NPX)配置
│   ├── trae_simple_config.json        # Trae简化配置
│   └── xmind_mcp_config.json          # XMind MCP服务器配置
├── docs/                       # 文档目录
│   ├── README.md                      # 项目说明
│   ├── README_CN.md                   # 中文项目说明
│   ├── TRAE_MCP_SETUP.md             # Trae MCP设置指南
│   ├── UNIVERSAL_CONVERTER_USAGE.md  # 通用转换器使用说明
│   ├── conversion_validation_report.md # 转换验证报告
│   └── xmind_ai_mcp_design.md        # XMind AI MCP设计文档
├── examples/                   # 示例文件目录
│   ├── test_auto/                     # 自动测试目录
│   ├── test_document.md               # 测试文档
│   ├── test_outline.docx              # Word测试文件
│   ├── test_outline.html              # HTML测试文件
│   ├── test_outline.txt               # 文本测试文件
│   └── test_outline.xlsx              # Excel测试文件
├── output/                     # 输出结果目录
├── tests/                      # 测试和演示代码目录
│   ├── batch_convert_demo.py          # 批量转换演示
│   ├── setup_mcp_server.py            # MCP服务器设置
│   └── xmind_mcp_client_demo.py       # XMind MCP客户端演示
├── venv/                       # Python虚拟环境目录
└── 核心Python文件              # 主要功能模块
    ├── start_mcp_server.py            # MCP服务器启动器
    ├── xmind_simple_server.py          # XMind简化服务器
    ├── xmind_mcp_client.py             # XMind MCP客户端
    ├── xmind_ai_extensions.py          # XMind AI扩展
    ├── universal_xmind_converter.py    # 通用XMind转换器
    └── validate_xmind_structure.py      # XMind结构验证器
```

## 使用说明

### 1. 配置文件
- 在 `configs/` 目录中选择合适的配置文件
- Trae用户推荐使用 `trae_simple_config.json`

### 2. 示例文件
- 示例输入文件在 `examples/` 目录中
- 转换后的输出文件在 `output/` 目录中

### 3. 运行服务器
```bash
python start_mcp_server.py
```

### 4. 运行测试
```bash
python tests/batch_convert_demo.py
```

## 文件说明

### 核心模块
- `start_mcp_server.py`: MCP服务器启动器，整合所有功能
- `xmind_simple_server.py`: XMind简化服务器引擎
- `xmind_mcp_client.py`: MCP客户端实现
- `xmind_ai_extensions.py`: AI扩展功能
- `universal_xmind_converter.py`: 通用文件转换器
- `markdown_to_xmind_converter.py`: Markdown专用转换器
- `validate_xmind_structure.py`: XMind文件验证器
- `demo_merged.py`: 统一功能演示脚本（合并版本，支持中英文模式）

### 配置和文档
- 所有配置文件在 `configs/` 目录中
- 使用说明文档在 `docs/` 目录中
- 示例文件和输出结果分别放在 `examples/` 和 `output/` 目录中

项目结构清晰，便于维护和扩展。

## 1. start_mcp_server.py - XMind MCP服务器启动器
这是一个基于 FastMCP 的 MCP 服务器（STDIO 连接）：

- 服务器功能 ：提供RESTful API接口
- 工具集成 ：整合了所有XMind相关工具（读取、创建、分析、转换、列出文件）
- AI功能 ：可选的AI扩展功能（主题生成、结构优化）
- 配置管理 ：支持JSON配置文件
- CORS支持 ：跨域请求处理
## 2. universal_xmind_converter.py - 通用文件转XMind转换器
这是一个支持多种文件格式的通用转换器：

- 多格式支持 ：TXT、HTML、Word、Excel、Markdown
- 智能解析 ：每种格式都有专门的解析器类
- 结构识别 ：
  - Markdown：基于标题层级
  - TXT：基于缩进层级
  - HTML：基于h1-h6标签或列表结构
  - Word：基于段落样式
  - Excel：基于行列结构
- 容错处理 ：可选依赖，缺失库时使用回退模式
## 3. validate_xmind_structure.py - XMind文件结构验证工具
用于验证转换后的XMind文件格式正确性：

- 格式验证 ：检查XMind文件内部结构（JSON、XML）
- 结构分析 ：统计节点数量、层级深度、标题列表
- 可视化展示 ：打印结构树
- 批量验证 ：支持验证多个文件并生成报告
- 错误检测 ：识别结构问题和格式错误
## 4. xmind_ai_extensions.py - XMind AI扩展功能模块
提供AI驱动的思维导图增强功能：

- 主题生成 ：基于上下文智能生成相关主题
- 结构优化 ：AI分析和优化思维导图结构
- 质量分析 ：评估思维导图的复杂度、平衡性、完整性
- 改进建议 ：提供结构化的优化建议
- 内容处理 ：关键词提取、内容分类、摘要生成
- 多模式支持 ：AI模式 + 回退模式（无API时）
## 5. xmind_mcp_client.py - XMind MCP客户端工具
MCP服务器的客户端封装：

- API封装 ：封装所有服务器API调用
- 工具调用 ：读取、创建、分析、转换、AI功能
- 演示功能 ：包含完整的演示函数
- 错误处理 ：统一的异常处理机制
- 健康检查 ：服务器状态检测
## 6. xmind_simple_server.py - XMind简化MCP服务器核心引擎
这是整个系统的核心引擎，提供基础功能：

- 文件读取 ：解析XMind文件内容
- 文件创建 ：基于JSON结构创建新XMind文件
- 结构分析 ：分析思维导图统计信息
- 格式转换 ：调用universal_xmind_converter进行文件转换
- 文件管理 ：列出和管理XMind文件
- 工具注册 ：提供工具函数的全局访问接口