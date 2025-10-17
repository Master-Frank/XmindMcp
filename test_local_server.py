#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试完整的MCP SSE服务器
"""

import asyncio
import json
import time
import httpx
import subprocess
import signal
import sys
from typing import Optional

class LocalServerTest:
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.base_url = "http://localhost:8080"
        
    def start_server(self):
        """启动本地服务器"""
        print("🚀 启动本地MCP服务器...")
        self.server_process = subprocess.Popen([
            sys.executable, "xmind_mcp_server.py"
        ], cwd="d:\\project\\XmindMcp")
        
        # 等待服务器启动
        time.sleep(3)
        print("✅ 服务器启动完成")
        
    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            print("🛑 停止本地服务器...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ 服务器已停止")
            
    async def test_sse_endpoint(self):
        """测试SSE端点"""
        print("\n🧪 测试SSE端点...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 测试SSE连接
                print(f"连接SSE端点: {self.base_url}/sse")
                async with client.stream("GET", f"{self.base_url}/sse") as response:
                    print(f"SSE响应状态码: {response.status_code}")
                    print(f"SSE响应头: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        print(f"Content-Type: {content_type}")
                        
                        if 'text/event-stream' in content_type:
                            print("✅ SSE端点返回正确的content-type")
                            
                            # 读取SSE事件
                            event_count = 0
                            async for line in response.aiter_lines():
                                if line.strip():
                                    print(f"📡 SSE事件: {line}")
                                    event_count += 1
                                    
                                    if event_count >= 5:  # 限制事件数量
                                        break
                            
                            print(f"✅ 接收到 {event_count} 个SSE事件")
                        else:
                            print("❌ SSE端点未返回text/event-stream content-type")
                            
                            # 读取响应内容
                            content = ""
                            async for chunk in response.aiter_text():
                                content += chunk
                                if len(content) > 500:  # 限制内容长度
                                    break
                            
                            print(f"响应内容: {content[:500]}...")
                    else:
                        print(f"❌ SSE端点返回错误状态码: {response.status_code}")
                        
            except Exception as e:
                print(f"❌ SSE测试失败: {e}")
                
    async def test_messages_endpoint(self):
        """测试消息端点"""
        print("\n🧪 测试消息端点...")
        
        # 首先创建SSE会话
        async with httpx.AsyncClient() as client:
            try:
                # 创建SSE连接以获取会话ID
                print("创建SSE会话...")
                sse_response = await client.get(f"{self.base_url}/sse", timeout=5.0)
                
                if sse_response.status_code != 200:
                    print("❌ 无法创建SSE会话")
                    return
                    
                # 从响应头中获取会话ID（简化处理）
                session_id = "test-session-123"  # 实际应该从SSE连接中提取
                
                # 发送初始化消息
                init_message = {
                    "jsonrpc": "2.0",
                    "id": "test-init",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {}
                    }
                }
                
                print(f"发送初始化消息到会话: {session_id}")
                response = await client.post(
                    f"{self.base_url}/messages/{session_id}",
                    json=init_message,
                    timeout=10.0
                )
                
                print(f"消息端点响应状态码: {response.status_code}")
                print(f"消息端点响应: {response.text}")
                
                if response.status_code == 200:
                    print("✅ 消息端点工作正常")
                else:
                    print("❌ 消息端点返回错误")
                    
            except Exception as e:
                print(f"❌ 消息端点测试失败: {e}")
                
    async def run_all_tests(self):
        """运行所有测试"""
        try:
            self.start_server()
            
            # 等待服务器完全启动
            await asyncio.sleep(2)
            
            # 测试基础端点
            print("\n🔍 测试基础端点...")
            async with httpx.AsyncClient() as client:
                # 测试根路径
                response = await client.get(f"{self.base_url}/")
                print(f"根路径状态码: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"根路径响应包含SSE信息: {'sse_url' in data}")
                
                # 测试健康检查
                response = await client.get(f"{self.base_url}/health")
                print(f"健康检查状态码: {response.status_code}")
                
                # 测试工具列表
                response = await client.get(f"{self.base_url}/tools")
                print(f"工具列表状态码: {response.status_code}")
            
            # 测试SSE端点
            await self.test_sse_endpoint()
            
            # 测试消息端点
            await self.test_messages_endpoint()
            
        finally:
            self.stop_server()

async def main():
    """主函数"""
    print("🎯 开始本地MCP SSE服务器测试")
    print("=" * 50)
    
    tester = LocalServerTest()
    
    try:
        await tester.run_all_tests()
        print("\n🎉 所有测试完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被中断")
        tester.stop_server()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        tester.stop_server()

if __name__ == "__main__":
    asyncio.run(main())