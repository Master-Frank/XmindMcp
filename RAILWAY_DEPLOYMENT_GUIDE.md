# Railway 部署指南

本指南将帮助你将XMind MCP项目部署到Railway平台。

## 🚄 快速部署（推荐）

### 方法1：一键部署按钮
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Master-Frank/XmindMcp&envs=PORT,ENVIRONMENT,DEBUG)

### 方法2：GitHub连接部署
1. 访问 [Railway官网](https://railway.app)
2. 使用GitHub账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择你的XMind MCP仓库
5. Railway会自动检测并配置项目

## 📋 部署前准备

### 1. 环境变量配置
在你的Railway项目中设置以下环境变量：

```bash
# 必需环境变量
PORT=8080
ENVIRONMENT=production

# 可选环境变量
DEBUG=false
HOST=0.0.0.0
```

### 2. 项目结构确认
确保你的项目包含以下文件：
- ✅ `requirements.txt` - Python依赖
- ✅ `xmind_mcp_server.py` - 主服务器文件
- ✅ `Dockerfile` - 容器配置
- ✅ `package.json` - 项目配置

## 🔧 详细部署步骤

### 步骤1：创建Railway账户
1. 访问 [railway.app](https://railway.app)
2. 点击 "Start Building for Free"
3. 使用GitHub账号授权登录

### 步骤2：创建新项目
1. 登录后点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 如果未连接GitHub，点击 "Configure GitHub App"
4. 选择你的XMind MCP仓库

### 步骤3：配置部署设置
Railway会自动检测你的项目类型并提供建议配置：

**服务配置：**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python xmind_mcp_server.py`
- **Health Check Path**: `/health`
- **Port**: `8080`

**环境变量：**
```
PORT=8080
ENVIRONMENT=production
```

### 步骤4：部署和验证
1. 点击 "Deploy" 开始部署
2. 等待部署完成（通常2-5分钟）
3. 部署完成后，Railway会提供访问URL
4. 测试健康检查端点：`https://your-app.railway.app/health`

## 🧪 部署后测试

### 健康检查测试
```bash
curl https://your-app.railway.app/health
```

预期响应：
```json
{"status": "healthy", "timestamp": "2024-..."}
```

### MCP工具列表测试
```bash
curl https://your-app.railway.app/tools
```

## 🔍 常见问题解决

### 1. 部署失败
- **问题**：依赖安装失败
- **解决**：检查requirements.txt文件格式

### 2. 应用启动失败
- **问题**：端口冲突
- **解决**：确保PORT环境变量设置为8080

### 3. 健康检查失败
- **问题**：应用未正确启动
- **解决**：查看Railway日志，检查错误信息

### 4. WebSocket连接问题
- **问题**：MCP客户端无法连接
- **解决**：确保使用HTTPS URL，Railway自动提供SSL

## 📊 Railway免费层限制

| 资源 | 免费层限制 | 说明 |
|------|------------|------|
| CPU | 共享 | 适合轻量级应用 |
| 内存 | 512MB | 足够MCP服务器运行 |
| 存储 | 1GB | 包含代码和依赖 |
| 网络 | 500MB/月 | 适合测试使用 |
| 运行时间 | 持续运行 | 无强制休眠 |

## 🚀 高级配置（可选）

### 自定义域名
1. 在Railway项目设置中添加自定义域名
2. 配置DNS解析到Railway提供的地址

### 环境变量管理
```bash
# 开发环境
ENVIRONMENT=development
DEBUG=true

# 生产环境
ENVIRONMENT=production
DEBUG=false
```

### 日志监控
- Railway提供实时日志查看
- 可以设置日志告警
- 支持日志导出到外部服务

## 📱 MCP客户端连接

部署完成后，使用以下配置连接你的MCP服务器：

```json
{
  "mcpServers": {
    "xmind-railway": {
      "url": "https://your-app.railway.app",
      "description": "XMind MCP server on Railway"
    }
  }
}
```

## 🎯 最佳实践

1. **代码更新**：推送代码到GitHub，Railway会自动重新部署
2. **监控**：定期检查Railway仪表板中的资源使用情况
3. **备份**：重要数据建议定期备份到外部存储
4. **安全**：不要在代码中硬编码敏感信息，使用环境变量

## 📞 获取帮助

- Railway文档：[docs.railway.app](https://docs.railway.app)
- Railway社区：[Discord](https://discord.gg/railway)
- 项目Issues：[GitHub Issues](https://github.com/Master-Frank/XmindMcp/issues)

---

🎉 **恭喜！** 你的XMind MCP服务器现在应该在Railway上成功运行了。记得测试所有功能确保一切正常！