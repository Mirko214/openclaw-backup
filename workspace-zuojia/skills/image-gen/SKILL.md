# image-gen — 作家配图生成 Skill

作家专用图片生成工具，支持中文描述 → 专业 prompt 扩写 → 调用 Gemini 生图（支持 ZenMux 或官方 API）。

## 快速使用

```bash
python3 {baseDir}/scripts/generate.py --desc "江南水墨春景，远山淡烟" --style ink
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--desc` | 中文图像描述（必填） | — |
| `--style` | 风格预设（见下方列表） | `illustration` |
| `--size` | 尺寸：`1K` / `2K` | `1K` |
| `--provider` | API 提供商：`zenmux` / `gemini` | `zenmux` |
| `--model` | 模型 ID | `google/gemini-3-pro-image-preview` |
| `--output` | 输出路径 | 自动生成时间戳文件名 |
| `--prompt-only` | 仅输出扩写后的 prompt，不生图 | — |

## 风格预设 (--style)

| 风格 ID | 描述 |
|---------|------|
| `ink` | 中国水墨画风格 |
| `illustration` | 现代插画风格（默认） |
| `cinematic` | 电影感写实风格 |
| `book-cover` | 书封面设计风格 |
| `poster` | 海报/宣传图风格 |
| `anime` | 动漫/二次元风格 |
| `watercolor` | 水彩画风格 |
| `oil-painting` | 油画风格 |
| `pixel` | 像素艺术风格 |
| `3d` | 3D 渲染风格 |
| `minimalism` | 极简主义风格 |
| `retro` | 复古/怀旧风格 |

## 完整示例

```bash
# 水墨风格书封配图
python3 {baseDir}/scripts/generate.py \
  --desc "独行侠客，夜雨孤灯，江湖路远" \
  --style ink \
  --size 2K \
  --output ~/Desktop/book-cover.png

# 电影感场景
python3 {baseDir}/scripts/generate.py \
  --desc "2049年上海夜晚，霓虹倒影在雨中街道" \
  --style cinematic

# 只看扩写后的英文 prompt（不生图）
python3 {baseDir}/scripts/generate.py \
  --desc "春日桃花林中的少女" \
  --style watercolor \
  --prompt-only
```

## 环境变量

- `ZENMUX_API_KEY` — ZenMux API 密钥（优先使用，配额有限）
- `GEMINI_API_KEY` — Google Gemini 官方 API 密钥（备用）

**说明**：
- 默认使用 `zenmux`（更灵活，支持多模型）
- 如 ZenMux 配额用完，自动切换到官方 Gemini
- 需要在运行环境中设置对应的 API key

## 输出

- 图片保存到指定路径（或自动生成时间戳文件名）
- 打印 `MEDIA: /path/to/image.png` 供 OpenClaw 自动附图发送
