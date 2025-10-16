#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind MCP服务器启动器
兼容旧版本的启动脚本，现在委托给xmind_mcp_server.py
"""

import sys
import warnings

# 显示兼容性警告
warnings.warn(
    "start_mcp_server.py 已被弃用，请使用 xmind_mcp_server.py\n"
    "命令: python xmind_mcp_server.py",
    DeprecationWarning,
    stacklevel=2
)

# 导入新的服务器模块
try:
    from xmind_mcp_server import XMindMCPServer
except ImportError as e:
    print(f"错误: 无法导入新的服务器模块: {e}")
    print("请确保 xmind_mcp_server.py 文件存在且可导入")
    sys.exit(1)

def main():
    """主函数 - 委托给新的服务器"""
    print("正在启动 XMind MCP Server (兼容模式)...")
    print("注意: 建议使用新的命令: python xmind_mcp_server.py")
    
    # 创建并启动服务器
    server = XMindMCPServer()
    server.main()

if __name__ == "__main__":
    main()