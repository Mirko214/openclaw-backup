# 萌宠卡通风格生成模板

## 📊 参考图片分析

### 原始风格
- **类型**: 写实宠物摄影
- **特点**: 真实毛发纹理、清晰眼睛细节、自然光影
- **宠物**: 英国短毛猫（蓝猫）、银虎斑猫

---

## 🎨 卡通风格分析（适合社交媒体）

### 推荐风格选择

| 风格 | 特点 | 适用场景 |
|------|------|----------|
| **迪士尼风格** | 圆润线条、大眼睛、可爱表情 | 头像、封面 |
| **Q版/大头仔** | 简化比例、大头小身、超级可爱 | 表情包、头像 |
| **漫画风格** | 清晰轮廓、鲜明色彩、动感 | 帖子、配图 |
| **治愈系插画** | 柔和色调、温暖氛围 | 日常分享 |
| **和风卡通** | 简约线条、日系萌感 | 文艺内容 |

### 社交媒体优化要点
1. **色彩鲜艳** - 吸引注意力
2. **表情夸张** - 增加趣味性
3. **简化细节** - 保持清晰度
4. **背景简洁** - 突出主体

---

## 📝 可复用 Prompt 模板

### 基础模板（zenmux-image-gen）

```
[宠物类型] in [风格描述], cute cartoon illustration, big sparkling eyes, adorable expression, soft rounded shapes, vibrant colors, clean background, trending on social media, Chinese social media style, 4k, high quality
```

### 完整模板变体

#### 1. 猫咪 - 迪士尼风格
```
A cute cartoon cat, Disney style, big round expressive eyes, fluffy appearance, sweet smiling expression, soft blue or cream color, minimalist clean background, trending on Chinese social media, adorable kawaii style, 4k illustration, high quality
```

#### 2. 狗狗 - Q版漫画风格
```
A cute cartoon puppy, Q版可爱风格, oversized head small body, big sparkly eyes, tongue sticking out, playful expression, soft fur texture, vibrant colors, pastel background, Chinese social media trending, kawaii style illustration, 4k
```

#### 3. 多宠物 - 治愈系插画
```
Cute cartoon pets collection, one cat and one dog sitting together, warm治愈系 style, big eyes, holding paws, soft pastel color palette, cozy atmosphere, trending on Xiaohongshu, adorable illustration, 4k high quality
```

#### 4. 猫咪 - 每日随机
```
Cute cartoon cat, [随机特征: ginger/orange tabby/Siamese/British Shorthair], big bright eyes, adorable curious expression, sitting pose, clean simple background, soft lighting, Chinese social media trending style, kawaii illustration, 4k
```

#### 5. 狗狗 - 每日随机
```
Cute cartoon dog, [随机特征: golden retriever/puppy/Corgi/Husky], playful expression, tongue out, big round eyes, fluffy ears, happy vibe, pastel background, trending on Chinese social media, adorable illustration, 4k
```

---

## 🔄 每日生成 3 张模板

### 变量池

**猫咪品种**:
- 橘猫 (orange tabby cat)
- 奶牛猫 (cow cat / tuxedo cat)
- 英短蓝猫 (British Shorthair blue)
- 暹罗猫 (Siamese cat)
- 波斯猫 (Persian cat)
- 狸花猫 (tabby cat)

**狗狗品种**:
- 金毛 (Golden Retriever)
- 柯基 (Corgi)
- 柴犬 (Shiba Inu)
- 哈士奇 (Husky)
- 泰迪/贵宾 (Poodle/Teddy)
- 萨摩耶 (Samoyed)

**表情**:
- 好奇 (curious)
- 开心 (happy/smiling)
- 睡觉 (sleeping)
- 歪头杀 (head tilt)
- 吐舌头 (tongue out)
- 犯困 (drowsy)

**场景**:
- 坐着 (sitting)
- 躺着 (lying down)
- 跳跃 (jumping)
- 伸懒腰 (stretching)
- 玩球 (playing with ball)

### 使用方式

**第1张 - 猫咪**:
```
Cute cartoon [猫咪品种], big round eyes, [表情], [场景], soft [颜色] fur, clean background, Chinese social media trending, kawaii style, 4k illustration
```

**第2张 - 狗狗**:
```
Cute cartoon [狗狗品种], playful expression, [表情], [场景], fluffy [颜色] fur, pastel background, trending on Xiaohongshu, adorable illustration, 4k
```

**第3张 - 多宠物/创意**:
```
Cute cartoon [宠物组合], [创意场景], heartwarming治愈系 vibe, big sparkly eyes, vibrant colors, trending on social media, adorable illustration, 4k high quality
```

---

## 🚀 生成命令示例

```bash
# 使用 illustration 风格生成猫咪
python3 skills/image-gen/scripts/generate.py --desc "Cute cartoon cat, Disney style, big round eyes, fluffy blue fur, sweet smile, sitting pose, clean white background, trending on Chinese social media, kawaii style, 4k" --style illustration

# 使用 anime 风格生成狗狗  
python3 skills/image-gen/scripts/generate.py --desc "Cute cartoon golden retriever puppy, Q版风格, big sparkly eyes, tongue out, happy expression, fluffy golden fur, pastel rainbow background, trending on Xiaohongshu, adorable, 4k" --style anime
```
