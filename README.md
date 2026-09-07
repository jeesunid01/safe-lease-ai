# 🛡️ SafeLease AI (안심계약 AI)
> **"도장 찍기 전 30초! 사장님의 수천만 원을 지켜주는 AI 계약서 독소조항 검토 & 협상 비서"**

---

## 📌 1. 프로젝트 개요 (Overview)

**SafeLease AI**는 대한민국 소상공인·자영업자가 상가 임대차 계약이나 프랜차이즈 가맹 계약 체결 시, 복잡한 법률 용어와 깨알 같은 특약 속에 숨겨진 **독소조항(원상복구 폭탄, 권리금 포기, 과도한 위약금 등)을 AI로 실시간 탐지**하고, 건물주나 가맹본사와 마찰 없이 조율할 수 있는 **완곡한 협상 대체 문구**를 제공하는 리걸테크(LegalTech) 솔루션입니다.

* **타깃 고객**: 상가 신규 입점/재계약 소상공인, 프랜차이즈 가맹점주, 공인중개사(B2B 안심 중개)
* **핵심 가치**: 변호사 자문료(30만~50만 원) 대비 1/10 수준의 비용(2만 원대)으로, 최대 수천만 원의 법적 분쟁 및 재산 손실 사전 예방
* **글로벌 벤치마크**: Product Hunt 인기 리걸테크 [Robin AI](https://www.producthunt.com/posts/robin-ai), [Pocketlaw](https://www.producthunt.com/posts/pocketlaw), [LegalOn]의 메커니즘을 한국 법률 시장에 맞게 로컬라이징

---

## 🚨 2. 해결하려는 진짜 문제 (Pain Points & Real Cases)

소상공인은 영업 현장(조리, 서빙)으로 인해 낮에는 계약서를 검토할 시간이 없으며, 마감 후 늦은 밤에 억지로 시간을 내어 검토해야 합니다. 법을 잘 모른 채 체결된 계약은 실제 파산 수준의 피해로 이어집니다.

### ⚠️ 실제 손해 발생 대표 판례 및 사례
1. **[대법원 2017다268142 판결 - 원상복구 폭탄]**:
   * 커피전문점을 포괄 양수한 세입자가 퇴거 시 "내가 설치한 시설에 한한다"는 특약을 넣지 않아, **전 임차인이 설치한 흡연실/천장 인테리어까지 수천만 원 철거비를 독박 쓴 사례**.
2. **[제소전 화해조서 기판력 악용 - 권리금 1억 증발]**:
   * "권리금을 포기한다"는 화해조서에 도장을 찍었다가, 대법원 확정판결과 동일한 효력(기판력) 때문에 **권리금 1억 2천만 원을 한 푼도 못 받고 강제 퇴거당한 사례**.
3. **[재건축 무조건 명도 특약 - 인테리어비 8천만 원 매몰]**:
   * "재건축 시 무조건 퇴거" 특약으로 인해 1년 6개월 만에 쫓겨나며 막대한 시설 투자금을 날린 사례.

---

## 🎯 3. 핵심 기능 (Core Features)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SafeLease AI 핵심 파이프라인                     │
├───────────────────┬──────────────────────────┬──────────────────────────────┤
│ 1. 멀티포맷 수용   │ 2. 독소조항 & 누락 탐지  │ 3. 실전 협상 가이드 지원      │
│ - 폰 사진(JPG/PNG)│ - 🔴위험/🟡주의/🟢안전   │ - 건물주용 완곡한 대체 조항  │
│ - PDF, HWP, DOCX  │ - 원문 정확 발췌(Quote)  │ - 넛지(Nudge) 협상 대화문    │
│ - 왜곡/그림자 보정│ - 빠져있는 필수조항 체크 │ - 등기부/건축물대장 3종 검증 │
└───────────────────┴──────────────────────────┴──────────────────────────────┘
```

1. **전천후 파일 포맷 지원 (Universal Ingestion)**:
   * 소상공인 유입의 70%인 **스마트폰 촬영 사진(JPG, PNG, HEIC)**의 비뚤어짐/그림자 자동 보정.
   * 공공/부동산 표준인 **PDF, HWP, HWPX(한글), DOCX** 무손실 텍스트 추출.
2. **원문 글자 그대로 발췌 (Verbatim Quote) & 스플릿 뷰**:
   * 할루시네이션(지어내기)을 원천 차단하고, 계약서 몇 조 몇 항의 어떤 문장이 왜 불리한지 1:1 하이라이트 매핑.
3. **누락된 필수 조항 탐지 (Missing Clauses Check)**:
   * 적혀 있는 글자만 보는 것이 아니라, *"구두로 약속받았지만 계약서에 쏙 빠져 있는 조항(주차, 관리비 상한, 에어컨 수리 주체)"*을 역으로 찾아내 체크리스트 제공.
4. **건물주 기분 안 상하게 하는 '협상 대체 문구'**:
   * "이 조항 빼주세요"가 아니라, *"단, 통상적 마모는 제외한다"*처럼 건물주가 거부감 없이 수용할 수 있는 현실적 타협안 및 대화 스크립트 출력.
5. **등기부등본 + 건축물대장 교차 검증**:
   * 위반건축물 표기(영업신고 거부 위험) 및 선순위 근저당(경매 시 깡통상가 위험) 통합 분석.

---

## 📚 4. 독소조항 판별 기준 (4대 공인 데이터베이스)

AI의 자의적 판단이 아닌, **국가 공인 4대 법률 기준**과 전문 변호사가 감수한 룰셋에 기반합니다.

1. **상위 법률 강행규정**: 「상가건물 임대차보호법」 제15조(임차인 불리 약정 무효), 「가맹사업법」, 「약관규제법」.
2. **정부 부처 공식 표준계약서**: 법무부·국토교통부 고시 **「상가건물 임대차 표준계약서」**, 공정위 **「표준가맹계약서」**.
3. **대법원 판례 DB**: 원상복구 범위, 권리금 회수 방해, 제소전 화해조서 기판력 등 확정 판결문.
4. **공정위 심결례 & 분쟁조정위원회 사례**: 실제 불공정 조항 시정명령 및 지자체 상가분쟁조정 합의 사례집.

---

## 🛠️ 5. 시스템 아키텍처 & 기술 스택 (Tech Stack)

* **Backend / CLI Engine**: Python 3.10+
  * 문서 처리: `OpenCV` (원근 왜곡 보정), `pdfplumber` / `PyMuPDF` (PDF), `hwpx` / `pyhwp` (한글), `python-docx` (워드)
  * 데이터 정규화: `Unstructured` 파이프라인
* **AI / LLM Engine**:
  * Multimodal LLM: `Gemini 2.0 Flash` / `Claude 3.5 Sonnet` (고해상도 문서 비전 인식 및 법률 추론)
  * RAG Knowledge Base: FAISS / ChromaDB (판례 및 표준계약서 벡터 임베딩)
* **API / Serving**:
  * FastAPI (RESTful API & CLI Subcommand)
  * 카카오톡 알림톡/챗봇 웹훅 연동 지원

---

## 📂 6. 프로젝트 디렉터리 구조 (Directory Structure)

```
📁 safe-lease-ai/
├── 📄 README.md                      # 본 프로젝트 통합 가이드
├── 📄 requirements.txt               # 파이썬 의존성 패키지 목록
├── 📄 .env.example                   # API 키 및 환경변수 템플릿
│
├── 📁 cli/                           # CLI 실행 진입점 및 명령어 모듈
│   ├── 📄 main.py                    # CLI 메인 인터페이스 (argparse/typer)
│   └── 📄 commands.py                # scan, analyze, report, export 명령어
│
├── 📁 core/                          # 핵심 처리 엔진
│   ├── 📁 parser/                    # 파일 포맷별 문서 파서
│   │   ├── 📄 image_ocr.py           # 스마트폰 사진 보정 & Vision OCR
│   │   ├── 📄 pdf_parser.py          # PDF 텍스트 및 레이아웃 추출
│   │   ├── 📄 hwp_parser.py          # HWP/HWPX 한글 문서 파서
│   │   └── 📄 docx_parser.py         # MS 워드 문서 파서
│   │
│   ├── 📁 analyzer/                  # 독소조항 분석 엔진
│   │   ├── 📄 rules_engine.py        # 표준계약서 대조 룰셋 엔진
│   │   ├── 📄 missing_checker.py     # 필수 누락 조항 탐지기
│   │   └── 📄 prompt_templates.py    # LLM 법률 분석 프롬프트
│   │
│   └── 📁 exporter/                  # 결과 출력 및 리포트 생성기
│       ├── 📄 console_view.py        # CLI 터미널 컬러 신호등 리포트 출력
│       └── 📄 markdown_report.py     # Markdown/PDF 리포트 생성
│
├── 📁 data/                          # 법률 지식베이스 & 표준 양식
│   ├── 📁 standard_contracts/        # 법무부/공정위 표준계약서 원문 (MD/JSON)
│   ├── 📁 precedents/                # 핵심 대법원 판례 요약 데이터 (JSONL)
│   └── 📁 ruleset/                   # 위험도별 판별 규칙 및 대체 문구 정의
│
└── 📁 tests/                         # 단위 테스트 및 가상 계약서 샘플
    ├── 📁 sample_contracts/          # 테스트용 계약서 (사진, PDF, HWP 샘플)
    └── 📄 test_analysis.py           # 분석 엔진 검증 테스트
```

---

## 🚀 7. CLI 빠른 시작 가이드 (Quick Start)

### ① 가상환경 생성 및 의존성 설치
```bash
# safe-lease-ai 디렉터리로 이동
cd C:\workspace\safe-lease-ai

# 파이썬 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\Activate.ps1

# 필수 패키지 설치
pip install -r requirements.txt
```

### ② 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 AI 모델 API 키를 등록합니다.
```env
GEMINI_API_KEY="your-gemini-api-key"
# 또는
ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### ③ CLI 계약서 검토 실행
```bash
# 1. 스마트폰 사진 계약서 검토 (터미널 신호등 리포트)
python -m cli.main analyze --file ./tests/sample_contracts/sample_lease.jpg --role tenant

# 2. HWP 한글 가맹계약서 검토 및 결과 마크다운 저장
python -m cli.main analyze --file ./tests/sample_contracts/franchise_draft.hwp --role franchisee --output report.md

# 3. 필수 누락 조항만 집중 체크
python -m cli.main check-missing --file ./tests/sample_contracts/sample_lease.pdf
```

---

## 🌐 8. 서비스 배포 가이드 (Deployment Guide)

### ① Vercel 배포 (Serverless REST API & 게이트웨이)
본 저장소는 Vercel 환경에 최적화된 `vercel.json` 및 `api/index.py` Serverless Function을 탑재하고 있습니다.
1. GitHub 저장소를 Vercel에 연동하여 바로 배포할 수 있습니다.
2. 배포 완료 시 제공되는 Serverless 엔드포인트:
   - `GET /` : 세련된 웹 게이트웨이 및 서비스 안내 페이지
   - `GET /api/health` : 서버 상태 및 무보관 원칙(Zero-Retention) 점검
   - `GET /api/rules` : 독소조항 탐지 룰셋 요약 조회
   - `GET /api/precedents?q=원상복구` : 대법원 확정 판례 키워드 검색
   - `POST /api/analyze` : 계약서 텍스트 즉시 진단 (JSON 입력 및 결과 반환)
3. 환경 변수 등록 (Vercel Project Settings > Environment Variables):
   - `GEMINI_API_KEY`: Gemini API 키
   - `APP_URL`: 배포 도메인 (생략 시 `VERCEL_URL` 자동 감지)

### ② Streamlit Community Cloud (원클릭 무료 풀 UI 호스팅)
소상공인 사장님 라운지 전체 웹 대시보드(카메라 OCR, 탭 화면 등)를 호스팅할 때:
1. [share.streamlit.io](https://share.streamlit.io/)에 접속하여 GitHub 저장소 연결
2. Main file path: `web/app.py` 지정 후 배포
3. Secrets에 `GEMINI_API_KEY` 등록 후 1분 만에 실서비스 가동

---

## ⚖️ 9. 컴플라이언스 및 면책 고지 (Legal Disclaimer)

* 본 프로그램은 변호사법 제109조를 준수하며, **법률적 대리나 개별 사안에 대한 확정적 법률 자문을 제공하지 않습니다.**
* 본 프로그램의 결과물은 **공개된 정부 표준계약서 및 법원 판례 DB와의 대조 분석 정보(참고자료)**로만 제공되며, 중대한 법적 분쟁이나 의사결정 시에는 반드시 변호사, 가맹거래사, 공인중개사 등 자격 있는 법률 전문가의 확인을 받으시기 바랍니다.

---
- **작성일**: 2026-09-07
- **참고 규정**: `C:\workspace\law.md`
