# 🔄 通用文件转XMind转换器

一键将多种格式文件转换为XMind思维导图。

## 🎯 支持格式

| 格式 | 文件扩展名 | 特点 |
|------|------------|------|
| Markdown | `.md` | 标题层级自动转换，支持列表和链接 |
| 纯文本 | `.txt` | 缩进层级智能识别 |
| HTML | `.html` | 标题标签转换，保持结构层次 |
| Word文档 | `.docx` | 标题样式转换，支持大纲结构 |
| Excel表格 | `.xlsx` | 首列层级识别，支持多层级 |
| OPML | `.opml` | 大纲格式，层级结构完整保留 |

## 🚀 快速开始

### 基本命令
```bash
python universal_xmind_converter.py <输入文件> [输出文件]
```

### 使用示例

#### 1. Markdown转XMind
```bash
python universal_xmind_converter.py examples/playwright-learning-guide.md output/playwright-guide.xmind
```

#### 2. 文本文件转XMind
```bash
python universal_xmind_converter.py examples/sample_outline.txt output/my-outline.xmind
```

#### 3. Word文档转XMind
```bash
python universal_xmind_converter.py examples/document.docx output/document-mindmap.xmind
```

#### 4. Excel表格转XMind
```bash
python universal_xmind_converter.py examples/data.xlsx output/data-analysis.xmind
```

#### 5. HTML网页转XMind
```bash
python universal_xmind_converter.py examples/article.html output/article-structure.xmind
```

#### 6. OPML大纲转XMind
```bash
python universal_xmind_converter.py examples/outline.opml output/project-plan.xmind
```

## 📋 格式说明

### Markdown格式
```markdown
# 主要主题
## 子主题1
### 详细内容1
### 详细内容2
## 子主题2
### 详细内容3
```

### 文本文件格式
```
主要主题
  子主题1
    详细内容1
    详细内容2
  子主题2
    详细内容3
```

### Word文档格式
使用Word的标题样式：
- 标题1 → 主要主题
- 标题2 → 子主题
- 标题3 → 详细内容

### Excel表格格式
第一列表示层级关系：
```
主要主题
主要主题,子主题1
主要主题,子主题1,详细内容1
主要主题,子主题1,详细内容2
主要主题,子主题2
主要主题,子主题2,详细内容3
```

## 🎨 转换特性

### 智能识别
- **自动格式检测**：根据文件扩展名自动选择转换策略
- **层级结构保持**：完整保留原文档的层次结构
- **内容优化**：智能处理标题、列表和段落格式

### 质量保证
- **格式完整**：生成的XMind文件格式标准，兼容性好
- **结构清晰**：层级关系明确，便于理解和编辑
- **内容准确**：保持原文档的内容完整性和准确性

### 错误处理
- **文件不存在**：提示文件路径错误
- **格式不支持**：提示不支持的文件格式
- **编码问题**：自动检测和处理文件编码
- **权限问题**：提示文件读写权限错误

## ⚙️ 高级选项

### 自定义输出
```bash
# 指定输出文件名
python universal_xmind_converter.py input.md my-custom-name.xmind

# 使用默认输出名（基于输入文件名）
python universal_xmind_converter.py input.md
```

### 批量转换
```bash
# 转换多个文件
for file in examples/*.md; do
    python universal_xmind_converter.py "$file" "output/$(basename "$file" .md).xmind"
done
```

## 🔧 扩展开发

### 添加新格式支持

1. **创建格式处理器**（在`universal_xmind_converter.py`中）：
```python
def handle_new_format(content, filepath):
    """处理新格式的内容"""
    # 解析内容并返回层级结构
    return structure_data
```

2. **注册格式检测**（在文件格式映射中）：
```python
FORMAT_HANDLERS = {
    '.md': handle_markdown,
    '.txt': handle_text,
    '.html': handle_html,
    '.docx': handle_word,
    '.xlsx': handle_excel,
    '.opml': handle_opml,
    '.new': handle_new_format,  # 添加新格式
}
```

3. **实现转换逻辑**：
```python
def handle_new_format(content, filepath):
    """处理新格式的思维导图结构"""
    try:
        # 解析文件内容
        parsed_content = parse_new_format(content)
        
        # 转换为层级结构
        structure = convert_to_structure(parsed_content)
        
        return structure
    except Exception as e:
        raise ValueError(f"新格式转换失败: {str(e)}")
```

## 📊 性能特点

- **快速转换**：平均转换时间 < 2秒
- **内存优化**：支持大文件处理
- **批量处理**：支持多个文件同时转换
- **格式验证**：确保输出文件格式正确

## 🔍 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 文件未找到 | 路径错误 | 使用绝对路径或检查相对路径 |
| 格式不支持 | 扩展名不正确 | 检查文件扩展名 |
| 转换失败 | 文件内容错误 | 检查源文件格式 |
| 输出错误 | 权限问题 | 检查输出目录权限 |

### 调试模式
```bash
# 启用详细输出
python universal_xmind_converter.py -v input.md output.xmind
```

## 📚 相关资源

- **[项目主页](README.md)** - 项目概览和快速开始
- **[Trae配置指南](TRAE_MCP_SETUP.md)** - MCP服务器配置
- **[验证报告](conversion_validation_report.md)** - 转换质量验证结果

---

**🎉 现在就开始将您的文档转换为精美的思维导图吧！**