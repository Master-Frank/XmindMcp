# 🔄 XMind MCP 工作流触发器配置指南

## 当前工作流概览

基于 `.github/workflows/unified-deploy.yml`，项目已配置了统一的部署工作流，支持多种触发方式：

### 1. 自动触发器

#### Push 触发
```yaml
on:
  push:
    branches: [ main ]
```
- **触发时机**: 代码推送到 main 分支时
- **执行内容**: 完整的 Python 测试 + Docker 构建 + GitHub Pages 部署
- **适用场景**: 主分支代码更新，需要完整部署流程

#### Pull Request 触发
```yaml
on:
  pull_request:
    branches: [ main ]
```
- **触发时机**: 向 main 分支发起 PR 时
- **执行内容**: 仅 Python 测试（安全考虑）
- **适用场景**: 代码审查阶段，验证功能完整性

### 2. 手动触发器（推荐）

#### 工作流分发（workflow_dispatch）
```yaml
on:
  workflow_dispatch:
    inputs:
      deploy_type:
        description: 'Deployment type'
        required: true
        default: 'all'
        type: choice
        options:
          - all          # 完整部署
          - python-only  # 仅 Python 测试
          - docker-only  # 仅 Docker 构建
          - pages-only   # 仅 GitHub Pages
```

**使用方法**:
1. 进入 GitHub 仓库 → Actions 标签页
2. 选择 "🚀 Unified Deploy" 工作流
3. 点击 "Run workflow" 按钮
4. 选择部署类型：
   - `all`: 完整部署流程（默认）
   - `python-only`: 仅测试 Python 服务器
   - `docker-only`: 仅构建和推送 Docker 镜像
   - `pages-only`: 仅部署 GitHub Pages

### 3. 工作流作业详解

#### Python 部署作业（python-deploy）
**触发条件**: 所有情况都会执行
**执行步骤**:
1. Python 3.9 环境配置
2. 依赖缓存和安装
3. 服务器启动验证（30秒超时）
4. 核心功能测试
5. 生成部署摘要

#### Docker 构建作业（docker-build）
**触发条件**: 
- 部署类型为 `all` 或 `docker-only`
- 当前分支为 main
- 配置了 Docker Hub 凭据

**执行步骤**:
1. Docker Buildx 设置
2. Docker Hub 登录（可选）
3. 多架构镜像构建（linux/amd64, linux/arm64）
4. 镜像测试
5. 推送到 Docker Hub

#### GitHub Pages 部署作业（deploy-pages）
**触发条件**:
- 部署类型为 `all` 或 `pages-only`
- 当前分支为 main

**执行步骤**:
1. Pages 环境配置
2. 构建静态文件
3. 部署到 GitHub Pages
4. 生成访问链接

## 🚀 推荐触发策略

### 开发阶段
```bash
# 手动触发 Python 测试
deploy_type: python-only
```

### 发布阶段
```bash
# 完整部署流程
deploy_type: all
```

### 文档更新
```bash
# 仅更新 GitHub Pages
deploy_type: pages-only
```

### Docker 镜像更新
```bash
# 仅构建 Docker 镜像
deploy_type: docker-only
```

## 🔧 环境配置要求

### 必需环境变量
- 无（基础功能不需要特殊配置）

### 可选环境变量
```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: masterfrank/xmind-mcp-server
```

### Docker Hub 凭据（可选）
需要在 GitHub 仓库设置中添加：
- `DOCKER_USERNAME`: Docker Hub 用户名
- `DOCKER_PASSWORD`: Docker Hub 密码/访问令牌

## 📊 触发器对比

| 触发方式 | 自动执行 | 手动控制 | 适用场景 | 执行时间 |
|---------|---------|----------|----------|----------|
| Push 触发 | ✅ | ❌ | 主分支更新 | ~3-5分钟 |
| PR 触发 | ✅ | ❌ | 代码审查 | ~2-3分钟 |
| Manual 触发 | ❌ | ✅ | 精确控制 | 可变 |

## 🎯 最佳实践建议

### 1. 日常开发
- 使用 PR 触发进行代码验证
- 合并后自动部署到主分支

### 2. 紧急修复
- 使用手动触发，选择 `python-only` 快速验证
- 确认无误后执行 `all` 完整部署

### 3. 文档更新
- 使用 `pages-only` 避免不必要的构建

### 4. Docker 发布
- 配置好凭据后使用 `docker-only`
- 支持多架构构建，适合生产环境

## 🔍 故障排查

### 常见问题

#### Python 测试失败
- 检查依赖安装是否成功
- 验证端口 8080 是否被占用
- 查看具体错误日志定位问题

#### Docker 构建失败
- 确认 Docker Hub 凭据是否正确
- 检查网络连接状态
- 验证 Dockerfile 语法

#### GitHub Pages 部署失败
- 确认 Pages 服务已启用
- 检查分支权限设置
- 验证静态文件路径

### 日志查看
1. 进入 GitHub 仓库 → Actions 标签页
2. 点击对应的工作流运行记录
3. 展开失败的作业步骤查看详细日志

## 🔗 相关链接

- [GitHub Actions 文档](https://docs.github.com/actions)
- [工作流文件参考](.github/workflows/unified-deploy.yml)
- [部署指南](CLOUD_USAGE.md)