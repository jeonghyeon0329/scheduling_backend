import os, uuid, httpx

HR_BASE = os.getenv("HR_API_BASE", "http://127.0.0.1:8001")
TIMEOUT = float(os.getenv("HR_TIMEOUT", "3.0"))
CORE_TO_HR_TOKEN = os.getenv("CORE_TO_HR_TOKEN", "")

def _headers():
    h = {
        "Idempotency-Key": str(uuid.uuid4()),
        "X-Request-ID": str(uuid.uuid4()),
    }
    if CORE_TO_HR_TOKEN:
        h["Authorization"] = f"Bearer {CORE_TO_HR_TOKEN}"
    return h

def hr_signup(email: str, password: str, name: str) -> dict:
    payload = {
        "email": email, 
        "password": password, 
        "name": name, 
    }
    
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(f"{HR_BASE}/api/v1/signup", json=payload, headers=_headers())
    r.raise_for_status()
    return r.status_code, r.json()

def hr_login(email: str, password: str) -> dict:
    payload = {
        "email": email, 
        "password": password, 
    }
    
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(f"{HR_BASE}/api/v1/login", json=payload, headers=_headers())
    r.raise_for_status()
    return r.status_code, r.json()
    