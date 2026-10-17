"""Explicit, immutable settings; environment reads happen at application creation."""
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Mapping
import os
import re

from .errors import XMindError
from .models import ReadLimits


@dataclass(frozen=True)
class Settings:
    base_dir: Path = field(default_factory=Path.cwd)
    default_output_dir: Path | None = field(default_factory=lambda: Path.home() / "Documents" / "XmindOutput")
    read_limits: ReadLimits = field(default_factory=ReadLimits)

    def __post_init__(self):
        base = Path(self.base_dir)
        if not base.is_absolute():
            raise ValueError("基准目录必须为绝对路径")
        object.__setattr__(self, "base_dir", base)
        output = Path(self.default_output_dir) if self.default_output_dir is not None else Path.home() / "Documents" / "XmindOutput"
        if not output.is_absolute():
            raise ValueError("默认输出目录必须为绝对路径")
        object.__setattr__(self, "default_output_dir", output)

    @classmethod
    def from_env(cls, default_output_dir=None, environ: Mapping | None = None):
        env = os.environ if environ is None else environ
        configured_base = env.get("XMIND_MCP_BASE_DIR")
        base = Path(configured_base) if configured_base and Path(configured_base).is_absolute() else Path.cwd()
        selected = None
        for candidate in (default_output_dir, env.get("XMIND_MCP_DEFAULT_OUTPUT_DIR")):
            if candidate:
                path = Path(candidate)
                if path.is_absolute():
                    selected = path
                    break
                if configured_base and Path(configured_base).is_absolute():
                    selected = base / path
                    break

        def integer(name, default, minimum):
            try:
                return max(minimum, int(env.get(name, default)))
            except (TypeError, ValueError):
                return default

        limits = ReadLimits(integer("XMIND_MAX_FILE_SIZE_MB", 200, 1) * 1024 * 1024,
                            integer("XMIND_MAX_NODE_COUNT", 50000, 1),
                            integer("XMIND_MAX_PARSE_DEPTH", 30, 0))
        settings = cls(base, selected, limits)
        settings.default_output_dir.mkdir(parents=True, exist_ok=True)
        return settings

    def input_path(self, value, *, require_absolute=False) -> Path:
        if not value:
            raise XMindError("文件路径不能为空")
        path = Path(value)
        if require_absolute and not path.is_absolute():
            raise XMindError("必须为绝对路径")
        return path if path.is_absolute() else self.base_dir / path

    def output_path(self, value, default_filename) -> Path:
        if value:
            path = Path(value)
            if not path.is_absolute():
                raise XMindError("输出路径必须为绝对路径")
        else:
            path = self.default_output_dir / default_filename
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


def sanitize_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', title).strip()[:100]
    return (name or "untitled").replace(' ', '_')
