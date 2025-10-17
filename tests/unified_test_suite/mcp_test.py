#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind MCP统一测试套件
整合所有测试功能到一个统一的测试框架中
"""

import sys
import os
import json
import time
import requests
import tempfile
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入核心模块
from xmind_core_engine import XMindCoreEngine


class UnifiedXMindTester:
    """统一的XMind测试器"""
    
    def __init__(self, server_url: str = "https://xmindmcp.onrender.com", use_chinese: bool = True):
        self.server_url = server_url
        self.use_chinese = use_chinese
        self.session_id = None
        self.core_engine = XMindCoreEngine()
        self.test_results = []
        self.project_root = project_root
        
    def log(self, message: str, level: str = "INFO"):
        """输出日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_symbol = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(level, "ℹ️")
        
        print(f"[{timestamp}] {level_symbol} {message}")
    
    def record_result(self, test_name: str, success: bool, details: str = "", category: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if success else "❌"
        self.log(f"{test_name}: {status_symbol} {details}")
    
    # ==================== 环境检查测试 ====================
    
    def test_environment_setup(self) -> float:
        """测试环境设置"""
        self.log("开始环境设置测试...", "INFO")
        
        # Python版本检查
        version = sys.version_info
        python_ok = version.major == 3 and version.minor >= 8
        self.record_result("Python版本检查", python_ok, 
                          f"Python {version.major}.{version.minor}.{version.micro}", "环境")
        
        # 依赖包检查
        required_packages = ['xmind', 'requests', 'openpyxl', 'lxml']
        packages_ok = 0
        for package in required_packages:
            try:
                __import__(package)
                packages_ok += 1
            except ImportError:
                pass
        
        packages_success = packages_ok == len(required_packages)
        self.record_result("依赖包检查", packages_success, 
                          f"{packages_ok}/{len(required_packages)} 个包已安装", "环境")
        
        # 目录结构检查
        required_dirs = ['examples', 'output', 'tests', 'configs']
        dirs_ok = 0
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                dirs_ok += 1
        
        dirs_success = dirs_ok == len(required_dirs)
        self.record_result("目录结构检查", dirs_success, 
                          f"{dirs_ok}/{len(required_dirs)} 个目录存在", "环境")
        
        # 核心文件检查
        core_files = [
            'xmind_core_engine.py',
            'xmind_mcp_server.py',
            'universal_xmind_converter.py',
            'mcp_sse_handler.py'
        ]
        files_ok = 0
        for file_name in core_files:
            file_path = self.project_root / file_name
            if file_path.exists() and file_path.is_file():
                files_ok += 1
        
        files_success = files_ok == len(core_files)
        self.record_result("核心文件检查", files_success, 
                          f"{files_ok}/{len(core_files)} 个文件存在", "环境")
        
        # 计算成功率
        total_tests = 4
        passed_tests = sum([python_ok, packages_success, dirs_success, files_success])
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"环境设置测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    # ==================== 核心引擎测试 ====================
    
    def test_core_engine_functionality(self) -> float:
        """测试核心引擎功能"""
        self.log("开始核心引擎功能测试...", "INFO")
        
        # 引擎初始化测试
        try:
            tools = self.core_engine.get_tools()
            engine_init_ok = len(tools) > 0
            self.record_result("引擎初始化", engine_init_ok, f"发现 {len(tools)} 个工具", "核心")
            
            # 显示工具列表
            for tool in tools[:3]:  # 显示前3个工具
                self.log(f"  📋 {tool['name']}: {tool['description'][:50]}...", "INFO")
            
        except Exception as e:
            engine_init_ok = False
            self.record_result("引擎初始化", False, f"错误: {str(e)}", "核心")
        
        # 创建思维导图测试
        try:
            result = self.core_engine.create_mind_map("测试思维导图", '["主题1", "主题2", "主题3"]')
            create_ok = result.get('status') == 'success' and os.path.exists(result.get('filename', ''))
            self.record_result("创建思维导图", create_ok, 
                              f"文件: {result.get('filename', 'N/A')}", "核心")
            
            # 清理测试文件
            if create_ok and result.get('filename'):
                os.remove(result['filename'])
                
        except Exception as e:
            create_ok = False
            self.record_result("创建思维导图", False, f"错误: {str(e)}", "核心")
        
        # 计算成功率
        total_tests = 2
        passed_tests = sum([engine_init_ok, create_ok])
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"核心引擎测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    # ==================== MCP服务器测试 ====================
    
    def test_mcp_server_connection(self) -> float:
        """测试MCP服务器连接"""
        self.log("开始MCP服务器连接测试...", "INFO")
        
        # 服务器健康检查
        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            health_ok = response.status_code == 200
            self.record_result("服务器健康检查", health_ok, 
                              f"状态码: {response.status_code}", "服务器")
        except Exception as e:
            health_ok = False
            self.record_result("服务器健康检查", False, f"错误: {str(e)}", "服务器")
        
        # SSE连接测试
        try:
            response = requests.get(f"{self.server_url}/sse", stream=True, timeout=10)
            self.session_id = response.headers.get("Session-ID")
            sse_ok = response.status_code == 200 and self.session_id is not None
            self.record_result("SSE连接", sse_ok, 
                              f"会话ID: {self.session_id[:8] if self.session_id else 'None'}...", "服务器")
        except Exception as e:
            sse_ok = False
            self.record_result("SSE连接", False, f"错误: {str(e)}", "服务器")
        
        # 计算成功率
        total_tests = 2
        passed_tests = sum([health_ok, sse_ok])
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"MCP服务器测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    def test_mcp_protocol_functionality(self) -> float:
        """测试MCP协议功能"""
        if not self.session_id:
            self.log("未建立SSE会话，跳过MCP协议测试", "WARNING")
            return 0.0
        
        self.log("开始MCP协议功能测试...", "INFO")
        
        # JSON-RPC初始化
        init_msg = {
            "jsonrpc": "2.0",
            "id": "unified-init",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True}
                },
                "clientInfo": {"name": "UnifiedTester", "version": "1.0.0"}
            }
        }
        
        try:
            response = self._send_mcp_message(init_msg)
            init_ok = "result" in response and "serverInfo" in response["result"]
            self.record_result("JSON-RPC初始化", init_ok, "协议格式正确", "协议")
        except Exception as e:
            init_ok = False
            self.record_result("JSON-RPC初始化", False, f"错误: {str(e)}", "协议")
        
        # 工具列表获取
        tools_msg = {
            "jsonrpc": "2.0",
            "id": "unified-tools",
            "method": "tools/list"
        }
        
        try:
            response = self._send_mcp_message(tools_msg)
            tools = response.get("result", {}).get("tools", [])
            tools_ok = len(tools) > 0
            
            tool_names = [tool["name"] for tool in tools]
            self.record_result("工具列表获取", tools_ok, 
                              f"发现 {len(tools)} 个工具: {', '.join(tool_names)}", "协议")
        except Exception as e:
            tools_ok = False
            self.record_result("工具列表获取", False, f"错误: {str(e)}", "协议")
        
        # 计算成功率
        total_tests = 2
        passed_tests = sum([init_ok, tools_ok])
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"MCP协议测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    def test_tool_functionality(self) -> float:
        """测试工具功能"""
        if not self.session_id:
            self.log("未建立SSE会话，跳过工具功能测试", "WARNING")
            return 0.0
        
        self.log("开始工具功能测试...", "INFO")
        
        test_cases = [
            {
                "name": "基本思维导图",
                "params": {
                    "title": "统一测试思维导图",
                    "topics": ["主题1", "主题2", "主题3"]
                }
            },
            {
                "name": "项目规划图",
                "params": {
                    "title": "项目规划",
                    "topics": ["需求分析", "设计阶段", "开发实现", "测试验证", "部署上线"]
                }
            },
            {
                "name": "学习路线图", 
                "params": {
                    "title": "学习路线",
                    "topics": ["基础知识", "进阶技能", "实践项目", "总结提升"]
                }
            }
        ]
        
        created_files = []
        passed_tests = 0
        total_tests = len(test_cases) * 3  # 创建、读取、分析
        
        for i, test_case in enumerate(test_cases):
            # 创建思维导图
            create_msg = {
                "jsonrpc": "2.0",
                "id": f"unified-create-{i}",
                "method": "tools/call",
                "params": {
                    "name": "create_mind_map",
                    "arguments": test_case["params"]
                }
            }
            
            try:
                response = self._send_mcp_message(create_msg)
                create_ok = "result" in response and "content" in response["result"]
                
                if create_ok:
                    content = response["result"]["content"][0]["text"]
                    self.record_result(f"创建{test_case['name']}", True, content, "工具")
                    
                    # 提取文件名用于后续测试
                    file_name = f"{test_case['params']['title']}.xmind"
                    created_files.append(file_name)
                else:
                    self.record_result(f"创建{test_case['name']}", False, "创建失败", "工具")
                    
            except Exception as e:
                self.record_result(f"创建{test_case['name']}", False, f"错误: {str(e)}", "工具")
                create_ok = False
            
            if create_ok:
                passed_tests += 1
                
                # 读取测试
                read_msg = {
                    "jsonrpc": "2.0",
                    "id": f"unified-read-{i}",
                    "method": "tools/call",
                    "params": {
                        "name": "read_xmind_file",
                        "arguments": {"file_path": f"{test_case['params']['title']}.xmind"}
                    }
                }
                
                try:
                    response = self._send_mcp_message(read_msg)
                    read_ok = "result" in response
                    self.record_result(f"读取{test_case['name']}", read_ok, "读取成功" if read_ok else "读取失败", "工具")
                    if read_ok:
                        passed_tests += 1
                except Exception as e:
                    self.record_result(f"读取{test_case['name']}", False, f"错误: {str(e)}", "工具")
                
                # 分析测试
                analyze_msg = {
                    "jsonrpc": "2.0",
                    "id": f"unified-analyze-{i}",
                    "method": "tools/call",
                    "params": {
                        "name": "analyze_mind_map",
                        "arguments": {"file_path": f"{test_case['params']['title']}.xmind"}
                    }
                }
                
                try:
                    response = self._send_mcp_message(analyze_msg)
                    analyze_ok = "result" in response
                    self.record_result(f"分析{test_case['name']}", analyze_ok, "分析完成" if analyze_ok else "分析失败", "工具")
                    if analyze_ok:
                        passed_tests += 1
                except Exception as e:
                    self.record_result(f"分析{test_case['name']}", False, f"错误: {str(e)}", "工具")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0.0
        self.log(f"工具功能测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    def test_error_handling_comprehensive(self) -> float:
        """综合错误处理测试"""
        if not self.session_id:
            self.log("未建立SSE会话，跳过错误处理测试", "WARNING")
            return 0.0
        
        self.log("开始综合错误处理测试...", "INFO")
        
        error_tests = [
            {
                "name": "不存在的工具",
                "message": {
                    "jsonrpc": "2.0",
                    "id": "error-test-1",
                    "method": "tools/call",
                    "params": {
                        "name": "nonexistent_tool",
                        "arguments": {}
                    }
                },
                "expected_error": True
            },
            {
                "name": "无效的文件路径",
                "message": {
                    "jsonrpc": "2.0",
                    "id": "error-test-2",
                    "method": "tools/call",
                    "params": {
                        "name": "read_xmind_file",
                        "arguments": {"file_path": "/invalid/path/file.xmind"}
                    }
                },
                "expected_error": True
            },
            {
                "name": "缺少必需参数",
                "message": {
                    "jsonrpc": "2.0",
                    "id": "error-test-3",
                    "method": "tools/call",
                    "params": {
                        "name": "create_mind_map",
                        "arguments": {}  # 缺少title参数
                    }
                },
                "expected_error": True
            },
            {
                "name": "空参数",
                "message": {
                    "jsonrpc": "2.0",
                    "id": "error-test-4",
                    "method": "tools/call",
                    "params": {
                        "name": "create_mind_map",
                        "arguments": {"title": "", "topics": []}
                    }
                },
                "expected_error": False  # 应该能处理空值
            },
            {
                "name": "格式错误的JSON-RPC",
                "message": {
                    "jsonrpc": "2.0",
                    "id": "error-test-5",
                    "method": "tools/call"
                    # 缺少params字段
                },
                "expected_error": True
            }
        ]
        
        passed_tests = 0
        total_tests = len(error_tests)
        
        for i, test in enumerate(error_tests):
            try:
                response = self._send_mcp_message(test["message"])
                has_error = "error" in response
                error_code = response.get("error", {}).get("code", "N/A")
                error_message = response.get("error", {}).get("message", "N/A")
                
                # 检查错误处理是否符合预期
                if test["expected_error"]:
                    test_passed = has_error
                    details = f"期望错误，实际: {'有错误' if has_error else '无错误'}"
                else:
                    test_passed = not has_error
                    details = f"期望成功，实际: {'成功' if not has_error else '失败'}"
                
                if has_error:
                    details += f" (错误码: {error_code}, 信息: {error_message})"
                else:
                    details += f" (结果: {response.get('result', {})})"
                
                self.record_result(f"错误处理 - {test['name']}", test_passed, details, "错误处理")
                if test_passed:
                    passed_tests += 1
                    
            except Exception as e:
                self.record_result(f"错误处理 - {test['name']}", False, f"请求异常: {e}", "错误处理")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0.0
        self.log(f"错误处理测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    def test_trae_integration_workflow(self) -> float:
        """Trae集成工作流测试"""
        self.log("开始Trae集成工作流测试...", "INFO")
        
        # 模拟Trae的完整工作流程
        workflow_steps = [
            {
                "name": "基础连接测试",
                "test_func": self._test_trae_connection
            },
            {
                "name": "Trae风格初始化",
                "test_func": self._test_trae_initialization
            },
            {
                "name": "工具列表获取",
                "test_func": self._test_trae_tools_list
            },
            {
                "name": "核心功能验证",
                "test_func": self._test_trae_core_functions
            },
            {
                "name": "性能压力测试",
                "test_func": self._test_trae_performance
            }
        ]
        
        passed_tests = 0
        total_tests = len(workflow_steps)
        
        for step in workflow_steps:
            try:
                success, details = step["test_func"]()
                self.record_result(f"Trae集成 - {step['name']}", success, details, "Trae集成")
                if success:
                    passed_tests += 1
            except Exception as e:
                self.record_result(f"Trae集成 - {step['name']}", False, f"异常: {str(e)}", "Trae集成")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0.0
        self.log(f"Trae集成测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    def _test_trae_connection(self) -> Tuple[bool, str]:
        """测试Trae基础连接"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            success = response.status_code == 200
            return success, f"状态码: {response.status_code}"
        except Exception as e:
            return False, f"连接错误: {str(e)}"
    
    def _test_trae_initialization(self) -> Tuple[bool, str]:
        """测试Trae风格初始化"""
        try:
            # 创建会话
            response = requests.get(f"{self.server_url}/sse", stream=True, timeout=10)
            if response.status_code != 200:
                return False, f"SSE连接失败: {response.status_code}"
            
            session_id = response.headers.get("Session-ID")
            if not session_id:
                return False, "未获取到会话ID"
            
            # Trae风格的初始化消息
            init_message = {
                "jsonrpc": "2.0",
                "id": "trae-init-001",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True},
                        "logging": {}
                    },
                    "clientInfo": {
                        "name": "Trae",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = requests.post(
                f"{self.server_url}/messages/{session_id}",
                json=init_message,
                timeout=10
            )
            
            result = response.json()
            success = "result" in result and "serverInfo" in result["result"]
            return success, "Trae初始化成功" if success else "初始化失败"
            
        except Exception as e:
            return False, f"初始化异常: {str(e)}"
    
    def _test_trae_tools_list(self) -> Tuple[bool, str]:
        """测试Trae工具列表获取"""
        try:
            tools_message = {
                "jsonrpc": "2.0",
                "id": "trae-tools-001",
                "method": "tools/list",
                "params": {}
            }
            
            response = self._send_mcp_message(tools_message)
            tools = response.get("result", {}).get("tools", [])
            success = len(tools) > 0
            
            if success:
                tool_names = [tool["name"] for tool in tools]
                return True, f"发现 {len(tools)} 个工具: {', '.join(tool_names)}"
            else:
                return False, "未找到工具"
                
        except Exception as e:
            return False, f"获取工具列表异常: {str(e)}"
    
    def _test_trae_core_functions(self) -> Tuple[bool, str]:
        """测试Trae核心功能"""
        try:
            # 创建思维导图
            create_message = {
                "jsonrpc": "2.0",
                "id": "trae-create-001",
                "method": "tools/call",
                "params": {
                    "name": "create_mind_map",
                    "arguments": {
                        "title": "Trae测试思维导图",
                        "topics": ["功能1", "功能2", "功能3"]
                    }
                }
            }
            
            response = self._send_mcp_message(create_message)
            create_success = "result" in response
            
            if not create_success:
                return False, "创建思维导图失败"
            
            # 读取思维导图
            read_message = {
                "jsonrpc": "2.0",
                "id": "trae-read-001",
                "method": "tools/call",
                "params": {
                    "name": "read_xmind_file",
                    "arguments": {"file_path": "Trae测试思维导图.xmind"}
                }
            }
            
            response = self._send_mcp_message(read_message)
            read_success = "result" in response
            
            # 分析思维导图
            analyze_message = {
                "jsonrpc": "2.0",
                "id": "trae-analyze-001",
                "method": "tools/call",
                "params": {
                    "name": "analyze_mind_map",
                    "arguments": {"file_path": "Trae测试思维导图.xmind"}
                }
            }
            
            response = self._send_mcp_message(analyze_message)
            analyze_success = "result" in response
            
            total_success = create_success and read_success and analyze_success
            return total_success, f"创建: {'✓' if create_success else '✗'}, 读取: {'✓' if read_success else '✗'}, 分析: {'✓' if analyze_success else '✗'}"
            
        except Exception as e:
            return False, f"核心功能测试异常: {str(e)}"
    
    def _test_trae_performance(self) -> Tuple[bool, str]:
        """测试Trae性能"""
        try:
            start_time = time.time()
            success_count = 0
            total_tests = 10
            
            for i in range(total_tests):
                perf_message = {
                    "jsonrpc": "2.0",
                    "id": f"trae-perf-{i}",
                    "method": "tools/call",
                    "params": {
                        "name": "create_mind_map",
                        "arguments": {
                            "title": f"性能测试{i+1}",
                            "topics": [f"主题{j+1}" for j in range(3)]
                        }
                    }
                }
                
                try:
                    response = self._send_mcp_message(perf_message)
                    if "result" in response:
                        success_count += 1
                except:
                    pass  # 忽略单个失败
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / total_tests
            success_rate = (success_count / total_tests) * 100
            
            success = success_rate >= 80 and avg_time < 2.0  # 80%成功率且平均时间<2秒
            return success, f"成功率: {success_rate:.1f}%, 平均时间: {avg_time:.2f}s"
            
        except Exception as e:
            return False, f"性能测试异常: {str(e)}"
    
    def test_local_server_comprehensive(self) -> float:
        """本地服务器综合测试"""
        self.log("开始本地服务器综合测试...", "INFO")
        
        server_tests = [
            {
                "name": "基础端点测试",
                "test_func": self._test_basic_endpoints
            },
            {
                "name": "SSE端点测试",
                "test_func": self._test_sse_endpoint
            },
            {
                "name": "消息端点测试",
                "test_func": self._test_message_endpoint
            },
            {
                "name": "服务器管理测试",
                "test_func": self._test_server_management
            }
        ]
        
        passed_tests = 0
        total_tests = len(server_tests)
        
        for test in server_tests:
            try:
                success, details = test["test_func"]()
                self.record_result(f"本地服务器 - {test['name']}", success, details, "本地服务器")
                if success:
                    passed_tests += 1
            except Exception as e:
                self.record_result(f"本地服务器 - {test['name']}", False, f"异常: {str(e)}", "本地服务器")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0.0
        self.log(f"本地服务器测试完成，成功率: {success_rate:.1f}%", "INFO")
        return success_rate
    
    def _test_basic_endpoints(self) -> Tuple[bool, str]:
        """测试基础端点"""
        try:
            # 根路径
            response = requests.get(f"{self.server_url}/", timeout=10)
            root_success = response.status_code == 200
            
            # 健康检查
            response = requests.get(f"{self.server_url}/health", timeout=10)
            health_success = response.status_code == 200
            
            # 工具列表
            response = requests.get(f"{self.server_url}/tools", timeout=10)
            tools_success = response.status_code == 200
            
            total_success = root_success and health_success and tools_success
            details = f"根路径: {'✓' if root_success else '✗'}, 健康检查: {'✓' if health_success else '✗'}, 工具列表: {'✓' if tools_success else '✗'}"
            
            return total_success, details
            
        except Exception as e:
            return False, f"基础端点测试异常: {str(e)}"
    
    def _test_sse_endpoint(self) -> Tuple[bool, str]:
        """测试SSE端点"""
        try:
            # 测试SSE连接
            response = requests.get(f"{self.server_url}/sse", stream=True, timeout=10)
            if response.status_code != 200:
                return False, f"SSE连接失败: {response.status_code}"
            
            session_id = response.headers.get("Session-ID")
            if not session_id:
                return False, "未获取到会话ID"
            
            # 测试事件接收
            lines = []
            for line in response.iter_lines():
                if line:
                    lines.append(line.decode('utf-8'))
                    if len(lines) >= 3:  # 接收3个事件
                        break
            
            has_events = len(lines) > 0
            return has_events, f"会话ID: {session_id[:8]}..., 事件数: {len(lines)}"
            
        except Exception as e:
            return False, f"SSE端点测试异常: {str(e)}"
    
    def _test_message_endpoint(self) -> Tuple[bool, str]:
        """测试消息端点"""
        try:
            # 首先创建会话
            response = requests.get(f"{self.server_url}/sse", stream=True, timeout=10)
            if response.status_code != 200:
                return False, "无法创建会话"
            
            session_id = response.headers.get("Session-ID")
            if not session_id:
                return False, "未获取到会话ID"
            
            # 发送初始化消息
            init_message = {
                "jsonrpc": "2.0",
                "id": "local-init-001",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "LocalTest", "version": "1.0.0"}
                }
            }
            
            response = requests.post(
                f"{self.server_url}/messages/{session_id}",
                json=init_message,
                timeout=10
            )
            
            result = response.json()
            success = "result" in result
            
            return success, f"消息发送成功" if success else f"消息发送失败: {response.status_code}"
            
        except Exception as e:
            return False, f"消息端点测试异常: {str(e)}"
    
    def _test_server_management(self) -> Tuple[bool, str]:
        """测试服务器管理功能"""
        try:
            # 测试服务器状态管理
            response = requests.get(f"{self.server_url}/health", timeout=10)
            if response.status_code != 200:
                return False, "服务器健康检查失败"
            
            # 测试会话管理（创建多个会话）
            session_ids = []
            for i in range(3):
                response = requests.get(f"{self.server_url}/sse", stream=True, timeout=10)
                if response.status_code == 200:
                    session_id = response.headers.get("Session-ID")
                    if session_id:
                        session_ids.append(session_id)
            
            success = len(session_ids) >= 2  # 至少成功创建2个会话
            return success, f"成功创建 {len(session_ids)} 个会话"
            
        except Exception as e:
            return False, f"服务器管理测试异常: {str(e)}"
    
    # ==================== 辅助方法 ====================
    
    def _send_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """发送MCP消息"""
        if not self.session_id:
            raise ValueError("会话ID未设置")
            
        response = requests.post(
            f"{self.server_url}/messages/{self.session_id}",
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.json()
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0.0
        
        # 按类别统计
        categories = {}
        for result in self.test_results:
            category = result.get("category", "其他")
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "total": 0}
            
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat()
            },
            "categories": categories,
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(success_rate, categories)
        }
        
        return report
    
    def _generate_recommendations(self, success_rate: float, categories: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if success_rate < 80:
            recommendations.append("🔧 建议检查基础配置和依赖安装")
        
        if "环境" in categories:
            env_rate = (categories["环境"]["passed"] / categories["环境"]["total"]) * 100
            if env_rate < 100:
                recommendations.append("📦 建议安装缺失的依赖包或修复环境配置")
        
        if "服务器" in categories:
            server_rate = (categories["服务器"]["passed"] / categories["服务器"]["total"]) * 100
            if server_rate < 100:
                recommendations.append("🌐 建议检查服务器连接和网络配置")
        
        if "协议" in categories:
            protocol_rate = (categories["协议"]["passed"] / categories["协议"]["total"]) * 100
            if protocol_rate < 100:
                recommendations.append("📋 建议检查MCP协议配置和JSON-RPC格式")
        
        if success_rate >= 95:
            recommendations.append("🎉 系统运行良好，可以开始正式使用！")
        elif success_rate >= 80:
            recommendations.append("✅ 基本功能正常，可以开始使用主要功能")
        
        return recommendations
    
    # ==================== 主测试流程 ====================
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        self.log("🚀 开始统一XMind测试套件...", "INFO")
        self.log(f"测试服务器: {self.server_url}", "INFO")
        
        # 运行各项测试
        env_rate = self.test_environment_setup()
        core_rate = self.test_core_engine_functionality()
        server_rate = self.test_mcp_server_connection()
        protocol_rate = self.test_mcp_protocol_functionality()
        tool_rate = self.test_tool_functionality()
        error_rate = self.test_error_handling_comprehensive()
        trae_rate = self.test_trae_integration_workflow()
        local_rate = self.test_local_server_comprehensive()
        
        # 生成报告
        report = self._generate_test_report()
        
        # 输出总结
        self.log("\n" + "="*60, "INFO")
        self.log("📊 统一测试套件完成总结", "INFO")
        self.log("="*60, "INFO")
        
        summary = report["summary"]
        self.log(f"总测试项: {summary['total_tests']}", "INFO")
        self.log(f"通过项: {summary['passed_tests']}", "INFO")
        self.log(f"失败项: {summary['failed_tests']}", "INFO")
        self.log(f"总成功率: {summary['success_rate']:.1f}%", "INFO")
        
        # 分类统计
        self.log("\n📈 分类测试结果:", "INFO")
        for category, stats in report["categories"].items():
            category_rate = (stats["passed"] / stats["total"]) * 100
            self.log(f"  {category}: {stats['passed']}/{stats['total']} ({category_rate:.1f}%)", "INFO")
        
        # 建议
        if report["recommendations"]:
            self.log("\n💡 建议:", "INFO")
            for rec in report["recommendations"]:
                self.log(f"  {rec}", "INFO")
        
        # 保存报告
        report_file = self.project_root / "tests" / "unified_test_suite" / "test_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n📄 详细报告已保存至: {report_file}", "INFO")
        
        return report


def main():
    """主函数"""
    print("🎯 XMind MCP统一测试套件")
    print("="*60)
    
    # 创建测试器
    tester = UnifiedXMindTester(server_url="https://xmindmcp.onrender.com", use_chinese=True)
    
    # 运行所有测试
    report = tester.run_all_tests()
    
    # 返回适当的退出码
    success_rate = report["summary"]["success_rate"]
    if success_rate >= 90:
        print(f"\n🎉 优秀！系统完全就绪 (成功率: {success_rate:.1f}%)")
        return 0
    elif success_rate >= 70:
        print(f"\n✅ 良好！基本功能正常 (成功率: {success_rate:.1f}%)")
        return 0
    else:
        print(f"\n⚠️ 需要改进！部分功能存在问题 (成功率: {success_rate:.1f}%)")
        return 1


if __name__ == "__main__":
    sys.exit(main())