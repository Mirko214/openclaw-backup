#!/usr/bin/env python3
"""
image-gen — 作家专用图片生成工具
中文描述 → 专业 prompt 扩写 → ZenMux Gemini 生图

用法:
  python3 generate.py --desc "江南水墨春景" --style ink
"""

import os
import sys
import json
import argparse
import base64
import requests
from pathlib import Path
from datetime import datetime

# ──────────────────────────────────────────────
# 风格预设库（来自 awesome-nano-banana-pro-prompts 精选）
# ──────────────────────────────────────────────
STYLE_PRESETS = {
    "ink": {
        "name": "中国水墨",
        "suffix": (
            "traditional Chinese ink wash painting style, "
            "sumi-e, monochromatic with subtle washes, "
            "rice paper texture, minimalist composition, "
            "elegant brushstrokes, misty atmosphere, "
            "masterful negative space, Song Dynasty aesthetic"
        ),
    },
    "illustration": {
        "name": "现代插画",
        "suffix": (
            "modern digital illustration, flat design with depth, "
            "vibrant colors, clean lines, editorial style, "
            "professional artwork, high detail"
        ),
    },
    "cinematic": {
        "name": "电影感",
        "suffix": (
            "cinematic photography style, dramatic lighting, "
            "film grain, anamorphic lens, shallow depth of field, "
            "golden hour or blue hour atmosphere, "
            "photorealistic, 8K, ultra-detailed"
        ),
    },
    "book-cover": {
        "name": "书封面",
        "suffix": (
            "professional book cover design, striking composition, "
            "typography-friendly layout, atmospheric lighting, "
            "high contrast, visually compelling, "
            "literary fiction aesthetic, award-winning design"
        ),
    },
    "poster": {
        "name": "海报",
        "suffix": (
            "professional poster design, bold composition, "
            "eye-catching colors, graphic design aesthetic, "
            "clean layout, strong visual hierarchy, "
            "print-ready quality"
        ),
    },
    "anime": {
        "name": "动漫",
        "suffix": (
            "anime illustration style, Studio Ghibli inspired, "
            "soft colors, detailed backgrounds, "
            "expressive characters, cel shading, "
            "high quality anime art"
        ),
    },
    "watercolor": {
        "name": "水彩",
        "suffix": (
            "watercolor painting style, soft washes, "
            "organic edges, translucent layers, "
            "paper texture visible, impressionistic, "
            "delicate and ethereal atmosphere"
        ),
    },
    "oil-painting": {
        "name": "油画",
        "suffix": (
            "oil painting style, rich impasto texture, "
            "classical technique, masterful color mixing, "
            "canvas texture, museum quality, "
            "Old Masters inspired"
        ),
    },
    "pixel": {
        "name": "像素艺术",
        "suffix": (
            "pixel art style, 16-bit or 32-bit aesthetic, "
            "retro game graphics, limited color palette, "
            "crisp pixel edges, nostalgic charm"
        ),
    },
    "3d": {
        "name": "3D 渲染",
        "suffix": (
            "3D render, Octane or Blender Cycles style, "
            "physically-based materials, studio lighting, "
            "ultra-realistic, 4K resolution, "
            "professional CGI quality"
        ),
    },
    "minimalism": {
        "name": "极简主义",
        "suffix": (
            "minimalist style, negative space, "
            "simple geometric forms, muted palette, "
            "zen aesthetic, less is more philosophy, "
            "Japanese wabi-sabi inspired"
        ),
    },
    "retro": {
        "name": "复古",
        "suffix": (
            "retro vintage style, 1970s aesthetic, "
            "grainy texture, muted tones, "
            "analog photography feel, nostalgic atmosphere, "
            "aged paper or film effect"
        ),
    },
}

DEFAULT_MODEL = "google/gemini-3-pro-image-preview"
DEFAULT_STYLE = "illustration"
DEFAULT_SIZE = "1K"
ZENMUX_API_BASE = "https://zenmux.ai/api/vertex-ai/v1"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# 默认自动 fallback（ZenMux → Gemini）
DEFAULT_PROVIDER = "auto"  # "auto", "zenmux", 或 "gemini"


def get_api_key(provider: str = "zenmux"):
    """获取 API key"""
    if provider == "zenmux":
        # 优先从环境变量读取
        key = os.environ.get("ZENMUX_API_KEY")
        if key:
            return key, "zenmux"
        # 回退：从配置文件读取（需要手动配置）
        print("⚠️ 警告: ZENMUX_API_KEY 未设置，尝试使用官方 Gemini...", file=sys.stderr)
        provider = "gemini"

    if provider == "gemini":
        key = os.environ.get("GEMINI_API_KEY")
        if key:
            return key, "gemini"
        # 从 openclaw.json 读取（通过配置文件注入）
        # 这里先返回空，让后面的逻辑处理
        return None, "gemini"

    print(f"❌ 错误: 未找到有效的 API key", file=sys.stderr)
    sys.exit(1)


def build_prompt(desc: str, style: str) -> str:
    """将中文描述 + 风格预设合并成专业英文 prompt"""
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS[DEFAULT_STYLE])
    
    # 核心内容用中文描述（Gemini 支持中文理解）
    # 风格词汇用英文（Gemini 对英文风格词汇更敏感）
    prompt = f"{desc}, {preset['suffix']}"
    return prompt


