# Render自动部署检查清单

## 📋 基于官方文档的关键检查点

根据Render官方文档，自动部署需要满足以下条件：

### ✅ 官方要求检查
1. **服务类型支持**：Web服务支持自动部署（✅ 你的服务是web类型）
2. **Git分支链接**：服务必须链接到GitHub仓库的特定分支（通常是main）
3. **自动部署设置**：Render Dashboard中必须启用自动部署
4. **GitHub集成**：Render账户必须正确连接GitHub

### 🚫 不支持自动部署的情况
- 拉取预构建Docker镜像的服务（❌ 不适用，你是Dockerfile构建）
- 手动禁用自动部署（需要检查设置）

## 🔍 问题诊断

### 1. Render端检查

#### 检查自动部署设置
1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 找到你的服务 `xmind-mcp-server`
3. 点击 "Settings" 标签
4. 检查 "Auto Deploy" 设置：
   - ✅ 应该显示为 "Yes"
   - ❌ 如果显示为 "No"，点击切换为启用状态

#### 检查GitHub连接
1. 在Render Dashboard中
2. 点击右上角头像 → "Account Settings"
3. 点击 "GitHub" 标签
4. 确认GitHub连接状态：
   - ✅ 显示 "Connected to GitHub"
   - ❌ 如果未连接，点击 "Connect to GitHub"

#### 检查部署触发
1. 在Render Dashboard中查看你的服务
2. 点击 "Events" 标签
3. 查看最近的部署事件：
   - 应该能看到 "Deploy triggered by push to main branch"
   - 如果没有，可能是连接问题

### 2. GitHub端检查

#### 检查Webhook配置
1. 访问你的GitHub仓库：[https://github.com/Master-Frank/XmindMcp](https://github.com/Master-Frank/XmindMcp)
2. 点击 "Settings" → "Webhooks"
3. 应该能看到Render的webhook：
   - URL: `https://api.render.com/deploy/...`
   - 最近推送应该有绿色勾选标记

#### 检查最近推送
1. 在GitHub仓库页面
2. 点击 "Actions" 标签
3. 查看是否有工作流运行记录

### 3. 官方文档提到的跳过部署情况

根据官方文档，以下情况会自动跳过部署：

#### 跳过短语检查
检查你的提交消息是否包含以下跳过短语：
- `[skip render]` 或 `[render skip]`
- `[skip deploy]` 或 `[deploy skip]`
- `[skip cd]` 或 `[cd skip]`

#### CI检查失败
如果你的仓库配置了CI检查：
- 当Render Dashboard设置为"After CI Checks Pass"时
- 任何CI检查失败都会阻止部署
- 零个检查检测到时也不会触发部署

### 4. 手动触发部署

如果自动部署不工作，可以手动触发：

#### 方法1：通过Render Dashboard（推荐）
1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 找到你的服务
3. 点击 "Manual Deploy" → "Deploy latest commit"

#### 方法2：通过GitHub Actions
1. 访问GitHub仓库的Actions页面
2. 点击 "Deploy to Render" 工作流
3. 点击 "Run workflow" → 选择 "Deploy"

#### 方法3：通过Render API
```bash
# 需要RENDER_API_KEY和RENDER_SERVICE_ID
curl -X POST \
  -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"clearCache": "clear"}' \
  "https://api.render.com/v1/services/YOUR_SERVICE_ID/deploys"
```

## 🛠️ 解决方案

### 方案1：检查跳过部署原因
根据官方文档，检查最近的提交消息：
```bash
git log --oneline -10
```
查看是否包含跳过短语如 `[skip render]` 等

### 方案2：重新连接GitHub
1. 在Render Dashboard中断开GitHub连接
2. 重新连接GitHub并授权
3. 重新创建服务

### 方案3：手动配置Webhook
1. 在Render Dashboard中找到服务的webhook URL
2. 在GitHub仓库设置中添加webhook
3. 设置触发事件为 "Push events"

### 方案4：使用GitHub Actions（最可靠）
确保以下Secrets已配置：
- `RENDER_API_KEY`: 从Render账户设置获取
- `RENDER_SERVICE_ID`: 从服务URL中获取

### 方案5：检查自动部署设置
在Render Dashboard中检查：
- **On Commit**: 推送立即部署（默认）
- **After CI Checks Pass**: 等待CI检查通过
- **Off**: 禁用自动部署

建议设置为 "On Commit" 避免CI检查问题

## 📋 验证步骤

1. **检查提交历史**：确认没有跳过部署的短语 ✅
2. **查看GitHub Actions**：访问仓库的Actions页面
3. **监控Render Dashboard**：观察服务状态变化
4. **检查部署日志**：在Render Dashboard中查看部署日志

## 🧪 当前测试状态

✅ **刚刚推送测试提交**（commit: `Test auto-deploy: Add deployment test file`）
✅ **提交消息无跳过短语**
✅ **GitHub推送成功**（main → main）
⏳ **等待Render响应**（通常需要1-3分钟）

## 🔧 立即行动建议

### 优先级1：立即检查（1-3分钟内）
1. **登录Render Dashboard**：[https://dashboard.render.com](https://dashboard.render.com)
2. **查看服务状态**：观察是否显示 "Deploying" 或新的部署记录
3. **检查GitHub Actions**：访问 [https://github.com/Master-Frank/XmindMcp/actions](https://github.com/Master-Frank/XmindMcp/actions)

### 优先级2：如果3分钟内无响应
1. **检查Auto Deploy设置**：在Render服务设置中确认状态
2. **手动触发部署**：使用Dashboard的 "Manual Deploy"
3. **检查GitHub集成**：确认Render账户的GitHub连接状态

### 优先级3：长期解决方案
1. **配置GitHub Secrets**（最可靠的方法）
2. **重新连接GitHub仓库**
3. **使用Webhook手动配置**

## 🆘 联系支持

如果以上方法都不奏效：

1. **Render支持**: [help.render.com](https://help.render.com)
2. **查看服务日志**: Render Dashboard → 你的服务 → "Logs"
3. **GitHub状态**: [www.githubstatus.com](https://www.githubstatus.com)

---

**当前状态**: 🔄 等待检查中...