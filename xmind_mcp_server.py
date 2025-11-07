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
# 保持工作目录稳定但不在日志中暴露绝对路径
try:
    os.chdir(PROJECT_ROOT)
    logger.info("工作目录已设置")
except Exception:
    # 若切换失败，保持现状，不暴露路径
    logger.warning("工作目录设置失败，继续使用当前目录")

DEFAULT_OUTPUT_DIR: Optional[str] = None

def init_default_output_dir(cli_default_output_dir: Optional[str] = None) -> None:
    """初始化默认输出目录，仅使用命令行参数或环境变量。
    优先级：CLI --default-output-dir > XMIND_MCP_DEFAULT_OUTPUT_DIR > XMIND_MCP_BASE_DIR + 相对目录
    """
    global DEFAULT_OUTPUT_DIR

    env_default_dir = os.getenv("XMIND_MCP_DEFAULT_OUTPUT_DIR")
    env_base_dir = os.getenv("XMIND_MCP_BASE_DIR")

    # CLI 优先
    if cli_default_output_dir:
        if os.path.isabs(cli_default_output_dir):
            DEFAULT_OUTPUT_DIR = cli_default_output_dir
            logger.info("默认输出目录来源：CLI --default-output-dir")
            return
        elif env_base_dir and os.path.isabs(env_base_dir):
            DEFAULT_OUTPUT_DIR = os.path.join(env_base_dir, cli_default_output_dir)
            logger.info("默认输出目录来源：CLI 相对目录 + XMIND_MCP_BASE_DIR")
            return
        else:
            logger.warning("CLI 默认输出目录无效（必须为绝对路径或提供绝对基准目录）")

    # 环境变量次之
    if env_default_dir:
        if os.path.isabs(env_default_dir):
            DEFAULT_OUTPUT_DIR = env_default_dir
            logger.info("默认输出目录来源：环境变量 XMIND_MCP_DEFAULT_OUTPUT_DIR")
            return
        elif env_base_dir and os.path.isabs(env_base_dir):
            DEFAULT_OUTPUT_DIR = os.path.join(env_base_dir, env_default_dir)
            logger.info("默认输出目录来源：XMIND_MCP_BASE_DIR + 相对默认目录")
            return
        else:
            logger.warning("环境变量默认输出目录无效（必须为绝对路径或提供绝对基准目录）")

    # 未配置默认输出目录
    DEFAULT_OUTPUT_DIR = None
    logger.info("未设置默认输出目录，输出型工具需要显式传入绝对路径")

def get_default_output_dir() -> Optional[str]:
    return DEFAULT_OUTPUT_DIR

def validate_absolute_path(path: str) -> bool:
    return os.path.isabs(path)

# 统一的输出路径解析与目录创建（仅接受绝对路径）
def _resolve_output_path(output_path: Optional[str], default_filename: str) -> Dict[str, Any]:
    """集中解析输出路径：
    - 若传入 `output_path`，必须为绝对路径；必要时创建父目录
    - 若未传入，则使用配置中的默认绝对目录并拼接 `default_filename`
    返回统一结构：
    {"ok": True, "path": final_output_path} 或 {"ok": False, "error": {status/message/suggestion}}
    """
    try:
        if output_path:
            if not validate_absolute_path(output_path):
                return {
                    "ok": False,
                    "error": {
                        "status": "error",
                        "message": "输出路径必须为绝对路径"
                    }
                }
            final_out = output_path
            out_dir = os.path.dirname(final_out)
            if out_dir and not os.path.exists(out_dir):
                try:
                    os.makedirs(out_dir)
                    logger.info("已创建输出目录")
                except Exception:
                    logger.error("创建输出目录失败")
                    return {
                        "ok": False,
                        "error": {
                            "status": "error",
                            "message": "无法创建输出目录"
                        }
                    }
            logger.info("使用指定输出路径")
            return {"ok": True, "path": final_out}
        else:
            default_output_dir = get_default_output_dir()
            if default_output_dir is None:
                return {
                    "ok": False,
                    "error": {
                        "status": "error",
                        "message": "未指定输出路径且未设置默认输出目录",
                        "suggestion": "通过 CLI --default-output-dir 或环境变量 XMIND_MCP_DEFAULT_OUTPUT_DIR 设置绝对输出目录，或在调用时传入绝对输出路径"
                    }
                }
            final_out = os.path.join(default_output_dir, default_filename)
            if not os.path.exists(default_output_dir):
                try:
                    os.makedirs(default_output_dir)
                    logger.info("已创建默认输出目录")
                except Exception:
                    logger.error("创建默认输出目录失败")
                    return {
                        "ok": False,
                        "error": {
                            "status": "error",
                            "message": "无法创建默认输出目录"
                        }
                    }
            return {"ok": True, "path": final_out}
    except Exception as e:
        logger.error(f"解析输出路径异常: {e}")
        return {"ok": False, "error": {"status": "error", "message": "解析输出路径异常"}}

