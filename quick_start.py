#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind MCP服务器快速启动器
一键启动MCP服务器，无需复杂配置
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python():
    """检查Python环境"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python环境正常: {result.stdout.strip()}")
            return True
        else:
            print("❌ Python环境检查失败")
            return False
    except Exception as e:
        print(f"❌ Python环境异常: {e}")
        return False

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        "fastapi", "uvicorn", "beautifulsoup4", 
        "python-docx", "openpyxl"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n📦 正在安装缺失的依赖包: {', '.join(missing_packages)}")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages, check=True)
            print("✅ 依赖包安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败")
            return False
    
    return True

def start_server():
    """启动服务器"""
    try:
        from xmind_mcp_server import XMindMCPServer
        
        print("\n🚀 正在启动 XMind MCP 服务器...")
        server = XMindMCPServer()
        
        # 使用简单的配置启动
        app = server.create_app()
        
        print("✅ 服务器初始化完成")
        print("🌐 服务器地址: http://localhost:8080")
        print("📚 API文档: http://localhost:8080/docs")
        print("🔧 可用工具:")
        
        # 显示可用工具
        tools = [
            "read_xmind_file - 读取XMind文件",
            "create_mind_map - 创建思维导图", 
            "analyze_mind_map - 分析思维导图",
            "convert_to_xmind - 转换文件为XMind",
            "list_xmind_files - 列出XMind文件",
            "ai_generate_topics - AI生成主题建议"
        ]
        
        for tool in tools:
            print(f"   • {tool}")
        
        print("\n🎉 服务器启动成功！按 Ctrl+C 停止服务")
        
        # 启动服务器
        import uvicorn
        uvicorn.run(app, host="localhost", port=8080)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        return False

def main():
    """主函数"""
    print("🧠 XMind MCP 服务器快速启动器")
    print("=" * 40)
    
    # 检查环境
    if not check_python():
        return 1
    
    if not check_dependencies():
        return 1
    
    # 启动服务器
    return 0 if start_server() else 1

if __name__ == "__main__":
    sys.exit(main())