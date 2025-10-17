@echo off
echo 🧠 XMind MCP 服务器安装器
echo =========================

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python环境正常

:: 安装依赖
echo 📦 正在安装依赖包...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install fastapi uvicorn beautifulsoup4 python-docx openpyxl >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ 依赖包安装完成
) else (
    echo ❌ 依赖包安装失败
    pause
    exit /b 1
)

:: 测试安装
echo 🧪 正在测试安装...
python -c "import fastapi, uvicorn, bs4, docx, openpyxl; print('✅ 所有依赖包安装成功')" >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ 安装验证通过
    echo.
    echo 🎉 安装完成！您现在可以运行以下命令启动服务器：
    echo    python quick_start.py      （一键启动）
    echo    python xmind_mcp_server.py （直接启动）
    echo    npm start                  （npm启动）
) else (
    echo ❌ 安装验证失败
)

pause