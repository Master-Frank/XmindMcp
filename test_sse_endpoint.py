#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP SSE端点
"""

import requests
import json
import time

def test_sse_endpoint():
    """测试SSE端点"""
    base_url = "https://xmindmcp.onrender.com"
    sse_url = f"{base_url}/sse"
    
    print(f"测试SSE端点: {sse_url}")
    
    try:
        # 测试SSE连接
        response = requests.get(sse_url, stream=True, timeout=10)
        print(f"SSE端点状态码: {response.status_code}")
        print(f"SSE端点响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SSE端点正常工作")
            # 尝试读取一些数据
            for i, line in enumerate(response.iter_lines()):
                if i < 3:  # 只读取前几行
                    print(f"SSE数据行 {i+1}: {line.decode('utf-8') if line else '空行'}")
                else:
                    break
        else:
            print(f"❌ SSE端点返回错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ SSE端点连接失败: {e}")
    
    # 测试其他端点
    endpoints = ["/", "/health", "/tools"]
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                except:
                    print(f"  响应: {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: 错误 - {e}")

if __name__ == "__main__":
    test_sse_endpoint()