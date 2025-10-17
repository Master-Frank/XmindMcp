# Railway一键部署按钮代码

## 部署按钮HTML代码
```html
<a href="https://railway.app/new/template?template=https://github.com/Master-Frank/XmindMcp&envs=PORT,ENVIRONMENT,DEBUG">
  <img src="https://railway.app/button.svg" alt="Deploy on Railway" />
</a>
```

## 部署按钮Markdown代码### Markdown格式
```markdown
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Master-Frank/XmindMcp&envs=PORT,ENVIRONMENT,DEBUG)
```
## 环境变量说明
- `PORT`: 服务器端口（默认8080）
- `ENVIRONMENT`: 运行环境（production/production）

## 部署URL参数
```
https://railway.app/new/template?
  template=https%3A%2F%2Fgithub.com%2FMaster-Frank%2FXmindMcp&
  envs=PORT%2CENVIRONMENT&
  PORT=8080&
  ENVIRONMENT=production
```

## 自定义部署按钮
你可以自定义按钮样式，例如：

```html
<a href="https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FMaster-Frank%2FXmindMcp">
  <button style="background-color: #0f172a; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
    🚄 Deploy to Railway
  </button>
</a>
```