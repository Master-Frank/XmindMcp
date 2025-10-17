#!/usr/bin/env python3
"""
Trae使用演示
展示如何在Trae IDE中使用XMind MCP功能
"""

import requests
import json
import time

def demo_trae_usage():
    """演示Trae中的典型使用场景"""
    
    base_url = "https://xmindmcp.onrender.com"
    
    print("🎯 Trae XMind MCP 使用演示")
    print("=" * 40)
    
    # 1. 创建会话
    print("\n1️⃣ 创建会话...")
    response = requests.get(f"{base_url}/sse", stream=True)
    session_id = response.headers.get("Session-ID")
    print(f"✅ 会话创建成功: {session_id}")
    
    # 2. 初始化（Trae会自动完成）
    print("\n2️⃣ 初始化MCP连接...")
    init_msg = {
        "jsonrpc": "2.0",
        "id": "demo-init",
        "method": "initialize",
        "params": {
            "clientInfo": {"name": "Trae", "version": "1.0.0"}
        }
    }
    
    response = requests.post(
        f"{base_url}/messages/{session_id}",
        json=init_msg
    )
    print("✅ 初始化完成")
    
    # 3. 获取工具列表
    print("\n3️⃣ 获取可用工具...")
    tools_msg = {
        "jsonrpc": "2.0", 
        "id": "demo-tools",
        "method": "tools/list"
    }
    
    response = requests.post(
        f"{base_url}/messages/{session_id}",
        json=tools_msg
    )
    
    tools = response.json()["result"]["tools"]
    print(f"✅ 发现 {len(tools)} 个工具:")
    for tool in tools:
        print(f"   • {tool['name']}: {tool['description']}")
    
    # 4. 创建思维导图（实际Trae中通过UI触发）
    print("\n4️⃣ 创建思维导图...")
    create_msg = {
        "jsonrpc": "2.0",
        "id": "demo-create",
        "method": "tools/call",
        "params": {
            "name": "create_mind_map",
            "arguments": {
                "title": "项目规划",
                "topics": ["需求分析", "设计阶段", "开发实现", "测试验证", "部署上线"]
            }
        }
    }
    
    response = requests.post(
        f"{base_url}/messages/{session_id}",
        json=create_msg
    )
    
    result = response.json()["result"]["content"][0]["text"]
    print(f"✅ {result}")
    
    # 5. 分析思维导图
    print("\n5️⃣ 分析思维导图结构...")
    analyze_msg = {
        "jsonrpc": "2.0",
        "id": "demo-analyze", 
        "method": "tools/call",
        "params": {
            "name": "analyze_mind_map",
            "arguments": {"file_path": "项目规划.xmind"}
        }
    }
    
    response = requests.post(
        f"{base_url}/messages/{session_id}",
        json=analyze_msg
    )
    
    result = response.json()["result"]["content"][0]["text"]
    print(f"✅ {result}")
    
    print("\n🎉 演示完成！")
    print("\n在Trae中，你可以：")
    print("• 直接输入'创建思维导图'来触发create_mind_map工具")
    print("• 输入'分析项目规划.xmind'来读取和分析文件")
    print("• Trae会自动识别你的意图并调用相应的MCP工具")

if __name__ == "__main__":
    demo_trae_usage()