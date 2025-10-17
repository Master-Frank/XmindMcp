# Render部署按钮代码

## HTML格式
```html
<a href="https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
</a>
```

## Markdown格式
```markdown
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp)
```

## 自定义按钮样式
```html
<!-- 蓝色主题按钮 -->
<a href="https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp" style="display: inline-block; background: #0E7A8D; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
  🚀 Deploy to Render
</a>

<!-- 小尺寸按钮 -->
<a href="https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" width="120">
</a>
```

## 带说明的部署按钮
```markdown
### 🚀 一键部署到Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp)

> ⚡ **快速开始**: 点击上方按钮，使用Render免费层快速部署XMind MCP服务器
>
> 📋 **准备工作**: 
> - 注册Render账号
> - 连接GitHub仓库
> - 自动部署配置
```

## 多个部署选项对比
```markdown
### 🚀 多平台部署选项

| 平台 | 部署按钮 | 特点 |
|------|----------|------|
| **Render** | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp) | 专业托管，免费层750小时/月 |
| **Railway** | [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/72f585a6-7feb-40e0-b09e-565cf6b80ccd) | WebSocket支持，$5免费额度 |
| **Fly.io** | 手动部署 | 高性能，Always On模式 |
```