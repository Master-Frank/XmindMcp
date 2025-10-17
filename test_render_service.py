#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render服务测试脚本
在Render部署完成后运行统一测试套件
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def check_render_service(url="https://xmindmcp.onrender.com", max_retries=30, retry_delay=10):
    """检查Render服务是否就绪"""
    print(f"🔍 检查Render服务状态: {url}")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ Render服务已启动! (尝试 {i+1}/{max_retries})")
                return True
            else:
                print(f"⏳ 服务返回状态码 {response.status_code}，等待 {retry_delay} 秒后重试...")
        except requests.exceptions.RequestException as e:
            print(f"⏳ 服务未就绪: {str(e)[:50]}...，等待 {retry_delay} 秒后重试...")
        
        time.sleep(retry_delay)
    
    print(f"❌ Render服务在 {max_retries * retry_delay} 秒内未能启动")
    return False

def run_unified_tests(server_url):
    """运行统一测试套件"""
    print(f"🚀 开始运行统一测试套件...")
    print(f"🌐 测试服务器: {server_url}")
    
    # 设置环境变量
    env = os.environ.copy()
    env['RENDER_SERVICE_URL'] = server_url
    
    # 切换到测试目录
    test_dir = Path(__file__).parent / "tests" / "unified_test_suite"
    os.chdir(test_dir)
    
    try:
        # 运行测试
        result = subprocess.run([
            sys.executable, "mcp_test.py"
        ], env=env, capture_output=True, text=True)
        
        print("=" * 60)
        print("📋 测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  错误输出:")
            print(result.stderr)
        
        print("=" * 60)
        
        # 检查测试报告
        report_file = test_dir / "test_report.json"
        if report_file.exists():
            print(f"✅ 测试报告已生成: {report_file}")
            
            # 读取并显示摘要
            import json
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            summary = report.get('summary', {})
            total_tests = summary.get('total_tests', 0)
            passed_tests = summary.get('passed_tests', 0)
            success_rate = summary.get('success_rate', 0)
            
            print(f"📊 测试摘要:")
            print(f"   总测试数: {total_tests}")
            print(f"   通过测试: {passed_tests}")
            print(f"   成功率: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print(f"🎉 测试通过! 成功率达到 {success_rate:.1f}%")
                return True
            else:
                print(f"⚠️  测试完成，但成功率较低: {success_rate:.1f}%")
                return False
        else:
            print("❌ 未找到测试报告文件")
            return False
            
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False
    finally:
        # 恢复原始目录
        os.chdir(Path(__file__).parent)

def main():
    """主函数"""
    print("🎯 Render服务统一测试套件")
    print("=" * 50)
    
    # 服务URL
    server_url = os.environ.get('RENDER_SERVICE_URL', 'https://xmindmcp.onrender.com')
    
    # 步骤1: 检查服务状态
    print("\n📍 步骤1: 检查Render服务状态")
    if not check_render_service(server_url):
        print("\n❌ Render服务检查失败，请确认服务已部署并运行")
        return 1
    
    # 步骤2: 运行统一测试
    print(f"\n📍 步骤2: 运行统一测试套件")
    success = run_unified_tests(server_url)
    
    # 步骤3: 结果总结
    print(f"\n📍 步骤3: 测试结果总结")
    if success:
        print("✅ 所有测试完成并通过!")
        print("🌟 Render服务已准备就绪，可以开始使用!")
        return 0
    else:
        print("⚠️  测试完成，但部分测试未通过")
        print("🔧 请检查测试报告了解详细信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())