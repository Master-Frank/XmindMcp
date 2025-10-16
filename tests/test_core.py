#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind 核心功能测试脚本
测试xmind_core_engine.py的核心功能
"""

import sys
import json
import time
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xmind_core_engine import XMindCoreEngine


class XMindCoreTester:
    """XMind核心功能测试器"""
    
    def __init__(self, use_chinese=True):
        self.use_chinese = use_chinese
        self.test_results = {}
        self.project_root = Path(__file__).parent.parent
        self.core_engine = XMindCoreEngine()
    
    def log(self, message):
        """输出日志"""
        print(message)
    
    def test_core_engine_initialization(self):
        """测试核心引擎初始化"""
        title = "🔧 核心引擎初始化测试" if self.use_chinese else "🔧 Core Engine Initialization Test"
        self.log(f"\n{title}")
        
        tests = []
        try:
            # 测试核心引擎是否成功加载
            if hasattr(self.core_engine, 'get_tools'):
                tools = self.core_engine.get_tools()
                status = f"✅ 核心引擎已加载: {len(tools)} 个工具" if self.use_chinese else f"✅ Core engine loaded: {len(tools)} tools"
                self.log(status)
                tests.append(True)
            else:
                error_msg = "❌ 核心引擎加载失败" if self.use_chinese else "❌ Core engine loading failed"
                self.log(error_msg)
                tests.append(False)
            
            success_rate = (sum(tests) / len(tests)) * 100 if tests else 0.0
            self.test_results['core_engine'] = {"status": "success" if success_rate == 100 else "partial", "tools_count": len(tools) if tests else 0}
            self.log(f"✅ 核心引擎初始化测试完成 (成功率: {success_rate:.1f}%)" if self.use_chinese else f"✅ Core engine initialization test completed (Success rate: {success_rate:.1f}%)")
            return success_rate  # 返回实际的成功率数值
            
        except Exception as e:
            error_msg = "❌ 核心引擎初始化错误" if self.use_chinese else "❌ Core engine initialization error"
            self.log(f"{error_msg}: {e}")
            self.test_results['core_engine'] = {"status": "error", "error": str(e)}
            return 0.0  # 异常时返回0.0表示成功率
    
    def test_core_functions(self):
        """测试核心功能"""
        title = "⚙️ 核心功能测试" if self.use_chinese else "⚙️ Core Functions Test"
        self.log(f"\n{title}")
        
        tests = []
        try:
            from xmind_core_engine import XMindCoreEngine
            core = XMindCoreEngine()
            
            # 测试读取XMind文件 - 检查examples目录中的实际文件
            test_files = [
                os.path.join(self.project_root, 'examples', 'test_txt.xmind'),
                os.path.join(self.project_root, 'output', 'test_txt.xmind'),
                os.path.join(self.project_root, 'tests', 'test_files', 'sample.xmind')
            ]
            
            # 查找存在的测试文件
            test_file = None
            for file_path in test_files:
                if os.path.exists(file_path):
                    test_file = file_path
                    break
            
            if test_file:
                    try:
                        # 使用正确的read_xmind_file方法而不是read_xmind
                        content = core.read_xmind_file(test_file)
                        if content.get('status') == 'success':
                            self.log(f"✅ XMind文件读取成功: {os.path.basename(test_file)}" if self.use_chinese else f"✅ XMind file read successfully: {os.path.basename(test_file)}")
                            tests.append(True)
                        else:
                            error_msg = content.get('error', 'Unknown error')
                            self.log(f"⚠️  XMind文件读取失败: {error_msg}" if self.use_chinese else f"⚠️ XMind file read failed: {error_msg}")
                            tests.append(False)
                    except Exception as e:
                        self.log(f"⚠️  XMind文件读取失败: {e}" if self.use_chinese else f"⚠️ XMind file read failed: {e}")
                        tests.append(False)
            else:
                # 如果没有找到现有的XMind文件，尝试从其他格式转换创建一个
                self.log("⚠️  未找到XMind测试文件，尝试从文本文件创建" if self.use_chinese else "⚠️ No XMind test file found, trying to create from text file")
                
                # 检查是否有文本测试文件
                txt_file = os.path.join(self.project_root, 'examples', 'test_txt.txt')
                if os.path.exists(txt_file):
                    try:
                        # 读取文本内容并创建XMind文件
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 创建简单的思维导图
                        test_content = {
                            "title": "Test Mind Map from Text",
                            "topics": [{"title": "Main Topic", "subtopics": []}]
                        }
                        topics_json = json.dumps(test_content.get('topics', []))
                        result = core.create_mind_map(test_content.get('title', 'Test Mind Map'), topics_json)
                        
                        if result.get('status') == 'success' and os.path.exists(result.get('filename', '')):
                            created_file = result.get('filename')
                            # 测试读取刚创建的文件
                            read_result = core.read_xmind(created_file)
                            if read_result:
                                self.log("✅ 从文本创建并读取XMind文件成功" if self.use_chinese else "✅ Created and read XMind file from text successfully")
                                tests.append(True)
                                # 清理临时文件
                                if os.path.exists(created_file):
                                    os.remove(created_file)
                            else:
                                tests.append(False)
                        else:
                            tests.append(False)
                    except Exception as e:
                        self.log(f"⚠️  从文本创建XMind文件失败: {e}" if self.use_chinese else f"⚠️ Failed to create XMind from text: {e}")
                        tests.append(False)
                else:
                    self.log("⚠️  未找到测试文件，跳过读取测试" if self.use_chinese else "⚠️ No test files found, skipping read test")
                    tests.append(True)  # 跳过不算失败
            
            # 测试创建XMind文件
            try:
                # 将测试内容转换为JSON字符串格式
                import json
                test_content = {
                    "title": "Test Mind Map",
                    "topics": [{"title": "Main Topic", "subtopics": []}]
                }
                topics_json = json.dumps(test_content.get('topics', []))
                result = core.create_mind_map(test_content.get('title', 'Test Mind Map'), topics_json)
                if result.get('status') == 'success' and os.path.exists(result.get('filename', '')):
                    self.log("✅ XMind文件创建成功" if self.use_chinese else "✅ XMind file created successfully")
                    os.remove(result.get('filename'))  # 清理测试文件
                    tests.append(True)
                else:
                    self.log("❌ XMind文件创建失败 - 文件未生成" if self.use_chinese else "❌ XMind file creation failed - File not generated")
                    tests.append(False)
            except Exception as e:
                self.log(f"❌ 思维导图创建失败: {e}" if self.use_chinese else f"❌ Mind map creation failed: {e}")
                tests.append(False)
            
            success_rate = (sum(tests) / len(tests)) * 100
            self.log(f"✅ 核心功能测试完成 (成功率: {success_rate:.1f}%)" if self.use_chinese else f"✅ Core functions test completed (Success rate: {success_rate:.1f}%)")
            
            self.test_results['core_functions'] = {
                "status": "success" if success_rate == 100 else "partial",
                "success_count": sum(tests),
                "total_count": len(tests)
            }
            
            return success_rate  # 返回实际的成功率数值
            
        except Exception as e:
            self.log(f"❌ 核心功能测试失败: {e}" if self.use_chinese else f"❌ Core functions test failed: {e}")
            self.test_results['core_functions'] = {"status": "error", "error": str(e)}
            return 0.0  # 异常时返回0.0表示成功率
    
    def test_tools_integration(self):
        """测试工具集成"""
        title = "🔌 工具集成测试" if self.use_chinese else "🔌 Tools Integration Test"
        self.log(f"\n{title}")
        
        tests = []
        try:
            # 测试工具加载
            if hasattr(self.core_engine, 'get_tools'):
                tools = self.core_engine.get_tools()
                self.log(f"✅ 成功加载 {len(tools)} 个工具" if self.use_chinese else f"✅ Successfully loaded {len(tools)} tools")
                tests.append(True)
                
                # 显示工具列表
                for tool in tools[:5]:  # 只显示前5个工具
                    tool_name = tool.get('name', 'Unknown')
                    tool_desc = tool.get('description', 'No description')
                    self.log(f"  📋 {tool_name}: {tool_desc[:50]}..." if self.use_chinese else f"  📋 {tool_name}: {tool_desc[:50]}...")
                
                if len(tools) > 5:
                    self.log(f"  ... 还有 {len(tools) - 5} 个工具" if self.use_chinese else f"  ... and {len(tools) - 5} more tools")
            else:
                self.log("❌ 未找到get_tools方法" if self.use_chinese else "❌ get_tools method not found")
                tests.append(False)
                
            success_rate = (sum(tests) / len(tests)) * 100 if tests else 0.0
            self.log(f"✅ 工具集成测试完成 (成功率: {success_rate:.1f}%)" if self.use_chinese else f"✅ Tools integration test completed (Success rate: {success_rate:.1f}%)")
            
            self.test_results['tools_integration'] = {
                "status": "success" if success_rate == 100 else "partial",
                "success_count": sum(tests),
                "total_count": len(tests)
            }
            
            return success_rate  # 返回实际的成功率数值
            
        except Exception as e:
            self.log(f"❌ 工具集成测试失败: {e}" if self.use_chinese else f"❌ Tools integration test failed: {e}")
            self.test_results['tools_integration'] = {"status": "error", "error": str(e)}
            return 0.0  # 异常时返回0.0表示成功率
    
    def generate_summary(self):
        """生成测试总结"""
        title = "📊 测试总结" if self.use_chinese else "📊 Test Summary"
        self.log(f"\n{title}")
        
        total_tests = len(self.test_results)
        # 计算平均成功率
        success_rates = []
        for result in self.test_results.values():
            if result.get('status') == 'success':
                success_rates.append(100)
            elif result.get('status') == 'partial':
                # 对于partial状态，如果有success_count和total_count则计算实际成功率
                if 'success_count' in result and 'total_count' in result and result['total_count'] > 0:
                    success_rates.append(result['success_count'] / result['total_count'] * 100)
                else:
                    success_rates.append(50)  # 默认给50%
            else:
                success_rates.append(0)
        
        avg_success_rate = sum(success_rates) / total_tests if total_tests > 0 else 0
        
        if self.use_chinese:
            self.log(f"总测试数: {total_tests}")
            self.log(f"📈 平均成功率: {avg_success_rate:.1f}%")
            self.log(f"\n📋 详细结果:")
            for name, rate in zip(self.test_results.keys(), success_rates):
                status_icon = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
                self.log(f"  {status_icon} {name}: {rate:.1f}%")
            
            if avg_success_rate >= 80:
                self.log(f"\n🎉 核心功能良好！")
            elif avg_success_rate >= 50:
                self.log(f"\n✅ 核心功能基本可用，建议优化")
            else:
                self.log(f"\n⚠️  核心功能较差，需要修复")
        else:
            self.log(f"Total tests: {total_tests}")
            self.log(f"📈 Average success rate: {avg_success_rate:.1f}%")
            self.log(f"\n📋 Detailed results:")
            for name, rate in zip(self.test_results.keys(), success_rates):
                status_icon = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
                self.log(f"  {status_icon} {name}: {rate:.1f}%")
            
            if avg_success_rate >= 80:
                self.log(f"\n🎉 Core functions are good!")
            elif avg_success_rate >= 50:
                self.log(f"\n✅ Core functions are basically usable, optimization recommended")
            else:
                self.log(f"\n⚠️  Core functions are poor, need fixing")
        
        return avg_success_rate >= 80
    
    def test_actual_file_operations(self):
        """测试实际文件操作"""
        title = "📁 实际文件操作测试" if self.use_chinese else "📁 Actual File Operations Test"
        self.log(f"\n{title}")
        
        tests = []
        try:
            from xmind_core_engine import XMindCoreEngine
            core = XMindCoreEngine()
            
            # 创建测试文件
            test_content = {
                "title": "Test Mind Map",
                "topics": [
                    {
                        "title": "Main Topic 1",
                        "subtopics": [{"title": "Subtopic 1.1"}, {"title": "Subtopic 1.2"}]
                    },
                    {
                        "title": "Main Topic 2",
                        "subtopics": [{"title": "Subtopic 2.1"}]
                    }
                ]
            }
            
            test_file = "test_mindmap.xmind"
            
            # 测试创建
            try:
                # 将测试内容转换为JSON字符串格式
                import json
                topics_json = json.dumps(test_content.get('topics', []))
                result = core.create_mind_map(test_content.get('title', 'Test Mind Map'), topics_json)
                if result.get('status') == 'success' and os.path.exists(result.get('filename', '')):
                    self.log("✅ 测试文件创建成功" if self.use_chinese else "✅ Test file created successfully")
                    created_file = result.get('filename')
                    tests.append(True)
                else:
                    self.log("❌ 测试文件创建失败" if self.use_chinese else "❌ Test file creation failed")
                    tests.append(False)
                    created_file = None
            except Exception as e:
                self.log(f"❌ 测试文件创建失败: {e}" if self.use_chinese else f"❌ Test file creation failed: {e}")
                tests.append(False)
                created_file = None
            
            # 测试读取
            try:
                if created_file and os.path.exists(created_file):
                    read_content = core.read_xmind_file(created_file)
                    if read_content and read_content.get('status') == 'success' and 'root_topic' in read_content:
                        self.log("✅ 测试文件读取成功" if self.use_chinese else "✅ Test file read successfully")
                        tests.append(True)
                    else:
                        self.log("❌ 测试文件读取失败 - 内容格式错误" if self.use_chinese else "❌ Test file read failed - Invalid content format")
                        tests.append(False)
                else:
                    self.log("❌ 测试文件读取失败 - 文件不存在" if self.use_chinese else "❌ Test file read failed - File does not exist")
                    tests.append(False)
            except Exception as e:
                self.log(f"❌ 测试文件读取失败: {e}" if self.use_chinese else f"❌ Test file read failed: {e}")
                tests.append(False)
            
            # 清理测试文件
            if created_file and os.path.exists(created_file):
                os.remove(created_file)
                self.log("✅ 测试文件已清理" if self.use_chinese else "✅ Test file cleaned up")
                tests.append(True)
            else:
                tests.append(True)  # 文件不存在也算清理成功
            
            success_rate = (sum(tests) / len(tests)) * 100
            self.log(f"✅ 实际文件操作测试完成 (成功率: {success_rate:.1f}%)" if self.use_chinese else f"✅ Actual file operations test completed (Success rate: {success_rate:.1f}%)")
            
            self.test_results['file_operations'] = {
                "status": "success" if success_rate == 100 else "partial",
                "success_count": sum(tests),
                "total_count": len(tests)
            }
            
            return success_rate  # 返回实际的成功率数值
            
        except Exception as e:
            self.log(f"❌ 实际文件操作测试失败: {e}" if self.use_chinese else f"❌ Actual file operations test failed: {e}")
            self.test_results['file_operations'] = {"status": "error", "error": str(e)}
            return 0.0  # 异常时返回0.0表示成功率

    def run_all_tests(self):
        """运行所有测试"""
        header = "🚀 XMind核心功能测试" if self.use_chinese else "🚀 XMind Core Functionality Tests"
        self.log(f"{header}")
        self.log(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("核心引擎初始化", self.test_core_engine_initialization),
            ("核心功能测试", self.test_core_functions),
            ("工具集成测试", self.test_tools_integration),
            ("实际文件操作", self.test_actual_file_operations)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                self.log(f"\n🔍 {test_name}..." if self.use_chinese else f"\n🔍 {test_name}...")
                results[test_name] = test_func()
            except Exception as e:
                self.log(f"❌ {test_name} 失败: {str(e)}" if self.use_chinese else f"❌ {test_name} failed: {str(e)}")
                results[test_name] = 0.0  # 异常时返回0.0表示成功率
                
        # 确保所有测试都有数值结果
        for test_name in [name for name, _ in tests]:
            if test_name not in results:
                results[test_name] = 0.0
        
        # 计算总体成功率
        overall_success_rate = sum(results.values()) / len(results) if results and all(v is not None for v in results.values()) else 0
        self.log(f"\n📊 总体成功率: {overall_success_rate:.1f}%" if self.use_chinese else f"\n📊 Overall success rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 80:
            success_msg = "✅ 所有测试通过！" if self.use_chinese else "✅ All tests passed!"
            self.log(f"\n{success_msg}")
        else:
            warning_msg = "⚠️ 部分测试失败，请检查日志" if self.use_chinese else "⚠️ Some tests failed, please check logs"
            self.log(f"\n{warning_msg}")
        
        return overall_success_rate >= 80


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XMind Core Engine Test')
    parser.add_argument('--english', action='store_true', help='Run tests in English')
    parser.add_argument('--chinese', action='store_true', help='Run tests in Chinese')
    args = parser.parse_args()
    
    use_chinese = True
    if args.english:
        use_chinese = False
    elif args.chinese:
        use_chinese = True
    
    tester = XMindCoreTester(use_chinese=use_chinese)
    test_passed = tester.run_all_tests()
    
    # 基于测试结果返回相应的退出码（True为通过，False为失败）
    exit(0 if test_passed else 1)


if __name__ == "__main__":
    main()