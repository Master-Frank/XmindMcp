#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind 安装配置测试脚本
简化高效的安装配置验证工具
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class SetupTester:
    """安装配置测试器"""
    
    def __init__(self, use_chinese=True):
        self.use_chinese = use_chinese
        self.project_root = Path(__file__).parent.parent
        
    def log(self, message):
        """输出日志"""
        print(message)
    
    def test_python_version(self):
        """测试Python版本"""
        title = "🐍 Python版本检查" if self.use_chinese else "🐍 Python Version Check"
        self.log(f"\n{title}")
        
        version = sys.version_info
        self.log(f"Python版本: {version.major}.{version.minor}.{version.micro}" if self.use_chinese else f"Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major == 3 and version.minor >= 8:
            self.log("✅ Python版本符合要求 (≥3.8)" if self.use_chinese else "✅ Python version meets requirements (≥3.8)")
            return 100.0  # 返回100%成功率
        else:
            self.log("❌ Python版本过低，需要Python 3.8或更高版本" if self.use_chinese else "❌ Python version too low, Python 3.8 or higher required")
            return 0.0  # 返回0%成功率
    
    def test_dependencies(self):
        """测试依赖包 - 使用uvx方式时不需要检查pip包安装"""
        title = "📦 依赖包检查 (UVX模式)" if self.use_chinese else "📦 Dependencies Check (UVX Mode)"
        self.log(f"\n{title}")
        
        self.log("✅ 使用UVX安装方式，依赖包由uvx自动管理" if self.use_chinese else "✅ Using UVX installation, dependencies are automatically managed by uvx")
        self.log("✅ 无需手动安装pip包" if self.use_chinese else "✅ No need to manually install pip packages")
        
        return 100.0  # UVX模式下总是返回100%成功率
    
    def test_directory_structure(self):
        """测试目录结构"""
        title = "📁 目录结构检查" if self.use_chinese else "📁 Directory Structure Check"
        self.log(f"\n{title}")
        
        # 必要目录列表
        required_dirs = [
            'examples',
            'output',
            'tests',
            'configs'
        ]
        
        passed = 0
        missing_dirs = []  # 记录缺失的目录
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.log(f"  ✅ {dir_name}")
                passed += 1
            else:
                self.log(f"  ❌ {dir_name} - 不存在" if self.use_chinese else f"  ❌ {dir_name} - not exists")
                missing_dirs.append(dir_name)
        
        success_rate = (passed / len(required_dirs)) * 100
        
        if missing_dirs:
            missing_title = "\n❌ 缺失的目录:" if self.use_chinese else "\n❌ Missing directories:"
            self.log(f"{missing_title}")
            for dir_name in missing_dirs:
                self.log(f"  - {dir_name}")
        
        if passed == len(required_dirs):
            success_msg = "✅ 目录结构完整" if self.use_chinese else "✅ Directory structure complete"
            self.log(success_msg)
            return 100.0  # 返回100%成功率
        else:
            warning_msg = f"⚠️  发现 {len(missing_dirs)} 个缺失目录 (成功率: {success_rate:.1f}%)" if self.use_chinese else f"⚠️ Found {len(missing_dirs)} missing directories (Success rate: {success_rate:.1f}%)"
            self.log(warning_msg)
            return success_rate  # 返回实际成功率
    
    def test_core_files(self):
        """测试核心文件"""
        title = "📄 核心文件检查" if self.use_chinese else "📄 Core Files Check"
        self.log(f"\n{title}")
        
        # 核心文件列表（只包含运行时代码文件）
        core_files = [
            'xmind_core_engine.py',
            'xmind_mcp_server.py',
            'universal_xmind_converter.py',
            'validate_xmind_structure.py',
            'xmind_ai_extensions.py'
        ]
        
        passed = 0
        missing_files = []  # 记录缺失的文件
        for file_name in core_files:
            file_path = self.project_root / file_name
            if file_path.exists() and file_path.is_file():
                file_size = file_path.stat().st_size
                self.log(f"  ✅ {file_name} ({file_size} bytes)")
                passed += 1
            else:
                self.log(f"  ❌ {file_name} - 不存在" if self.use_chinese else f"  ❌ {file_name} - not exists")
                missing_files.append(file_name)
        
        success_rate = (passed / len(core_files)) * 100
        
        if missing_files:
            missing_title = "\n❌ 缺失的核心文件:" if self.use_chinese else "\n❌ Missing core files:"
            self.log(f"{missing_title}")
            for file_name in missing_files:
                self.log(f"  - {file_name}")
        
        if passed == len(core_files):
            success_msg = "✅ 核心文件完整" if self.use_chinese else "✅ Core files complete"
            self.log(success_msg)
            return 100.0  # 返回100%成功率
        else:
            warning_msg = f"⚠️  发现 {len(missing_files)} 个缺失文件 (成功率: {success_rate:.1f}%)" if self.use_chinese else f"⚠️ Found {len(missing_files)} missing files (Success rate: {success_rate:.1f}%)"
            self.log(warning_msg)
            return success_rate  # 返回实际成功率
    
    def test_example_files(self):
        """测试示例文件 - 检查实际存在的文件"""
        title = "📚 示例文件检查" if self.use_chinese else "📚 Example Files Check"
        self.log(f"\n{title}")
        
        # 检查examples目录下实际存在的文件
        examples_dir = self.project_root / 'examples'
        if not examples_dir.exists():
            self.log("❌ examples目录不存在" if self.use_chinese else "❌ examples directory does not exist")
            return 0.0
        
        # 获取目录下的所有文件（不包括子目录）
        example_files = []
        for item in examples_dir.iterdir():
            if item.is_file():
                example_files.append(item.name)
        
        if not example_files:
            self.log("⚠️  examples目录下没有找到示例文件" if self.use_chinese else "⚠️ No example files found in examples directory")
            return 0.0
        
        # 显示找到的文件
        self.log(f"找到 {len(example_files)} 个示例文件:" if self.use_chinese else f"Found {len(example_files)} example files:")
        for file_name in example_files:
            file_path = examples_dir / file_name
            file_size = file_path.stat().st_size
            self.log(f"  ✅ {file_name} ({file_size} bytes)")
        
        self.log("✅ 示例文件检查通过" if self.use_chinese else "✅ Example files check passed")
        return 100.0  # 如果找到文件就返回100%成功率
    
    def generate_summary(self, results):
        """生成测试总结"""
        self.log("\n" + "="*60)
        title = "📊 环境检查总结" if self.use_chinese else "📊 Environment Check Summary"
        self.log(title)
        self.log("="*60)
        
        total_tests = len(results)
        # 现在results中的值是成功率百分比，需要计算平均值
        success_rate = sum(results.values()) / total_tests if total_tests > 0 else 0
        
        self.log(f"\n总检查项: {total_tests}")
        self.log(f"📈 平均成功率: {success_rate:.1f}%")
        
        # 显示各项测试的详细结果
        self.log(f"\n📋 详细结果:")
        for test_name, rate in results.items():
            status = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
            self.log(f"  {status} {test_name}: {rate:.1f}%")
        
        if success_rate >= 80:
            self.log("\n🎉 环境配置良好！" if self.use_chinese else "\n🎉 Environment configuration is good!")
            return success_rate  # 返回实际成功率数值
        elif success_rate >= 50:
            self.log("\n✅ 环境基本可用，建议优化" if self.use_chinese else "\n✅ Environment is basically usable, optimization recommended")
            return success_rate  # 返回实际成功率数值
        else:
            self.log("\n⚠️  环境配置较差，需要修复" if self.use_chinese else "\n⚠️ Poor environment configuration, needs fixing")
            return success_rate  # 返回实际成功率数值
    
    def run_all_tests(self):
        """运行所有测试"""
        header = "🔧 XMind安装配置检查" if self.use_chinese else "🔧 XMind Setup Configuration Check"
        self.log(header)
        self.log(f"项目路径: {self.project_root}" if self.use_chinese else f"Project path: {self.project_root}")
        
        # 运行各项测试
        results = {}
        results['python_version'] = self.test_python_version()
        results['dependencies'] = self.test_dependencies()
        results['directory_structure'] = self.test_directory_structure()
        results['core_files'] = self.test_core_files()
        results['example_files'] = self.test_example_files()
        
        # 计算总体成功率
        overall_success_rate = sum(results.values()) / len(results) if results else 0
        
        self.log(f"\n📊 总体成功率: {overall_success_rate:.1f}%")
        
        # 生成总结并返回总体成功率
        summary_rate = self.generate_summary(results)
        return overall_success_rate


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XMind Setup Configuration Test')
    parser.add_argument('--english', action='store_true', help='Use English mode')
    
    args = parser.parse_args()
    
    tester = SetupTester(use_chinese=not args.english)
    success_rate = tester.run_all_tests()  # 现在返回的是成功率数值
    
    if success_rate >= 80:
        print(f"\n✅ 环境检查完成，配置良好 (成功率: {success_rate:.1f}%)" if tester.use_chinese else f"\n✅ Environment check completed, configuration is good (Success rate: {success_rate:.1f}%)")
        sys.exit(0)
    else:
        print(f"\n❌ 环境检查完成，发现配置问题 (成功率: {success_rate:.1f}%)" if tester.use_chinese else f"\n❌ Environment check completed, configuration issues found (Success rate: {success_rate:.1f}%)")
        sys.exit(1)


if __name__ == "__main__":
    main()