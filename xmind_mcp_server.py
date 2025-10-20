#!/usr/bin/env python3
"""
XMind MCP Server - FastMCP Implementation
只使用真实XMind核心引擎，移除所有模拟实现
"""

import logging
import sys
import json
import os
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator

# 导入版本信息（统一来源）
try:
    from xmind_mcp import __version__ as __version__
except Exception:
    __version__ = "0.0.0"  # 本地开发异常时回退

# 导入真实的XMind核心引擎
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from xmind_core_engine import (
        get_engine, 
        read_xmind_file as core_read_xmind_file, 
        create_mind_map as core_create_mind_map, 
        analyze_mind_map as core_analyze_mind_map, 
        convert_to_xmind as core_convert_to_xmind, 
        list_xmind_files as core_list_xmind_files
    )
    REAL_ENGINE_AVAILABLE = True
    logging.info("真实XMind核心引擎已加载")
except ImportError as e:
    REAL_ENGINE_AVAILABLE = False
    logging.error(f"真实XMind核心引擎加载失败: {e}")
    logging.error("MCP服务器无法启动，需要真实引擎支持")
    sys.exit(1)

# 尝试导入FastMCP，失败则回退到标准实现
try:
    from mcp.server.fastmcp import FastMCP, Context
    FASTMCP_AVAILABLE = True
    logging.info("使用FastMCP实现")
except ImportError:
    FASTMCP_AVAILABLE = False
    logging.warning("FastMCP不可用，使用标准MCP实现")
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("XMindMCPServer")

# 强制设置工作目录为项目目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
logger.info(f"工作目录已设置为: {PROJECT_ROOT}")

