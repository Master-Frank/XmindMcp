# 🚀 XMind MCP 快速启动指南

## ⚡ 超简单启动方案

### 方案1：一键启动（推荐）
```bash
# 下载项目后，直接运行
python quick_start.py
```
✅ 自动检查环境  
✅ 自动安装依赖  
✅ 自动启动服务器  

### 方案2：npm启动
```bash
# 使用npm启动
npm start

# 或使用yarn
yarn start
```

### 方案3：传统方式
```bash
# 手动安装依赖后启动
pip install fastapi uvicorn beautifulsoup4 python-docx openpyxl
python xmind_mcp_server.py
```

## 🐳 Docker启动

### 快速启动
```bash
# 使用docker-compose
docker-compose up

# 或直接docker运行
docker build -t xmind-mcp .
docker run -p 8080:8080 xmind-mcp
```

## 📦 安装脚本（Windows）

### 一键安装
双击运行 `install.bat`：
- ✅ 检查Python环境
- ✅ 自动安装所有依赖
- ✅ 验证安装结果

## 🎯 验证启动成功

启动后访问：
- 🌐 服务器地址: http://localhost:8080
- 📚 API文档: http://localhost:8080/docs
- 🏥 健康检查: http://localhost:8080/health

## 🔧 Trae IDE集成

### 快速配置
在Trae的MCP配置中添加：
```json
{
  "mcpServers": {
    "xmind-ai": {
      "command": "cmd",
      "args": ["/c", "cd", "d:/project/XmindMcp", "&&", "python", "quick_start.py"],
      "description": "XMind AI MCP Server"
    }
  }
}
```

## 📋 系统要求

- Python 3.8+
- 2GB+ 内存
- 100MB+ 磁盘空间

## 🆘 常见问题

### Q: 启动失败怎么办？
**A**: 
1. 检查Python版本: `python --version`
2. 运行安装脚本: `install.bat`
3. 查看错误日志，确认端口未被占用

### Q: 依赖安装失败？
**A**:
1. 升级pip: `python -m pip install --upgrade pip`
2. 手动安装: `pip install fastapi uvicorn beautifulsoup4 python-docx openpyxl`

### Q: 端口被占用？
**A**:
修改端口启动: `python xmind_mcp_server.py --port 9000`

## 🎉 启动成功标志

看到以下输出表示成功：
```
🧠 XMind MCP 服务器快速启动器
========================================
✅ Python环境正常
✅ 依赖包安装完成
🚀 正在启动 XMind MCP 服务器...
✅ 服务器初始化完成
🌐 服务器地址: http://localhost:8080
📚 API文档: http://localhost:8080/docs
🎉 服务器启动成功！
```

---

**💡 提示**: 推荐新手使用 `python quick_start.py` 一键启动！