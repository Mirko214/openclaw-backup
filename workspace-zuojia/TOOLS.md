# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod

### Telegram

- Mirko chatId (DM): 8526351790
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## 图片生成

- **Skill 路径**: `skills/image-gen/`
- **调用方式**: `python3 skills/image-gen/scripts/generate.py --desc "中文描述" --style [风格]`
- **API**: 
  - 首选：ZenMux (`ZENMUX_API_KEY`)，默认模型 `google/gemini-3-pro-image-preview`
  - 备用：官方 Gemini (`GEMINI_API_KEY`)，模型 `imagen-3.0-generate-002`
- **可用风格**: `ink`(水墨) / `illustration`(插画) / `cinematic`(电影感) / `book-cover`(书封面) / `poster`(海报) / `anime`(动漫) / `watercolor`(水彩) / `oil-painting`(油画) / `pixel`(像素) / `3d`(3D) / `minimalism`(极简) / `retro`(复古)
- **输出**: 图片自动保存到 `~/.openclaw/media/`，打印 `MEDIA:` 行供 OpenClaw 附图发送

**测试结果**:
- ✅ Gemini 官方 API 可用（key: `AIzaSyDsARVtwZoTDKx8DnAzYSvRAOWXywvAeAM`）
- ⚠️ ZenMux 配额已用完，需升级套餐或等待恢复

---

Add whatever helps you do your job. This is your cheat sheet.
