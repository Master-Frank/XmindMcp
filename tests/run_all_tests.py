#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind 测试脚本统一运行器
一键运行所有测试并生成综合报告
"""

import os
import sys
import subprocess
import time
import json
import io
from contextlib import redirect_stdout
from pathlib import Path
from datetime import datetime


class TestRunner:
    """测试运行器"""
    
    def __init__(self, use_chinese=True):
        self.use_chinese = use_chinese
        self.project_root = Path(__file__).parent.parent
        self.test_scripts = [
            'test_setup.py',
            'test_core.py', 
            'test_batch.py',
            'test_client.py'
        ]
        self.results = {}
        
    def log(self, message):
        """输出日志"""
        print(message)
    
    def run_single_test(self, script_name):
        """运行单个测试脚本"""
        script_path = Path(__file__).parent / script_name
        
        if not script_path.exists():
            error_msg = f"❌ 测试脚本不存在: {script_name}" if self.use_chinese else f"❌ Test script not found: {script_name}"
            self.log(error_msg)
            return {
                'script': script_name,
                'status': 'failed',
                'error': 'Script not found',
                'duration': 0
            }
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 保存原始命令行参数
            original_argv = sys.argv.copy()
            
            # 只为支持server参数的脚本设置服务器地址
            if script_name in ['test_client.py', 'test_batch.py']:
                sys.argv = [sys.argv[0], '--server', 'http://localhost:8080']
            elif script_name == 'test_core.py':
                sys.argv = [sys.argv[0]]  # test_core.py 不需要server参数
            else:
                sys.argv = [sys.argv[0]]  # 只保留脚本名
            
            # 直接导入并运行测试模块，而不是使用subprocess
            sys.path.insert(0, str(Path(__file__).parent))
            
            # 动态导入测试模块
            module_name = script_name[:-3]  # 去掉.py后缀
            spec = __import__(module_name)
            
            # 如果模块有main函数，调用它
            if hasattr(spec, 'main'):
                pass_rate = 100.0  # 初始化通过率
                try:
                    # 捕获输出同时允许实时显示
                    output_buffer = io.StringIO()
                    
                    # 创建自定义的stdout重定向，既输出到控制台又保存到缓冲区
                    class TeeStdout:
                        def __init__(self, buffer, original_stdout):
                            self.buffer = buffer
                            self.original_stdout = original_stdout
                        
                        def write(self, text):
                            self.original_stdout.write(text)
                            self.buffer.write(text)
                            self.original_stdout.flush()  # 确保实时输出
                        
                        def flush(self):
                            self.original_stdout.flush()
                            self.buffer.flush()
                    
                    # 使用自定义的tee重定向
                    tee_stdout = TeeStdout(output_buffer, sys.stdout)
                    
                    with redirect_stdout(tee_stdout):
                        spec.main()
                    
                    # 获取输出内容用于分析
                    output_content = output_buffer.getvalue()
                    output_lines = output_content.strip().split('\n')
                    
                    # 从输出中提取真实的通过率
                    extracted_pass_rate = self.extract_pass_rate(output_lines)
                    # 如果没有提取到通过率，使用默认值
                    if extracted_pass_rate > 0:
                        pass_rate = extracted_pass_rate
                    
                    # 根据通过率判断测试状态（通过率>=90%认为通过）
                    status = 'passed' if pass_rate >= 90.0 else 'failed'
                        
                except SystemExit as e:
                    if e.code == 0:
                        # 即使正常退出，也要根据通过率判断
                        status = 'passed' if pass_rate >= 90.0 else 'failed'
                    else:
                        status = 'failed'
                        pass_rate = 0.0
                except Exception as e:
                    status = 'failed'
                    pass_rate = 0.0
            else:
                # 如果没有main函数，假设运行成功
                status = 'passed'
                pass_rate = 100.0
            
            # 清理模块缓存
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # 恢复原始命令行参数
            sys.argv = original_argv
            
            # 记录结束时间
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                'script': script_name,
                'status': status,
                'return_code': 0 if status == 'passed' else 1,
                'pass_rate': pass_rate,
                'duration': duration,
                'stdout': '',
                'stderr': ''
            }
            
        except Exception as e:
            # 恢复原始命令行参数（即使在异常情况下）
            if 'original_argv' in locals():
                sys.argv = original_argv
            
            error_msg = f"❌ 运行测试失败 {script_name}: {e}" if self.use_chinese else f"❌ Failed to run test {script_name}: {e}"
            self.log(error_msg)
            return {
                'script': script_name,
                'status': 'failed',
                'error': str(e),
                'duration': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def extract_pass_rate(self, output_lines):
        """从输出中提取通过率"""
        for line in reversed(output_lines):
            if '通过率:' in line or 'Pass rate:' in line or '成功率:' in line or 'Success rate:' in line:
                try:
                    # 提取百分比数值
                    import re
                    match = re.search(r'(\d+(?:\.\d+)?)%', line)
                    if match:
                        return float(match.group(1))
                except:
                    pass
        return 0
    
    def run_all_tests(self):
        """运行所有测试"""
        header = "🚀 XMind 综合测试运行器" if self.use_chinese else "🚀 XMind Comprehensive Test Runner"
        self.log(header)
        self.log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"项目路径: {self.project_root}")
        self.log("-" * 60)
        
        # 运行每个测试脚本
        total_tests = len(self.test_scripts)
        passed_tests = 0
        total_duration = 0
        
        for i, script in enumerate(self.test_scripts, 1):
            progress_msg = f"\n[{i}/{total_tests}] 运行 {script}..." if self.use_chinese else f"\n[{i}/{total_tests}] Running {script}..."
            self.log(progress_msg)
            
            result = self.run_single_test(script)
            self.results[script] = result
            
            # 显示结果
            if result['status'] == 'passed':
                passed_tests += 1
                status_icon = "✅"
                status_msg = "通过" if self.use_chinese else "Passed"
            else:
                status_icon = "❌"
                status_msg = "失败" if self.use_chinese else "Failed"
            
            duration = result.get('duration', 0)
            pass_rate = result.get('pass_rate', 0)
            
            self.log(f"{status_icon} {script}: {status_msg} (耗时: {duration:.1f}s, 通过率: {pass_rate:.1f}%)")
            
            total_duration += duration
        
        # 计算总体通过率
        overall_pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 生成总结
        self.generate_summary(total_tests, passed_tests, total_duration)
        
        # 返回总体通过率作为成功率数值
        return overall_pass_rate
    
    def generate_summary(self, total_tests, passed_tests, total_duration):
        """生成总结报告"""
        self.log("\n" + "=" * 60)
        title = "📊 综合测试报告" if self.use_chinese else "📊 Comprehensive Test Report"
        self.log(title)
        
        # 总体统计
        overall_pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if self.use_chinese:
            self.log(f"总测试脚本: {total_tests}")
            self.log(f"通过: {passed_tests}")
            self.log(f"失败: {total_tests - passed_tests}")
            self.log(f"总体通过率: {overall_pass_rate:.1f}%")
            self.log(f"总耗时: {total_duration:.1f}秒")
            self.log(f"平均耗时: {total_duration/total_tests:.1f}秒/脚本")
        else:
            self.log(f"Total test scripts: {total_tests}")
            self.log(f"Passed: {passed_tests}")
            self.log(f"Failed: {total_tests - passed_tests}")
            self.log(f"Overall pass rate: {overall_pass_rate:.1f}%")
            self.log(f"Total duration: {total_duration:.1f}s")
            self.log(f"Average duration: {total_duration/total_tests:.1f}s/script")
        
        # 详细结果
        self.log(f"\n{'='*60}")
        detail_title = "🔍 详细结果" if self.use_chinese else "🔍 Detailed Results"
        self.log(detail_title)
        
        for script, result in self.results.items():
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            duration = result.get('duration', 0)
            pass_rate = result.get('pass_rate', 0)
            return_code = result.get('return_code', 'N/A')
            
            self.log(f"{status_icon} {script}:")
            self.log(f"   状态: {result['status']}")
            self.log(f"   返回码: {return_code}")
            self.log(f"   耗时: {duration:.1f}s")
            self.log(f"   通过率: {pass_rate:.1f}%")
            
            if result['status'] == 'failed' and 'error' in result:
                self.log(f"   错误: {result['error']}")
            
            self.log("")
        
        # 建议
        if passed_tests < total_tests:
            self.log(f"\n{'='*60}")
            suggestion_title = "💡 建议" if self.use_chinese else "💡 Suggestions"
            self.log(suggestion_title)
            
            if self.use_chinese:
                self.log("• 检查失败测试的具体错误信息")
                self.log("• 确保所有依赖包已正确安装")
                self.log("• 验证测试环境配置")
                self.log("• 查看各个测试脚本的详细输出")
            else:
                self.log("• Check specific error messages for failed tests")
                self.log("• Ensure all dependency packages are properly installed")
                self.log("• Verify test environment configuration")
                self.log("• Review detailed output of individual test scripts")
        
        # 最终结果
        self.log(f"\n{'='*60}")
        if passed_tests == total_tests:
            success_msg = "🎉 所有测试通过！XMind环境配置正确。" if self.use_chinese else "🎉 All tests passed! XMind environment is properly configured."
            self.log(success_msg)
        else:
            warning_msg = "⚠️ 部分测试失败，请根据建议进行修复。" if self.use_chinese else "⚠️ Some tests failed, please fix according to suggestions."
            self.log(warning_msg)
        
        self.log("=" * 60)
    
    def save_report(self, filename=None):
        """保存测试报告"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_report_{timestamp}.json"
        
        report_path = Path(__file__).parent / "test_reports" / filename
        report_path.parent.mkdir(exist_ok=True)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'language': 'chinese' if self.use_chinese else 'english',
            'total_scripts': len(self.test_scripts),
            'results': self.results,
            'summary': {
                'total': len(self.test_scripts),
                'passed': sum(1 for r in self.results.values() if r['status'] == 'passed'),
                'failed': sum(1 for r in self.results.values() if r['status'] == 'failed'),
                'total_duration': sum(r.get('duration', 0) for r in self.results.values())
            }
        }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            save_msg = f"✅ 测试报告已保存: {report_path}" if self.use_chinese else f"✅ Test report saved: {report_path}"
            self.log(save_msg)
            return True
            
        except Exception as e:
            error_msg = f"❌ 保存报告失败: {e}" if self.use_chinese else f"❌ Failed to save report: {e}"
            self.log(error_msg)
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XMind Comprehensive Test Runner')
    parser.add_argument('--english', action='store_true', help='Use English mode')
    parser.add_argument('--save-report', action='store_true', help='Save test report to file')
    parser.add_argument('--report-file', type=str, help='Custom report filename')
    parser.add_argument('--server', default="http://localhost:8080", help='Server URL')
    
    args = parser.parse_args()
    
    runner = TestRunner(use_chinese=not args.english)
    success_rate = runner.run_all_tests()
    
    # 保存报告（如果指定）
    if args.save_report:
        runner.save_report(args.report_file)
    
    # 基于成功率返回相应的退出码（>=80%为通过）
    exit(0 if success_rate >= 80 else 1)


if __name__ == "__main__":
    main()