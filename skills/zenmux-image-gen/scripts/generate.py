#!/usr/bin/env python3
"""
ZenMux Image Generator - Generate images via ZenMux Vertex AI
"""

import os
import sys
import json
import argparse
import base64
import requests
from pathlib import Path

DEFAULT_MODEL = "google/gemini-2.5-flash-image"
DEFAULT_SIZE = "1K"
DEFAULT_AR = "1:1"
DEFAULT_OUTPUT = "output.png"

API_BASE = "https://zenmux.ai/api/vertex-ai/v1"


def get_api_key():
    """Get ZenMux API key from environment variable."""
    key = os.environ.get("ZENMUX_API_KEY")
    if not key:
        # Try the second key format (sk-ss-v1-...)
        key = os.environ.get("ZENMUX_API_KEY")
    if not key:
        print("Error: ZENMUX_API_KEY environment variable not set", file=sys.stderr)
        print("Get your API key from https://zenmux.ai", file=sys.stderr)
        sys.exit(1)
    return key


def parse_aspect_ratio(ar: str) -> dict:
    """Parse aspect ratio string to image config."""
    # Note: ZenMux Vertex AI doesn't support custom width/height
    # Only imageSize (1K, 2K) is supported
    return {}


def generate_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: str = DEFAULT_SIZE,
    ar: str = DEFAULT_AR,
    output: str = DEFAULT_OUTPUT,
) -> str:
    """Generate image using ZenMux Vertex AI API."""
    api_key = get_api_key()
    
    # Build the URL
    url = f"{API_BASE}/models/{model}:generateContent"
    
    # Build request body
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "imageSize": size
            }
        }
    }
    
    print(f"Generating image with model: {model}", file=sys.stderr)
    print(f"Prompt: {prompt[:50]}...", file=sys.stderr)
    
    # Make the request
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    response = requests.post(url, json=body, headers=headers, timeout=120)
    
    if response.status_code != 200:
        print(f"Error: API returned {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)
    
    data = response.json()
    
    # Extract image data
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            print("Error: No candidates in response", file=sys.stderr)
            print(json.dumps(data, indent=2), file=sys.stderr)
            sys.exit(1)
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        
        image_data = None
        for part in parts:
            if "inlineData" in part:
                image_data = part["inlineData"]["data"]
                break
        
        if not image_data:
            print("Error: No image in response", file=sys.stderr)
            print(json.dumps(data, indent=2), file=sys.stderr)
            sys.exit(1)
        
    except Exception as e:
        print(f"Error parsing response: {e}", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)
    
    # Save the image
    image_bytes = base64.b64decode(image_data)
    
    # Ensure output directory exists
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    
    print(f"Image saved to: {output_path}", file=sys.stderr)
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using ZenMux Vertex AI"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image prompt text"
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"Model ID (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--size", "-s",
        default=DEFAULT_SIZE,
        choices=["1K", "2K"],
        help=f"Image size (default: {DEFAULT_SIZE})"
    )
    parser.add_argument(
        "--ar",
        default=DEFAULT_AR,
        help=f"Aspect ratio (default: {DEFAULT_AR})"
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Output file path (default: {DEFAULT_OUTPUT})"
    )
    
    args = parser.parse_args()
    
    output_path = generate_image(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
        ar=args.ar,
        output=args.output,
    )
    
    print(output_path)


if __name__ == "__main__":
    main()
