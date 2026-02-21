# memory-abstract-gen.py 使用说明

为 Markdown 文件生成提取式摘要（`.abstract` JSON 文件），支持增量更新。

灵感来自 [qmd](https://github.com/tobi/qmd) 的上下文索引思路。

## 特性

- **零依赖** — 仅使用 Python 3.8+ 标准库
- **提取式摘要** — 基于句子评分（标题关键词重叠 + 位置权重 + 长度偏好），不调用 LLM
- **增量更新** — 基于 SHA-256 哈希，文件内容不变则跳过
- **中英文混合** — 支持中文内容的 token 近似估算
- **JSON 输出** — 方便程序读取

## 用法

```bash
# 扫描默认目录 ./memory/
python3 memory-abstract-gen.py

# 指定目录
python3 memory-abstract-gen.py -d ~/notes/

# 调整摘要长度（默认约 100 tokens）
python3 memory-abstract-gen.py --tokens 150

# 强制重新生成所有摘要
python3 memory-abstract-gen.py --force

# 静默模式，直接输出 INDEX JSON 到 stdout
python3 memory-abstract-gen.py --json
```

## 生成的文件

对于目录中的每个 `.md` 文件，会在同目录生成对应的 `.abstract` 文件：

```
memory/
├── 2024-01-15.md
├── 2024-01-15.abstract    ← 单文件摘要 (JSON)
├── 2024-01-16.md
├── 2024-01-16.abstract
└── INDEX.abstract          ← 目录总索引 (JSON)
```

### 单文件摘要格式 (`.abstract`)

```json
{
  "source": "2024-01-15.md",
  "source_hash": "sha256...",
  "headings": ["标题1", "标题2"],
  "summary": "提取式摘要文本...",
  "tokens_approx": 98
}
```

### 目录索引格式 (`INDEX.abstract`)

```json
{
  "directory": "./memory",
  "file_count": 5,
  "overview": "Topics covered: 标题1; 标题2; ...",
  "files": [
    { "file": "2024-01-15.md", "headings": [...], "summary": "..." },
    ...
  ],
  "index_hash": "sha256..."
}
```

## 作为模块使用

```python
from pathlib import Path
import memory_abstract_gen as mag  # 需要重命名文件或 symlink

# 处理单个文件
abstract = mag.process_file(Path("memory/notes.md"), target_tokens=100)

# 处理整个目录
index = mag.run(Path("./memory/"), target_tokens=100)
```

## 摘要算法

1. 从 Markdown 中提取所有标题作为主题指示词
2. 清除 Markdown 格式，将正文切分为句子
3. 为每个句子打分：
   - **标题词重叠** — 包含标题关键词的句子得分更高
   - **位置权重** — 文档前 20% 和后 20% 的句子有加分
   - **长度偏好** — 8-40 词的句子优先
4. 按得分从高到低，贪心地选取句子直到达到 token 预算
5. 按原始顺序拼接，保持可读性
