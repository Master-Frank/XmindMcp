# XMind MCP 服务器使用指南

## 概述

XMind MCP 服务器是一个基于 FastAPI 的思维导图操作服务器，提供 RESTful API 接口来处理 XMind 文件。支持读取、分析、创建、转换和列出 XMind 文件等功能。

## 快速开始

### 1. 启动服务器

```bash
python start_mcp_server.py
```

服务器启动后，可以通过以下地址访问：
- 主页面: http://localhost:8080
- API文档: http://localhost:8080/docs
- 工具列表: http://localhost:8080/tools

### 2. 基本功能测试

运行完整测试套件验证服务器功能：

```bash
# 中文模式
python complete_test_suite.py

# 英文模式（避免编码问题）
python complete_test_suite.py --english
```

测试完成后会生成JSON格式的测试报告到 `test_reports` 目录：
- 中文模式：`test_reports/test_report_merged.json`
- 英文模式：`test_reports/test_report_merged_english.json`

## API 接口说明

### 基础工具

#### 1. 读取XMind文件
**接口**: `POST /tools/read_xmind`
**参数**:
```json
{
    "filepath": "path/to/your/file.xmind"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8080/tools/read_xmind" \
  -H "Content-Type: application/json" \
  -d '{"filepath": "output/test_markdown.xmind"}'
```

#### 2. 分析思维导图
**接口**: `POST /tools/analyze_mind_map`
**参数**:
```json
{
    "filepath": "path/to/your/file.xmind"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8080/tools/analyze_mind_map" \
  -H "Content-Type: application/json" \
  -d '{"filepath": "output/test_markdown.xmind"}'
```

#### 3. 创建思维导图
**接口**: `POST /tools/create_mind_map`
**参数**:
```json
{
    "title": "我的思维导图",
    "topics_json": "[{\"title\": \"主题1\", \"children\": [{\"title\": \"子主题1.1\"}]}]"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8080/tools/create_mind_map" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "项目计划",
    "topics_json": "[{\"title\": \"需求分析\", \"children\": [{\"title\": \"用户需求\"}]}, {\"title\": \"开发\", \"children\": [{\"title\": \"前端开发\"}]}]"
  }'
```

#### 4. 文件格式转换
**接口**: `POST /tools/convert_to_xmind`
**参数**:
```json
{
    "source_filepath": "path/to/source.md",
    "output_filepath": "optional/output.xmind"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8080/tools/convert_to_xmind" \
  -H "Content-Type: application/json" \
  -d '{
    "source_filepath": "examples/test_markdown.md",
    "output_filepath": "output/converted.xmind"
  }'
```

#### 5. 列出XMind文件
**接口**: `POST /tools/list_xmind_files`
**参数**:
```json
{
    "directory": "path/to/directory",
    "recursive": true
}
```

**示例**:
```bash
curl -X POST "http://localhost:8080/tools/list_xmind_files" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "output",
    "recursive": true
  }'
```

### 辅助接口

#### 健康检查
**接口**: `GET /health`
**返回**:
```json
{
    "status": "healthy",
    "ai_available": false
}
```

#### 工具列表
**接口**: `GET /tools`
**返回**: 所有可用工具的列表和状态

#### 根信息
**接口**: `GET /`
**返回**: 服务器基本信息

## 支持的文件格式

### 输入格式
- **XMind文件**: `.xmind` (主要格式)
- **Markdown文件**: `.md` (可转换为XMind)
- **文本文件**: `.txt` (可转换为XMind)
- **HTML文件**: `.html` (可转换为XMind)
- **Excel文件**: `.xlsx` (可转换为XMind)
- **Word文件**: `.docx` (可转换为XMind)

### 输出格式
- **XMind文件**: `.xmind` (主要输出格式)

## 功能特性

### 1. 文件读取
- 解析XMind文件结构
- 提取主题和子主题信息
- 计算节点数量和层级深度

### 2. 结构分析
- **复杂度分析**: 基于节点数量评估思维导图复杂度
- **平衡性分析**: 评估分支分布的均衡程度
- **完整性分析**: 检查结构的完整性
- **优化建议**: 提供结构优化建议

### 3. 文件转换
- 支持多种格式转换为XMind
- 自动识别文件类型
- 保持原有结构层次

### 4. 文件创建
- 基于JSON结构创建新思维导图
- 支持多级主题嵌套
- 自动生成XMind文件

## 错误处理

所有API接口都返回标准格式的响应：

**成功响应**:
```json
{
    "status": "success",
    "data": { ... }
}
```

**错误响应**:
```json
{
    "status": "error",
    "error": "错误描述信息"
}
```

## 配置选项

服务器支持配置文件 `xmind_mcp_config.json`：

```json
{
    "server": {
        "port": 8080,
        "host": "localhost"
    },
    "ai": {
        "enabled": true,
        "api_key": "your_api_key_here"
    }
}
```

## PowerShell 使用示例

### 读取XMind文件
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8080/tools/read_xmind" `
  -Method Post -ContentType "application/json" `
  -Body '{"filepath": "D:/project/XmindMcp/output/test_markdown.xmind"}'

$response | Format-List
```

### 分析思维导图
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8080/tools/analyze_mind_map" `
  -Method Post -ContentType "application/json" `
  -Body '{"filepath": "D:/project/fileToXmind/output/test_markdown.xmind"}'

Write-Host "复杂度: $($response.structure_analysis.complexity)"
Write-Host "平衡性: $($response.structure_analysis.balance)"
```

### 列出所有XMind文件
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8080/tools/list_xmind_files" `
  -Method Post -ContentType "application/json" `
  -Body '{"directory": "D:/project/fileToXmind/output", "recursive": true}'

$response.files | Format-Table -Property name, size -AutoSize
```

## 注意事项

1. **文件路径**: 使用绝对路径可以避免路径问题
2. **编码**: 所有文本数据使用UTF-8编码
3. **权限**: 确保有读写文件的权限
4. **备份**: 转换文件前建议备份原始文件
5. **网络**: 确保服务器端口未被占用

## 故障排除

### 常见问题

1. **服务器启动失败**
   - 检查端口是否被占用
   - 确认Python环境正确
   - 查看错误日志信息

2. **文件读取失败**
   - 确认文件路径正确
   - 检查文件是否存在
   - 验证文件格式支持

3. **转换失败**
   - 检查源文件格式
   - 确认输出目录存在
   - 查看错误详情

### 调试信息

服务器启动时会显示：
- 配置文件状态
- AI功能状态
- 服务端口信息
- API文档地址

通过查看这些信息可以快速定位问题。