"""Pure document analysis, shared by every application entry point."""
from .models import Document, collect_stats


def analyze_document(document: Document):
    stats = collect_stats(document.root)
    nodes = stats.total_nodes
    complexity = "简单" if nodes < 10 else "中等" if nodes < 30 else "复杂" if nodes < 60 else "非常复杂"
    branches = stats.branch_count
    balance = "优秀" if branches <= 3 else "良好" if branches <= 5 else "一般"
    suggestions = []
    if stats.max_depth > 4:
        suggestions.append("建议减少层级深度，保持3-4层最佳")
    if nodes > 50:
        suggestions.append("节点较多，考虑拆分为多个思维导图")
    return {"complexity": complexity, "balance": balance, "completeness": "完整",
            "suggestions": suggestions or ["结构良好，无需优化"]}, stats
