#!/usr/bin/env python3
"""
Railway部署助手脚本
帮助你将XMind MCP项目快速部署到Railway平台
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_requirements():
    """检查部署所需的文件是否齐全"""
    required_files = [
        'requirements.txt',
        'Dockerfile',
        'xmind_mcp_server.py',
        'railway.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必需文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✅ 所有必需文件检查通过")
    return True

def validate_dockerfile():
    """验证Dockerfile配置"""
    try:
        with open('Dockerfile', 'r') as f:
            content = f.read()
        
        if 'EXPOSE 8080' not in content:
            print("⚠️  Dockerfile中未找到EXPOSE 8080配置")
            return False
        
        if 'python xmind_mcp_server.py' not in content:
            print("⚠️  Dockerfile中启动命令可能需要检查")
        
        print("✅ Dockerfile验证通过")
        return True
    except Exception as e:
        print(f"❌ Dockerfile验证失败: {e}")
        return False

def validate_requirements():
    """验证requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        required_packages = ['fastapi', 'uvicorn']
        missing_packages = []
        
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️  requirements.txt可能缺少: {missing_packages}")
            return False
        
        print("✅ requirements.txt验证通过")
        return True
    except Exception as e:
        print(f"❌ requirements.txt验证失败: {e}")
        return False

def create_railway_config():
    """创建Railway配置文件"""
    config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "DOCKERFILE",
            "dockerfilePath": "Dockerfile"
        },
        "deploy": {
            "startCommand": "python xmind_mcp_server.py",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 300,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    try:
        with open('railway.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Railway配置文件创建成功")
        return True
    except Exception as e:
        print(f"❌ Railway配置文件创建失败: {e}")
        return False

def generate_deployment_info():
    """生成部署信息"""
    info = {
        "project_name": "XMind MCP Server",
        "description": "AI-powered mind mapping tool with MCP protocol support",
        "repository": "https://github.com/Master-Frank/XmindMcp",
        "port": 8080,
        "health_check": "/health",
        "environment_variables": {
            "PORT": "8080",
            "ENVIRONMENT": "production",
            "HOST": "0.0.0.0"
        },
        "features": [
            "WebSocket support for MCP protocol",
            "24/7 continuous operation",
            "Automatic HTTPS",
            "GitHub integration"
        ]
    }
    
    return info

def main():
    """主函数"""
    print("🚄 XMind MCP Railway部署助手")
    print("=" * 40)
    
    # 检查当前目录
    if not os.path.exists('xmind_mcp_server.py'):
        print("❌ 请在XMind MCP项目根目录运行此脚本")
        sys.exit(1)
    
    # 步骤1: 检查必需文件
    print("\n📋 步骤1: 检查必需文件...")
    if not check_requirements():
        print("请确保所有必需文件都存在")
        sys.exit(1)
    
    # 步骤2: 验证配置文件
    print("\n🔧 步骤2: 验证配置文件...")
    validate_dockerfile()
    validate_requirements()
    
    # 步骤3: 生成Railway配置
    print("\n⚙️ 步骤3: 生成Railway配置...")
    create_railway_config()
    
    # 步骤4: 显示部署信息
    print("\n📊 部署信息:")
    info = generate_deployment_info()
    print(f"项目: {info['project_name']}")
    print(f"端口: {info['port']}")
    print(f"健康检查: {info['health_check']}")
    
    print("\n🚀 下一步:")
    print("1. 访问 https://railway.app")
    print("2. 使用GitHub账号登录")
    print("3. 创建新项目并连接此GitHub仓库")
    print("4. Railway会自动检测并部署你的项目")
    
    print("\n📖 详细部署指南:")
    print("查看 RAILWAY_DEPLOYMENT_GUIDE.md 获取完整说明")
    
    print("\n✅ 准备完成！你的项目已准备好部署到Railway")

if __name__ == "__main__":
    main()