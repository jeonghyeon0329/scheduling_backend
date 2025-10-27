# scheduling backend
스케줄링 시스템 백엔드 개발
---
## 📦 요구 사항
- Python 3.13+
- Django 5.x
- Django REST Framework
- PostgreSQL

## 🛠 설치
```bash
# 1) 저장소 클론
git clone https://github.com/jeonghyeon0329/django_server.git

# 2) 가상환경 & 패키지 설치 (pip)
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) 마이그레이션 & 서버 실행
python manage.py migrate
python manage.py runserver
```

📂 프로젝트 구성
1. core_system
- 역할: 게이트웨이 시스템
- 외부 요청을 받아 hr_system과 통신

2. hr_system
- 역할: 인사관리 서비스 (HR 전용)
- 사용자 계정(User) 관리