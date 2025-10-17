#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae MCP连接诊断工具
模拟Trae的MCP客户端行为，诊断连接问题
"""

import asyncio
import json
import httpx
import time
from typing import Optional, Dict, Any

class TraeMCPDiagnostic:
    def __init__(self):
        self.base_url = "https://xmindmcp.onrender.com"
        self.sse_url = f"{self.base_url}/sse"
        self.session_id: Optional[str] = None
        
    async def test_basic_connectivity(self):
        """测试基础连接性"""
        print("🔍 测试基础连接性...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 测试根路径
                print("测试根路径...")
                response = await client.get(self.base_url)
                print(f"根路径状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"服务器版本: {data.get('version')}")
                    print(f"SSE端点: {data.get('sse_url')}")
                    print(f"消息端点: {data.get('messages_url')}")
                    print(f"MCP协议: {data.get('mcp_protocol')}")
                
                # 测试健康检查
                print("\n测试健康检查...")
                response = await client.get(f"{self.base_url}/health")
                print(f"健康检查状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"服务器状态: {data.get('status')}")
                    print(f"时间戳: {data.get('timestamp')}")
                
                return True
                
        except Exception as e:
            print(f"❌ 基础连接测试失败: {e}")
            return False
            
    async def test_sse_connection(self):
        """测试SSE连接（模拟Trae行为）"""
        print("\n🔍 测试SSE连接（模拟Trae客户端）...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"连接到SSE端点: {self.sse_url}")
                
                # 设置与Trae类似的请求头
                headers = {
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "User-Agent": "TraeMCP-Client/1.0"
                }
                
                start_time = time.time()
                
                async with client.stream("GET", self.sse_url, headers=headers) as response:
                    print(f"SSE响应状态码: {response.status_code}")
                    print(f"响应头: {dict(response.headers)}")
                    
                    if response.status_code != 200:
                        print(f"❌ SSE连接失败，状态码: {response.status_code}")
                        return False
                    
                    content_type = response.headers.get('content-type', '')
                    print(f"Content-Type: {content_type}")
                    
                    if 'text/event-stream' not in content_type:
                        print("❌ 响应Content-Type不是text/event-stream")
                        return False
                    
                    print("✅ SSE连接建立成功")
                    
                    # 读取前几个事件（模拟Trae的等待行为）
                    event_count = 0
                    timeout = 10  # 10秒超时
                    
                    print("等待SSE事件...")
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            print(f"📡 收到事件: {line}")
                            
                            # 解析事件数据
                            if line.startswith('data: '):
                                try:
                                    data = json.loads(line[6:])  # 去掉"data: "前缀
                                    if data.get('method') == 'connected':
                                        self.session_id = data.get('params', {}).get('session_id')
                                        print(f"✅ 会话创建成功: {self.session_id}")
                                        
                                        # 测试消息端点
                                        await self.test_message_endpoint()
                                        
                                except json.JSONDecodeError as e:
                                    print(f"❌ 解析事件数据失败: {e}")
                            
                            event_count += 1
                            
                            # 如果收到连接确认，可以认为连接成功
                            if self.session_id:
                                print("✅ SSE连接完全建立")
                                return True
                        
                        # 检查超时
                        if time.time() - start_time > timeout:
                            print(f"⏰ SSE连接超时（{timeout}秒）")
                            break
                    
                    if event_count == 0:
                        print("⚠️  未收到任何SSE事件")
                        return False
                    
                    return True
                    
        except httpx.ReadTimeout:
            print("❌ SSE连接超时（30秒）")
            return False
        except Exception as e:
            print(f"❌ SSE连接测试失败: {e}")
            return False
            
    async def test_message_endpoint(self):
        """测试消息端点"""
        print(f"\n🔍 测试消息端点（会话: {self.session_id}）...")
        
        if not self.session_id:
            print("❌ 没有可用的会话ID")
            return False
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 发送初始化消息（模拟MCP协议）
                init_message = {
                    "jsonrpc": "2.0",
                    "id": "diagnostic-init-1",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": True}
                        },
                        "clientInfo": {
                            "name": "TraeMCP-Diagnostic",
                            "version": "1.0.0"
                        }
                    }
                }
                
                messages_url = f"{self.base_url}/messages/{self.session_id}"
                print(f"发送初始化消息到: {messages_url}")
                
                response = await client.post(
                    messages_url,
                    json=init_message,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"消息端点响应状态码: {response.status_code}")
                print(f"消息端点响应: {response.text}")
                
                if response.status_code == 200:
                    print("✅ 消息端点工作正常")
                    return True
                else:
                    print(f"❌ 消息端点返回错误: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 消息端点测试失败: {e}")
            return False
            
    async def run_full_diagnostic(self):
        """运行完整诊断"""
        print("🎯 Trae MCP连接诊断工具")
        print("=" * 50)
        print(f"目标服务器: {self.base_url}")
        print(f"SSE端点: {self.sse_url}")
        print("=" * 50)
        
        # 基础连接测试
        basic_ok = await self.test_basic_connectivity()
        
        if basic_ok:
            # SSE连接测试
            sse_ok = await self.test_sse_connection()
            
            if sse_ok and self.session_id:
                print(f"\n🎉 诊断完成！连接成功")
                print(f"会话ID: {self.session_id}")
                print("✅ 服务器已准备好接受Trae连接")
            else:
                print(f"\n⚠️  诊断完成，但SSE连接可能有问题")
                print("建议检查服务器日志和网络连接")
        else:
            print(f"\n❌ 诊断失败 - 基础连接有问题")
            print("建议检查服务器状态和网络配置")

async def main():
    """主函数"""
    diagnostic = TraeMCPDiagnostic()
    await diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    asyncio.run(main())