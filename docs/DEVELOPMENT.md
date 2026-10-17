# 开发与发布

[返回文档导航](README.md)

## 本地开发

项目要求 Python 3.11+。在仓库根目录创建环境并安装开发测试依赖：

```bash
uv venv --python 3.12
uv pip install -e '.[test]'
```

macOS/Linux 使用 `.venv/bin/python`；Windows 使用 `.venv/Scripts/python.exe`。以下命令以 macOS/Linux 为例：

```bash
.venv/bin/python -m xmind_mcp --help
.venv/bin/python -m xmind_mcp --stdio --default-output-dir /absolute/path/to/output
```

日常 MCP 客户端连接配置见 [使用指南](USAGE_GUIDE.md)。包内接口与依赖注入示例见 [架构说明](ARCHITECTURE.md)。

## 测试

```bash
.venv/bin/python tests/run_all_tests.py -q
.venv/bin/python tests/run_all_tests.py tests/test_architecture.py -q
.venv/bin/python tests/run_all_tests.py -q --report-file output/test-report.json
```

统一入口以 pytest 的退出码判断成功，JSON 报告记录实际测试结果。主要测试分为：

| 文件 | 覆盖内容 |
| --- | --- |
| `tests/test_regressions.py` | 并发创建、原子写入、预算、解析回退、层级及测试退出码 |
| `tests/test_mcp_protocol.py` | 实际 STDIO 子进程、新旧协议、工具调用及启动参数兼容 |
| `tests/test_architecture.py` | 导入副作用、配置隔离、解析器注册、统一模型、翻译器注入及包边界 |
| `tests/test_workflows.py` | 测试/发布依赖、产物传递、发布分支条件及缺失凭据处理 |
| `tests/test_release_version.py` | 补丁版本规划、PyPI 异常处理及工作区版本更新 |
| `tests/check_distribution.py` | 从构建 wheel 加载模块，在源码目录外验证 MCP 启动入口和工具调用 |

测试直接使用 `xmind_mcp` 包内接口。旧根目录兼容模块及依赖它们的 HTTP 演示、模拟检查脚本已删除。

## 构建与分发验证

```bash
uv build
.venv/bin/python tests/check_distribution.py dist/*.whl
```

`uv build` 生成源代码包和 wheel。分发检查使用当前解释器中的依赖，但从 wheel 解压目录加载本项目，并验证现代/旧协议的工具调用。若 `dist` 中有多个历史 wheel，应传入本次构建的具体文件路径。

CI 与发布统一在 `.github/workflows/publish-pypi.yml`，不再有独立的测试工作流。

| 触发事件 | 行为 |
| --- | --- |
| 推送任意分支 | 在 Python 3.11、3.12、3.13 上运行单元/协议测试、构建、Twine 元数据检查和 wheel 验证 |
| Pull Request | 执行相同检查，不发布 |
| 推送 `main` | 所有矩阵测试通过后，自动发布已验证的分发包 |
| 在 `main` 手动运行工作流 | 先跑完整检查，再发布；其他分支手动运行只检查 |

发布任务通过 `needs: [prepare, test]` 等待版本规划及整个测试矩阵成功。Python 3.12 任务将验证后的 `dist/` 上传为工作流产物，发布任务直接下载并上传这一份文件，不重新构建。任一检查失败时，发布任务跳过。

发布条件还限定仓库为 `Master-Frank/XmindMcp`；Fork 只运行检查。工作流按分支串行执行，覆盖版本规划、测试到发布全过程，避免同时选择相同版本。Git 标签推送不触发这条流程。GitHub 默认只保留一个运行中和一个等待中的流程，连续推送可能替换较早的等待流程，以 Actions 实际执行的提交为准。

## 版本管理与发布

### 版本来源

源码中的版本基线维护在 `pyproject.toml` 的 `[project].version`，使用稳定的 `MAJOR.MINOR.PATCH` 格式。正式发布的版本由流水线自动规划；普通分支和 PR 测试仍使用源码版本。