# 统一裁剪返回中的绝对路径并填充文件名
def _mask_output_result(result: Any, final_output_path: str, success_message: Optional[str] = None) -> Dict[str, Any]:
    """裁剪返回中的绝对路径字段，仅保留文件名。
    注意：仅在成功状态时覆盖成功消息，避免错误状态出现“成功”提示。
    """
    try:
        if not isinstance(result, dict):
            result = {"status": "success", "data": {}, "message": success_message or "操作成功"}
        data = result.get("data") or {}
        # 移除可能含绝对路径的字段
        for key in ("output_path", "absolute_path", "output_file", "source_file"):
            data.pop(key, None)
        data["filename"] = os.path.basename(final_output_path)
        result["data"] = data
        # 仅在成功状态时覆盖消息
        if success_message and str(result.get("status")).lower() == "success":
            result["message"] = success_message
        return result
    except Exception:
        # 回退为最小成功结构（不暴露路径）
        return {"status": "success", "message": success_message or "操作成功", "data": {"filename": os.path.basename(final_output_path)}}

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
                    "message": "文件路径不能为空"
                }, ensure_ascii=False)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return json.dumps({
                    "status": "error",
                    "message": f"文件不存在: {file_path}"
                }, ensure_ascii=False)
            
            # 检查文件扩展名
            if not file_path.lower().endswith('.xmind'):
                logger.warning(f"文件扩展名不是.xmind: {file_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return json.dumps({
                    "status": "error",
                    "message": "文件为空"
                }, ensure_ascii=False)
            
            logger.info(f"读取XMind文件: {file_path}, 大小: {file_size} 字节")
            
            # 调用核心引擎读取文件
            result = core_read_xmind_file(file_path)

            # 将文件路径信息放入 data 中
            if isinstance(result, dict) and result.get("status") == "success":
                data = result.get("data") or {}
                data["file_path"] = file_path
                data["file_size"] = file_size
                result["data"] = data
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"读取XMind文件错误: {e}")
            return json.dumps({
                "status": "error",
                "message": str(e)
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
            
            # 统一解析输出路径
            ro = _resolve_output_path(output_path, f"{safe_title}.xmind")
            if not ro.get("ok"):
                return json.dumps(ro.get("error"), ensure_ascii=False)
            final_output_path = ro.get("path")
            
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
            # 统一顶层结构为列表，避免传入单个字典导致引擎解析报错
            if isinstance(normalized_topics, dict):
                normalized_topics = [normalized_topics]
            topics_json_str = json.dumps(normalized_topics, ensure_ascii=False)
            
            # 调用核心引擎创建思维导图
            result = core_create_mind_map(title, topics_json_str, final_output_path)
            # 若引擎返回错误，直接透传错误信息，避免误导性“文件不存在”提示
            if isinstance(result, dict) and str(result.get("status")).lower() != "success":
                return json.dumps(result, ensure_ascii=False)
            logger.info("创建思维导图成功")

            # 验证文件是否真的被创建
            if os.path.exists(final_output_path):
                masked = _mask_output_result(result, final_output_path, "思维导图已创建")
                return json.dumps(masked, ensure_ascii=False)
            else:
                # 文件未创建，返回错误信息但不暴露路径
                logger.error("文件创建失败，目标文件不存在")
                return json.dumps({
                    "status": "error",
                    "message": "文件创建失败，目标文件不存在"
                }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"创建思维导图错误: {e}")
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def analyze_mind_map(ctx: Context, file_path: str) -> str:
        """分析思维导图结构（统计节点数、最大层级等）"""
        try:
            result = core_analyze_mind_map(file_path)
            logger.info(f"分析思维导图: {file_path}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"分析思维导图错误: {e}")
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def convert_to_xmind(ctx: Context, source_filepath: str = None, output_filepath: str = None, source_file: str = None, output_file: str = None) -> str:
        """将纯文本、Markdown、HTML、Word、Excel等文件转换为XMind。

        要求：`source_filepath` 必须为绝对路径；相对路径会被拒绝并返回错误提示。
        注意：不要传入 JSON 结构；JSON 结构请使用 `create_mind_map`。

        Args:
            source_filepath: 源文件绝对路径（支持 .txt/.md/.html/.docx/.xlsx 等）
            output_filepath: 可选。输出XMind文件绝对路径；未指定时由服务器配置的默认绝对目录决定
            source_file: 兼容旧参数名（同 source_filepath）
            output_file: 兼容旧参数名（同 output_filepath）
        """
        try:
            src = source_filepath or source_file
            out = output_filepath or output_file
            if not src:
                return json.dumps({
                    "status": "error",
                    "message": "必须提供源文件路径：source_filepath 或 source_file"
                }, ensure_ascii=False)
            # 源路径必须为绝对路径（避免进程工作目录差异导致解析错误）
            if not validate_absolute_path(src):
                return json.dumps({
                    "status": "error",
                    "message": "必须为绝对路径",
                    "suggestion": "传入绝对路径，或在 MCP 配置中设置 XMIND_MCP_BASE_DIR 后使用该目录中的相对路径"
                }, ensure_ascii=False)
            # 统一解析输出路径
            base_name = os.path.splitext(os.path.basename(src))[0]
            ro = _resolve_output_path(out, f"{base_name}.xmind")
            if not ro.get("ok"):
                return json.dumps(ro.get("error"), ensure_ascii=False)
            final_out = ro.get("path")

            result = core_convert_to_xmind(src, final_out)
            logger.info("转换文件为XMind格式成功")
            masked = _mask_output_result(result, final_out, "文件转换成功")
            return json.dumps(masked, ensure_ascii=False)
        except Exception as e:
            logger.error(f"文件转换错误: {e}")
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def list_xmind_files(ctx: Context, directory: str = None, recursive: bool = True, pattern: str = None, max_depth: int = None) -> str:
        """列出XMind文件
        
        Args:
            directory: 要搜索的目录，如果为None则使用配置文件中的默认输出目录
            recursive: 是否递归遍历目录（默认 True）
        """
        try:
            # 如果未指定目录，使用默认输出目录（CLI/ENV）
            if directory is None:
                default_output_dir = get_default_output_dir()
                if default_output_dir is None:
                    return json.dumps({
                        "status": "error",
                        "message": "未指定搜索目录且未设置默认输出目录",
                        "suggestion": "通过 CLI --default-output-dir 或环境变量 XMIND_MCP_DEFAULT_OUTPUT_DIR 设置绝对目录，或在调用时指定 directory"
                    }, ensure_ascii=False)
                directory = default_output_dir
                logger.info(f"使用默认输出目录: {directory}")
            else:
                # 指定了目录，验证是否为绝对路径
                if not validate_absolute_path(directory):
                    return json.dumps({
                        "status": "error",
                        "message": "搜索目录必须为绝对路径"
                    }, ensure_ascii=False)
                logger.info(f"使用指定目录: {directory}")
            
            # 验证目录是否存在
            if not os.path.exists(directory):
                return json.dumps({
                    "status": "error",
                    "message": f"目录不存在: {directory}"
                }, ensure_ascii=False)
            
            # 验证是否为目录
            if not os.path.isdir(directory):
                return json.dumps({
                    "status": "error",
                    "message": f"路径不是目录: {directory}"
                }, ensure_ascii=False)
            
            logger.info(f"搜索XMind文件，目录: {directory}，递归: {recursive}，pattern: {pattern}，max_depth: {max_depth}")
            
            # 调用核心引擎列出文件
            result = core_list_xmind_files(directory, recursive, pattern, max_depth)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"列出XMind文件错误: {e}")
            return json.dumps({
                "status": "error",
                "message": str(e)
            }, ensure_ascii=False)

    @mcp.tool("translate_xmind_titles")
    def translate_xmind_titles(source_filepath: str, output_filepath: str = None, target_lang: str = "en", overwrite: bool = False):
        """翻译XMind中的标题并输出新文件。
        - source_filepath: 源XMind文件路径
        - output_filepath: 输出XMind文件绝对路径（可选，未指定时由默认绝对目录决定）
        - target_lang: 目标语言代码（默认 'en'）
        - overwrite: 如果输出已存在，是否覆盖（默认 False）
        """
        try:
            if not source_filepath:
                return json.dumps({
                    "status": "error",
                    "message": "必须提供源文件路径"
                }, ensure_ascii=False)

            # 统一解析输出路径
            base_name = os.path.splitext(os.path.basename(source_filepath))[0]
            ro = _resolve_output_path(output_filepath, f"{base_name}_{target_lang}.xmind")
            if not ro.get("ok"):
                return json.dumps(ro.get("error"), ensure_ascii=False)
            final_out = ro.get("path")

            engine = get_engine()
            result = engine.translate_xmind_titles(source_filepath, final_out, target_lang, overwrite)
            masked = _mask_output_result(result, final_out, "标题翻译并写入成功")
            try:
                return json.dumps(masked, ensure_ascii=False)
            except Exception:
                return str(masked)
        except Exception as e:
            logger.error(f"translate_xmind_titles 执行异常: {e}")
            return json.dumps({
                "status": "error",
                "message": "翻译执行异常"
            }, ensure_ascii=False)

def main():
    """主函数 - 支持 --mode fastmcp|stdio"""
    parser = argparse.ArgumentParser(description='XMind MCP服务器')
    parser.add_argument('--version', action='version', version=f'XMind MCP Server {__version__}')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--mode', choices=['fastmcp', 'stdio'], help='选择运行模式：fastmcp 或 stdio')
    parser.add_argument('--stdio', action='store_true', help='以 STDIO 模式运行（别名）')
    parser.add_argument('--default-output-dir', help='指定默认输出目录（绝对路径），也可通过环境变量 XMIND_MCP_DEFAULT_OUTPUT_DIR 设置')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("调试模式已启用")

    # 初始化默认输出目录（CLI/ENV）
    init_default_output_dir(args.default_output_dir)

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