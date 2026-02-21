# MediaFlow Skill

## Overview

MediaFlow is a comprehensive media processing toolkit that provides:
- **Video/Audio Download** - Support for YouTube, X (Twitter), Xiaohongshu (小红书), Douyin (抖音), Kuaishou (快手), and many other platforms
- **Transcription** - Audio/Video transcription using Faster Whisper with LLM translation
- **Subtitle Processing** - Edit, translate, and export subtitles
- **Video Enhancement** - OCR, watermark removal, upscaling, and more

## Configuration

MediaFlow runs as a FastAPI backend service. The skill communicates with it via HTTP API.

### Environment Variables
- `MEDIAFLOW_HOST`: Backend host (default: 127.0.0.1)
- `MEDIAFLOW_PORT`: Backend port (default: 8002)

## Tools

### analyze_url
Analyze a URL to extract metadata (title, duration, thumbnail).

**Input:**
```json
{
  "url": "string (required) - URL to analyze"
}
```

**Output:**
```json
{
  "url": "string",
  "title": "string",
  "thumbnail": "string",
  "duration": "float",
  "platform": "string",
  "is_video": "boolean"
}
```

### download_media
Download media from a URL.

**Input:**
```json
{
  "url": "string (required) - Media URL to download",
  "format": "string - Quality format: best, 4k, 2k, 1080p, 720p, 480p, audio",
  "output_path": "string (optional) - Output directory path"
}
```

**Output:**
```json
{
  "task_id": "string - Task ID to track progress",
  "status": "string - pending/running/completed/failed",
  "message": "string"
}
```

### transcribe_audio
Transcribe audio/video to text with timestamps.

**Input:**
```json
{
  "audio_path": "string (required) - Path to audio/video file",
  "model": "string - Whisper model: tiny, base, small, medium, large-v1, large-v2, large-v3, large-v3-turbo",
  "device": "string - Device: cpu, cuda",
  "language": "string (optional) - Language code (e.g., en, zh, ja)",
  "initial_prompt": "string (optional) - Prompt to guide transcription"
}
```

**Output:**
```json
{
  "task_id": "string - Task ID to track progress",
  "status": "string - pending/running/completed/failed"
}
```

### translate_subtitles
Translate subtitle segments using LLM.

**Input:**
```json
{
  "segments": "array (required) - List of SubtitleSegment objects",
  "target_language": "string (required) - Target language (e.g., zh, en, ja, ko)",
  "provider": "string - LLM provider: openai (default)",
  "mode": "string - Translation mode: standard (default), reflect"
}
```

SubtitleSegment format:
```json
{
  "start": "float - Start time in seconds",
  "end": "float - End time in seconds",
  "text": "string - Subtitle text"
}
```

**Output:**
```json
{
  "task_id": "string - Task ID to track progress",
  "status": "string - pending/running/completed/failed",
  "segments": "array - Translated segments (when completed)"
}
```

### get_task_status
Get the status of a background task.

**Input:**
```json
{
  "task_id": "string (required) - Task ID to check"
}
```

**Output:**
```json
{
  "id": "string",
  "status": "string - pending/running/completed/failed",
  "progress": "float - Progress percentage",
  "result": "object - Task result data (when completed)",
  "error": "string - Error message (if failed)"
}
```

### list_tasks
List all background tasks.

**Input:** None

**Output:**
```json
[
  {
    "id": "string",
    "status": "string",
    "progress": "float",
    "name": "string",
    "type": "string",
    "created_at": "string",
    "result": "object"
  }
]
```

## Usage Examples

### Download a YouTube video
```
Call analyze_url with url="https://www.youtube.com/watch?v=..."
Then call download_media with the URL
Check task status with get_task_status
```

### Transcribe and translate a video
```
1. First download the video
2. Call transcribe_audio with audio_path pointing to the downloaded file
3. Wait for task to complete
4. Get the transcription result
5. Call translate_subtitles with the segments
```

## Notes

- MediaFlow backend must be running before using the skill
- Long-running tasks (download, transcribe) return a task_id and are processed asynchronously
- Use WebSocket or poll get_task_status to track progress
- Translation requires OpenAI API key to be configured in MediaFlow settings
