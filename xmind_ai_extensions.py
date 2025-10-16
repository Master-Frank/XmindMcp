#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind AI扩展功能模块
提供AI驱动的思维导图增强功能
"""

import json
import re
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 假设OpenAI API可用
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIFunction(Enum):
    """AI功能枚举"""
    GENERATE_TOPICS = "generate_topics"
    OPTIMIZE_STRUCTURE = "optimize_structure"
    SUGGEST_IMPROVEMENTS = "suggest_improvements"
    CATEGORIZE_CONTENT = "categorize_content"
    EXTRACT_KEYWORDS = "extract_keywords"
    GENERATE_SUMMARY = "generate_summary"


@dataclass
class AITopic:
    """AI生成的主题"""
    title: str
    description: Optional[str] = None
    priority: int = 1
    relevance_score: float = 0.8
    subtopics: List['AITopic'] = None
    
    def __post_init__(self):
        if self.subtopics is None:
            self.subtopics = []


@dataclass
class AIMindMapAnalysis:
    """AI思维导图分析结果"""
    complexity_score: float
    balance_score: float
    completeness_score: float
    overall_quality: str
    suggestions: List[str]
    optimization_opportunities: List[str]
    structural_issues: List[str]


class XMindAIExtensions:
    """XMind AI扩展功能类"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.openai_client = None
        
        if OPENAI_AVAILABLE and api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
    
    def is_ai_available(self) -> bool:
        """检查AI功能是否可用"""
        return OPENAI_AVAILABLE and self.openai_client is not None
    
    async def generate_topics(
        self, 
        context: str, 
        existing_topics: List[str] = None,
        max_topics: int = 10,
        creativity_level: float = 0.7
    ) -> List[AITopic]:
        """基于上下文生成相关主题"""
        if not self.is_ai_available():
            return self._generate_fallback_topics(context, max_topics)
        
        try:
            prompt = self._build_topic_generation_prompt(
                context, existing_topics, max_topics, creativity_level
            )
            
            response = await self._call_openai_api(prompt)
            return self._parse_generated_topics(response)
            
        except Exception as e:
            print(f"AI主题生成失败: {e}")
            return self._generate_fallback_topics(context, max_topics)
    
    async def optimize_structure(
        self, 
        mind_map_data: Dict[str, Any],
        optimization_goals: List[str] = None
    ) -> Dict[str, Any]:
        """优化思维导图结构"""
        if not self.is_ai_available():
            return self._basic_structure_optimization(mind_map_data)
        
        try:
            prompt = self._build_structure_optimization_prompt(
                mind_map_data, optimization_goals
            )
            
            response = await self._call_openai_api(prompt)
            return self._parse_optimized_structure(response)
            
        except Exception as e:
            print(f"AI结构优化失败: {e}")
            return self._basic_structure_optimization(mind_map_data)
    
    async def analyze_mind_map_quality(
        self, 
        mind_map_data: Dict[str, Any]
    ) -> AIMindMapAnalysis:
        """分析思维导图质量"""
        if not self.is_ai_available():
            return self._basic_quality_analysis(mind_map_data)
        
        try:
            prompt = self._build_quality_analysis_prompt(mind_map_data)
            response = await self._call_openai_api(prompt)
            return self._parse_quality_analysis(response)
            
        except Exception as e:
            print(f"AI质量分析失败: {e}")
            return self._basic_quality_analysis(mind_map_data)
    
    async def suggest_improvements(
        self, 
        mind_map_data: Dict[str, Any],
        focus_areas: List[str] = None
    ) -> List[str]:
        """提供改进建议"""
        if not self.is_ai_available():
            return self._generate_basic_suggestions(mind_map_data)
        
        try:
            prompt = self._build_improvement_suggestions_prompt(
                mind_map_data, focus_areas
            )
            
            response = await self._call_openai_api(prompt)
            return self._parse_improvement_suggestions(response)
            
        except Exception as e:
            print(f"AI改进建议生成失败: {e}")
            return self._generate_basic_suggestions(mind_map_data)
    
    async def categorize_content(
        self, 
        content: str,
        category_definitions: Dict[str, str] = None
    ) -> Dict[str, List[str]]:
        """对内容进行智能分类"""
        if not self.is_ai_available():
            return self._basic_content_categorization(content)
        
        try:
            prompt = self._build_content_categorization_prompt(
                content, category_definitions
            )
            
            response = await self._call_openai_api(prompt)
            return self._parse_content_categories(response)
            
        except Exception as e:
            print(f"AI内容分类失败: {e}")
            return self._basic_content_categorization(content)
    
    async def extract_keywords(
        self, 
        content: str,
        max_keywords: int = 10
    ) -> List[str]:
        """提取关键词"""
        if not self.is_ai_available():
            return self._basic_keyword_extraction(content, max_keywords)
        
        try:
            prompt = self._build_keyword_extraction_prompt(content, max_keywords)
            response = await self._call_openai_api(prompt)
            return self._parse_extracted_keywords(response)
            
        except Exception as e:
            print(f"AI关键词提取失败: {e}")
            return self._basic_keyword_extraction(content, max_keywords)
    
    def get_ai_tools(self) -> List[Dict[str, Any]]:
        """获取AI工具列表"""
        return [
            {
                "name": "ai_generate_topics",
                "description": "AI生成思维导图主题",
                "endpoint": "/ai-generate-topics",
                "method": "POST",
                "parameters": {
                    "topic": "主题",
                    "count": "生成数量",
                    "style": "风格"
                }
            },
            {
                "name": "ai_optimize_structure",
                "description": "AI优化思维导图结构",
                "endpoint": "/ai-optimize-structure",
                "method": "POST",
                "parameters": {
                    "file": "XMind文件",
                    "optimization_type": "优化类型"
                }
            },
            {
                "name": "ai_analyze_quality",
                "description": "AI分析思维导图质量",
                "endpoint": "/ai-analyze-quality",
                "method": "POST",
                "parameters": {
                    "file": "XMind文件"
                }
            }
        ]
    
    async def generate_summary(
        self, 
        mind_map_data: Dict[str, Any],
        max_length: int = 500
    ) -> str:
        """生成思维导图摘要"""
        if not self.is_ai_available():
            return self._basic_summary_generation(mind_map_data, max_length)
        
        try:
            prompt = self._build_summary_generation_prompt(mind_map_data, max_length)
            response = await self._call_openai_api(prompt)
            return response.strip()
            
        except Exception as e:
            print(f"AI摘要生成失败: {e}")
            return self._basic_summary_generation(mind_map_data, max_length)
    
    # 私有方法
    
    def _build_topic_generation_prompt(
        self, context: str, existing_topics: List[str], max_topics: int, creativity: float
    ) -> str:
        """构建主题生成提示"""
        existing_str = ", ".join(existing_topics) if existing_topics else "无"
        
        return f"""基于以下上下文生成相关的思维导图主题：

上下文：{context}

现有主题：{existing_str}

请生成 {max_topics} 个相关主题，要求：
1. 主题应该与上下文高度相关
2. 避免与现有主题重复
3. 考虑不同层次和角度
4. 创造力水平：{creativity}

请按以下JSON格式返回：
[
  {{
    "title": "主题标题",
    "description": "主题描述",
    "priority": 1,
    "relevance_score": 0.9,
    "subtopics": []
  }}
]
"""
    
    def _build_structure_optimization_prompt(
        self, mind_map_data: Dict[str, Any], goals: List[str]
    ) -> str:
        """构建结构优化提示"""
        goals_str = ", ".join(goals) if goals else "提高可读性和逻辑性"
        
        return f"""请优化以下思维导图的结构：

当前结构：
{json.dumps(mind_map_data, ensure_ascii=False, indent=2)}

优化目标：{goals_str}

请提供优化后的结构，要求：
1. 保持原有内容完整性
2. 改善逻辑层次关系
3. 提高可读性和美观度
4. 确保结构平衡

按以下JSON格式返回优化后的结构：
{{
  "title": "优化后的标题",
  "children": [
    {{
      "title": "子主题1",
      "children": []
    }}
  ]
}}
"""
    
    def _build_quality_analysis_prompt(self, mind_map_data: Dict[str, Any]) -> str:
        """构建质量分析提示"""
        return f"""请分析以下思维导图的质量：

结构数据：
{json.dumps(mind_map_data, ensure_ascii=False, indent=2)}

请从以下维度进行分析：
1. 复杂度（是否合理，是否过于复杂或简单）
2. 平衡性（各分支是否均衡发展）
3. 完整性（内容是否全面）
4. 结构问题（层次是否清晰）
5. 优化机会

按以下JSON格式返回分析结果：
{{
  "complexity_score": 0.8,
  "balance_score": 0.7,
  "completeness_score": 0.9,
  "overall_quality": "良好",
  "suggestions": ["建议1", "建议2"],
  "optimization_opportunities": ["机会1", "机会2"],
  "structural_issues": ["问题1", "问题2"]
}}
"""
    
    async def _call_openai_api(self, prompt: str) -> str:
        """调用OpenAI API"""
        if not self.openai_client:
            raise Exception("OpenAI客户端未初始化")
        
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _parse_generated_topics(self, response: str) -> List[AITopic]:
        """解析生成的主题"""
        try:
            # 尝试从响应中提取JSON
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                topics_data = json.loads(json_match.group())
            else:
                topics_data = json.loads(response)
            
            topics = []
            for topic_data in topics_data:
                topic = AITopic(
                    title=topic_data.get("title", ""),
                    description=topic_data.get("description"),
                    priority=topic_data.get("priority", 1),
                    relevance_score=topic_data.get("relevance_score", 0.8)
                )
                
                # 处理子主题
                if "subtopics" in topic_data:
                    for subtopic_data in topic_data["subtopics"]:
                        subtopic = AITopic(
                            title=subtopic_data.get("title", ""),
                            description=subtopic_data.get("description"),
                            priority=subtopic_data.get("priority", 1),
                            relevance_score=subtopic_data.get("relevance_score", 0.8)
                        )
                        topic.subtopics.append(subtopic)
                
                topics.append(topic)
            
            return topics
            
        except Exception as e:
            print(f"解析生成的主题失败: {e}")
            return []
    
    def _parse_optimized_structure(self, response: str) -> Dict[str, Any]:
        """解析优化的结构"""
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except Exception as e:
            print(f"解析优化的结构失败: {e}")
            return {}
    
    def _parse_quality_analysis(self, response: str) -> AIMindMapAnalysis:
        """解析质量分析结果"""
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                analysis_data = json.loads(response)
            
            return AIMindMapAnalysis(
                complexity_score=analysis_data.get("complexity_score", 0.5),
                balance_score=analysis_data.get("balance_score", 0.5),
                completeness_score=analysis_data.get("completeness_score", 0.5),
                overall_quality=analysis_data.get("overall_quality", "未知"),
                suggestions=analysis_data.get("suggestions", []),
                optimization_opportunities=analysis_data.get("optimization_opportunities", []),
                structural_issues=analysis_data.get("structural_issues", [])
            )
        except Exception as e:
            print(f"解析质量分析失败: {e}")
            return AIMindMapAnalysis(0.5, 0.5, 0.5, "未知", [], [], [])
    
    # 回退方法（当AI不可用时使用）
    
    def _generate_fallback_topics(self, context: str, max_topics: int) -> List[AITopic]:
        """生成回退主题"""
        # 基于简单关键词匹配生成主题
        keywords = self._extract_basic_keywords(context)
        topics = []
        
        for i, keyword in enumerate(keywords[:max_topics]):
            topic = AITopic(
                title=f"{keyword} 相关主题",
                description=f"关于 {keyword} 的详细内容",
                priority=i + 1,
                relevance_score=0.7
            )
            topics.append(topic)
        
        return topics
    
    def _basic_structure_optimization(self, mind_map_data: Dict[str, Any]) -> Dict[str, Any]:
        """基本结构优化"""
        # 简单的结构平衡调整
        if "children" in mind_map_data:
            children = mind_map_data["children"]
            # 平衡各分支的子节点数量
            avg_children = len(children) // 2 if children else 0
            
            for child in children:
                if "children" in child and len(child["children"]) > avg_children + 3:
                    # 重新分配子节点
                    excess_children = child["children"][avg_children:]
                    child["children"] = child["children"][:avg_children]
                    
                    # 创建新分支
                    new_branch = {
                        "title": f"{child['title']} 补充",
                        "children": excess_children
                    }
                    children.append(new_branch)
        
        return mind_map_data
    
    def _basic_quality_analysis(self, mind_map_data: Dict[str, Any]) -> AIMindMapAnalysis:
        """基本质量分析"""
        # 简单的启发式分析
        total_nodes = self._count_nodes(mind_map_data)
        max_depth = self._calculate_max_depth(mind_map_data)
        
        complexity_score = min(1.0, total_nodes / 50)  # 基于节点数量
        balance_score = self._calculate_balance_score(mind_map_data)
        completeness_score = 0.8 if total_nodes > 5 else 0.5
        
        suggestions = []
        if max_depth > 4:
            suggestions.append("建议减少层级深度")
        if total_nodes < 3:
            suggestions.append("建议增加更多内容")
        if balance_score < 0.6:
            suggestions.append("建议平衡各分支内容")
        
        return AIMindMapAnalysis(
            complexity_score=complexity_score,
            balance_score=balance_score,
            completeness_score=completeness_score,
            overall_quality="良好" if complexity_score > 0.6 else "需要改进",
            suggestions=suggestions,
            optimization_opportunities=[],
            structural_issues=[]
        )
    
    def _generate_basic_suggestions(self, mind_map_data: Dict[str, Any]) -> List[str]:
        """生成基本建议"""
        suggestions = []
        
        total_nodes = self._count_nodes(mind_map_data)
        max_depth = self._calculate_max_depth(mind_map_data)
        
        if total_nodes < 5:
            suggestions.append("建议增加更多主题和子主题")
        if max_depth < 2:
            suggestions.append("建议增加层级深度")
        if max_depth > 5:
            suggestions.append("建议减少层级深度，保持结构清晰")
        
        return suggestions
    
    def _basic_content_categorization(self, content: str) -> Dict[str, List[str]]:
        """基本内容分类"""
        # 简单的关键词分类
        categories = {
            "技术": ["编程", "代码", "开发", "算法", "系统"],
            "业务": ["市场", "销售", "客户", "产品", "策略"],
            "学习": ["知识", "技能", "培训", "教育", "研究"]
        }
        
        result = {category: [] for category in categories}
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in content:
                    result[category].append(keyword)
        
        return result
    
    def _basic_keyword_extraction(self, content: str, max_keywords: int) -> List[str]:
        """基本关键词提取"""
        # 简单的词频统计
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        
        for word in words:
            if len(word) > 2:  # 过滤短词
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def _basic_summary_generation(self, mind_map_data: Dict[str, Any], max_length: int) -> str:
        """基本摘要生成"""
        title = mind_map_data.get("title", "思维导图")
        total_nodes = self._count_nodes(mind_map_data)
        
        summary = f"思维导图《{title}》包含{total_nodes}个节点。"
        
        if "children" in mind_map_data and mind_map_data["children"]:
            main_topics = [child.get("title", "") for child in mind_map_data["children"][:3]]
            if main_topics:
                summary += f"主要涵盖：{', '.join(main_topics)}等主题。"
        
        return summary[:max_length]
    
    def _extract_basic_keywords(self, content: str) -> List[str]:
        """提取基本关键词"""
        words = re.findall(r'\b\w+\b', content.lower())
        # 简单的停用词过滤
        stop_words = {"的", "了", "在", "是", "有", "和", "与", "或", "但", "而", "及", "等", "等等"}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return list(set(keywords))[:10]  # 返回去重后的前10个
    
    def _count_nodes(self, data: Dict[str, Any]) -> int:
        """计算节点数量"""
        count = 1  # 当前节点
        if "children" in data:
            for child in data["children"]:
                count += self._count_nodes(child)
        return count
    
    def _calculate_max_depth(self, data: Dict[str, Any], current_depth: int = 0) -> int:
        """计算最大深度"""
        max_depth = current_depth
        if "children" in data:
            for child in data["children"]:
                child_depth = self._calculate_max_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
    
    def _calculate_balance_score(self, data: Dict[str, Any]) -> float:
        """计算平衡性评分"""
        if "children" not in data or not data["children"]:
            return 1.0
        
        child_counts = []
        for child in data["children"]:
            count = self._count_nodes(child)
            child_counts.append(count)
        
        if not child_counts:
            return 1.0
        
        # 计算标准差，评估平衡性
        avg = sum(child_counts) / len(child_counts)
        variance = sum((x - avg) ** 2 for x in child_counts) / len(child_counts)
        std_dev = variance ** 0.5
        
        # 转换为0-1评分，标准差越小评分越高
        balance_score = max(0, 1 - (std_dev / (avg + 1)))
        return balance_score


