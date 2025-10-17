#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控服务器连接状态
模拟Trae连接过程，查看详细日志
"""

import asyncio
import json
import time
import httpx
from datetime import datetime

class RealtimeMonitor:
    def __init__(self):
        self.base_url = "https://xmindmcp.onrender.com"
        self.sse_url = f"{self.base_url}/sse"
        
    def log(self, message: str):
        """带时间戳的日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
        
    async def monitor_sse_connection(self):
        """监控SSE连接过程"""
        self.log("🚀 开始监控SSE连接过程...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 记录开始时间
                start_time = time.time()
                
                self.log(f"正在连接: {self.sse_url}")
                
                # 设置请求头（模拟Trae）
                headers = {
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache", 
                    "Connection": "keep-alive",
                    "User-Agent": "TraeMCP-Client/1.0"
                }
                
                self.log("请求头设置完成，开始流式连接...")
                
                async with client.stream("GET", self.sse_url, headers=headers) as response:
                    connect_time = time.time() - start_time
                    self.log(f"✅ 连接建立成功！耗时: {connect_time:.2f}秒")
                    self.log(f"响应状态码: {response.status_code}")
                    self.log(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
                    self.log(f"会话ID: {response.headers.get('session-id', 'unknown')}")
                    
                    if response.status_code != 200:
                        self.log(f"❌ 连接失败，状态码: {response.status_code}")
                        return False
                    
                    # 监控事件接收
                    event_count = 0
                    last_event_time = time.time()
                    
                    self.log("等待接收SSE事件...")
                    
                    async for line in response.aiter_lines():
                        current_time = time.time()
                        time_since_last = current_time - last_event_time
                        
                        if line.strip():
                            self.log(f"📡 收到事件 (距离上次: {time_since_last:.2f}秒): {line}")
                            event_count += 1
                            last_event_time = current_time
                            
                            # 解析事件
                            if line.startswith('data: '):
                                try:
                                    data = json.loads(line[6:])
                                    if data.get('method') == 'connected':
                                        session_id = data.get('params', {}).get('session_id')
                                        self.log(f"🎉 会话建立成功: {session_id}")
                                        
                                        # 测试消息端点
                                        await self.test_message_with_session(session_id)
                                        
                                        # 继续监听一段时间
                                        self.log("继续监听30秒...")
                                        await asyncio.sleep(30)
                                        break
                                        
                                except json.JSONDecodeError as e:
                                    self.log(f"❌ 解析事件失败: {e}")
                        
                        # 检查是否超时
                        if current_time - last_event_time > 30:
                            self.log("⚠️  30秒内未收到新事件，可能连接有问题")
                            break
                    
                    total_time = time.time() - start_time
                    self.log(f"监控结束 - 总耗时: {total_time:.2f}秒, 收到事件: {event_count}个")
                    
                    return True
                    
        except httpx.ReadTimeout:
            self.log("❌ 连接超时（60秒）")
            return False
        except Exception as e:
            self.log(f"❌ 监控失败: {e}")
            return False
            
    async def test_message_with_session(self, session_id: str):
        """测试消息端点"""
        self.log(f"测试消息端点（会话: {session_id}）...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 发送初始化消息
                init_message = {
                    "jsonrpc": "2.0",
                    "id": "monitor-init-1",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": True}
                        },
                        "clientInfo": {
                            "name": "TraeMCP-Monitor",
                            "version": "1.0.0"
                        }
                    }
                }
                
                messages_url = f"{self.base_url}/messages/{session_id}"
                self.log(f"发送初始化消息到: {messages_url}")
                
                start_time = time.time()
                response = await client.post(
                    messages_url,
                    json=init_message,
                    headers={"Content-Type": "application/json"}
                )
                
                response_time = time.time() - start_time
                self.log(f"消息响应时间: {response_time:.2f}秒")
                self.log(f"消息响应状态码: {response.status_code}")
                self.log(f"消息响应内容: {response.text}")
                
                if response.status_code == 200:
                    self.log("✅ 消息端点响应正常")
                else:
                    self.log(f"❌ 消息端点异常: {response.status_code}")
                    
        except Exception as e:
            self.log(f"❌ 消息测试失败: {e}")
            
    async def monitor_connection_health(self):
        """监控连接健康状态"""
        self.log("🔍 开始连接健康检查...")
        
        for i in range(3):  # 检查3次
            self.log(f"第{i+1}次健康检查...")
            
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.base_url}/health")
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log(f"✅ 服务器健康 - 状态: {data.get('status')}")
                    else:
                        self.log(f"⚠️  健康检查异常 - 状态码: {response.status_code}")
                        
            except Exception as e:
                self.log(f"❌ 健康检查失败: {e}")
                
            await asyncio.sleep(2)
            
    async def run_monitor(self):
        """运行完整监控"""
        print("🎯 Trae MCP连接实时监控")
        print("=" * 60)
        
        # 先检查基础健康
        await self.monitor_connection_health()
        
        # 监控SSE连接
        success = await self.monitor_sse_connection()
        
        if success:
            print("\n✅ 监控完成 - 服务器连接正常")
            print("💡 如果Trae还在转圈，建议：")
            print("   1. 耐心等待（首次连接可能需要30-60秒）")
            print("   2. 检查Trae网络设置")
            print("   3. 尝试重新添加MCP")
        else:
            print("\n❌ 监控发现问题 - 请查看详细日志")

async def main():
    monitor = RealtimeMonitor()
    await monitor.run_monitor()

if __name__ == "__main__":
    asyncio.run(main())