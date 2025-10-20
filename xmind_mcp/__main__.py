#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind MCP Package Entry Point

这是xmind-mcp包的主入口点，支持通过uvx安装和运行。
"""

import sys
import os

# 将当前目录添加到Python路径，确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主模块，统一到服务器入口
from xmind_mcp_server import main

if __name__ == "__main__":
    main()