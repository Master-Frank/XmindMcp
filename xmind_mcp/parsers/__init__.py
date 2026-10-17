"""Input adapters, independently usable without MCP."""
from .base import BaseParser
from .registry import ParserRegistry

__all__ = ["BaseParser", "ParserRegistry"]
