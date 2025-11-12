from decouple import config
import httpx

HR_BASE = config('HR_BASE_URL')

def hr_post(path: str, data: dict):
    try:
        with httpx.Client() as client:
            r = client.post(f"{HR_BASE}{path}", json=data, timeout=3)
            try:
                res_json = r.json()
                return r.status_code, res_json
            except ValueError:
                return r.status_code, {
                    "success": False,
                    "code": "HS_A2",
                    "detail": "Invalid JSON response."
                }
    except httpx.RequestError:
        return 502, {
            "success": False,
            "code": "HS_A1",
            "detail": "Failed to reach HR system."
        }
