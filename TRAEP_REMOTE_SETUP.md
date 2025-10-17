# Trae IDE 远程MCP服务器配置指南

## 🎯 目标
配置Trae IDE使用已部署在Render上的XMind MCP服务器（https://xmindmcp.onrender.com）

## 📋 前提条件
- Trae IDE已安装并更新到最新版本
- 网络可以访问 `https://xmindmcp.onrender.com`
- 已有XMind文件用于测试

## 🔧 配置步骤

### 方法1：直接配置（推荐）

1. **打开Trae IDE设置**
   - 点击左下角设置图标
   - 选择 `Settings` → `MCP Servers`

2. **添加远程MCP服务器**
   ```json
   {
     "mcpServers": {
       "xmind-ai-remote": {
         "url": "https://xmindmcp.onrender.com",
         "description": "XMind AI MCP Server - 远程版",
         "enabled": true,
         "timeout": 30
       }
     }
   }
   ```

3. **保存配置**
   - 点击保存按钮
   - 重启Trae IDE

### 方法2：使用配置文件

1. **找到Trae配置目录**
   - Windows: `%APPDATA%\Trae\User\settings.json`
   - macOS: `~/Library/Application Support/Trae/User/settings.json`
   - Linux: `~/.config/Trae/User/settings.json`

2. **添加MCP配置**
   在 `settings.json` 中添加：
   ```json
   {
     "mcp.servers": {
       "xmind-ai-remote": {
         "url": "https://xmindmcp.onrender.com",
         "description": "XMind AI MCP Server - 远程版",
         "enabled": true,
         "timeout": 30
       }
     }
   }
   ```

## 🧪 测试连接

### 测试1：健康检查
在Trae的MCP面板中，应该看到：
- ✅ `xmind-ai-remote` 状态为 "Connected"
- 服务器描述显示正确

### 测试2：功能测试
在Trae中尝试以下命令：

```
使用XMind MCP读取一个思维导图文件
```

或者：

```
帮我创建一个关于"项目管理"的思维导图
```

## 🛠️ 可用功能

### 1. 读取XMind文件
```
读取这个XMind文件：[文件路径]
```

### 2. 创建思维导图
```
创建一个关于"学习计划"的思维导图，包含以下主题：
- 编程语言
- 数据结构
- 算法
- 项目实战
```

### 3. 文件转换
```
把这个Markdown文件转换成XMind格式：[文件路径]
```

### 4. AI生成主题
```
基于"人工智能发展趋势"生成思维导图主题建议
```

## ⚠️ 注意事项

### 1. 文件路径
- 由于服务器在云端，**本地文件路径可能无法访问**
- 建议使用相对路径或确保文件在服务器的可访问目录

### 2. 网络延迟
- 免费版Render有冷启动时间（通常15-30秒）
- 建议启用保活功能（已配置KEEP_ALIVE=true）

### 3. 文件大小限制
- Render免费版有内存限制（512MB）
- 大型XMind文件可能处理较慢

## 🔍 故障排除

### 问题1：连接失败
```
检查步骤：
1. 访问 https://xmindmcp.onrender.com/health
2. 确认返回 {"status":"healthy"}
3. 检查网络连接
4. 确认Trae MCP配置中的URL正确
```

### 问题2：文件读取失败
```
解决方案：
1. 使用绝对路径：/app/data/yourfile.xmind
2. 确保文件已上传到服务器可访问目录
3. 检查文件权限
```

### 问题3：响应慢
```
正常现象：
- Render免费版冷启动需要15-30秒
- 保活机制已启用，后续请求会更快
- 建议等待完成，不要重复点击
```

## 📚 高级用法

### 批量处理
```
批量转换这个目录下的所有Markdown文件为XMind格式
```

### 复杂分析
```
分析这个思维导图的结构复杂度，并提供优化建议
```

### 主题生成
```
基于当前技术趋势，生成一个完整的思维导图框架
```

## 🆘 获取帮助

- **服务器状态**：访问 https://xmindmcp.onrender.com/health
- **GitHub仓库**：https://github.com/Master-Frank/XmindMcp
- **问题反馈**：在GitHub提交Issue

## ✅ 验证清单

配置完成后，请确认：
- [ ] MCP服务器显示为 "Connected"
- [ ] 可以成功创建新的思维导图
- [ ] 文件转换功能正常工作
- [ ] AI主题生成功能可用
- [ ] 响应时间在可接受范围内

---

**🎉 恭喜！现在你可以在Trae IDE中使用远程XMind MCP服务器了！**