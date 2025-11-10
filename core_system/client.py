from decouple import config
import httpx

HR_BASE = config('HR_BASE_URL')

def hr_post(path: str, data: dict):
    try:
        with httpx.Client() as client:
            r = client.post(f"{HR_BASE}{path}", json=data, timeout=10)
            try:
                return r.status_code, r.json()
            except ValueError:
                return r.status_code, {"detail": r.text or "Invalid JSON response"}
    except httpx.RequestError as e:
        return 502, {"detail": f"HR 시스템 연결 실패: {str(e)}"}