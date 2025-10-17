#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保活脚本 - 防止Render免费层休眠
定期访问自身的健康检查端点，保持服务活跃
"""

import asyncio
import aiohttp
import os
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self):
        self.port = int(os.environ.get("PORT", 8080))
        self.host = "0.0.0.0"
        self.base_url = f"http://{self.host}:{self.port}"
        self.health_endpoint = f"{self.base_url}/health"
        self.interval = 300  # 5分钟检查一次（避免15分钟休眠）
        self.timeout = 10   # 请求超时时间
        
    async def check_health(self):
        """检查服务健康状态"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(self.health_endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ 健康检查成功: {data.get('status', 'unknown')}")
                        return True
                    else:
                        logger.warning(f"⚠️  健康检查返回状态码: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ 健康检查失败: {e}")
            return False
    
    async def keep_alive_loop(self):
        """保活循环"""
        logger.info(f"🚀 启动保活服务 - 每{self.interval}秒检查一次")
        logger.info(f"📍 健康检查端点: {self.health_endpoint}")
        
        while True:
            try:
                await self.check_health()
                await asyncio.sleep(self.interval)
            except KeyboardInterrupt:
                logger.info("⏹️  保活服务已停止")
                break
            except Exception as e:
                logger.error(f"保活循环异常: {e}")
                await asyncio.sleep(self.interval)
    
    def run(self):
        """运行保活服务"""
        try:
            asyncio.run(self.keep_alive_loop())
        except KeyboardInterrupt:
            logger.info("保活服务已停止")

async def single_health_check():
    """单次健康检查（用于测试）"""
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    health_endpoint = f"http://{host}:{port}/health"
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(health_endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 服务健康: {data}")
                    return True
                else:
                    print(f"⚠️  服务异常: 状态码 {response.status}")
                    return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # 单次检查模式
        asyncio.run(single_health_check())
    else:
        # 保活模式
        service = KeepAliveService()
        service.run()