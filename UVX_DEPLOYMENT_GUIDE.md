# XMind MCP uvx部署指南

## 概述
XMind MCP服务器已正确配置为支持uvx部署。uvx是uv包管理器的工具，允许无需安装即可运行Python包。

## 安装要求
- 已安装uv（Python包管理器）
- Python 3.8+

## 部署方法

### 1. 本地开发模式
在项目目录下运行：
```bash
# 查看版本
uvx --from . xmind-mcp --version

# 查看帮助
uvx --from . xmind-mcp --help

# 以FastMCP模式运行
uvx --from . xmind-mcp --mode fastmcp
```

### 2. 已发布包模式（发布后）
一旦发布到PyPI，可以直接运行：
```bash
# 查看版本
uvx xmind-mcp --version

# 以FastMCP模式运行
uvx xmind-mcp --mode fastmcp
```

## 支持的命令行参数
- `--version`: 显示版本信息
- `--help`: 显示帮助信息
- `--mode {fastmcp,stdio}`: 选择运行模式（推荐使用fastmcp）
- `--debug`: 启用调试模式
- `--config CONFIG`: 指定配置文件路径

## 功能特性
✅ **思维导图创建**: 创建新的XMind思维导图
✅ **思维导图读取**: 读取和分析现有XMind文件
✅ **格式转换**: 支持多种格式转换为XMind
✅ **文件列表**: 列出目录中的XMind文件
✅ **MCP工具集成**: 完整的MCP服务器功能

## 配置
服务器支持配置文件，可以指定默认输出目录等设置。配置文件路径可以通过`--config`参数指定。

## 使用示例
```bash
# 基本使用
uvx --from . xmind-mcp-server --mode fastmcp

# 带调试模式
uvx --from . xmind-mcp --mode fastmcp --debug

# 指定配置文件
uvx --from . xmind-mcp --mode fastmcp --config /path/to/config.json
```

## 注意事项
- 推荐使用FastMCP模式，性能更好
- 确保使用绝对路径作为文件参数
- 输出目录会自动创建（如果不存在）

## 故障排除
如果遇到问题，请检查：
1. uv是否正确安装：`uv --version`
2. Python版本是否兼容：`python --version`
3. 使用`--debug`标志获取详细日志

项目已完全支持uvx部署，可以开始使用MCP工具功能了！