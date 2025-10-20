# XMind MCP 发布与版本管理指南

本文档说明版本号的统一管理、PyPI 凭据放置方式，以及 GitHub Actions 发布流程的使用方法。

## 版本号统一管理

- 单一真源：`pyproject.toml` 的 `[project] version` 字段（例如 `1.1.8`）。
- 代码引用：统一通过 `xmind_mcp.__version__` 获取版本号。
  - 包内 `__init__.py` 优先使用已安装的包元数据；在本地开发环境下回退读取 `pyproject.toml`。
- 冗余移除：已删除根目录的 `_version.py`，避免多处维护导致不一致。
- 更新版本流程：
  - 修改 `pyproject.toml` 中的 `version`（遵循语义化版本，如 `MAJOR.MINOR.PATCH`）。
  - 提交变更并推送：`git commit -m "chore: bump version to X.Y.Z" && git push`。
  - 如需通过 CI 发布，建议打标签：`git tag vX.Y.Z && git push origin vX.Y.Z`（工作流会校验标签与 `pyproject` 版本一致）。

## 凭据配置（仅 PyPI）

- 本地凭据文件：`configs/.pypi-token.env`
  - 已加入 `.gitignore`，不会被提交。
  - 内容示例：
    ```env
    TWINE_USERNAME=__token__
    TWINE_PASSWORD=pypi-XXXXX...  # 你的 PyPI API Token
    ```
- GitHub 仓库 Secrets：`PYPI_API_TOKEN`
  - 用于 CI 工作流上传到 PyPI。
  - 值为同一个 PyPI API Token，配置路径：GitHub 仓库 → Settings → Secrets and variables → Actions。

## GitHub Actions 发布流程

- 工作流文件：`/.github/workflows/publish-pypi.yml`
- 触发方式：
  - 手动触发：`workflow_dispatch`
  - 推送标签：以 `v*` 为前缀的标签（例如 `v1.1.9`）
- 核心步骤：
  - 设置 Python 3.12 环境并安装构建依赖（`build`）。
  - 若由标签触发，校验 `pyproject.toml` 的 `version` 与标签一致（去掉前导 `v` 后比较）。
  - 构建分发包：`python -m build` 生成 `dist/*`。
  - 发布到 PyPI：`pypa/gh-action-pypi-publish@release/v1`，凭据取自 `secrets.PYPI_API_TOKEN`，并启用 `skip_existing`。

## 本地发布到 PyPI

- 前置：确保 `configs/.pypi-token.env` 已包含有效 token，且 `.gitignore` 已忽略该文件。
- 在 PowerShell 中加载环境变量：
  ```powershell
  Get-Content configs\.pypi-token.env | ForEach-Object {
    $kv = $_.Split('='); [System.Environment]::SetEnvironmentVariable($kv[0], $kv[1])
  }
  ```
- 构建与上传：
  ```powershell
  python -m pip install --upgrade pip build twine
  python -m build
  python -m twine upload --repository pypi dist/*
  ```

## 校验与回滚

- 发布后校验：
  - `pip install xmind-mcp` 并在 Python 中：
    ```python
    import xmind_mcp
    print(xmind_mcp.__version__)
    ```
- 若需要回滚：
  - 在 PyPI 不能覆盖已存在版本，需提升版本号重新发布。
  - Git 标签可删除重新打，但建议保持语义化版本递增。

## 版本规范建议

- 遵循语义化版本：
  - `MAJOR`：重大变更或不兼容改动
  - `MINOR`：新增功能，保持兼容
  - `PATCH`：修复与兼容性小改动
- 发布前检查：
  - 版本是否在 `pyproject.toml` 正确更新
  - 依赖是否完整（含 `mcp[cli]>=1.3.0`）
  - 运行测试：`python tests/run_all_tests.py`

## 常见问题

- 标签与版本不一致导致工作流失败：
  - 解决：修改 `pyproject.toml` 或重新打标签一致的版本（例如 `v1.1.9`）。
- 凭据未生效：
  - 本地：确认 PowerShell 已正确加载 `.pypi-token.env`。
  - CI：确认仓库 Secrets 已设置 `PYPI_API_TOKEN` 且未过期。

——
以上设置后：
- 版本号仅维护在 `pyproject.toml`，代码运行时统一读取；
- 本地可通过 `.pypi-token.env` 进行发布；
- CI 可通过标签或手动触发自动构建并发布到 PyPI。