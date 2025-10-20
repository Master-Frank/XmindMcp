"""
XMind MCP Package

智能思维导图操作和转换的MCP服务器包。
"""



# xmind_mcp package initialization

# Unified version resolution: prefer installed metadata, fallback to local pyproject
try:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError
except Exception:  # pragma: no cover
    # For very old Python versions, importlib_metadata may be available
    try:
        from importlib_metadata import version as _pkg_version, PackageNotFoundError  # type: ignore
    except Exception:
        _pkg_version = None
        PackageNotFoundError = Exception  # type: ignore

__version__ = "0.0.0"

if _pkg_version is not None:
    try:
        __version__ = _pkg_version("xmind-mcp")
    except PackageNotFoundError:  # not installed, likely local dev
        try:
            import os
            import re
            root_dir = os.path.dirname(os.path.dirname(__file__))
            pyproject_path = os.path.join(root_dir, "pyproject.toml")
            with open(pyproject_path, "r", encoding="utf-8") as f:
                pyproject_content = f.read()
            # Robust but simple regex for version = "X.Y.Z"
            m = re.search(r"^version\s*=\s*\"([0-9]+\.[0-9]+\.[0-9]+)\"", pyproject_content, re.MULTILINE)
            if m:
                __version__ = m.group(1)
        except Exception:
            # Keep default "0.0.0" when resolution fails
            pass

# 从主服务器模块导入main函数，支持uvx运行
try:
    from xmind_mcp_server import main
    __all__ = ["__version__", "main"]
except ImportError:
    # 如果导入失败，只导出版本
    __all__ = ["__version__"]