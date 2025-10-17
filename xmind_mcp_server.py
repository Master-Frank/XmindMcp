#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind MCP服务器
基于FastAPI的MCP服务器，提供XMind文件处理的RESTful API
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# 导入核心引擎和AI扩展
from xmind_core_engine import XMindCoreEngine, get_available_tools
from xmind_ai_extensions import XMindAIExtensions


class CreateMindMapRequest(BaseModel):
    """创建思维导图请求"""
    title: str
    topics_json: str


class ConvertFileRequest(BaseModel):
    """转换文件请求"""
    source_filepath: str
    output_filepath: Optional[str] = None


class XMindMCPServer:
    """XMind MCP服务器"""
    
    def __init__(self):
        self.engine = XMindCoreEngine()
        self.ai_extensions = XMindAIExtensions()
        self.app = None
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_file = "server_config.json"
        default_config = {
            "host": "0.0.0.0",  # 修复：绑定到所有网络接口，支持容器部署
            "port": int(os.environ.get("PORT", 8080)),  # 修复：使用环境变量PORT，支持Render等平台
            "debug": False,
            "cors_origins": ["*"],
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "allowed_extensions": [".xmind", ".txt", ".md", ".json"],
            "ai_enabled": True,
            "ai_model": "default"
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {config_file}: {e}")
        
        return default_config
    
    def create_app(self) -> FastAPI:
        """创建FastAPI应用"""
        app = FastAPI(
            title="XMind MCP Server",
            description="基于FastAPI的XMind文件处理MCP服务器",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config["cors_origins"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.app = app
        self._setup_routes()
        return app
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.get("/")
        async def root():
            """根路径"""
            return {
                "message": "XMind MCP Server 正在运行",
                "version": "1.0.0",
                "docs_url": "/docs",
                "tools_url": "/tools"
            }
        
        @self.app.get("/health")
        async def health():
            """健康检查"""
            from datetime import datetime
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/tools")
        async def get_tools():
            """获取可用工具列表"""
            try:
                tools = get_available_tools()
                if self.config.get("ai_enabled"):
                    ai_tools = self.ai_extensions.get_ai_tools()
                    tools.extend(ai_tools)
                return {"tools": tools}
            except Exception as e:
                # 如果get_available_tools失败，返回核心引擎的工具
                core_tools = self.engine.get_tools() if hasattr(self.engine, 'get_tools') else []
                return {"tools": core_tools, "error": str(e)}
        
        @self.app.post("/read-file")
        async def read_file(file: UploadFile = File(...)):
            """读取XMind文件"""
            try:
                # 检查文件类型
                if not file.filename.endswith('.xmind'):
                    raise HTTPException(status_code=400, detail="仅支持.xmind文件")
                
                # 保存上传的文件
                temp_dir = "temp_uploads"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # 安全文件名处理
                safe_filename = self.engine._sanitize_filename(file.filename)
                temp_filepath = os.path.join(temp_dir, safe_filename)
                
                # 保存文件
                with open(temp_filepath, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # 读取文件
                result = self.engine.read_xmind_file(temp_filepath)
                
                # 清理临时文件
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                
                return result
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/create-mind-map")
        async def create_mind_map(request: CreateMindMapRequest):
            """创建思维导图"""
            try:
                result = self.engine.create_mind_map(request.title, request.topics_json)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/analyze-mind-map")
        async def analyze_mind_map(file: UploadFile = File(...)):
            """分析思维导图"""
            try:
                # 检查文件类型
                if not file.filename.endswith('.xmind'):
                    raise HTTPException(status_code=400, detail="仅支持.xmind文件")
                
                # 保存上传的文件
                temp_dir = "temp_uploads"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                temp_filepath = os.path.join(temp_dir, file.filename)
                
                # 保存文件
                with open(temp_filepath, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # 分析文件
                result = self.engine.analyze_mind_map(temp_filepath)
                
                # 清理临时文件
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                
                return result
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/convert-to-xmind")
        async def convert_to_xmind(file: UploadFile = File(...)):
            """转换文件为XMind格式"""
            try:
                # 检查文件类型
                allowed_extensions = ['.txt', '.md', '.json', '.xml']
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in allowed_extensions:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"不支持的文件类型。支持的类型: {', '.join(allowed_extensions)}"
                    )
                
                # 保存上传的文件
                temp_dir = "temp_uploads"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                temp_filepath = os.path.join(temp_dir, file.filename)
                
                # 保存文件
                with open(temp_filepath, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # 转换文件
                result = self.engine.convert_to_xmind(temp_filepath)
                
                # 清理临时文件
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                
                return result
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/list-files")
        async def list_files(directory: str = ".", recursive: bool = True):
            """列出XMind文件"""
            try:
                result = self.engine.list_xmind_files(directory, recursive)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/ai-generate-topics")
        async def ai_generate_topics(
            topic: str = Form(...),
            count: int = Form(5),
            style: str = Form("creative")
        ):
            """AI生成主题"""
            if not self.config.get("ai_enabled"):
                raise HTTPException(status_code=400, detail="AI功能已禁用")
            
            # 输入验证
            if not topic or len(topic.strip()) == 0:
                raise HTTPException(status_code=400, detail="主题不能为空")
            
            if count <= 0 or count > 1000:  # 限制生成数量
                raise HTTPException(status_code=400, detail="生成数量必须在1-1000之间")
            
            if style not in ["creative", "analytical", "structured"]:
                raise HTTPException(status_code=400, detail="无效的风格参数")
            
            try:
                result = self.ai_extensions.generate_topics(topic.strip(), count, style)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/ai-optimize-structure")
        async def ai_optimize_structure(
            file: UploadFile = File(...),
            optimization_type: str = Form("balance")
        ):
            """AI优化结构"""
            if not self.config.get("ai_enabled"):
                raise HTTPException(status_code=400, detail="AI功能已禁用")
            
            try:
                # 保存上传的文件
                temp_dir = "temp_uploads"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                temp_filepath = os.path.join(temp_dir, file.filename)
                
                # 保存文件
                with open(temp_filepath, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # 读取文件内容
                read_result = self.engine.read_xmind_file(temp_filepath)
                if read_result["status"] != "success":
                    raise HTTPException(status_code=400, detail="无法读取文件")
                
                # AI优化
                result = self.ai_extensions.optimize_structure(
                    read_result["root_topic"], 
                    optimization_type
                )
                
                # 清理临时文件
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                
                return result
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/batch")
        async def batch_convert(
            files: List[UploadFile] = File(...),
            output_dir: str = Form("output")
        ):
            """批量转换文件为XMind格式"""
            try:
                # 输出目录安全检查
                if not output_dir or not output_dir.strip():
                    output_dir = "output"
                
                # 防止路径遍历攻击
                output_dir = os.path.normpath(output_dir)
                if output_dir.startswith("..") or os.path.isabs(output_dir):
                    output_dir = "output"
                
                # 创建输出目录
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                results = []
                success_count = 0
                
                for file in files:
                    try:
                        # 保存上传的文件
                        temp_dir = "temp_uploads"
                        if not os.path.exists(temp_dir):
                            os.makedirs(temp_dir)
                        
                        # 安全文件名处理
                        safe_filename = self.engine._sanitize_filename(file.filename)
                        temp_filepath = os.path.join(temp_dir, safe_filename)
                        
                        # 保存文件
                        with open(temp_filepath, "wb") as f:
                            content = await file.read()
                            f.write(content)
                        
                        # 转换文件
                        result = self.engine.convert_to_xmind(temp_filepath)
                        
                        # 移动输出文件到指定目录
                        if result["status"] == "success":
                            output_filename = os.path.basename(result["output_file"])
                            final_output_path = os.path.join(output_dir, output_filename)
                            
                            # 如果输出文件存在，移动它
                            if os.path.exists(result["output_file"]):
                                import shutil
                                shutil.move(result["output_file"], final_output_path)
                                result["output_file"] = final_output_path
                            
                            success_count += 1
                        
                        results.append({
                            "filename": file.filename,
                            "status": result["status"],
                            "output_file": result.get("output_file", ""),
                            "error": result.get("error", "")
                        })
                        
                        # 清理临时文件
                        if os.path.exists(temp_filepath):
                            os.remove(temp_filepath)
                            
                    except Exception as e:
                        results.append({
                            "filename": file.filename,
                            "status": "error",
                            "output_file": "",
                            "error": str(e)
                        })
                
                return {
                    "status": "success",
                    "total_count": len(files),
                    "success_count": success_count,
                    "failed_count": len(files) - success_count,
                    "results": results,
                    "output_directory": os.path.abspath(output_dir)
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    def start_server(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
        """启动服务器"""
        if host is None:
            host = self.config.get("host", "localhost")
        if port is None:
            port = self.config.get("port", 8080)
        if debug is None:
            debug = self.config.get("debug", False)
        
        # 创建应用
        app = self.create_app()
        
        # 启动服务器
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info" if not debug else "debug"
        )
    
    def main(self):
        """主函数"""
        import argparse
        
        parser = argparse.ArgumentParser(description="XMind MCP Server")
        parser.add_argument("--host", default=None, help="主机地址")
        parser.add_argument("--port", type=int, default=None, help="端口")
        parser.add_argument("--debug", action="store_true", help="调试模式")
        parser.add_argument("--config", help="配置文件路径")
        
        args = parser.parse_args()
        
        # 加载自定义配置
        if args.config:
            try:
                with open(args.config, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    self.config.update(custom_config)
            except Exception as e:
                print(f"警告: 无法加载自定义配置文件 {args.config}: {e}")
        
        print(f"正在启动 XMind MCP Server...")
        print(f"配置: host={args.host or self.config.get('host', 'localhost')}, port={args.port or self.config.get('port', 8080)}")
        print(f"AI功能: {'启用' if self.config.get('ai_enabled') else '禁用'}")
        print(f"文档: http://{args.host or self.config.get('host', 'localhost')}:{args.port or self.config.get('port', 8080)}/docs")
        
        try:
            self.start_server(host=args.host, port=args.port, debug=args.debug)
        except KeyboardInterrupt:
            print("\n服务器已停止")
        except Exception as e:
            print(f"服务器启动失败: {e}")
            sys.exit(1)


if __name__ == "__main__":
    server = XMindMCPServer()
    server.main()