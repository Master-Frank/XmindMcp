#!/bin/bash
# Docker一键启动脚本 - 无需拉取代码

set -e

echo "🚀 XMind MCP Server - Docker一键启动"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 创建临时目录
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

echo "📄 创建Docker Compose配置文件..."

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  xmind-mcp-server:
    image: masterfrank/xmind-mcp-server:latest
    container_name: xmind-mcp-server
    ports:
      - "8080:8080"
    environment:
      - PYTHONPATH=/app
      - HOST=0.0.0.0
      - PORT=8080
    volumes:
      - ./examples:/app/examples
      - ./output:/app/output
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

echo "🐳 启动XMind MCP服务器..."
docker-compose up -d

echo "⏳ 等待服务器启动..."
sleep 15

# 检查服务状态
if curl -f http://localhost:8080/health &> /dev/null; then
    echo "✅ 服务器启动成功！"
    echo "🌐 访问地址: http://localhost:8080"
    echo "📚 API文档: http://localhost:8080/docs"
    echo "🎯 使用说明:"
    echo "  - 读取XMind文件: POST http://localhost:8080/read-file"
    echo "  - 创建思维导图: POST http://localhost:8080/create-mind-map"
    echo "  - 健康检查: GET http://localhost:8080/health"
else
    echo "❌ 服务器启动失败，请检查日志"
    docker-compose logs
fi

echo ""
echo "🛑 停止服务器: docker-compose down"
echo "🔄 重启服务器: docker-compose restart"
echo "📋 查看日志: docker-compose logs -f"

# 保持容器运行
echo "容器正在后台运行，按Ctrl+C退出..."
trap 'docker-compose down; cd ~; rm -rf $TEMP_DIR; exit 0' INT
wait