class ConfigManager:
    """配置管理器 - 处理配置文件加载和默认路径管理"""
    
    def __init__(self):
        self.config = {}
        self.default_output_dir = None
        self.config_file_path = None
    
    def load_config(self, config_file_path: str = None) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_file_path: 配置文件路径，如果为None则使用默认路径
            
        Returns:
            配置字典
        """
        if config_file_path is None:
            config_file_path = os.path.join(PROJECT_ROOT, "xmind_mcp_config.json")
        
        self.config_file_path = config_file_path
        
        # 如果配置文件存在，加载它
        if os.path.exists(config_file_path):
            try:
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"配置文件加载成功: {config_file_path}")
            except Exception as e:
                logger.warning(f"配置文件加载失败: {e}，使用默认配置")
                self.config = {}
        else:
            logger.info(f"配置文件不存在: {config_file_path}，使用默认配置")
            self.config = {}
        
        # 设置默认输出目录
        self._setup_default_output_dir()
        
        return self.config
    
    def _setup_default_output_dir(self):
        """设置默认输出目录"""
        # 从配置中获取默认输出目录
        config_default_dir = self.config.get("default_output_dir")
        
        if config_default_dir:
            # 确保路径为绝对路径
            if os.path.isabs(config_default_dir):
                self.default_output_dir = config_default_dir
            else:
                # 相对路径则转换为相对于项目根目录的绝对路径
                self.default_output_dir = os.path.abspath(os.path.join(PROJECT_ROOT, config_default_dir))
            
            logger.info(f"使用配置文件中的默认输出目录: {self.default_output_dir}")
        else:
            # 没有配置默认输出目录
            self.default_output_dir = None
            logger.info("未配置默认输出目录，输出路径为必填参数")
    
    def get_default_output_dir(self) -> Optional[str]:
        """获取默认输出目录"""
        return self.default_output_dir
    
    def validate_absolute_path(self, path: str) -> bool:
        """验证路径是否为绝对路径"""
        return os.path.isabs(path)

# 全局配置管理器实例
config_manager = ConfigManager()

@dataclass
class XMindConfig:
    def ensure_data_dir(self):
        """确保数据目录存在 - 现在使用相对路径"""
        pass  # 不再需要单独的数据目录配置

# 全局配置实例
config = XMindConfig()

if FASTMCP_AVAILABLE:
    # FastMCP实现
    @asynccontextmanager
    async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
        """管理服务器生命周期"""
        logger.info("XMind MCP服务器启动")
        config.ensure_data_dir()
        yield {}
        logger.info("XMind MCP服务器关闭")

    # 创建FastMCP服务器
    mcp = FastMCP("XMindMCP")

    @mcp.tool()
    def read_xmind_file(ctx: Context, file_path: str) -> str:
        """读取XMind文件内容（返回结构与统计信息）
        
        Args:
            file_path: XMind文件路径
        """
        try:
            # 验证文件路径
            if not file_path:
                return json.dumps({
                    "status": "error",
                    "error": "文件路径不能为空"
                }, ensure_ascii=False)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return json.dumps({
                    "status": "error",
                    "error": f"文件不存在: {file_path}",
                    "file_path": file_path
                }, ensure_ascii=False)
            
            # 检查文件扩展名
            if not file_path.lower().endswith('.xmind'):
                logger.warning(f"文件扩展名不是.xmind: {file_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return json.dumps({
                    "status": "error",
                    "error": "文件为空",
                    "file_path": file_path
                }, ensure_ascii=False)
            
            logger.info(f"读取XMind文件: {file_path}, 大小: {file_size} 字节")
            
            # 调用核心引擎读取文件
            result = core_read_xmind_file(file_path)
            
            # 添加文件路径信息到结果中
            if isinstance(result, dict):
                result["file_path"] = file_path
                result["file_size"] = file_size
            
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"读取XMind文件错误: {e}")
            return json.dumps({
                "status": "error",
                "error": str(e),
                "file_path": file_path
            }, ensure_ascii=False)

    @mcp.tool()
    def create_mind_map(ctx: Context, title: str, topics_json: str, output_path: str = None) -> str:
        """创建新的思维导图（支持 children/topics/subtopics 等别名，服务器自动归一化）
        
        Args:
            title: 思维导图标题（作为根节点标题）
            topics_json: 主题JSON结构（字符串或Python对象）。每个节点至少包含`title`；子节点推荐使用`children`，也兼容`topics`/`subtopics`/`nodes`/`items`（服务器会自动归一化）。必须为合法JSON结构，不要使用Markdown或纯文本。
            output_path: 可选输出文件绝对路径；未指定时优先使用配置中的 `default_output_dir`
        """
        try:
            # 修复字典参数问题 - 统一处理topics_json格式
            if isinstance(topics_json, (dict, list)):
                # 如果已经是Python对象，直接使用
                topics_data = topics_json
                logger.info(f"topics_json是Python对象: {type(topics_json)}")
            elif isinstance(topics_json, str):
                # 如果是字符串，尝试解析为JSON
                try:
                    topics_data = json.loads(topics_json)
                    logger.info(f"topics_json字符串解析成功")
                except json.JSONDecodeError:
                    # 如果解析失败，创建简单的主题结构
                    topics_data = [{"title": topics_json}]
                    logger.info(f"topics_json作为简单字符串处理")
            else:
                # 其他类型，转换为字符串后处理
                topics_data = [{"title": str(topics_json)}]
                logger.info(f"topics_json转换为字符串: {type(topics_json)}")
            
            # 使用核心引擎的sanitize方法来处理文件名
            engine = get_engine()
            safe_title = engine._sanitize_filename(title)
            
            # 确定输出路径 - 新的逻辑
            if output_path:
                # 如果指定了输出路径，验证是否为绝对路径
                if not config_manager.validate_absolute_path(output_path):
                    return json.dumps({
                        "status": "error", 
                        "error": "输出路径必须为绝对路径",
                        "title": title,
                        "output_path": output_path
                    }, ensure_ascii=False)
                
                final_output_path = output_path
                output_dir = os.path.dirname(final_output_path)
                if output_dir and not os.path.exists(output_dir):
                    try:
                        os.makedirs(output_dir)
                        logger.info(f"创建输出目录: {output_dir}")
                    except Exception as e:
                        logger.error(f"创建输出目录失败: {str(e)}")
                        return json.dumps({
                            "status": "error",
                            "error": f"无法创建输出目录: {str(e)}",
                            "title": title
                        }, ensure_ascii=False)
                logger.info(f"使用指定输出路径: {final_output_path}")
            else:
                # 未指定输出路径，检查配置文件中的默认输出目录
                default_output_dir = config_manager.get_default_output_dir()
                
                if default_output_dir is None:
                    # 配置文件中没有指定默认输出目录
                    return json.dumps({
                        "status": "error",
                        "error": "未指定输出路径且配置文件中没有默认输出目录配置",
                        "title": title,
                        "suggestion": "请在配置文件中设置default_output_dir或在调用时指定output_path参数"
                    }, ensure_ascii=False)
                
                # 使用配置文件中的默认输出目录
                final_output_path = os.path.join(default_output_dir, f"{safe_title}.xmind")
                logger.info(f"使用配置文件默认输出路径: {final_output_path}")
                
                # 确保默认输出目录存在
                if not os.path.exists(default_output_dir):
                    try:
                        os.makedirs(default_output_dir)
                        logger.info(f"创建默认输出目录: {default_output_dir}")
                    except Exception as e:
                        logger.error(f"创建默认输出目录失败: {str(e)}")
                        return json.dumps({
                            "status": "error",
                            "error": f"无法创建默认输出目录: {str(e)}",
                            "title": title,
                            "default_output_dir": default_output_dir
                        }, ensure_ascii=False)
            
            # 将topics_data归一化为children结构，兼容topics/subtopics
            def _normalize_children(obj):
                if isinstance(obj, list):
                    return [_normalize_children(x) for x in obj]
                if isinstance(obj, dict):
                    title_val = obj.get("title") or obj.get("name") or obj.get("text") or ""
                    children_val = (
                        obj.get("children")
                        or obj.get("topics")
                        or obj.get("subtopics")
                        or obj.get("nodes")
                        or obj.get("items")
                    )
                    normalized = {"title": title_val}
                    if children_val:
                        normalized["children"] = _normalize_children(children_val)
                    return normalized
                return {"title": str(obj)}

            normalized_topics = _normalize_children(topics_data) if topics_data else []
            topics_json_str = json.dumps(normalized_topics, ensure_ascii=False)
            
            # 调用核心引擎创建思维导图
            result = core_create_mind_map(title, topics_json_str, final_output_path)
            logger.info(f"创建思维导图: {title} -> {final_output_path}")
            
            # 验证文件是否真的被创建
            if os.path.exists(final_output_path):
                logger.info(f"文件创建成功，大小: {os.path.getsize(final_output_path)} 字节")
                
                # 修改返回格式
                result_data = result
                if isinstance(result_data, dict) and result_data.get("status") == "success":
                    # 获取绝对路径
                    abs_path = os.path.abspath(final_output_path)
                    # 修改返回数据
                    result_data["filename"] = os.path.basename(final_output_path)
                    result_data["message"] = f"思维导图已创建: {abs_path}"
                    result_data["absolute_path"] = abs_path
                    result_data["output_path"] = final_output_path
                    
                    return json.dumps(result_data, ensure_ascii=False)
                else:
                    # 核心引擎返回失败，但仍然返回详细信息
                    if isinstance(result_data, dict):
                        result_data["filename"] = os.path.basename(final_output_path)
                        result_data["absolute_path"] = os.path.abspath(final_output_path)
                        result_data["output_path"] = final_output_path
                    return json.dumps(result_data, ensure_ascii=False)
            else:
                logger.error(f"文件创建失败，路径: {final_output_path}")
                return json.dumps({
                    "status": "error",
                    "error": f"文件创建失败，路径: {final_output_path}",
                    "title": title,
                    "output_path": final_output_path
                }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"创建思维导图错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def analyze_mind_map(ctx: Context, file_path: str) -> str:
        """分析思维导图结构（统计节点数、最大层级等）"""
        try:
            result = core_analyze_mind_map(file_path)
            logger.info(f"分析思维导图: {file_path}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"分析思维导图错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def convert_to_xmind(ctx: Context, source_filepath: str = None, output_filepath: str = None, source_file: str = None, output_file: str = None) -> str:
        """将纯文本、Markdown、HTML、Word、Excel等文件转换为XMind。
        
        注意：不要传入JSON结构；JSON结构请使用 `create_mind_map`。
        
        Args:
            source_filepath: 源文件路径（支持 .txt/.md/.html/.docx/.xlsx 等）
            output_filepath: 可选。输出XMind文件绝对路径；未指定时自动输出到 `output/<源文件名>.xmind`
            source_file: 兼容旧参数名（同 source_filepath）
            output_file: 兼容旧参数名（同 output_filepath）
        """
        try:
            src = source_filepath or source_file
            out = output_filepath or output_file
            if not src:
                return json.dumps({
                    "status": "error",
                    "error": "必须提供源文件路径：source_filepath 或 source_file"
                }, ensure_ascii=False)
            result = core_convert_to_xmind(src, out)
            logger.info(f"转换文件为XMind格式: {src}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"文件转换错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def list_xmind_files(ctx: Context, directory: str = None, recursive: bool = True) -> str:
        """列出XMind文件
        
        Args:
            directory: 要搜索的目录，如果为None则使用配置文件中的默认输出目录
            recursive: 是否递归遍历目录（默认 True）
        """
        try:
            # 如果未指定目录，检查配置文件中的默认输出目录
            if directory is None:
                default_output_dir = config_manager.get_default_output_dir()
                
                if default_output_dir is None:
                    # 配置文件中没有指定默认输出目录
                    return json.dumps({
                        "status": "error",
                        "error": "未指定搜索目录且配置文件中没有默认输出目录配置",
                        "suggestion": "请在配置文件中设置default_output_dir或在调用时指定directory参数"
                    }, ensure_ascii=False)
                
                directory = default_output_dir
                logger.info(f"使用配置文件默认输出目录: {directory}")
            else:
                # 指定了目录，验证是否为绝对路径
                if not config_manager.validate_absolute_path(directory):
                    return json.dumps({
                        "status": "error",
                        "error": "搜索目录必须为绝对路径",
                        "directory": directory
                    }, ensure_ascii=False)
                logger.info(f"使用指定目录: {directory}")
            
            # 验证目录是否存在
            if not os.path.exists(directory):
                return json.dumps({
                    "status": "error",
                    "error": f"目录不存在: {directory}",
                    "directory": directory
                }, ensure_ascii=False)
            
            # 验证是否为目录
            if not os.path.isdir(directory):
                return json.dumps({
                    "status": "error",
                    "error": f"路径不是目录: {directory}",
                    "directory": directory
                }, ensure_ascii=False)
            
            logger.info(f"搜索XMind文件，目录: {directory}，递归: {recursive}")
            
            # 调用核心引擎列出文件
            result = core_list_xmind_files(directory, recursive)
            
            # 添加目录信息到结果中
            if isinstance(result, dict):
                result["directory"] = directory
                result["recursive"] = recursive
            
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"列出XMind文件错误: {e}")
            return json.dumps({
                "status": "error",
                "error": str(e),
                "directory": directory if 'directory' in locals() else None
            }, ensure_ascii=False)

def main():
    """主函数 - 支持 --mode fastmcp|stdio"""
    parser = argparse.ArgumentParser(description='XMind MCP服务器')
    parser.add_argument('--version', action='version', version=f'XMind MCP Server {__version__}')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--mode', choices=['fastmcp', 'stdio'], help='选择运行模式：fastmcp 或 stdio')
    parser.add_argument('--stdio', action='store_true', help='以 STDIO 模式运行（别名）')
    parser.add_argument('--config', help='指定配置文件路径')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("调试模式已启用")

    # 加载配置文件
    config_manager.load_config(args.config)

    requested_mode = 'fastmcp' if FASTMCP_AVAILABLE else 'stdio'
    if args.stdio:
        requested_mode = 'stdio'
    if args.mode:
        requested_mode = args.mode

    if requested_mode == 'fastmcp':
        if not FASTMCP_AVAILABLE:
            logger.error("FastMCP 不可用，请安装 mcp[cli]>=1.3.0 或使用 --mode stdio")
            sys.exit(1)
        print("启动XMind MCP服务器 (FastMCP模式)")
        logger.info("启动XMind MCP服务器 (FastMCP模式)")
        mcp.run()
    else:
        print("启动XMind MCP服务器 (STDIO模式)")
        logger.info("启动XMind MCP服务器 (STDIO模式)")
        try:
            # 使用已验证的STDIO实现
            import subprocess
            import sys
            
            # 运行简化的STDIO MCP服务器
            cmd = [sys.executable, "-m", "xmind_mcp.stdio_server"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"STDIO服务器启动失败: {result.stderr}")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"STDIO 模式启动失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()