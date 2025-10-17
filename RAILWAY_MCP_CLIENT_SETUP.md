# MCP客户端连接Railway部署指南

## 🎯 连接配置

当你的XMind MCP服务器成功部署到Railway后，你需要配置MCP客户端来连接它。

## 📋 获取Railway应用URL

1. 登录 [Railway Dashboard](https://railway.app)
2. 找到你的XMind MCP项目
3. 复制应用的URL（格式：`https://your-app.railway.app`）

## 🔧 客户端配置

### Trae IDE配置
在你的Trae IDE中，编辑MCP配置文件：

**文件路径**: `~/.trae/mcp_config.json` 或项目目录下的 `mcp_config.json`

```json
{
  "mcpServers": {
    "xmind-railway": {
      "url": "https://your-app.railway.app",
      "description": "XMind MCP server deployed on Railway",
      "timeout": 30000
    }
  }
}
```

### VS Code配置
如果使用VS Code的MCP扩展：

**文件路径**: `.vscode/mcp.json`

```json
{
  "servers": {
    "xmind-railway": {
      "url": "https://your-app.railway.app",
      "description": "XMind MCP server on Railway"
    }
  }
}
```

### 通用MCP客户端配置
```json
{
  "servers": [
    {
      "name": "xmind-railway",
      "url": "https://your-app.railway.app",
      "description": "XMind AI mind mapping tool",
      "enabled": true
    }
  ]
}
```

## 🧪 连接测试

### 1. 健康检查测试
```bash
curl https://your-app.railway.app/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "version": "1.0.0"
}
```

### 2. 工具列表测试
```bash
curl https://your-app.railway.app/tools
```

**预期响应**:
```json
{
  "tools": [
    {
      "name": "convert_to_xmind",
      "description": "Convert various file formats to XMind"
    },
    {
      "name": "read_xmind",
      "description": "Read and analyze XMind files"
    },
    {
      "name": "create_mind_map",
      "description": "Create new mind maps"
    }
  ]
}
```

## 🔒 安全连接

### HTTPS证书
Railway自动为你的应用提供SSL证书，确保安全的HTTPS连接。

### 认证配置（可选）
如果需要添加认证，可以在服务器端配置API密钥：

**环境变量设置**:
```bash
API_KEY=your-secret-api-key
```

**客户端配置**:
```json
{
  "mcpServers": {
    "xmind-railway": {
      "url": "https://your-app.railway.app",
      "headers": {
        "Authorization": "Bearer your-secret-api-key"
      }
    }
  }
}
```

## 🐛 常见问题排查

### 连接超时
**问题**: 客户端连接Railway应用超时
**解决**: 
- 检查Railway应用是否正常运行
- 验证URL是否正确
- 检查网络连接

### 404错误
**问题**: 访问端点返回404
**解决**:
- 确认应用已成功部署
- 检查健康检查端点 `/health`
- 验证端点URL拼写

### WebSocket连接失败
**问题**: MCP客户端无法建立WebSocket连接
**解决**:
- 确保使用 `wss://` 协议（不是 `ws://`）
- Railway支持WebSocket，但需要HTTPS
- 检查客户端WebSocket配置

### 响应缓慢
**问题**: API响应时间过长
**解决**:
- 检查Railway资源使用情况
- 考虑升级到付费套餐获得更多资源
- 优化代码性能

## 📊 性能优化建议

### 1. 缓存配置
在客户端启用适当的缓存策略

### 2. 连接池
使用连接池复用HTTP连接

### 3. 超时设置
合理设置连接超时时间（建议30秒）

### 4. 重试策略
实现指数退避重试机制

## 🎯 最佳实践

### 生产环境配置
```json
{
  "mcpServers": {
    "xmind-railway": {
      "url": "https://your-app.railway.app",
      "description": "XMind MCP production server",
      "timeout": 30000,
      "retry": {
        "maxAttempts": 3,
        "delay": 1000
      }
    }
  }
}
```

### 开发环境配置
```json
{
  "mcpServers": {
    "xmind-local": {
      "url": "http://localhost:8080",
      "description": "Local development server"
    },
    "xmind-railway": {
      "url": "https://your-app.railway.app",
      "description": "Railway staging server"
    }
  }
}
```

## 📞 获取帮助

如果遇到连接问题：

1. 检查Railway应用状态
2. 查看Railway部署日志
3. 测试健康检查端点
4. 验证客户端配置
5. 查看 [Railway文档](https://docs.railway.app)

---

🎉 **恭喜！** 现在你可以使用MCP客户端连接到你的Railway部署的XMind MCP服务器了！