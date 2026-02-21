"""
MediaFlow Skill Implementation

This skill provides tools for video downloading, transcription, and translation
using the MediaFlow backend API.
"""
import os
import httpx
from typing import Optional, List, Dict, Any


MEDIAFLOW_HOST = os.environ.get("MEDIAFLOW_HOST", "127.0.0.1")
MEDIAFLOW_PORT = os.environ.get("MEDIAFLOW_PORT", "8002")
BASE_URL = f"http://{MEDIAFLOW_HOST}:{MEDIAFLOW_PORT}"


class MediaFlowClient:
    """Client for MediaFlow API."""
    
    def __init__(self):
        self.base_url = BASE_URL
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to MediaFlow API."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
    
    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a URL to extract metadata.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dict with url, title, thumbnail, duration, platform, is_video
        """
        return await self._request(
            "POST",
            "/api/v1/analyze/",
            json={"url": url}
        )
    
    async def download_media(
        self,
        url: str,
        format: str = "best",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download media from a URL.
        
        Args:
            url: Media URL to download
            format: Quality format (best, 4k, 2k, 1080p, 720p, 480p, audio)
            output_path: Output directory path
            
        Returns:
            Dict with task_id, status
        """
        # For download, we need to use pipeline or direct download endpoint
        # Using analyze first to get the media info
        return await self._request(
            "POST",
            "/api/v1/pipeline/run",
            json={
                "url": url,
                "steps": [
                    {
                        "step_type": "download",
                        "params": {
                            "format": format,
                            "output_path": output_path
                        }
                    }
                ]
            }
        )
    
    async def transcribe_audio(
        self,
        audio_path: str,
        model: str = "base",
        device: str = "cpu",
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio/video to text.
        
        Args:
            audio_path: Path to audio/video file
            model: Whisper model (tiny, base, small, medium, large-v1, large-v2, large-v3, large-v3-turbo)
            device: Device (cpu, cuda)
            language: Language code (e.g., en, zh, ja)
            initial_prompt: Prompt to guide transcription
            
        Returns:
            Dict with task_id, status
        """
        payload = {
            "audio_path": audio_path,
            "model": model,
            "device": device
        }
        if language:
            payload["language"] = language
        if initial_prompt:
            payload["initial_prompt"] = initial_prompt
            
        return await self._request(
            "POST",
            "/api/v1/transcribe/",
            json=payload
        )
    
    async def translate_subtitles(
        self,
        segments: List[Dict[str, Any]],
        target_language: str,
        provider: str = "openai",
        mode: str = "standard"
    ) -> Dict[str, Any]:
        """
        Translate subtitle segments using LLM.
        
        Args:
            segments: List of SubtitleSegment objects
            target_language: Target language (e.g., zh, en, ja, ko)
            provider: LLM provider (openai)
            mode: Translation mode (standard, reflect)
            
        Returns:
            Dict with task_id, status
        """
        return await self._request(
            "POST",
            "/api/v1/translate/",
            json={
                "segments": segments,
                "target_language": target_language,
                "provider": provider,
                "mode": mode
            }
        )
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a background task.
        
        Args:
            task_id: Task ID to check
            
        Returns:
            Dict with id, status, progress, result, error
        """
        return await self._request(
            "GET",
            f"/api/v1/tasks/{task_id}"
        )
    
    async def list_tasks(self) -> List[Dict[str, Any]]:
        """
        List all background tasks.
        
        Returns:
            List of task objects
        """
        return await self._request(
            "GET",
            "/api/v1/tasks/"
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if MediaFlow backend is running."""
        return await self._request(
            "GET",
            "/health"
        )


# Global client instance
_client: Optional[MediaFlowClient] = None


def get_client() -> MediaFlowClient:
    """Get or create MediaFlow client."""
    global _client
    if _client is None:
        _client = MediaFlowClient()
    return _client


# === Tool Implementations ===

async def analyze_url(url: str) -> Dict[str, Any]:
    """
    Analyze a URL to extract metadata (title, duration, thumbnail).
    
    Args:
        url: URL to analyze
        
    Returns:
        Dict with url, title, thumbnail, duration, platform, is_video
    """
    client = get_client()
    return await client.analyze_url(url)


async def download_media(
    url: str,
    format: str = "best",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Download media from a URL.
    
    Args:
        url: Media URL to download
        format: Quality format (best, 4k, 2k, 1080p, 720p, 480p, audio)
        output_path: Output directory path
        
    Returns:
        Dict with task_id, status
    """
    client = get_client()
    return await client.download_media(url, format, output_path)


async def transcribe_audio(
    audio_path: str,
    model: str = "base",
    device: str = "cpu",
    language: Optional[str] = None,
    initial_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribe audio/video to text with timestamps.
    
    Args:
        audio_path: Path to audio/video file
        model: Whisper model (tiny, base, small, medium, large-v1, large-v2, large-v3, large-v3-turbo)
        device: Device (cpu, cuda)
        language: Language code (e.g., en, zh, ja)
        initial_prompt: Prompt to guide transcription
        
    Returns:
        Dict with task_id, status
    """
    client = get_client()
    return await client.transcribe_audio(
        audio_path, model, device, language, initial_prompt
    )


async def translate_subtitles(
    segments: List[Dict[str, Any]],
    target_language: str,
    provider: str = "openai",
    mode: str = "standard"
) -> Dict[str, Any]:
    """
    Translate subtitle segments using LLM.
    
    Args:
        segments: List of SubtitleSegment objects with start, end, text
        target_language: Target language (e.g., zh, en, ja, ko)
        provider: LLM provider (openai)
        mode: Translation mode (standard, reflect)
        
    Returns:
        Dict with task_id, status
    """
    client = get_client()
    return await client.translate_subtitles(
        segments, target_language, provider, mode
    )


async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a background task.
    
    Args:
        task_id: Task ID to check
        
    Returns:
        Dict with id, status, progress, result, error
    """
    client = get_client()
    return await client.get_task_status(task_id)


async def list_tasks() -> List[Dict[str, Any]]:
    """
    List all background tasks.
    
    Returns:
        List of task objects
    """
    client = get_client()
    return await client.list_tasks()


async def health_check() -> Dict[str, Any]:
    """Check if MediaFlow backend is running."""
    client = get_client()
    return await client.health_check()
