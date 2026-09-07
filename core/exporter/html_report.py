"""
SafeLease AI - A4 규격 맞춤 인쇄 / PDF 법률 의견서 HTML 생성기
브라우저 인쇄(Ctrl+P) 및 PDF 저장 시 관공서/로펌 공문서 수준의 고품질 출력 레이아웃을 제공합니다.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import html
from core.analyzer.rules_engine import AnalysisResult
from core.analyzer.missing_checker import MissingCheckItem
from core.analyzer.precedent_matcher import PrecedentDB


def generate_a4_html_report(
    analysis: AnalysisResult,
    missing_items: Optional[List[MissingCheckItem]] = None,
    tenant_name: str = "의뢰인",
    version_label: str = "최종 검토본",
    doc_no: Optional[str] = None
) -> str:
    """A4 인쇄 및 PDF 저장에 최적화된 독립형 공문서 스타일 HTML 리포트 생성"""
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y년 %m월 %d일 %H:%M")
    doc_id = doc_no or f"SL-{now_dt.strftime('%Y%m%d')}-{abs(hash(tenant_name)) % 9000 + 1000}"

    score = analysis.safety_score
    if score >= 80:
        grade_text = "🟢 안전 표준 계약서 (우수)"
        grade_color = "#059669"
        grade_bg = "#ECFDF5"
    elif score >= 60:
        grade_text = "🟡 주의 권장 (일부 특약 조율 필요)"
        grade_color = "#D97706"
        grade_bg = "#FFFBEB"
    else:
        grade_text = "🔴 위험 (강행규정 위반 및 독소조항 다수)"
        grade_color = "#DC2626"
        grade_bg = "#FEF2F2"

    red_count = analysis.risk_summary.get("RED", 0)
    yellow_count = analysis.risk_summary.get("YELLOW", 0)

    prec_db = PrecedentDB()

    # 이슈 카드 HTML 생성
    issues_html = ""
    if not analysis.detected_issues:
        issues_html = """
        <div class="safe-banner">
            <h3>🎉 축하합니다! 안전한 표준 계약서입니다.</h3>
            <p>상가건물임대차보호법 강행규정(제15조)이나 대법원 판례에 반하여 임차인에게 일방적으로 불리한 특약이 발견되지 않았습니다.</p>
        </div>
        """
    else:
        for idx, iss in enumerate(analysis.detected_issues, 1):
            badge_class = "badge-red" if iss.risk_level == "RED" else "badge-yellow"
            badge_label = "🔴 조율 필요 (RED)" if iss.risk_level == "RED" else "🟡 주의 권장 (YELLOW)"
            page_info = f"제{getattr(iss, 'page', 1)}페이지 • {iss.matched_clause_no or '특약'}"

            matched_prec = prec_db.find_by_case_no(iss.legal_basis)
            prec_html = ""
            if matched_prec:
                prec_html = f"""
                <div class="precedent-box">
                    <b>⚖️ 대법원 확정 판례 ({matched_prec.case_no})</b><br>
                    <span class="prec-summary">{html.escape(matched_prec.summary)}</span><br>
                    <div class="prec-quote">"{html.escape(matched_prec.key_quote)}"</div>
                </div>
                """

            issues_html += f"""
            <div class="issue-card avoid-break">
                <div class="issue-header">
                    <span class="badge {badge_class}">{badge_label}</span>
                    <span class="issue-loc">{page_info} | {html.escape(iss.category)}</span>
                    <h3 class="issue-title">{idx}. {html.escape(iss.title)}</h3>
                </div>
                <div class="quote-box">
                    <span class="quote-label">🔍 계약서 원문 발췌:</span>
                    <div class="quote-content">"{html.escape(iss.verbatim_quote)}"</div>
                </div>
                <div class="two-col">
                    <div class="col">
                        <div class="col-title">⚠️ 사장님께 불리한 이유</div>
                        <p>{html.escape(iss.danger_explanation)}</p>
                    </div>
                    <div class="col">
                        <div class="col-title">📜 법적 근거 및 실정법</div>
                        <p><b>{html.escape(iss.legal_basis)}</b></p>
                        {prec_html}
                    </div>
                </div>
                <div class="solution-box">
                    <div class="solution-title">✨ 권장 대체 조항 (계약서 수정 반영용)</div>
                    <div class="solution-code">{html.escape(iss.recommended_replacement)}</div>
                </div>
                <div class="talk-box">
                    <b>💬 임대인 협상용 정중한 대화문:</b> "{html.escape(iss.nudge_script_polite)}"
                </div>
            </div>
            """

    # 누락 조항 테이블
    missing_html = ""
    if missing_items:
        missing_only = [m for m in missing_items if m.is_missing]
        if missing_only:
            rows_html = ""
            for m in missing_only:
                rows_html += f"""
                <tr>
                    <td style="font-weight: 700;">{html.escape(m.title)}</td>
                    <td>{html.escape(m.why_important)}</td>
                    <td style="font-family: monospace; font-size: 8.5pt;">{html.escape(m.recommended_clause)}</td>
                </tr>
                """
            missing_html = f"""
            <div class="section-block avoid-break">
                <h2 class="section-title">⚠️ 2. 누락된 필수 보호 특약 체크리스트</h2>
                <table class="report-table">
                    <thead>
                        <tr>
                            <th style="width: 25%;">점검 항목</th>
                            <th style="width: 35%;">누락 시 위험 요소</th>
                            <th style="width: 40%;">추천 보완 문구</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>안심진단의견서_{tenant_name}_{version_label}</title>
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    * {{
        box-sizing: border-box;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }}

    body {{
        margin: 0;
        padding: 20px;
        background: #F1F5F9;
        color: #1E293B;
        font-size: 9.5pt;
        line-height: 1.5;
    }}

    /* 인쇄 툴바 (화면 전용) */
    .print-toolbar {{
        max-width: 800px;
        margin: 0 auto 16px auto;
        padding: 12px 18px;
        background: #1E293B;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .btn-print {{
        background: #2563EB;
        color: white;
        border: none;
        padding: 9px 18px;
        font-size: 13px;
        font-weight: 700;
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.2s;
    }}
    .btn-print:hover {{
        background: #1D4ED8;
    }}
    .print-tip {{
        font-size: 12px;
        color: #94A3B8;
    }}

    /* A4 용지 규격 컨테이너 */
    .a4-container {{
        max-width: 800px;
        margin: 0 auto;
        background: white;
        padding: 32px 36px;
        border-radius: 4px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
    }}

    /* 공문서 헤더 */
    .doc-header {{
        border-bottom: 2px solid #0F172A;
        padding-bottom: 14px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }}
    .doc-title-box h1 {{
        font-size: 18pt;
        font-weight: 800;
        margin: 0 0 4px 0;
        color: #0F172A;
        letter-spacing: -0.02em;
    }}
    .doc-title-box p {{
        font-size: 9.5pt;
        color: #64748B;
        margin: 0;
    }}
    .doc-meta-right {{
        text-align: right;
        font-size: 8.5pt;
        color: #475569;
    }}
    .doc-meta-right b {{
        color: #0F172A;
    }}

    /* 핵심 요약 메트릭스 그리드 */
    .meta-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 22px;
        font-size: 9pt;
    }}
    .meta-table th {{
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        padding: 7px 10px;
        text-align: left;
        width: 18%;
        color: #334155;
    }}
    .meta-table td {{
        border: 1px solid #CBD5E1;
        padding: 7px 10px;
        color: #0F172A;
    }}

    /* 점수 하이라이트 배너 */
    .score-banner {{
        background: {grade_bg};
        border: 1.5px solid {grade_color};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .score-banner .score-text {{
        font-size: 16pt;
        font-weight: 800;
        color: {grade_color};
    }}
    .score-banner .score-desc {{
        font-size: 10pt;
        font-weight: 700;
        color: #1E293B;
    }}

    /* 4대 공인 출처 인증 배지 바 */
    .auth-bar {{
        background: #F8FAFC;
        border: 1px dashed #94A3B8;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 24px;
        font-size: 8pt;
        color: #475569;
        display: flex;
        justify-content: space-around;
        text-align: center;
    }}
    .auth-item b {{
        color: #1E293B;
        display: block;
        font-size: 8.5pt;
    }}

    /* 섹션 제목 */
    .section-title {{
        font-size: 12pt;
        font-weight: 800;
        color: #0F172A;
        border-left: 4px solid #2563EB;
        padding-left: 8px;
        margin: 22px 0 12px 0;
    }}

    /* 이슈 카드 */
    .issue-card {{
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 14px;
        background: #FFFFFF;
    }}
    .issue-header {{
        margin-bottom: 8px;
    }}
    .issue-title {{
        font-size: 11pt;
        font-weight: 700;
        margin: 6px 0 0 0;
        color: #0F172A;
    }}
    .issue-loc {{
        font-size: 8.5pt;
        color: #64748B;
        margin-left: 6px;
    }}
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 7.5pt;
        font-weight: 700;
    }}
    .badge-red {{
        background: #FEE2E2;
        color: #B91C1C;
    }}
    .badge-yellow {{
        background: #FEF3C7;
        color: #92400E;
    }}

    .quote-box {{
        background: #F8FAFC;
        border-left: 3px solid #64748B;
        padding: 6px 10px;
        margin: 8px 0;
        font-size: 8.5pt;
    }}
    .quote-label {{
        font-weight: 700;
        color: #475569;
    }}
    .quote-content {{
        font-style: italic;
        color: #0F172A;
        margin-top: 2px;
    }}

    .two-col {{
        display: flex;
        gap: 12px;
        margin: 8px 0;
        font-size: 8.5pt;
    }}
    .col {{
        flex: 1;
        background: #FAFAFA;
        padding: 8px 10px;
        border-radius: 6px;
        border: 1px solid #F1F5F9;
    }}
    .col-title {{
        font-weight: 700;
        margin-bottom: 4px;
        color: #1E293B;
    }}
    .col p {{
        margin: 0;
        color: #334155;
    }}

    .precedent-box {{
        margin-top: 6px;
        background: #EFF6FF;
        border-radius: 4px;
        padding: 6px 8px;
        font-size: 8pt;
        border: 1px solid #DBEAFE;
    }}
    .prec-quote {{
        font-style: italic;
        color: #1E40AF;
        margin-top: 3px;
        font-weight: 600;
    }}

    .solution-box {{
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 6px;
        padding: 8px 10px;
        margin-top: 8px;
        font-size: 8.5pt;
    }}
    .solution-title {{
        font-weight: 700;
        color: #15803D;
        margin-bottom: 3px;
    }}
    .solution-code {{
        font-family: monospace;
        color: #14532D;
        white-space: pre-wrap;
    }}

    .talk-box {{
        background: #FFFBEB;
        border-radius: 6px;
        padding: 6px 10px;
        margin-top: 6px;
        font-size: 8pt;
        color: #78350F;
    }}

    /* 표 스타일 */
    .report-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 8.5pt;
        margin-top: 8px;
    }}
    .report-table th {{
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        padding: 6px 8px;
        color: #334155;
        text-align: left;
    }}
    .report-table td {{
        border: 1px solid #CBD5E1;
        padding: 6px 8px;
        color: #1E293B;
    }}

    /* 공문서 하단 면책 및 서명 */
    .doc-footer {{
        border-top: 2px solid #0F172A;
        margin-top: 30px;
        padding-top: 14px;
        font-size: 8pt;
        color: #64748B;
        line-height: 1.5;
    }}
    .sign-box {{
        margin-top: 18px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }}
    .sign-org {{
        font-size: 10.5pt;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
    }}
    .stamp-badge {{
        display: inline-block;
        border: 2px solid #DC2626;
        color: #DC2626;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 9pt;
        transform: rotate(-3deg);
    }}

    /* 인쇄 최적화 (A4 규격 강제) */
    @media print {{
        body {{
            background: white !important;
            padding: 0 !important;
            color: #000 !important;
            font-size: 9pt !important;
        }}
        .no-print {{
            display: none !important;
        }}
        .a4-container {{
            max-width: 100% !important;
            box-shadow: none !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        .avoid-break {{
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }}
        @page {{
            size: A4 portrait;
            margin: 12mm 15mm 12mm 15mm;
        }}
    }}
</style>
</head>
<body>

<div class="no-print print-toolbar">
    <button onclick="window.print()" class="btn-print">🖨️ 의견서 바로 인쇄 / PDF 저장</button>
    <span class="print-tip">💡 인쇄 대화상자에서 [대상: PDF로 저장]을 선택하시면 고화질 A4 PDF 파일이 생성됩니다.</span>
</div>

<div class="a4-container">
    <!-- 1. 공문서 헤더 -->
    <div class="doc-header">
        <div class="doc-title-box">
            <h1>상가건물 임대차 계약 사전 법률 진단 의견서</h1>
            <p>소상공인 권익 보호 및 분쟁 예방을 위한 불리한 특약 정밀 검토서</p>
        </div>
        <div class="doc-meta-right">
            문서번호: <b>{doc_id}</b><br>
            발행일시: {now_str}<br>
            검토단계: <b>{html.escape(version_label)}</b>
        </div>
    </div>

    <!-- 2. 의뢰 정보 메트릭스 -->
    <table class="meta-table">
        <tr>
            <th>의뢰 매장명</th>
            <td style="font-weight: 700;">{html.escape(tenant_name)}</td>
            <th>검토 대상 파일</th>
            <td><code>{html.escape(analysis.document_name)}</code> ({analysis.total_clauses}개 조항)</td>
        </tr>
        <tr>
            <th>진단 기관</th>
            <td>SafeLease AI 안심진단센터</td>
            <th>대조 기준</th>
            <td>법무부 표준계약서 • 상가법 제15조 • 대법원 판례 DB</td>
        </tr>
    </table>

    <!-- 3. 종합 안심 지수 배너 -->
    <div class="score-banner">
        <div>
            <span class="score-desc">종합 안심 계약 지수: </span>
            <span class="score-text">{score}점 / 100점</span>
        </div>
        <div style="font-weight: 700;">
            진단 결과: {grade_text} (조율 필요 {red_count}건 • 주의 {yellow_count}건)
        </div>
    </div>

    <!-- 4대 공인 출처 대조 확인 바 -->
    <div class="auth-bar">
        <div class="auth-item">
            <b>📜 법무부·국토부</b>
            상가 표준계약서 대조
        </div>
        <div class="auth-item">
            <b>⚖️ 실정법 강행규정</b>
            상가임대차법 제15조 준수
        </div>
        <div class="auth-item">
            <b>👨‍⚖️ 대법원 판례</b>
            9대 확정 판례 1:1 매칭
        </div>
        <div class="auth-item">
            <b>🤝 분쟁조정기구</b>
            공공 실무 합의례 반영
        </div>
    </div>

    <!-- 4. 세부 이슈 검토 내용 -->
    <h2 class="section-title">🚨 1. 주의가 필요한 불리한 특약 정밀 분석</h2>
    {issues_html}

    <!-- 5. 누락 특약 체크리스트 -->
    {missing_html}

    <!-- 6. 공문서 푸터 및 서명 -->
    <div class="doc-footer avoid-break">
        <b>⚖️ [변호사법 제109조 준수 고지]</b><br>
        본 진단 의견서는 대한민국 정부 공인 표준계약서, 상가건물 임대차보호법 편면적 강행규정(제15조) 및 대법원 확정 판례 DB를 바탕으로 기계적 대조 알고리즘에 의해 자동 생성된 사전 권리 분석 참고자료입니다. 개별 사안에 대한 소송 대리나 확정적 법률 자문이 아니므로, 중대한 계약 체결 전 공인중개사, 가맹거래사, 전문 변호사의 조력을 권장합니다.
        
        <div class="sign-box">
            <div class="sign-org">SafeLease AI 소상공인 법률 안심 검증 엔진</div>
            <div class="stamp-badge">[공인 대조 검증완료]</div>
        </div>
    </div>
</div>

</body>
</html>
"""
    return full_html
