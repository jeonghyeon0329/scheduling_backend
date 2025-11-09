import httpx

HR_BASE = "http://hr_web:8001/api/v1"

def hr_post(path: str, data: dict):
    with httpx.Client() as client:
        r = client.post(f"{HR_BASE}{path}", json=data, timeout=10)
    return r.status_code, r.json()