def generate_image(prompt: str, model: str, size: str, output: str, provider: str = "zenmux") -> str:
    """使用指定 provider 生成图片，支持自动 fallback"""
    
    # 获取 API key
    api_key = os.environ.get("GEMINI_API_KEY")  # 优先用环境变量
    if not api_key:
        # 尝试从配置文件读取 hardcoded key（仅供测试，生产环境用环境变量）
        api_key = os.environ.get("ZENMUX_API_KEY")
    
    if not api_key and provider == "gemini":
        # fallback: 使用已知的有效 key（仅供测试）
        api_key = os.environ.get("GEMINI_API_KEY")

    # 构建请求体
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"imageSize": size},
        },
    }

    # 定义两个 provider 的配置
    providers_config = {
        "zenmux": {
            "api_key": os.environ.get("ZENMUX_API_KEY", "sk-ss-v1-5e186a278e1a4a224673fd00cfd1bcc11b508af898972dfb94dff07ef2f76d6d"),
            "url": f"{ZENMUX_API_BASE}/models/{model}:generateContent",
            "header_key": "x-goog-api-key",
        },
        "gemini": {
            "api_key": api_key,
            "url": f"{GEMINI_API_BASE}/models/{model}:generateContent",
            "header_key": "key",
        },
    }

    # 按顺序尝试 providers
    if provider == "auto":
        providers_to_try = ["zenmux", "gemini"]
    elif provider == "zenmux":
        providers_to_try = ["zenmux", "gemini"]  # zenmux 失败也 fallback
    else:
        providers_to_try = ["gemini"]
    
    last_error = None
    for prov in providers_to_try:
        cfg = providers_config[prov]
        if not cfg["api_key"]:
            print(f"⚠️ {prov} API key 未配置，跳过...", file=sys.stderr)
            continue
            
        # 构建 headers
        if prov == "zenmux":
            headers = {
                "Content-Type": "application/json",
                cfg["header_key"]: cfg["api_key"],
            }
            url = cfg["url"]
        else:
            # 官方 Gemini: key 在 URL 参数中
            url = f"{cfg['url']}?key={cfg['api_key']}"
            headers = {"Content-Type": "application/json"}

        print(f"🔧 尝试 Provider: {prov}", file=sys.stderr)
        print(f"🎨 模型: {model}", file=sys.stderr)
        print(f"📝 Prompt: {prompt[:80]}...", file=sys.stderr)

        try:
            response = requests.post(url, json=body, headers=headers, timeout=180)
            
            # 检查错误码，判断是否需要 fallback
            if response.status_code in [403, 404, 500, 502, 503]:
                print(f"⚠️ {prov} 返回错误 {response.status_code}，尝试下一个 provider...", file=sys.stderr)
                last_error = f"{prov} error {response.status_code}"
                continue
                
            if response.status_code != 200:
                print(f"❌ {prov} API 错误 {response.status_code}: {response.text}", file=sys.stderr)
                last_error = f"API error {response.status_code}"
                continue

            data = response.json()
            break  # 成功获取数据，跳出循环
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ {prov} 请求异常: {e}，尝试下一个 provider...", file=sys.stderr)
            last_error = str(e)
            continue

    else:
        # 所有 provider 都失败了
        print(f"❌ 所有 provider 都失败: {last_error}", file=sys.stderr)
        sys.exit(1)

    # 解析响应
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates in response")

        parts = candidates[0].get("content", {}).get("parts", [])
        image_data = next(
            (p["inlineData"]["data"] for p in parts if "inlineData" in p), None
        )

        if not image_data:
            raise ValueError("No image data in response")

    except Exception as e:
        print(f"❌ 解析响应失败: {e}", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)

    image_bytes = base64.b64decode(image_data)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="作家专用图片生成工具")
    parser.add_argument("--desc", "-d", required=True, help="中文图像描述")
    parser.add_argument(
        "--style",
        "-s",
        default=DEFAULT_STYLE,
        choices=list(STYLE_PRESETS.keys()),
        help=f"风格预设 (默认: {DEFAULT_STYLE})",
    )
    parser.add_argument("--size", default=DEFAULT_SIZE, choices=["1K", "2K"], help="图片尺寸")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="模型 ID")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="仅输出扩写后的 prompt，不生图",
    )
    parser.add_argument(
        "--provider",
        "-p",
        default=DEFAULT_PROVIDER,
        choices=["auto", "zenmux", "gemini"],
        help=f"选择 API 提供商 (默认: {DEFAULT_PROVIDER}, auto=自动 fallback)",
    )

    args = parser.parse_args()

    # 构建 prompt
    prompt = build_prompt(args.desc, args.style)
    style_name = STYLE_PRESETS[args.style]["name"]

    if args.prompt_only:
        print(f"🎨 风格: {style_name}")
        print(f"📝 完整 Prompt:\n{prompt}")
        return

    # 自动生成输出文件名
    if args.output is None:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{timestamp}-{args.style}.png"
        output = str(Path.home() / ".openclaw" / "media" / filename)
    else:
        output = args.output

    print(f"🎨 风格: {style_name}", file=sys.stderr)

    path = generate_image(
        prompt=prompt,
        model=args.model,
        size=args.size,
        output=output,
        provider=args.provider,
    )

    print(f"✅ 图片已保存: {path}", file=sys.stderr)
    # OpenClaw 自动附图协议
    print(f"MEDIA:{path}")


if __name__ == "__main__":
    main()
