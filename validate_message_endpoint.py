#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息端点响应验证器
验证消息端点是否返回正确的JSON-RPC响应
"""

import asyncio
import json
import httpx
from datetime import datetime

class MessageEndpointValidator:
    def __init__(self):
        self.base_url = "https://xmindmcp.onrender.com"
        self.session_id = None
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
        
    async def get_session_id(self):
        """获取会话ID"""
        self.log("获取会话ID...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
                
                async with client.stream("GET", f"{self.base_url}/sse", headers=headers) as response:
                    self.log(f"SSE响应状态: {response.status_code}")
                    
                    # 读取第一个connected事件
                    async for line in response.aiter_lines():
                        if line.strip() and line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if data.get('method') == 'connected':
                                    self.session_id = data.get('params', {}).get('session_id')
                                    self.log(f"会话ID: {self.session_id}")
                                    break
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            self.log(f"获取会话ID失败: {e}", "ERROR")
            
    async def test_message_endpoint(self):
        """测试消息端点"""
        if not self.session_id:
            await self.get_session_id()
            
        if not self.session_id:
            self.log("无法获取会话ID", "ERROR")
            return
            
        self.log("测试消息端点...")
        
        # 测试初始化消息
        await self.send_initialize_message()
        
        # 测试工具列表消息
        await self.send_tools_list_message()
        
    async def send_initialize_message(self):
        """发送初始化消息"""
        self.log("发送初始化消息...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                init_message = {
                    "jsonrpc": "2.0",
                    "id": "test-init-1",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": True}
                        },
                        "clientInfo": {
                            "name": "TestClient",
                            "version": "1.0.0"
                        }
                    }
                }
                
                messages_url = f"{self.base_url}/messages/{self.session_id}"
                self.log(f"POST {messages_url}")
                self.log(f"请求: {json.dumps(init_message, ensure_ascii=False)}")
                
                response = await client.post(
                    messages_url,
                    json=init_message,
                    headers={"Content-Type": "application/json"}
                )
                
                self.log(f"响应状态: {response.status_code}")
                self.log(f"响应头: {dict(response.headers)}")
                self.log(f"响应体: {response.text}")
                
                # 验证响应格式
                try:
                    response_data = response.json()
                    self.log(f"解析的JSON: {json.dumps(response_data, ensure_ascii=False)}")
                    
                    # 检查是否是完整的JSON-RPC响应
                    if "jsonrpc" in response_data and "id" in response_data:
                        if "result" in response_data:
                            self.log("✅ 收到完整的JSON-RPC响应（包含result）")
                        elif "error" in response_data:
                            self.log(f"⚠️  收到JSON-RPC错误响应: {response_data['error']}")
                        else:
                            self.log("⚠️  JSON-RPC响应格式不完整")
                    else:
                        self.log("⚠️  响应不是JSON-RPC格式")
                        
                except json.JSONDecodeError:
                    self.log("❌ 响应不是有效的JSON格式")
                    
        except Exception as e:
            self.log(f"发送初始化消息失败: {e}", "ERROR")
            
    async def send_tools_list_message(self):
        """发送工具列表消息"""
        self.log("发送工具列表消息...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                tools_message = {
                    "jsonrpc": "2.0",
                    "id": "test-tools-1",
                    "method": "tools/list",
                    "params": {}
                }
                
                messages_url = f"{self.base_url}/messages/{self.session_id}"
                self.log(f"POST {messages_url}")
                self.log(f"请求: {json.dumps(tools_message, ensure_ascii=False)}")
                
                response = await client.post(
                    messages_url,
                    json=tools_message,
                    headers={"Content-Type": "application/json"}
                )
                
                self.log(f"响应状态: {response.status_code}")
                self.log(f"响应体: {response.text}")
                
                # 验证响应格式
                try:
                    response_data = response.json()
                    self.log(f"解析的JSON: {json.dumps(response_data, ensure_ascii=False)}")
                    
                    # 检查是否是完整的JSON-RPC响应
                    if "jsonrpc" in response_data and "id" in response_data:
                        if "result" in response_data:
                            self.log("✅ 收到完整的JSON-RPC响应（包含result）")
                            if "tools" in response_data["result"]:
                                tools_count = len(response_data["result"]["tools"])
                                self.log(f"📋 工具数量: {tools_count}")
                        elif "error" in response_data:
                            self.log(f"⚠️  收到JSON-RPC错误响应: {response_data['error']}")
                        else:
                            self.log("⚠️  JSON-RPC响应格式不完整")
                    else:
                        self.log("⚠️  响应不是JSON-RPC格式")
                        
                except json.JSONDecodeError:
                    self.log("❌ 响应不是有效的JSON格式")
                    
        except Exception as e:
            self.log(f"发送工具列表消息失败: {e}", "ERROR")

async def main():
    validator = MessageEndpointValidator()
    await validator.test_message_endpoint()

if __name__ == "__main__":
    asyncio.run(main())