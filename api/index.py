"""
SafeLease AI - Vercel Serverless Function API Entrypoint
소상공인을 위한 안심 임대차 계약 진단 서비스 Serverless API
"""

import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler

# 프로젝트 루트 경로를 sys.path에 등록
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.analyzer.rules_engine import RulesEngine
from core.analyzer.missing_checker import MissingChecker
from core.analyzer.precedent_matcher import PrecedentDB
from core.parser.txt_parser import TxtParser
from core.parser.base_parser import ContractDocument, ClauseItem
from core.security.anonymizer import mask_pii
from config import get_app_url


class handler(BaseHTTPRequestHandler):
    """Vercel Python Serverless HTTP Request Handler"""

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        """CORS Preflight 대응"""
        self._set_headers(200)

    def do_GET(self):
        """GET 요청 처리: 헬스체크, 판례 조회, 룰셋 정보, 웹 랜딩 페이지"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/")
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # 1. 헬스체크 및 서비스 상태 (/api/health 또는 /api)
        if path in ["/api/health", "/api/status", "/api"]:
            response_data = {
                "status": "healthy",
                "service": "SafeLease AI - Serverless API",
                "version": "1.2.0",
                "app_url": get_app_url(),
                "endpoints": {
                    "health": "GET /api/health",
                    "rules": "GET /api/rules",
                    "precedents": "GET /api/precedents?q={keyword}",
                    "analyze": "POST /api/analyze"
                },
                "security": {
                    "zero_retention": True,
                    "pii_masking": True
                }
            }
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(response_data, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # 2. 판례 검색 (/api/precedents)
        if path == "/api/precedents":
            db = PrecedentDB()
            query = query_params.get("q", [""])[0].strip()
            if query:
                results = db.search(query)
            else:
                results = db.get_all()

            data = [
                {
                    "precedent_id": p.precedent_id,
                    "case_no": p.case_no,
                    "case_date": p.case_date,
                    "title": p.title,
                    "category": p.category,
                    "summary": p.summary,
                    "key_quote": p.key_quote,
                    "action_guide": p.action_guide
                }
                for p in results
            ]
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({"total": len(data), "items": data}, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # 3. 룰셋 목록 (/api/rules)
        if path == "/api/rules":
            contract_type = query_params.get("type", ["all"])[0]
            engine = RulesEngine(contract_type=contract_type)
            rules_summary = [
                {
                    "rule_id": r.get("rule_id"),
                    "title": r.get("title"),
                    "category": r.get("category"),
                    "risk_level": r.get("risk_level"),
                    "legal_basis": r.get("legal_basis")
                }
                for r in engine.rules
            ]
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({"count": len(rules_summary), "rules": rules_summary}, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # 4. 루트 웹 랜딩 페이지 (브라우저 접속 시 모던 랜딩 페이지 렌더링)
        accept_header = self.headers.get("Accept", "")
        if "text/html" in accept_header or path in ["", "/"]:
            landing_html = self._render_landing_page()
            self._set_headers(200, "text/html")
            self.wfile.write(landing_html.encode("utf-8"))
            return

        # 404 처리
        self._set_headers(404, "application/json")
        self.wfile.write(json.dumps({"error": "Not Found", "path": path}, ensure_ascii=False).encode("utf-8"))

    def do_POST(self):
        """POST 요청 처리: 계약서 본문 비동기 검사 (/api/analyze)"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/")

        if path == "/api/analyze":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length == 0:
                    self._set_headers(400, "application/json")
                    self.wfile.write(json.dumps({"error": "본문 데이터가 비어 있습니다."}, ensure_ascii=False).encode("utf-8"))
                    return

                post_body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(post_body)
                raw_text = data.get("text", "").strip()
                contract_type = data.get("contract_type", "lease")
                filename = data.get("filename", "api_contract.txt")

                if not raw_text:
                    self._set_headers(400, "application/json")
                    self.wfile.write(json.dumps({"error": "'text' 필드는 필수 항목입니다."}, ensure_ascii=False).encode("utf-8"))
                    return

                # Zero-Retention & PII Masking
                masked_text, masked_count = mask_pii(raw_text)

                # 조항 분리 및 ContractDocument 생성
                parser = TxtParser()
                clauses = parser.extract_clauses(masked_text)
                if not clauses:
                    clauses = [ClauseItem(article_no="전문", title=None, content=masked_text, page=1)]

                doc = ContractDocument(
                    filename=filename,
                    file_type="txt",
                    raw_text=masked_text,
                    clauses=clauses,
                    masked_items_count=masked_count,
                    char_count=len(masked_text)
                )

                # 룰셋 및 필수조항 검사 실행
                engine = RulesEngine(contract_type=contract_type)
                result = engine.analyze(doc)
                missing_checker = MissingChecker()
                missing_items = missing_checker.check(doc)

                response_payload = {
                    "status": "success",
                    "document_name": result.document_name,
                    "safety_score": result.safety_score,
                    "risk_summary": result.risk_summary,
                    "has_critical_toxic": result.has_critical_toxic,
                    "masked_pii_count": masked_count,
                    "detected_issues": [
                        {
                            "rule_id": iss.rule_id,
                            "category": iss.category,
                            "risk_level": iss.risk_level,
                            "title": iss.title,
                            "matched_clause_no": iss.matched_clause_no,
                            "verbatim_quote": iss.verbatim_quote,
                            "legal_basis": iss.legal_basis,
                            "danger_explanation": iss.danger_explanation,
                            "recommended_replacement": iss.recommended_replacement,
                            "nudge_script_polite": iss.nudge_script_polite
                        }
                        for iss in result.detected_issues
                    ],
                    "missing_clauses": [
                        {
                            "check_id": m.check_id,
                            "category": m.category,
                            "title": m.title,
                            "why_important": m.why_important,
                            "legal_basis": m.legal_basis,
                            "recommended_clause": m.recommended_clause,
                            "is_missing": m.is_missing
                        }
                        for m in missing_items if m.is_missing
                    ]
                }

                self._set_headers(200, "application/json")
                self.wfile.write(json.dumps(response_payload, ensure_ascii=False, indent=2).encode("utf-8"))

            except Exception as e:
                self._set_headers(500, "application/json")
                self.wfile.write(json.dumps({"error": f"분석 중 오류가 발생했습니다: {str(e)}"}, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "application/json")
        self.wfile.write(json.dumps({"error": "Endpoint Not Found"}, ensure_ascii=False).encode("utf-8"))

    def _render_landing_page(self) -> str:
        """Vercel 웹 브라우저 방문자용 세련된 안심 라운지 소개 및 API 게이트웨이 페이지"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeLease AI | 사장님의 안심계약 비서</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-accent: #2563eb;
            --bg: #f8fafc;
            --surface: #ffffff;
            --text-main: #0f172a;
            --text-muted: #475569;
            --border: #e2e8f0;
            --emerald: #059669;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Pretendard', sans-serif; }
        body { background: var(--bg); color: var(--text-main); line-height: 1.6; }
        .hero {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%);
            color: #ffffff;
            padding: 80px 24px;
            text-align: center;
        }
        .hero h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 16px; letter-spacing: -0.5px; }
        .hero p { font-size: 1.2rem; opacity: 0.92; max-width: 680px; margin: 0 auto 28px; }
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 20px;
            backdrop-filter: blur(8px);
        }
        .container { max-width: 1040px; margin: -40px auto 60px; padding: 0 20px; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
        .card {
            background: var(--surface);
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
            border: 1px solid var(--border);
        }
        .card h2 { font-size: 1.3rem; font-weight: 700; color: var(--primary); margin-bottom: 12px; }
        .card p { color: var(--text-muted); font-size: 0.98rem; }
        .code-box {
            background: #0f172a;
            color: #f8fafc;
            padding: 16px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 0.88rem;
            margin-top: 16px;
            overflow-x: auto;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: var(--emerald);
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 16px;
        }
        .status-dot { width: 10px; height: 10px; background: var(--emerald); border-radius: 50%; display: inline-block; }
        .footer { text-align: center; padding: 40px 20px; color: var(--text-muted); font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="hero">
        <span class="badge">🛡️ SafeLease AI • Vercel Serverless Edition</span>
        <h1>도장 찍기 전 30초! 사장님의 안심계약 비서</h1>
        <p>상가임대차보호법 강행규정(제15조) 및 대법원 확정 판례 기반 자동 진단 엔진</p>
    </div>

    <div class="container">
        <div class="card-grid">
            <div class="card">
                <div class="status-pill"><span class="status-dot"></span> Serverless Engine Operational</div>
                <h2>⚡ 고성능 진단 REST API</h2>
                <p>계약서 본문을 전송하면 독소조항, 누락 필수조항, 안전 점수를 1초 이내에 자동 진단합니다.</p>
                <div class="code-box">POST /api/analyze<br>GET /api/precedents<br>GET /api/rules</div>
            </div>

            <div class="card">
                <h2>🔒 3대 안심 보장 원칙</h2>
                <p>1. 주민번호·계좌번호 즉시 자동 마스킹 (PII Scrubbing)<br>
                   2. 진단 완료 후 원본 즉시 파기 (Zero-Retention)<br>
                   3. 임대인 심기를 건드리지 않는 완곡한 협상 문구 제공</p>
            </div>

            <div class="card">
                <h2>📱 Streamlit 종합 라운지 연결</h2>
                <p>웹 브라우저, 아이패드, 갤럭시 탭에서 직접 파일 업로드 및 카메라 촬영으로 전체 UI를 이용할 수 있습니다.</p>
                <div class="code-box">python -m streamlit run web/app.py</div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>SafeLease AI v1.2 • Commercial & Franchise Real Estate Contract Protector</p>
    </div>
</body>
</html>
"""
