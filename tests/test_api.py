"""
SafeLease AI - Vercel Serverless API 테스트
"""

import io
import json
import pytest
from unittest.mock import MagicMock
from api.index import handler


class DummyHandler(handler):
    """테스트용 BaseHTTPRequestHandler 목 인스턴스"""
    def __init__(self, method: str, path: str, body: bytes = b"", headers: dict = None):
        self.command = method
        self.path = path
        self.request_version = "HTTP/1.1"
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.headers = headers or {}
        if "Content-Length" not in self.headers and body:
            self.headers["Content-Length"] = str(len(body))
        self.status_code = None
        self.sent_headers = {}

    def send_response(self, code, message=None):
        self.status_code = code

    def send_header(self, keyword, value):
        self.sent_headers[keyword] = value

    def end_headers(self):
        pass


def test_api_health_endpoint():
    """헬스체크 엔드포인트(/api/health) 응답 검증"""
    req = DummyHandler("GET", "/api/health")
    req.do_GET()

    assert req.status_code == 200
    response_body = json.loads(req.wfile.getvalue().decode("utf-8"))
    assert response_body["status"] == "healthy"
    assert "SafeLease AI" in response_body["service"]
    assert response_body["security"]["zero_retention"] is True


def test_api_precedents_endpoint():
    """판례 조회 및 키워드 검색 엔드포인트(/api/precedents) 검증"""
    req = DummyHandler("GET", "/api/precedents?q=원상복구")
    req.do_GET()

    assert req.status_code == 200
    response_body = json.loads(req.wfile.getvalue().decode("utf-8"))
    assert response_body["total"] > 0
    assert any("원상복구" in item["title"] or "원상회복" in item["summary"] for item in response_body["items"])


def test_api_rules_endpoint():
    """룰셋 조회 엔드포인트(/api/rules) 검증"""
    req = DummyHandler("GET", "/api/rules?type=lease")
    req.do_GET()

    assert req.status_code == 200
    response_body = json.loads(req.wfile.getvalue().decode("utf-8"))
    assert response_body["count"] > 0
    assert len(response_body["rules"]) > 0


def test_api_analyze_toxic_contract():
    """계약서 본문 독소조항 진단 API(/api/analyze) 검증"""
    payload = {
        "text": "제5조 (원상복구) 임차인은 이전 세입자의 시설물 일체를 철거하여 공실 상태로 원상복구한다. 권리금은 일체 인정하지 않는다.",
        "contract_type": "lease",
        "filename": "test_toxic.txt"
    }
    body_bytes = json.dumps(payload).encode("utf-8")
    req = DummyHandler("POST", "/api/analyze", body=body_bytes, headers={"Content-Length": str(len(body_bytes))})
    req.do_POST()

    assert req.status_code == 200
    response_body = json.loads(req.wfile.getvalue().decode("utf-8"))
    assert response_body["status"] == "success"
    assert response_body["safety_score"] < 100
    assert len(response_body["detected_issues"]) >= 1