运行时通过 `xmind_mcp.__version__` 获取版本：优先读取安装元数据，未安装时回退读取源码配置。发布产物及安装后的包显示 CI 选定的发布版本；源码版本不自动回写仓库。

Python 安装与命令入口以 `pyproject.toml` 为准；根目录 `package.json` 是辅助脚本描述，不作为 Python 包的版本来源。

### 首次启用自动发布

1. 在 PyPI 创建对 `xmind-mcp` 有发布权限的 API Token，或使用已有有效 Token。
2. 在 [仓库 Actions Secrets](https://github.com/Master-Frank/XmindMcp/settings/secrets/actions) 添加 Repository secret：名称为 `PYPI_API_TOKEN`，值为完整 Token。已有同名有效配置时无需重复添加。
3. 确认仓库已启用 GitHub Actions，且允许使用工作流中的 GitHub 官方 Actions 和 `pypa/gh-action-pypi-publish`。
4. 提交本次代码和工作流，推送到 `main`；也可以通过 PR 合并到 `main`。无需手动增加补丁版本号。
5. 在 [Actions](https://github.com/Master-Frank/XmindMcp/actions) 查看 `Test and publish to PyPI`：三个测试任务成功后，应出现成功的发布任务。

凭据只提供给测试通过后的发布任务；未设置时，该任务明确报错提示配置 `PYPI_API_TOKEN`。本地代码无法验证远端 Secret 是否已经设置或 Token 是否有效。

### 自动版本递增与日常发布

主分支推送或在主分支手动触发完整工作流时：

1. `prepare` 读取 PyPI 发布记录，忽略预发布和开发版本。
2. 若源码版本比已发布稳定版本更新，使用源码版本；否则将最新稳定版本的补丁号加一。例如已发布 `1.3.9` 时，下一次发布为 `1.3.10`。
3. 所有测试任务先在各自 CI 工作区应用同一个版本，再安装、测试和构建，发布这一份验证过的产物。
4. 不向 `main` 提交版本号变更，也不需要机器人向仓库推送的权限。

因此日常只需要推送或合并代码到 `main`。若要主动升级主版本或次版本，例如从 `1.3.x` 升至 `2.0.0`，再手动提高源码中的版本基线。PyPI 项目尚不存在时，首次使用源码版本；PyPI 查询失败时停止流程，不猜测版本。

发布 Action 保留 `skip-existing: true`，用于重试时跳过已上传文件。若同一次上传部分失败，使用 Actions 的 **Re-run failed jobs** 重试，继续使用原来规划的版本；手动 **Run workflow** 是一次新发布，会重新规划版本。

此流程使用 PyPI API Token，通过 `password` 输入传给发布 Action；产物目录和重复文件选项使用 `packages-dir`、`skip-existing`。

版本脚本可在本地只读预览下一次版本，不修改仓库或上传文件：

```bash
.venv/bin/python .github/scripts/release_version.py plan --release
```

### 本地发布

先完成测试与分发验证，准备好本次版本的分发文件，再使用 Twine：

```bash
uv tool run --from twine twine check dist/*
uv tool run --from twine twine upload dist/*
```

上传使用环境变量 `TWINE_USERNAME=__token__`、`TWINE_PASSWORD` 或本机凭据配置。项目既有的 `configs/.pypi-token.env` 已列入 `.gitignore`，如使用该方式，需在本机显式加载到环境变量；文档不保存实际 Token。

### 发布后确认

```bash
uvx --refresh xmind-mcp --version
```

确认显示目标版本，并使用 [使用指南](USAGE_GUIDE.md) 的配置连接已发布包。若没有出现新版本，检查 `prepare` 规划的版本及测试/发布任务状态；若上传鉴权失败，检查本机凭据或仓库 Secret。

相关机制参考：[GitHub 工作流产物与任务依赖](https://docs.github.com/en/actions/tutorials/store-and-share-data)、[PyPA 发布 Action](https://github.com/pypa/gh-action-pypi-publish)。
