"""XMind MCP package. Importing it never starts or configures an application."""
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib

try:
    __version__ = version("xmind-mcp")
except PackageNotFoundError:
    try:
        __version__ = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())["project"]["version"]
    except (OSError, KeyError):
        __version__ = "0.0.0"


__all__ = ["__version__"]
