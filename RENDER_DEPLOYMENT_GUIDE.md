# XMind MCP Server - Render部署指南

## 🚀 快速部署到Render

### 一键部署
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp)

### 手动部署步骤

#### 1. 准备工作
- 注册 [Render账号](https://render.com)
- Fork本项目到你的GitHub仓库

#### 2. 创建Web服务
1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 "New" → "Web Service"
3. 连接你的GitHub仓库
4. 选择 `Master-Frank/XmindMcp` 项目

#### 3. 配置部署设置
- **Name**: `xmind-mcp-server`
- **Environment**: `Docker`
- **Dockerfile Path**: `./Dockerfile`
- **Build Command**: 留空（使用Dockerfile中的默认构建）
- **Start Command**: 留空（Dockerfile中已定义启动命令）
- **Instance Type**: 选择 "Free" 免费层

#### 4. 环境变量配置
添加以下环境变量：
```
PORT=8080
PYTHONUNBUFFERED=1
RENDER=true
```

#### 5. 健康检查配置
- **Health Check Path**: `/health`
- **Health Check Timeout**: 300秒

#### 6. 部署应用
点击 "Create Web Service" 开始部署

### 📋 部署后配置

#### 获取服务URL
部署完成后，Render会提供一个 `.onrender.com` 结尾的URL

#### 测试服务
```bash
# 测试健康检查
curl https://your-app-name.onrender.com/health

# 测试API文档
curl https://your-app-name.onrender.com/docs
```

#### MCP客户端配置
在MCP客户端中添加以下配置：
```json
{
  "mcpServers": {
    "xmind": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://your-app-name.onrender.com/sse"],
      "description": "XMind MCP Server on Render"
    }
  }
}
```

### ⚠️ Render免费层限制

- **休眠策略**: 15分钟无请求自动休眠
- **启动时间**: 首次访问需30-60秒冷启动
- **资源限制**: 512MB内存，共享CPU
- **月度限额**: 750小时/月（约31天连续运行）
- **并发限制**: 单个实例，无自动扩展

### 🔧 高级配置

#### 自定义域名
1. 在Render Dashboard中选择你的服务
2. 点击 "Settings" → "Custom Domains"
3. 添加你的域名并配置DNS

#### 自动部署
- 默认启用：每次推送到main分支自动重新部署
- 可手动关闭：在 "Settings" → "Auto Deploy" 中配置

#### 环境变量管理
- 在 "Settings" → "Environment Variables" 中添加/修改变量
- 修改后需要重新部署才能生效

### 🐛 常见问题排查

#### 部署失败
1. 检查Dockerfile是否能本地构建：`docker build -t test .`
2. 检查端口配置是否正确（默认8080）
3. 查看Render部署日志获取详细错误信息

#### 服务启动慢
- 这是Render免费层的正常现象（30-60秒冷启动）
- 考虑升级到付费计划获得更好性能

#### 内存不足
- 免费层只有512MB内存
- 优化代码或减少依赖
- 考虑升级到更高配置计划

### 📞 技术支持

- **Render文档**: [https://render.com/docs](https://render.com/docs)
- **项目Issues**: [GitHub Issues](https://github.com/Master-Frank/XmindMcp/issues)
- **MCP协议**: [Model Context Protocol](https://modelcontextprotocol.io)

### 🎯 总结

Render是一个专业的云平台，适合托管Web应用和API服务。虽然免费层有休眠和冷启动限制，但对于MCP服务器的轻量级使用场景来说已经足够。如果预算允许，升级到付费计划可以获得更好的性能和稳定性。