# 使用示例和测试
if __name__ == "__main__":
    import asyncio
    
    async def test_ai_extensions():
        """测试AI扩展功能"""
        print("🧪 测试XMind AI扩展功能")
        print("=" * 50)
        
        # 创建AI扩展实例（不使用真实API）
        ai_ext = XMindAIExtensions()
        
        # 测试主题生成
        print("\n📝 测试主题生成...")
        context = "人工智能和机器学习"
        topics = await ai_ext.generate_topics(context, max_topics=5)
        print(f"生成的主题: {[topic.title for topic in topics]}")
        
        # 测试质量分析
        print("\n🔍 测试质量分析...")
        sample_mind_map = {
            "title": "AI学习路径",
            "children": [
                {"title": "基础知识", "children": [
                    {"title": "数学基础"},
                    {"title": "编程基础"}
                ]},
                {"title": "机器学习", "children": [
                    {"title": "监督学习"},
                    {"title": "无监督学习"}
                ]}
            ]
        }
        
        analysis = await ai_ext.analyze_mind_map_quality(sample_mind_map)
        print(f"复杂度评分: {analysis.complexity_score}")
        print(f"平衡性评分: {analysis.balance_score}")
        print(f"整体质量: {analysis.overall_quality}")
        print(f"建议: {analysis.suggestions}")
        
        # 测试结构优化
        print("\n🔄 测试结构优化...")
        optimized = await ai_ext.optimize_structure(sample_mind_map)
        print(f"优化后标题: {optimized.get('title', 'N/A')}")
        
        # 测试关键词提取
        print("\n🔑 测试关键词提取...")
        content = "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器"
        keywords = await ai_ext.extract_keywords(content, max_keywords=5)
        print(f"提取的关键词: {keywords}")
        
        # 测试内容分类
        print("\n📊 测试内容分类...")
        categories = await ai_ext.categorize_content(content)
        print(f"分类结果: {categories}")
        
        print("\n" + "=" * 50)
        print("✅ AI扩展功能测试完成!")
    
    asyncio.run(test_ai_extensions())