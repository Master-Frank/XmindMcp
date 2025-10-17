#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试SSE实现的脚本
在重新部署到Render之前，先在本地测试新的SSE功能
"""

import asyncio
import json
import time
from mcp_sse_handler import MCPSSEHandler

async def test_sse_handler():
    """测试SSE处理器"""
    print("🧪 测试MCP SSE处理器...")
    
    handler = MCPSSEHandler()
    
    # 测试1: 创建会话
    print("\n1️⃣ 测试创建会话")
    session_id = handler.create_session()
    print(f"✅ 创建会话: {session_id}")
    
    # 测试2: 获取会话信息
    print("\n2️⃣ 测试获取会话信息")
    session_info = handler.get_session(session_id)
    print(f"✅ 会话信息: {json.dumps(session_info, indent=2, ensure_ascii=False)}")
    
    # 测试3: 处理初始化消息
    print("\n3️⃣ 测试初始化消息处理")
    init_message = {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {}
        }
    }
    
    response = await handler.process_mcp_message(session_id, init_message)
    print(f"✅ 初始化响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    # 测试4: 处理工具列表请求
    print("\n4️⃣ 测试工具列表请求")
    tools_message = {
        "jsonrpc": "2.0",
        "id": "test-2",
        "method": "tools/list"
    }
    
    response = await handler.process_mcp_message(session_id, tools_message)
    print(f"✅ 工具列表响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    # 测试5: 发送消息到SSE连接
    print("\n5️⃣ 测试SSE消息发送")
    test_message = {
        "jsonrpc": "2.0",
        "id": "test-3",
        "result": {"test": "SSE消息测试"}
    }
    
    await handler.send_message(session_id, test_message)
    print("✅ 消息已发送到SSE队列")
    
    # 测试6: SSE连接处理
    print("\n6️⃣ 测试SSE连接处理")
    print("开始SSE流...")
    
    message_count = 0
    async for event in handler.handle_sse_connection(session_id):
        print(f"📡 SSE事件: {event.strip()}")
        message_count += 1
        
        # 限制测试消息数量
        if message_count >= 3:
            break
            
        # 模拟发送更多消息
        if message_count == 1:
            await handler.send_message(session_id, {
                "jsonrpc": "2.0",
                "id": "test-4",
                "result": {"follow_up": "第二条测试消息"}
            })
    
    print(f"✅ 处理了 {message_count} 个SSE事件")
    
    # 测试7: 清理会话
    print("\n7️⃣ 测试会话清理")
    handler.remove_session(session_id)
    print(f"✅ 会话已清理: {session_id}")
    
    print("\n🎉 所有SSE处理器测试完成！")

if __name__ == "__main__":
    asyncio.run(test_sse_handler())