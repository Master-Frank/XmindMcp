# 🚀 Trae MCP 配置指南

在Trae中配置XMind AI MCP服务器，实现智能思维导图操作。

## ⚙️ 快速配置

### 推荐配置（直接复制使用）

在Trae的MCP配置中添加：

```json
{
  "mcpServers": {
    "xmind-ai": {
      "command": "cmd",
      "args": ["/c", "cd", "d:/project/XmindMcp", "&&", "python", "start_mcp_server.py"],
      "description": "XMind AI MCP Server - 智能思维导图操作"
    }
  }
}
```

## 📋 配置说明

| 参数 | 说明 | 示例 |
|------|------|-------|
| `command` | 执行命令 | `cmd` |
| `args` | 命令参数 | 切换到项目目录并启动服务器 |
| `description` | 服务器描述 | 显示在Trae中的名称 |

## 🔧 替代配置方案

### 方案1：直接Python启动
```json
{
  "mcpServers": {
    "xmind-ai": {
      "command": "python",
      "args": ["d:/project/XmindMcp/start_mcp_server.py"],
    "cwd": "d:/project/XmindMcp",
      "description": "XMind AI MCP Server"
    }
  }
}
```

### 方案2：使用npx
```json
{
  "mcpServers": {
    "xmind-ai": {
      "command": "npx",
      "args": ["-y", "python", "start_mcp_server.py"],
      "cwd": "d:/project/XmindMcp",
      "description": "XMind AI MCP Server"
    }
  }
}
```

## ✅ 验证配置

1. **保存配置**：在Trae设置中保存MCP配置
2. **重启Trae**：重新启动Trae IDE
3. **检查状态**：查看输出面板确认服务器启动
4. **测试工具**：使用MCP工具测试功能

## 🎯 可用工具

配置成功后，在Trae中可以使用以下工具：

| 工具名称 | 功能描述 | 使用场景 |
|----------|----------|----------|
| `read_xmind_file` | 读取XMind文件内容 | 查看思维导图结构 |
| `create_mind_map` | 创建新的思维导图 | 新建思维导图 |
| `analyze_mind_map` | 分析思维导图结构 | 分析现有导图 |
| `convert_to_xmind` | 转换文件为XMind格式 | 文档转思维导图 |
| `list_xmind_files` | 列出XMind文件 | 浏览导图文件 |
| `ai_generate_topics` | AI生成主题建议 | 智能内容生成 |

## 💡 使用示例

### 转换文档为思维导图
```json
{
  "source_filepath": "examples/playwright-learning-guide.md",
  "output_filepath": "output/my-guide.xmind"
}
```

### AI生成学习路径
```json
{
  "context": "Python编程学习路径",
  "max_topics": 20
}
```

### 分析思维导图结构
```json
{
  "filepath": "output/test_outline.xmind"
}
```

## ⚠️ 常见问题

### Q: 服务器启动失败？
**A**: 检查Python是否安装，路径是否正确

### Q: 工具无法使用？
**A**: 确认服务器状态正常，重启Trae后再试

### Q: 文件路径错误？
**A**: 使用绝对路径，确保文件存在

### Q: 转换失败？
**A**: 检查源文件格式是否正确，编码是否为UTF-8

## 🔗 相关链接

- **[通用转换器指南](UNIVERSAL_CONVERTER_USAGE.md)** - 文件转换详细说明
- **[项目主页](README.md)** - 项目概览和快速开始
- **[验证报告](conversion_validation_report.md)** - 转换质量验证

## 📞 技术支持

遇到问题请：
1. 检查配置文件路径和格式
2. 查看Trae输出面板的错误信息
3. 确认Python环境和依赖包
4. 在项目中提交Issue反馈

---

**✨ 配置完成后，即可在Trae中享受智能思维导图操作体验！**