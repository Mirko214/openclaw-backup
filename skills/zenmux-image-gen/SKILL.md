# ZenMux Image Generator

通过 ZenMux Vertex AI 调用 Google Gemini 生成图片。

## 环境变量

```bash
ZENMUX_API_KEY=your_zenmux_api_key
```

## 使用方法

```bash
# 基本用法
python3 scripts/generate.py --prompt "A cute cat"

# 指定模型和尺寸
python3 scripts/generate.py --prompt "A cute cat" --model google/gemini-3-pro-image-preview --size 1K

# 指定输出路径
python3 scripts/generate.py --prompt "A cute cat" --output ./my-image.png

# 阿拉伯宽高比
python3 scripts/generate.py --prompt "A cute cat" --ar 16:9
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 图片描述文本 | 必填 |
| `--model` | 模型 ID | google/gemini-2.5-flash-image |
| `--size` | 图片尺寸 (1K/2K) | 1K |
| `--ar` | 宽高比 (如 1:1, 16:9) | 1:1 |
| `--output` | 输出文件路径 | ./output.png |

## 支持的模型

- `google/gemini-3-pro-image-preview` - 质量最高
- `google/gemini-2.5-flash-image` - 速度快，免费
- `google/gemini-3-pro-image-preview-free` - 免费预览版
- `google/gemini-2.5-flash-image-free` - 免费快速版

## 依赖

- Python 3.7+
- requests 库 (`pip install requests`)
