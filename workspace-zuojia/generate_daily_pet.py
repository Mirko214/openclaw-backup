#!/usr/bin/env python3
"""
每日萌宠图片生成脚本
- 从品种库随机选一个未生成过的品种
- 用 nano-banana-pro 生成卡通风格图片
- 记录已生成品种防止重复
"""

import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent
BREEDS_FILE = WORKSPACE / "pet-breeds.json"
LOG_FILE = WORKSPACE / "pet-generated-log.json"
OUTPUT_DIR = WORKSPACE / "generated-images"
SKILL_SCRIPT = Path.home() / ".openclaw/skills/zenmux-image-gen/scripts/generate.py"

def load_breeds():
    with open(BREEDS_FILE) as f:
        data = json.load(f)
    all_breeds = []
    for category, breeds in data.items():
        for breed in breeds:
            all_breeds.append({"name": breed, "category": category})
    return all_breeds

def load_log():
    with open(LOG_FILE) as f:
        return json.load(f)

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def pick_breed(all_breeds, log):
    generated_names = {entry["breed"] for entry in log["generated"]}
    available = [b for b in all_breeds if b["name"] not in generated_names]
    
    # 如果全部用完，重置记录重新开始
    if not available:
        print("所有品种已生成过一轮，重置记录重新开始！")
        log["generated"] = []
        save_log(log)
        available = all_breeds
    
    return random.choice(available)

def build_prompt(breed):
    category = breed["category"]
    name = breed["name"]
    
    styles = [
        "Disney Pixar style, big sparkly eyes, fluffy fur",
        "cute chibi anime style, big round eyes, kawaii",
        "cartoon illustration style, adorable, colorful",
        "soft watercolor cartoon style, cute and fluffy",
    ]
    
    backgrounds = [
        "pastel pink background",
        "soft blue sky background",
        "cozy home interior background",
        "garden with flowers background",
        "warm sunset background",
    ]
    
    style = random.choice(styles)
    bg = random.choice(backgrounds)
    
    if category == "cats":
        subject = f"adorable {name} cat"
    elif category == "dogs":
        subject = f"cute {name} dog"
    else:
        subject = f"cute {name}"
    
    return f"A {subject}, {style}, {bg}, social media ready, high quality, no text"

def generate_image(prompt, filename):
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / filename
    
    cmd = [
        "python3", str(SKILL_SCRIPT),
        "--prompt", prompt,
        "--output", str(output_path),
        "--model", "google/gemini-3-pro-image-preview",
        "--ar", "1:1"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"生成失败: {result.stderr}")
        return None
    
    print(result.stdout)
    return str(output_path)

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    all_breeds = load_breeds()
    log = load_log()
    
    # 检查今天是否已生成
    today_entries = [e for e in log["generated"] if e["date"] == today]
    if today_entries:
        print(f"今天已生成：{today_entries[0]['breed']}，跳过。")
        return
    
    # 选品种
    breed = pick_breed(all_breeds, log)
    print(f"今日品种：{breed['name']}（{breed['category']}）")
    
    # 生成 prompt
    prompt = build_prompt(breed)
    print(f"Prompt: {prompt}")
    
    # 生成图片
    filename = f"{timestamp}-{breed['name']}.png"
    image_path = generate_image(prompt, filename)
    
    if image_path:
        # 记录日志
        log["generated"].append({
            "date": today,
            "breed": breed["name"],
            "category": breed["category"],
            "prompt": prompt,
            "image": image_path
        })
        save_log(log)
        print(f"\n✅ 成功生成：{image_path}")
        print(f"品种：{breed['name']}")
        print(f"今日文案参考：今天介绍一下{breed['name']}～")

if __name__ == "__main__":
    main()
