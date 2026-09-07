"""
SafeLease AI - 전역 설정 및 경로 관리 모듈
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# 기본 디렉터리 경로 설정
BASE_DIR = Path(__file__).resolve().parent

# 핵심 서브 디렉터리 경로
CORE_DIR = BASE_DIR / "core"
DATA_DIR = BASE_DIR / "data"
CLI_DIR = BASE_DIR / "cli"
WEB_DIR = BASE_DIR / "web"
TESTS_DIR = BASE_DIR / "tests"

# 데이터 관련 세부 경로
HISTORY_DIR = DATA_DIR / "history"
RULESET_DIR = DATA_DIR / "ruleset"
PRECEDENTS_DIR = DATA_DIR / "precedents"
STANDARD_CONTRACTS_DIR = DATA_DIR / "standard_contracts"

# 임시 파일 디렉터리 (Zero-Retention: 처리 후 즉시 파기)
TEMP_DIR = BASE_DIR / "temp"

# 데이터베이스 설정
DB_PATH = HISTORY_DIR / os.getenv("DB_NAME", "safe_lease.db")

# AI API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 필수 디렉터리 자동 생성 보장
for directory in [HISTORY_DIR, RULESET_DIR, PRECEDENTS_DIR, STANDARD_CONTRACTS_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def get_app_url() -> str:
    """배포 환경(Vercel, 도메인 등) 또는 로컬 네트워크 IP 동적 반환 (하드코딩 URL 원천 제거)"""
    # 1. 환경 변수 우선 (Vercel 기본 제공 변수 또는 사용자 지정 도메인)
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}" if not vercel_url.startswith("http") else vercel_url

    app_url = os.getenv("APP_URL")
    if app_url:
        return app_url

    # 2. 로컬 Wi-Fi / 네트워크 IP 자동 감지
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        port = os.getenv("PORT", "8501")
        return f"http://{local_ip}:{port}"
    except Exception:
        return "http://localhost:8501"
