#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP SSE (Server-Sent Events) 处理器
为XMind MCP服务器提供SSE支持，兼容MCP协议
"""

import json
import asyncio
import uuid
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


class MCPMessage(BaseModel):
    """MCP消息模型"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPSSEHandler:
    """MCP SSE处理器"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
    
    def create_session(self) -> str:
        """创建新的SSE会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0
        }
        self.message_queues[session_id] = asyncio.Queue()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id: str):
        """移除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.message_queues:
            del self.message_queues[session_id]
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """向指定会话发送消息"""
        if session_id in self.message_queues:
            await self.message_queues[session_id].put(message)
            # 更新会话活动时间
            if session_id in self.sessions:
                self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
                self.sessions[session_id]["message_count"] += 1
    
    async def handle_sse_connection(self, session_id: str) -> AsyncGenerator[str, None]:
        """处理SSE连接"""
        if session_id not in self.sessions:
            # 发送错误消息
            error_msg = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": "Invalid session ID"
                }
            }
            yield f"data: {json.dumps(error_msg)}\n\n"
            return
        
        # 发送endpoint事件（MCP规范要求）
        endpoint_msg = f"event: endpoint\ndata: /messages/{session_id}\n\n"
        yield endpoint_msg
        
        # 发送初始连接确认
        init_msg = {
            "jsonrpc": "2.0",
            "method": "connected",
            "params": {"session_id": session_id}
        }
        yield f"data: {json.dumps(init_msg)}\n\n"
        
        queue = self.message_queues[session_id]
        
        try:
            while True:
                try:
                    # 等待消息，设置超时以避免无限阻塞
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # 发送SSE格式的消息
                    sse_data = f"data: {json.dumps(message)}\n\n"
                    yield sse_data
                    
                except asyncio.TimeoutError:
                    # 发送心跳消息保持连接
                    heartbeat = {
                        "jsonrpc": "2.0",
                        "method": "heartbeat",
                        "params": {"timestamp": datetime.now().isoformat()}
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    
        except GeneratorExit:
            # 客户端断开连接
            self.remove_session(session_id)
        except Exception as e:
            # 发送错误消息
            error_msg = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            yield f"data: {json.dumps(error_msg)}\n\n"
            self.remove_session(session_id)
    
    async def process_mcp_message(self, session_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP消息"""
        try:
            # 验证消息格式
            if message.get("jsonrpc") != "2.0":
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "jsonrpc field must be '2.0'"
                    }
                }
            
            method = message.get("method")
            msg_id = message.get("id")
            
            if not method:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "method field is required"
                    }
                }
            
            # 处理不同的MCP方法
            if method == "initialize":
                return await self._handle_initialize(msg_id, message.get("params", {}))
            elif method == "tools/list":
                return await self._handle_tools_list(msg_id)
            elif method == "tools/call":
                return await self._handle_tools_call(msg_id, message.get("params", {}))
            elif method == "ping":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"pong": True}
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
    
    async def _handle_initialize(self, msg_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True},
                    "logging": {}
                },
                "serverInfo": {
                    "name": "xmind-mcp-server",
                    "version": "1.0.0",
                    "description": "XMind MCP Server with SSE support"
                }
            }
        }
    
    async def _handle_tools_list(self, msg_id: str) -> Dict[str, Any]:
        """处理工具列表请求"""
        # 这里返回XMind工具列表
        tools = [
            {
                "name": "read_xmind_file",
                "description": "读取XMind文件内容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "XMind文件路径"}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "create_mind_map",
                "description": "创建新的思维导图",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "思维导图标题"},
                        "topics": {"type": "array", "description": "主题列表"}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "analyze_mind_map",
                "description": "分析思维导图结构",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "XMind文件路径"}
                    },
                    "required": ["file_path"]
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": tools}
        }
    
    async def _handle_tools_call(self, msg_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求"""
        try:
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            # 这里应该调用实际的XMind工具
            # 现在返回模拟结果
            if tool_name == "read_xmind_file":
                result = {
                    "content": [{
                        "type": "text",
                        "text": f"成功读取XMind文件: {tool_args.get('file_path', 'unknown')}"
                    }]
                }
            elif tool_name == "create_mind_map":
                result = {
                    "content": [{
                        "type": "text", 
                        "text": f"成功创建思维导图: {tool_args.get('title', 'untitled')}"
                    }]
                }
            elif tool_name == "analyze_mind_map":
                result = {
                    "content": [{
                        "type": "text",
                        "text": f"成功分析思维导图: {tool_args.get('file_path', 'unknown')}"
                    }]
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": "Tool execution error",
                    "data": str(e)
                }
            }


# 创建全局处理器实例
sse_handler = MCPSSEHandler()


async def sse_endpoint():
    """SSE端点处理函数"""
    session_id = sse_handler.create_session()
    
    async def event_generator():
        async for event in sse_handler.handle_sse_connection(session_id):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Session-ID": session_id
        }
    )


async def messages_endpoint(session_id: str, message: Dict[str, Any]):
    """消息处理端点"""
    try:
        response = await sse_handler.process_mcp_message(session_id, message)
        await sse_handler.send_message(session_id, response)
        # 返回完整的JSON-RPC响应，而不是简单的状态
        return response
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }