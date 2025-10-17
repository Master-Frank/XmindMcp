#!/bin/bash

# Render部署脚本
# 用于手动部署XMind MCP服务器到Render

set -e

echo "🎨 XMind MCP Server - Render部署脚本"
echo "=================================="

# 检查是否安装了必要的工具
check_dependencies() {
    echo "🔍 检查依赖..."
    
    if ! command -v curl &> /dev/null; then
        echo "❌ curl未安装，请先安装curl"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        echo "❌ git未安装，请先安装git"
        exit 1
    fi
    
    echo "✅ 依赖检查通过"
}

# 检查GitHub仓库状态
check_github_repo() {
    echo "🔍 检查GitHub仓库..."
    
    if [ ! -d ".git" ]; then
        echo "❌ 当前目录不是Git仓库，请先初始化Git仓库"
        echo "运行: git init"
        exit 1
    fi
    
    # 获取远程仓库URL
    remote_url=$(git config --get remote.origin.url 2>/dev/null || echo "")
    
    if [ -z "$remote_url" ]; then
        echo "⚠️ 未检测到远程GitHub仓库"
        echo "请先将项目推送到GitHub:"
        echo "1. 在GitHub创建新仓库"
        echo "2. git remote add origin <你的仓库URL>"
        echo "3. git push -u origin main"
        exit 1
    fi
    
    echo "✅ GitHub仓库已配置: $remote_url"
}

# 检查render.yaml配置
check_render_config() {
    echo "🔍 检查Render配置..."
    
    if [ ! -f "render.yaml" ]; then
        echo "❌ render.yaml文件不存在"
        echo "正在创建默认配置..."
        
        cat > render.yaml << 'EOF'
# Render部署配置文件
services:
  - type: web
    name: xmind-mcp-server
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: PORT
        value: 8080
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: RENDER
        value: "true"
    healthCheckPath: /health
    buildCommand: ""
    startCommand: "python xmind_mcp_server.py"
    plan: free # 使用免费层
    autoDeploy: true # 自动部署
EOF
        
        echo "✅ render.yaml已创建"
    else
        echo "✅ render.yaml已存在"
    fi
}

# 检查Dockerfile
check_dockerfile() {
    echo "🔍 检查Dockerfile..."
    
    if [ ! -f "Dockerfile" ]; then
        echo "❌ Dockerfile不存在"
        echo "请确保项目根目录有Dockerfile"
        exit 1
    fi
    
    echo "✅ Dockerfile已存在"
}

# 提供部署指导
provide_deployment_guide() {
    echo ""
    echo "🚀 部署到Render的步骤："
    echo "=================================="
    echo ""
    echo "1️⃣ 注册Render账号"
    echo "   访问: https://render.com"
    echo "   点击 'Sign Up' 注册新账号"
    echo ""
    echo "2️⃣ 创建新的Web Service"
    echo "   登录Render Dashboard"
    echo "   点击 'New' → 'Web Service'"
    echo "   连接你的GitHub仓库"
    echo ""
    echo "3️⃣ 配置部署设置"
    echo "   Name: xmind-mcp-server"
    echo "   Environment: Docker"
    echo "   Dockerfile Path: ./Dockerfile"
    echo "   Start Command: python xmind_mcp_server.py"
    echo "   Plan: Free (免费层)"
    echo ""
    echo "4️⃣ 配置环境变量"
    echo "   PORT=8080"
    echo "   PYTHONUNBUFFERED=1"
    echo "   RENDER=true"
    echo ""
    echo "5️⃣ 配置健康检查"
    echo "   Health Check Path: /health"
    echo "   Timeout: 300秒"
    echo ""
    echo "6️⃣ 部署应用"
    echo "   点击 'Create Web Service' 开始部署"
    echo "   等待2-5分钟完成部署"
    echo ""
    echo "📋 部署后配置："
    echo "   - 获取服务URL (格式: https://xxx.onrender.com)"
    echo "   - 测试健康检查: https://xxx.onrender.com/health"
    echo "   - 配置MCP客户端连接到服务"
    echo ""
    echo "⚠️ 重要提醒："
    echo "   - 免费层有15分钟休眠限制"
    echo "   - 首次访问需要30-60秒冷启动"
    echo "   - 月度限制: 750小时 (足够24/7运行)"
    echo "   - 内存限制: 512MB"
    echo ""
    echo "📖 详细指南: RENDER_DEPLOYMENT_GUIDE.md"
    echo "🎨 一键部署: https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp"
}

# 主函数
main() {
    echo "🎯 开始Render部署准备..."
    echo ""
    
    check_dependencies
    echo ""
    
    check_github_repo
    echo ""
    
    check_render_config
    echo ""
    
    check_dockerfile
    echo ""
    
    provide_deployment_guide
    
    echo ""
    echo "✅ 部署准备完成！"
    echo "🚀 现在你可以按照上面的步骤部署到Render了"
    echo ""
    echo "💡 提示: 你也可以使用一键部署按钮："
    echo "https://render.com/deploy?repo=https://github.com/Master-Frank/XmindMcp"
}

# 运行主函数
main "$@"