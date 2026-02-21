#!/usr/bin/env python3
"""Quick test script for MediaFlow skill."""
import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_health():
    """Test health endpoint."""
    print("Testing health check...")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.json()}")
    return resp.status_code == 200

def test_analyze():
    """Test URL analyze."""
    print("\nTesting analyze...")
    resp = requests.post(
        f"{BASE_URL}/api/v1/analyze/",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(resp.json(), indent=2)}")
    return resp.status_code == 200

def test_translate():
    """Test translation."""
    print("\nTesting translate...")
    resp = requests.post(
        f"{BASE_URL}/api/v1/translate/",
        json={
            "segments": [
                {"start": 0.0, "end": 5.0, "text": "Hello world"},
                {"start": 5.0, "end": 10.0, "text": "This is a test"}
            ],
            "target_language": "zh",
            "provider": "openai"
        }
    )
    print(f"  Status: {resp.status_code}")
    data = resp.json()
    print(f"  Response: {json.dumps(data, indent=2)}")
    
    # Check task status
    if resp.status_code == 200 and "task_id" in data:
        task_id = data["task_id"]
        print(f"\n  Checking task {task_id}...")
        resp2 = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
        print(f"  Task Status: {resp2.json()['status']}")
    
    return resp.status_code == 200

def test_list_tasks():
    """Test list tasks."""
    print("\nTesting list tasks...")
    resp = requests.get(f"{BASE_URL}/api/v1/tasks/")
    print(f"  Status: {resp.status_code}")
    print(f"  Tasks: {len(resp.json())}")
    return resp.status_code == 200

def main():
    print("=" * 50)
    print("MediaFlow Skill Test")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Analyze URL", test_analyze),
        ("Translate", test_translate),
        ("List Tasks", test_list_tasks),
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("Summary:")
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    print("=" * 50)

if __name__ == "__main__":
    main()
