.replit
```
run = "python quick_start.py"
language = "python3"
entrypoint = "xmind_mcp_server.py"

[env]
PYTHONPATH = "."

[nix]
channel = "stable-22_11"

[packager]
language = "python3"

[packager.features]
packageSearch = true
guessImports = true

[deployment]
run = ["python", "quick_start.py"]
department = "backend"
```

replit.nix
```nix
{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.pip
    pkgs.python39Packages.fastapi
    pkgs.python39Packages.uvicorn
  ];
}
```

main.py
```python
#!/usr/bin/env python3
"""
Replit XMind MCP Server - 在线版本
无需下载代码，直接在Replit上运行
"""

import os
import sys
import subprocess

def install_requirements():
    """安装依赖"""
    requirements = [
        "fastapi", "uvicorn", "openpyxl", 
        "beautifulsoup4", "python-docx"
    ]
    
    for req in requirements:
        try:
            __import__(req.replace("-", "_"))
        except ImportError:
            print(f"📦 安装 {req}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def start_server():
    """启动MCP服务器"""
    print("🚀 启动XMind MCP服务器...")
    
    # 设置环境变量
    os.environ["PYTHONPATH"] = "."
    os.environ["REPLIT"] = "true"
    
    # 启动服务器
    from xmind_mcp_server import app
    import uvicorn
    
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🌐 服务器地址: https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.repl.co")
    print(f"📚 API文档: https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.repl.co/docs")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    print("🎯 XMind MCP Server - Replit在线版本")
    print("=" * 50)
    
    install_requirements()
    start_server()
```