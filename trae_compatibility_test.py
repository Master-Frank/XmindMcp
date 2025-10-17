#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae MCP兼容性测试器
模拟Trae客户端的完整连接流程
"""

import asyncio
import json
import httpx
from datetime import datetime

class TraeMCPCompatibilityTester:
    def __init__(self):
        self.base_url = "https://xmindmcp.onrender.com"
        self.session_id = None
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
        
    async def test_full_trae_flow(self):
        """测试完整的Trae连接流程"""
        self.log("🚀 开始Trae MCP兼容性测试...")
        
        # 1. 测试基础连接
        await self.test_basic_connection()
        
        # 2. 建立SSE连接
        await self.establish_sse_connection()
        
        # 3. 发送初始化消息
        await self.send_initialize_message()
        
        # 4. 获取工具列表
        await self.get_tools_list()
        
        self.log("✅ Trae兼容性测试完成")
        
    async def test_basic_connection(self):
        """测试基础连接"""
        self.log("测试基础连接...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                self.log(f"健康检查: {response.status_code}")
                
                response = await client.get(f"{self.base_url}/tools")
                self.log(f"工具列表: {response.status_code}")
                
        except Exception as e:
            self.log(f"基础连接失败: {e}", "ERROR")
            
    async def establish_sse_connection(self):
        """建立SSE连接（模拟Trae行为）"""
        self.log("建立SSE连接...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "User-Agent": "TraeMCP-Client/1.0"
                }
                
                self.log("发送SSE连接请求...")
                
                async with client.stream("GET", f"{self.base_url}/sse", headers=headers) as response:
                    self.log(f"SSE响应状态: {response.status_code}")
                    self.log(f"Content-Type: {response.headers.get('content-type')}")
                    
                    # 读取前几个事件
                    event_count = 0
                    async for line in response.aiter_lines():
                        if line.strip():
                            self.log(f"收到事件: {line}")
                            
                            # 解析事件
                            if line.startswith('event: '):
                                event_type = line[7:]
                                self.log(f"事件类型: {event_type}")
                            elif line.startswith('data: '):
                                try:
                                    data = json.loads(line[6:])
                                    self.log(f"事件数据: {json.dumps(data, ensure_ascii=False)}")
                                    
                                    # 检查是否是connected事件
                                    if data.get('method') == 'connected':
                                        self.session_id = data.get('params', {}).get('session_id')
                                        self.log(f"会话建立成功: {self.session_id}")
                                        
                                except json.JSONDecodeError as e:
                                    self.log(f"解析事件数据失败: {e}", "ERROR")
                            
                            event_count += 1
                            if event_count >= 5:  # 读取前5个事件
                                break
                                
                    self.log(f"共收到 {event_count} 个事件")
                    
        except Exception as e:
            self.log(f"SSE连接失败: {e}", "ERROR")
            
    async def send_initialize_message(self):
        """发送初始化消息"""
        if not self.session_id:
            self.log("没有可用的会话ID", "ERROR")
            return
            
        self.log("发送初始化消息...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 构建初始化消息（严格按照MCP规范）
                init_message = {
                    "jsonrpc": "2.0",
                    "id": "trae-init-1",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": True},
                            "logging": {}
                        },
                        "clientInfo": {
                            "name": "TraeMCP-Test",
                            "version": "1.0.0"
                        }
                    }
                }
                
                messages_url = f"{self.base_url}/messages/{self.session_id}"
                self.log(f"POST {messages_url}")
                self.log(f"消息内容: {json.dumps(init_message, ensure_ascii=False)}")
                
                response = await client.post(
                    messages_url,
                    json=init_message,
                    headers={"Content-Type": "application/json"}
                )
                
                self.log(f"初始化响应: {response.status_code}")
                self.log(f"响应内容: {response.text}")
                
        except Exception as e:
            self.log(f"初始化失败: {e}", "ERROR")
            
    async def get_tools_list(self):
        """获取工具列表"""
        if not self.session_id:
            self.log("没有可用的会话ID", "ERROR")
            return
            
        self.log("获取工具列表...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                tools_message = {
                    "jsonrpc": "2.0",
                    "id": "trae-tools-1",
                    "method": "tools/list",
                    "params": {}
                }
                
                messages_url = f"{self.base_url}/messages/{self.session_id}"
                self.log(f"POST {messages_url}")
                self.log(f"消息内容: {json.dumps(tools_message, ensure_ascii=False)}")
                
                response = await client.post(
                    messages_url,
                    json=tools_message,
                    headers={"Content-Type": "application/json"}
                )
                
                self.log(f"工具列表响应: {response.status_code}")
                self.log(f"响应内容: {response.text}")
                
        except Exception as e:
            self.log(f"获取工具列表失败: {e}", "ERROR")

async def main():
    tester = TraeMCPCompatibilityTester()
    await tester.test_full_trae_flow()

if __name__ == "__main__":
    asyncio.run(main())