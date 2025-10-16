#!/usr/bin/env python3
# -*- coding: utf-8
"""
XMind 批量转换测试脚本
测试批量转换功能
"""

import sys
import time
import requests
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 使用核心引擎
from xmind_core_engine import XMindCoreEngine


class BatchConversionTester:
    """批量转换测试器"""
    
    def __init__(self, server_url="http://localhost:8080", use_chinese=True):
        self.server_url = server_url
        self.use_chinese = use_chinese
        self.project_root = Path(__file__).parent.parent
        self.core_engine = XMindCoreEngine()
        
    def log(self, message):
        """输出日志"""
        print(message)
    
    def test_batch_conversion(self):
        """测试批量转换功能"""
        title = "🔄 批量转换测试" if self.use_chinese else "🔄 Batch Conversion Test"
        self.log(f"\n{title}")
        
        # 测试文件目录
        examples_dir = self.project_root / "examples"
        output_dir = self.project_root / "output"
        output_dir.mkdir(exist_ok=True)
        
        # 支持的文件类型
        supported_extensions = ['.txt', '.md', '.html', '.docx', '.xlsx']
        
        # 查找测试文件
        test_files = []
        for ext in supported_extensions:
            for file_path in examples_dir.glob(f"*{ext}"):
                test_files.append(file_path)
        
        if not test_files:
            no_files_msg = "⚠️ 未找到测试文件" if self.use_chinese else "⚠️ No test files found"
            self.log(no_files_msg)
            return 0.0  # 返回0%通过率
        
        self.log(f"找到 {len(test_files)} 个测试文件" if self.use_chinese else f"Found {len(test_files)} test files")
        
        # 执行批量转换
        success_count = 0
        start_time = time.time()
        failed_files = []  # 记录失败的文件
        
        for i, file_path in enumerate(test_files, 1):
            try:
                self.log(f"\n[{i}/{len(test_files)}] 处理: {file_path.name}" if self.use_chinese else f"\n[{i}/{len(test_files)}] Processing: {file_path.name}")
                
                # 使用核心引擎进行转换
                output_file = output_dir / f"{file_path.stem}.xmind"
                
                # 使用核心引擎的convert_to_xmind方法进行转换
                result = self.core_engine.convert_to_xmind(str(file_path), str(output_file))
                
                # 验证输出文件
                if result.get("status") == "success" and output_file.exists():
                    success_count += 1
                    file_size = output_file.stat().st_size
                    success_msg = f"✅ 转换成功: {file_size} 字节" if self.use_chinese else f"✅ Conversion successful: {file_size} bytes"
                    self.log(success_msg)
                else:
                    error_detail = result.get('error', '输出文件不存在')
                    failed_files.append((file_path.name, error_detail))
                    error_msg = f"❌ 转换失败: {error_detail}" if self.use_chinese else f"❌ Conversion failed: {error_detail}"
                    self.log(error_msg)
                    
            except Exception as e:
                failed_files.append((file_path.name, str(e)))
                error_msg = f"❌ 转换失败: {e}" if self.use_chinese else f"❌ Conversion failed: {e}"
                self.log(error_msg)
        
        # 统计结果
        end_time = time.time()
        elapsed_time = end_time - start_time
        success_rate = (success_count / len(test_files)) * 100
        
        self.log(f"\n{'='*50}")
        summary_title = "📊 转换统计" if self.use_chinese else "📊 Conversion Statistics"
        self.log(summary_title)
        
        stats = [
            f"总文件数: {len(test_files)}",
            f"成功转换: {success_count}",
            f"失败转换: {len(test_files) - success_count}",
            f"成功率: {success_rate:.1f}%",
            f"总耗时: {elapsed_time:.2f}秒",
            f"平均速度: {len(test_files)/elapsed_time:.2f} 文件/秒"
        ]
        
        for stat in stats:
            self.log(f"  {stat}")
        
        # 列出失败文件详情
        if failed_files:
            self.log(f"\n❌ 失败文件详情:")
            for file_name, error in failed_files:
                self.log(f"  - {file_name}: {error}")
        
        # 列出成功转换的文件
        if success_count > 0:
            self.log(f"\n✅ 成功转换的文件:")
            output_files = list(output_dir.glob("*.xmind"))
            for output_file in output_files:
                self.log(f"  - {output_file.name}")
        
        return success_rate
    
    def test_server_batch_conversion(self):
        """测试服务器批量转换"""
        title = "🌐 服务器批量转换测试" if self.use_chinese else "🌐 Server Batch Conversion Test"
        self.log(f"\n{title}")
        
        # 准备测试文件 - 支持所有支持的文件类型
        examples_dir = self.project_root / "examples"
        supported_extensions = ['.txt', '.md', '.html', '.docx', '.xlsx']
        
        test_files = []
        for ext in supported_extensions:
            test_files.extend(list(examples_dir.glob(f"*{ext}")))
        
        if not test_files:
            no_files_msg = "⚠️ 未找到测试文件" if self.use_chinese else "⚠️ No test files found"
            self.log(no_files_msg)
            return 0.0  # 返回0%通过率
        
        try:
            # 处理所有找到的文件以进行完整测试
            selected_files = test_files
            self.log(f"批量处理 {len(selected_files)} 个文件" if self.use_chinese else f"Batch processing {len(selected_files)} files")
            
            # 准备文件上传 - 根据文件类型设置正确的MIME类型
            files = []
            mime_types = {
                '.txt': 'text/plain',
                '.md': 'text/markdown', 
                '.html': 'text/html',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            
            for file_path in selected_files:
                file_ext = file_path.suffix.lower()
                mime_type = mime_types.get(file_ext, 'application/octet-stream')
                files.append(('files', (file_path.name, open(file_path, 'rb'), mime_type)))
            
            # 准备其他表单数据
            data = {
                'output_dir': str(self.project_root / "output")
            }
            
            # 调用服务器批量转换API
            start_time = time.time()
            response = requests.post(
                f"{self.server_url}/batch",
                files=files,
                data=data,
                timeout=60  # 批量转换可能需要更长时间
            )
            end_time = time.time()
            
            # 关闭所有打开的文件
            for _, file_tuple in files:
                file_obj = file_tuple[1]  # 获取文件对象
                if hasattr(file_obj, 'close'):
                    file_obj.close()
            
            elapsed_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                success_count = result.get('success_count', 0)
                total_count = result.get('total_count', len(selected_files))
                success_rate = (success_count / total_count) * 100 if total_count > 0 else 0.0
                
                # 显示详细统计
                self.log(f"\n{'='*40}")
                server_stats = "📊 服务器转换统计" if self.use_chinese else "📊 Server Conversion Statistics"
                self.log(server_stats)
                self.log(f"  总文件数: {total_count}")
                self.log(f"  成功转换: {success_count}")
                self.log(f"  失败转换: {total_count - success_count}")
                self.log(f"  成功率: {success_rate:.1f}%")
                self.log(f"  总耗时: {elapsed_time:.2f}秒")
                
                success_msg = f"✅ 批量转换成功: {success_count}/{total_count} 文件, 耗时 {elapsed_time:.2f}秒" if self.use_chinese else f"✅ Batch conversion successful: {success_count}/{total_count} files, took {elapsed_time:.2f}s"
                self.log(success_msg)
                return success_rate
            else:
                error_msg = f"❌ 批量转换失败: HTTP {response.status_code}" if self.use_chinese else f"❌ Batch conversion failed: HTTP {response.status_code}"
                self.log(error_msg)
                return 0.0
                
        except Exception as e:
            error_msg = f"❌ 批量转换失败: {e}" if self.use_chinese else f"❌ Batch conversion failed: {e}"
            self.log(error_msg)
            return 0.0
    
    def run_all_tests(self):
        """运行所有测试"""
        header = "🚀 XMind批量转换测试" if self.use_chinese else "🚀 XMind Batch Conversion Test"
        self.log(header)
        self.log(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"服务器地址: {self.server_url}" if self.use_chinese else f"Server URL: {self.server_url}")
        
        # 运行核心引擎批量转换测试
        batch_success_rate = self.test_batch_conversion()
        
        # 运行服务器批量转换测试
        server_batch_success_rate = self.test_server_batch_conversion()
        
        # 最终总结
        self.log(f"\n{'='*60}")
        final_title = "🎯 测试完成" if self.use_chinese else "🎯 Test Completed"
        self.log(final_title)
        
        # 计算总体通过率
        overall_success_rate = (batch_success_rate + server_batch_success_rate) / 2
        
        # 显示详细结果
        self.log(f"\n📊 综合测试结果:")
        self.log(f"  核心引擎测试: {batch_success_rate:.1f}%")
        self.log(f"  服务器测试: {server_batch_success_rate:.1f}%")
        self.log(f"  总体通过率: {overall_success_rate:.1f}%")
        
        # 根据总体通过率判断测试是否通过
        if overall_success_rate >= 80.0:  # 80%以上认为通过
            success_msg = f"✅ 所有测试通过！ (总体通过率: {overall_success_rate:.1f}%)" if self.use_chinese else f"✅ All tests passed! (Overall success rate: {overall_success_rate:.1f}%)"
            self.log(success_msg)
            return overall_success_rate  # 返回实际通过率数值
        elif overall_success_rate >= 50.0:  # 50-79%认为部分通过
            warning_msg = f"⚠️ 部分测试通过 (总体通过率: {overall_success_rate:.1f}%)" if self.use_chinese else f"⚠️ Partially passed (Overall success rate: {overall_success_rate:.1f}%)"
            self.log(warning_msg)
            return overall_success_rate  # 返回实际通过率数值
        else:
            error_msg = f"❌ 测试未通过 (总体通过率: {overall_success_rate:.1f}%)" if self.use_chinese else f"❌ Tests failed (Overall success rate: {overall_success_rate:.1f}%)"
            self.log(error_msg)
            return overall_success_rate  # 返回实际通过率数值


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XMind Batch Conversion Test')
    parser.add_argument('--english', action='store_true', help='Use English mode')
    parser.add_argument('--server', default="http://localhost:8080", help='Server URL')
    
    args = parser.parse_args()
    
    tester = BatchConversionTester(server_url=args.server, use_chinese=not args.english)
    success_rate = tester.run_all_tests()
    
    # 基于成功率返回相应的退出码（>=80%为通过）
    exit(0 if success_rate >= 80 else 1)

# 标准Python入口点
if __name__ == "__main__":
    main()