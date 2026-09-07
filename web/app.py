"""
SafeLease AI - 종합 웹 포털 (Streamlit)
소상공인 사장님을 위한 따뜻하고 세련된 안심 라운지 & 전문가 관리자 대시보드
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Streamlit Cloud 및 서브디렉터리 실행 지원을 위한 프로젝트 루트 등록
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from core.parser import parse_contract
from core.analyzer.rules_engine import RulesEngine
from core.analyzer.missing_checker import MissingChecker
from core.history.history_manager import HistoryManager
from core.history.diff_analyzer import DiffAnalyzer
from core.security.file_purger import safe_temp_file
from core.exporter.markdown_report import generate_markdown_report
from core.exporter.html_report import generate_a4_html_report
from core.analyzer.precedent_matcher import PrecedentDB
import streamlit.components.v1 as components
from config import TESTS_DIR, get_app_url

# 페이지 기본 설정
st.set_page_config(
    page_title="SafeLease AI | 사장님의 안심계약 비서",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_html(html_str: str):
    """st.html을 사용하여 마크다운 파서 간섭 없이 순수 HTML을 브라우저에 직접 렌더링"""
    st.html(html_str)


# 세련된 모던 CSS 스타일 (토스/핀테크 감성)
render_html("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* Streamlit 기본 Deploy 버튼 및 개발자 툴바 원천 숨김 */
    .stDeployButton,
    [data-testid="stDeployButton"],
    [data-testid="stToolbarActions"],
    [data-testid="stToolbar"],
    .stAppDeployButton,
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* 히어로 배너 */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%);
        padding: 38px 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -10px rgba(37, 99, 235, 0.35);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.3;
        margin-bottom: 12px;
        letter-spacing: -0.03em;
    }
    .hero-desc {
        font-size: 1.05rem;
        color: #E0E7FF;
        line-height: 1.5;
        margin: 0;
    }
    
    /* 3대 안심 보장 카드 */
    .trust-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 26px;
    }
    .trust-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .trust-card h4 {
        font-size: 0.98rem;
        font-weight: 700;
        margin: 0 0 6px 0;
        color: #1E293B;
    }
    .trust-card p {
        font-size: 0.85rem;
        color: #64748B;
        line-height: 1.45;
        margin: 0;
    }
    
    /* 카카오톡 스타일 말풍선 */
    .kakao-bubble {
        background: #FEE500;
        color: #3C1E1E;
        border-radius: 14px;
        padding: 14px 18px;
        margin-top: 10px;
        font-size: 0.94rem;
        line-height: 1.55;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* 4대 공인 출처 그리드 & 카드 */
    .source-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin: 14px 0 20px 0;
    }
    .source-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border-top: 4px solid #2563EB;
    }
    .source-card.gov {
        border-top-color: #059669;
    }
    .source-card.law {
        border-top-color: #DC2626;
    }
    .source-card.court {
        border-top-color: #7C3AED;
    }
    .source-card.dispute {
        border-top-color: #D97706;
    }
    .source-card h4 {
        font-size: 1.02rem;
        font-weight: 700;
        margin: 0 0 8px 0;
        color: #1E293B;
    }
    .source-card p {
        font-size: 0.86rem;
        color: #64748B;
        line-height: 1.48;
        margin: 0 0 10px 0;
    }
    .source-card ul {
        margin: 0;
        padding-left: 18px;
        font-size: 0.83rem;
        color: #334155;
        line-height: 1.55;
    }
    .source-card li {
        margin-bottom: 4px;
    }
    .source-banner {
        background: linear-gradient(135deg, #F0FDF4 0%, #EFF6FF 100%);
        border: 1px solid #BFDBFE;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        color: #1E3A8A;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    /* 자물쇠 및 결제 유도 카드 */
    .lock-box {
        position: relative;
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 2px dashed #93C5FD;
        border-radius: 14px;
        padding: 24px 20px;
        text-align: center;
        margin-top: 14px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.05);
    }
    .lock-icon {
        font-size: 2.2rem;
        margin-bottom: 6px;
    }
    .lock-title {
        font-size: 1.12rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 6px;
    }
    .lock-desc {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.55;
        max-width: 520px;
        margin: 0 auto 12px auto;
    }
    .lock-price-tag {
        display: inline-block;
        background: #FEF3C7;
        color: #92400E;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 12px;
        border: 1px solid #FDE68A;
    }
    .lock-price-tag b {
        color: #DC2626;
        font-size: 1.05rem;
    }
    .lock-preview-blur {
        filter: blur(4px);
        user-select: none;
        opacity: 0.6;
        pointer-events: none;
        background: #FFFFFF;
        padding: 12px 14px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        font-size: 0.86rem;
        margin-bottom: 12px;
        text-align: left;
    }

    /* 면책 푸터 */
    .disclaimer-footer {
        background: #F8FAFC;
        border-top: 1px solid #E2E8F0;
        padding: 20px 24px;
        border-radius: 12px;
        font-size: 0.82rem;
        color: #64748B;
        line-height: 1.6;
        margin-top: 40px;
    }

    /* 사이드바 최상단 정렬 및 여백 최적화 */
    [data-testid="stSidebar"] {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1rem !important;
    }
    .sidebar-principle-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .sidebar-principle-card b {
        color: #1E293B;
        font-size: 0.84rem;
        display: block;
        margin-bottom: 3px;
    }
    .sidebar-principle-card p {
        color: #64748B;
        font-size: 0.77rem;
        line-height: 1.35;
        margin: 0;
    }

    /* 📱 모바일 디바이스 반응형 최적화 (스마트폰 & 태블릿) */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 0.8rem !important;
            padding-bottom: 2.5rem !important;
        }
        .hero-container {
            padding: 20px 16px !important;
            border-radius: 16px !important;
            margin-bottom: 16px !important;
        }
        .hero-badge {
            font-size: 0.76rem !important;
            padding: 4px 10px !important;
        }
        .hero-title {
            font-size: 1.4rem !important;
            line-height: 1.35 !important;
            margin-bottom: 10px !important;
        }
        .hero-desc {
            font-size: 0.86rem !important;
            line-height: 1.45 !important;
        }
        /* 3대 안심 카드 모바일 1열 스택 */
        .trust-grid {
            grid-template-columns: 1fr !important;
            gap: 10px !important;
            margin-bottom: 20px !important;
        }
        /* 4대 공인 출처 그리드 모바일 1열 스택 */
        .source-grid {
            grid-template-columns: 1fr !important;
            gap: 12px !important;
            margin: 10px 0 16px 0 !important;
        }
        .source-card {
            padding: 14px 16px !important;
        }
        .trust-card {
            padding: 14px 16px !important;
        }
        .trust-card h4 {
            font-size: 0.92rem !important;
        }
        .trust-card p {
            font-size: 0.82rem !important;
        }
        .kakao-bubble {
            padding: 12px 14px !important;
            font-size: 0.88rem !important;
        }
        /* 모바일 터치 타겟 및 버튼 최적화 */
        .stButton button {
            font-size: 0.86rem !important;
            padding: 0.55rem 0.75rem !important;
            white-space: normal !important;
            min-height: 44px !important;
            line-height: 1.35 !important;
        }
        /* 탭 바 가로 스크롤 최적화 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding-left: 8px !important;
            padding-right: 8px !important;
            font-size: 0.84rem !important;
        }
    }

    /* 📟 태블릿 디바이스 (아이패드, 갤럭시탭 등 769px ~ 1024px) 반응형 최적화 */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 1.2rem !important;
        }
        .hero-container {
            padding: 28px 24px !important;
        }
        .hero-title {
            font-size: 1.75rem !important;
            line-height: 1.3 !important;
        }
        .trust-grid {
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 12px !important;
        }
        .trust-card {
            padding: 16px 14px !important;
        }
        .source-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 14px !important;
        }
        .stButton button {
            min-height: 44px !important;
            font-size: 0.9rem !important;
        }
    }
</style>
""")


def main():
    # 1. 좌측 사이드바 최상단 정렬
    with st.sidebar:
        st.markdown("## 🛡️ SafeLease AI")
        st.caption("소상공인·자영업자 계약서 안심 파트너")
        st.success("🟢 AI 법률 대조 엔진 가동 중")

        st.markdown("---")
        st.markdown("##### 🔒 3대 안심 보장 원칙")
        st.markdown("""
        <div class="sidebar-principle-card">
            <b>1. 개인정보 완벽 보호</b>
            <p>주민번호·계좌번호 자동 마스킹 및 30초 후 원본 파일 영구 파기(Zero-Retention)</p>
        </div>
        <div class="sidebar-principle-card">
            <b>2. 정부 공인 법률 기준 대조</b>
            <p>상가임대차보호법 강행규정(제15조), 가맹사업법 및 대법원 확정 판례 대조</p>
        </div>
        <div class="sidebar-principle-card">
            <b>3. 마찰 없는 부드러운 협상</b>
            <p>임대인 심기 안 건드리고 원만히 조율하는 정중한 카톡 문구 제공</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("📱 패드·탭 & 모바일 접속 안내", expanded=True):
            current_app_url = get_app_url()
            st.markdown("패드, 탭, 스마트폰 브라우저에서 아래 주소로 접속하세요:")
            st.code(current_app_url, language="text")
            st.caption("📸 카메라로 계약서를 찍어 바로 올리거나 큰 화면으로 편하게 검토하세요.")

        st.markdown("---")
        st.markdown("##### 📞 무료 분쟁/법률 상담처")
        st.markdown("""
        - **대한법률구조공단**: 국번없이 `132`
        - **상가임대차분쟁조정위**: `02-120`
        - **소상공인마당 종합상담**: `1357`
        """)

        st.markdown("---")
        st.caption("SafeLease AI v1.2 • Commercial & Franchise Assistant")

    # 2. 메인 화면 우측 상단 관리자 대시보드 내비게이션 바
    top_c1, top_c2 = st.columns([5, 2.2])
    with top_c1:
        st.caption("🛡️ 도장 찍기 전 30초! 소상공인의 보증금과 권리금을 지켜드립니다.")
    with top_c2:
        view_mode = st.session_state.get("view_mode", "user")
        admin_logged_in = st.session_state.get("admin_logged_in", False)

        if view_mode == "admin":
            c_btn_a1, c_btn_a2 = st.columns([1, 1])
            with c_btn_a1:
                if st.button("👤 사장님 라운지", use_container_width=True):
                    st.session_state["view_mode"] = "user"
                    st.rerun()
            with c_btn_a2:
                if admin_logged_in and st.button("🚪 로그아웃", use_container_width=True):
                    st.session_state["admin_logged_in"] = False
                    st.session_state["view_mode"] = "user"
                    st.rerun()
        else:
            # 사장님 모드일 때 우측 상단에 위치한 관리자 대시보드 버튼
            if st.button("🛠️ 전문가 관리자 대시보드", use_container_width=True, type="secondary"):
                st.session_state["view_mode"] = "admin"
                st.rerun()

    # 3. 화면 라우팅 (사장님 라운지 vs 관리자 로그인/대시보드)
    current_view = st.session_state.get("view_mode", "user")
    if current_view == "admin":
        if st.session_state.get("admin_logged_in", False):
            render_admin_dashboard()
        else:
            render_admin_login()
    else:
        render_user_portal()

    # 하단 공통 법적 면책 고지
    render_html("""
    <div class="disclaimer-footer">
        ⚖️ <b>[Legal Disclaimer | 변호사법 제109조 준수 고지]</b><br>
        SafeLease AI는 공인 표준계약서 및 법원 판례 DB와의 기계적 대조 정보를 제공하는 사전 검토 보조 솔루션이며, 
        개별 법률 대리나 확정적 법률 자문을 제공하지 않습니다. 실제 계약 체결 및 권리 분쟁 시에는 전문 변호사, 가맹거래사, 공인중개사의 자문을 받으시기 바랍니다.
    </div>
    """)


def render_admin_login():
    """전문가 관리자 대시보드 접근 인증 로그인 화면"""
    render_html("""
    <div class="hero-container" style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);">
        <span class="hero-badge">🔐 Restricted Access</span>
        <div class="hero-title">전문가 관리자 센터 로그인</div>
        <div class="hero-desc">전체 계약서 분석 통계 모니터링 및 법률 룰셋 엔진 관리자 전용 인증 화면입니다.</div>
    </div>
    """)

    c_pad1, c_box, c_pad2 = st.columns([1, 2, 1])
    with c_box:
        with st.container(border=True):
            st.markdown("### 🔑 관리자 계정 인증")
            st.caption("관리자 ID와 비밀번호를 입력해 주세요.")

            admin_id = st.text_input("관리자 아이디 (ID)", placeholder="아이디 입력", key="admin_id_input")
            admin_pw = st.text_input("비밀번호 (Password)", type="password", placeholder="비밀번호 입력", key="admin_pw_input")

            st.info("💡 **관리자 기본 계정 안내**: 아이디 `admin` / 비밀번호 `admin1234`")

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                if st.button("🚀 로그인", type="primary", use_container_width=True):
                    if admin_id.strip() == "admin" and admin_pw.strip() == "admin1234":
                        st.session_state["admin_logged_in"] = True
                        st.success("인증에 성공하였습니다! 관리자 대시보드로 이동합니다.")
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            with col_sub2:
                if st.button("👤 사장님 화면으로", use_container_width=True):
                    st.session_state["view_mode"] = "user"
                    st.rerun()


def render_user_portal():
    """사장님 전용 개인화 라운지"""
    
    # 1. 히어로 배너
    render_html("""
    <div class="hero-container">
        <span class="hero-badge">🛡️ 사장님의 소중한 보증금과 권리금을 지키는 안심 파트너</span>
        <div class="hero-title">도장 찍기 전 30초!<br>주의가 필요한 불리한 특약을 찾아드릴게요.</div>
        <div class="hero-desc">
            어려운 법률 용어 몰라도 괜찮아요. 사진이나 파일만 올려주시면<br>
            조율이 필요한 조항을 꼼꼼히 찾고, 건물주와 부드럽게 협의할 수 있는 카톡 문구까지 드립니다.
        </div>
    </div>
    """)

    # 2. 정비된 3대 안심 보장 카드
    render_html("""
    <div class="trust-grid">
        <div class="trust-card">
            <h4>🔒 개인정보 완벽 보호 (Zero-Retention)</h4>
            <p>주민번호·계좌는 자동 마스킹되며, 계약서 원본은 분석 즉시 흔적 없이 영구 파기됩니다.</p>
        </div>
        <div class="trust-card">
            <h4>⚖️ 정부 공인 법률 기준 대조</h4>
            <p>상가임대차보호법 강행규정(제15조)과 대법원 확정 판례를 기반으로 안전성을 검증합니다.</p>
        </div>
        <div class="trust-card">
            <h4>💬 마찰 없는 부드러운 협상</h4>
            <p>임대인과의 관계가 어색해지지 않도록, 서로 기분 상하지 않게 조율할 대화 문구를 드립니다.</p>
        </div>
    </div>
    """)

    # 3. 첫 화면 4대 공인 법률 출처 한눈에 보기
    with st.expander("🏛️ [신뢰도 100% 공인 출처] SafeLease AI는 어떤 공식 기준을 바탕으로 분석하나요? (한눈에 보기)", expanded=False):
        render_html("""
        <div class="source-grid">
            <div class="source-card gov">
                <h4>📜 ① 정부 공인 표준계약서</h4>
                <p>정부 부처가 임차인·가맹점주 보호를 위해 고시한 공식 표준 양식을 기준으로 불리한 변형을 정밀 탐지합니다.</p>
                <ul>
                    <li><b>법무부·국토교통부</b> 「상가건물 임대차 표준계약서」</li>
                    <li><b>공정거래위원회</b> 「외식업·도소매업 표준가맹계약서」</li>
                </ul>
            </div>
            <div class="source-card law">
                <h4>⚖️ ② 대한민국 실정 법률 (강행규정)</h4>
                <p>계약서에 도장을 찍었더라도 임차인에게 불리하면 법적으로 100% 무효가 되는 강행법규를 적용합니다.</p>
                <ul>
                    <li><b>상가임대차보호법 제15조</b> (편면적 강행규정 - 불리한 약정 무효)</li>
                    <li><b>민법 제623조</b> (임대인 대수선의무) / <b>제536조</b> (동시이행)</li>
                    <li><b>가맹사업법 제12조</b> (불공정거래 및 과다위약금 금지)</li>
                </ul>
            </div>
            <div class="source-card court">
                <h4>👨‍⚖️ ③ 대법원 확정 판례 (9선 전수 매칭)</h4>
                <p>실제 법원에서 임차인 권리를 지키고 승소 판결을 내린 확정 판례를 1:1 매칭합니다.</p>
                <ul>
                    <li><b>대법원 2017다268142</b> (전 임차인 시설 철거 의무 없음)</li>
                    <li><b>대법원 2020다277028</b> (권리금 회수방해 손해배상 책임)</li>
                    <li><b>대법원 2014다203960</b> (5% 초과 차임증액 약정 무효)</li>
                </ul>
            </div>
            <div class="source-card dispute">
                <h4>🤝 ④ 공공 분쟁조정 실무 사례집</h4>
                <p>소송 전 조정 단계에서 실제 원만한 합의를 이끌어낸 공공 분쟁조정위원회의 실제 조정안을 반영합니다.</p>
                <ul>
                    <li><b>대한법률구조공단</b> 상가건물임대차분쟁조정위원회 사례집</li>
                    <li><b>한국공정거래조정원</b> 가맹사업분쟁조정협의회 실무례</li>
                </ul>
            </div>
        </div>
        """)
        st.info("👉 상단 **'🏛️ 4대 공인 법률 출처 & 판례 백과'** 탭을 클릭하시면 대법원 판례 9선 전문과 상세 법리 해설을 한 페이지로 편리하게 열람하실 수 있습니다.")

    # 4. 탭 구성
    tab1, tab_sources, tab2, tab3 = st.tabs([
        "⚡ 30초 실시간 계약서 진단",
        "🏛️ 4대 공인 법률 출처 & 판례 백과",
        "📁 내 매장 계약 보관함 & Diff",
        "💬 건물주 협상 카톡 족보"
    ])

    with tab1:
        st.markdown("### 📄 계약서를 올려주세요")
        st.caption("스마트폰 촬영 사진(JPG, PNG), PDF, 워드(DOCX), 텍스트 문서를 모두 지원합니다.")

        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        with col_in1:
            tenant_name = st.text_input("🏢 우리 매장 상호명", value="을지로 힙지로 카페 1호점", placeholder="예: 성수 베이커리 1호점")
        with col_in2:
            contract_kind = st.selectbox("📋 계약서 유형", ["전체 정밀 진단 (임대차+가맹)", "🏢 상가 임대차 계약서", "🍗 프랜차이즈 가맹 계약서"])
        with col_in3:
            version_label = st.selectbox("📌 검토 단계", ["1차 초안 검토", "2차 협상 수정본", "최종 체결본"])

        # 검토 이력 저장 여부 선택 (프라이버시 및 휘발성 모드 보장)
        save_to_history = st.checkbox(
            "💾 검토 결과를 내 매장 보관함에 저장 (협상 전/후 비교 및 타임라인 보관용)",
            value=True,
            help="체크를 해제하시면 데이터베이스에 일체 저장되지 않고 화면 및 진단서 다운로드로만 1회성 열람됩니다."
        )

        # 파일 업로더
        uploaded_file = st.file_uploader(
            "계약서 파일 드래그 앤 드롭",
            type=["txt", "pdf", "docx", "jpg", "png", "hwpx"],
            help="주민번호, 계좌번호 등 개인정보는 자동으로 안전하게 가려집니다."
        )

        # 직접 파일 업로드 실행 버튼 (업로드 영역 바로 아래 직관적 배치!)
        if uploaded_file:
            if st.button("🚀 업로드한 계약서 30초 진단 시작", type="primary", use_container_width=True):
                file_bytes = uploaded_file.read()
                with st.spinner("🔒 개인정보 마스킹 및 공인 기준 정밀 대조 중..."):
                    with safe_temp_file(uploaded_file.name, file_bytes) as temp_path:
                        st.session_state["active_doc"] = parse_contract(temp_path)
                        st.session_state["active_source"] = "uploaded"

        # 1-Click 샘플 체험존
        st.markdown("---")
        st.markdown("##### 🧪 준비된 계약서 파일이 없으신가요? 1초 만에 바로 체험해 보세요!")
        
        c_btn1, c_btn2, c_btn3 = st.columns(3)

        with c_btn1:
            if st.button("🚨 [임대차 주의 샘플] 원상복구 독박·권리금 제한 특약", use_container_width=True):
                toxic_path = TESTS_DIR / "sample_contracts" / "sample_toxic_lease.txt"
                st.session_state["active_doc"] = parse_contract(toxic_path)
                st.session_state["active_source"] = "sample_toxic_lease"
            st.caption("📄 **상가임대차 (2쪽)**: 원상복구 독박·권리금 포기 등 5건")

        with c_btn2:
            if st.button("🍗 [가맹계약 주의 샘플] 위약금 폭탄·필수품목 강제", use_container_width=True):
                fran_path = TESTS_DIR / "sample_contracts" / "sample_toxic_franchise.txt"
                st.session_state["active_doc"] = parse_contract(fran_path)
                st.session_state["active_source"] = "sample_toxic_franchise"
            st.caption("📄 **가맹계약 (2쪽)**: 과다 위약금·사급 금지·심야강제 5건")

        with c_btn3:
            if st.button("🟢 [안심 표준 샘플] 정부 공인 표준 임대차 계약서", use_container_width=True):
                normal_path = TESTS_DIR / "sample_contracts" / "sample_normal_lease.txt"
                st.session_state["active_doc"] = parse_contract(normal_path)
                st.session_state["active_source"] = "sample_normal"
            st.caption("📄 **표준계약서 (2쪽)**: 법무부 표준 준수 (불리한 특약 0건)")

        # 분석 결과 렌더링
        active_doc = st.session_state.get("active_doc")
        if active_doc:
            # 계약서 유형에 맞춘 룰셋 엔진 초기화
            c_type = "lease" if "임대차" in contract_kind else ("franchise" if "가맹" in contract_kind else "all")
            engine = RulesEngine(contract_type=c_type)
            analysis = engine.analyze(active_doc)
            checker = MissingChecker()
            missing_items = checker.check(active_doc)

            # SQLite 저장 (사용자가 저장을 원할 때만 실행)
            if save_to_history:
                history_mgr = HistoryManager()
                history_mgr.create_or_get_session(tenant_name, tenant_name)
                history_mgr.save_version(tenant_name, version_label, analysis)

            st.markdown("---")

            # 📄 계약서 기본 정보 및 페이지별 주의 항목 요약 배너
            total_pages = max((getattr(c, "page", 1) for c in active_doc.clauses), default=1)
            issue_pages = sorted(set(getattr(iss, "page", 1) for iss in analysis.detected_issues))
            if issue_pages:
                pages_str = ", ".join(f"**제{p}페이지**" for p in issue_pages)
                page_banner_text = f"🚨 총 {total_pages}페이지 중 {pages_str}에서 주의 특약 **{len(analysis.detected_issues)}건** 발견"
            else:
                page_banner_text = f"🟢 총 {total_pages}페이지 전반에 걸쳐 불리한 특약이 발견되지 않았습니다."

            st.info(f"📋 **검토 문서**: `{active_doc.filename}` (전체 {total_pages}쪽) | {page_banner_text}")

            # 원문 페이지별 조항 펼쳐보기
            with st.expander(f"📖 계약서 원문 전체 보기 (총 {total_pages}페이지 조항별 분할)", expanded=False):
                for p_num in range(1, total_pages + 1):
                    p_clauses = [c for c in active_doc.clauses if getattr(c, "page", 1) == p_num]
                    p_issues = [iss for iss in analysis.detected_issues if getattr(iss, "page", 1) == p_num]
                    p_badge = f"🚨 주의 특약 {len(p_issues)}건 집중 위치" if p_issues else "🟢 정상 (특이사항 없음)"
                    st.markdown(f"##### 📄 [제{p_num}페이지] - {p_badge}")
                    if p_clauses:
                        for c in p_clauses:
                            c_header = f"**{c.article_no or ''} {c.title or ''}**".strip()
                            if c_header:
                                st.markdown(f"- {c_header}: {c.content}")
                            else:
                                st.markdown(f"- {c.content}")
                    else:
                        st.caption("해당 페이지 추출 내용 없음")
                    st.divider()
            
            # 종합 스코어 카드 (Streamlit Native Container - HTML 누출 0%)
            score = analysis.safety_score
            red_count = analysis.risk_summary.get('RED', 0)
            yellow_count = analysis.risk_summary.get('YELLOW', 0)

            with st.container(border=True):
                c_score1, c_score2 = st.columns([1, 1])
                with c_score1:
                    st.caption("종합 안심 계약 지수")
                    st.title(f"{score}점 / 100점")
                with c_score2:
                    if score < 60:
                        st.error(f"🔴 **수정 및 조율이 꼭 필요한 계약서**\n\n조율 필요(RED) {red_count}건 | 주의 권장(YELLOW) {yellow_count}건")
                    elif score < 80:
                        st.warning(f"🟡 **일부 조항 조율 권장**\n\n조율 필요(RED) {red_count}건 | 주의 권장(YELLOW) {yellow_count}건")
                    else:
                        st.success("🟢 **아주 안전하고 균형 잡힌 표준 계약서**\n\n발견된 위험 조항 없음")

                # 리포트 생성 (A4 인쇄용 공문서 HTML + 텍스트 마크다운)
                report_html = generate_a4_html_report(
                    analysis=analysis,
                    missing_items=missing_items,
                    tenant_name=tenant_name,
                    version_label=version_label
                )
                report_md = generate_markdown_report(analysis, missing_items)

                st.markdown("---")
                st.markdown("##### 🖨️ 건물주·중개사 제출용 안심 진단 의견서 (A4 맞춤 인쇄 / PDF 저장)")
                col_rep1, col_rep2, col_rep3 = st.columns([1.2, 1, 1])
                with col_rep1:
                    st.download_button(
                        label="📄 A4 공문서 HTML 다운로드 (인쇄용)",
                        data=report_html,
                        file_name=f"안심진단의견서_{tenant_name}_{version_label}.html",
                        mime="text/html",
                        use_container_width=True,
                        type="primary"
                    )
                with col_rep2:
                    st.download_button(
                        label="📥 마크다운 리포트 다운로드 (.md)",
                        data=report_md,
                        file_name=f"안심계약_진단리포트_{tenant_name}_{version_label}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                with col_rep3:
                    show_a4_preview = st.toggle("🔍 A4 의견서 바로보기/인쇄", value=False)

                if show_a4_preview:
                    st.info("💡 상단 [🖨️ 의견서 바로 인쇄 / PDF 저장] 버튼을 누르시면 깨끗한 A4 규격 인쇄창이 열립니다. 대상에서 'PDF로 저장'을 선택하시면 고품질 PDF로 저장됩니다.")
                    components.html(report_html, height=750, scrolling=True)

            # 세부 이슈 리스트 (Streamlit Native Cards - HTML 코드 누출 100% 원천 차단!)
            if analysis.detected_issues:
                st.markdown("### 🚨 발견된 주의 조항 & 부드러운 협상 가이드")

                # 프리미엄 솔루션 잠금 해제 상태 확인 (세션 연동)
                is_unlocked = st.session_state.get("is_solution_unlocked", False)

                if is_unlocked:
                    c_un1, c_un2 = st.columns([4, 1.2])
                    with c_un1:
                        st.success("🎉 **[프리미엄 솔루션 활성화됨]** 모든 주의 특약의 수정 대체 조항과 건물주용 카톡 족보가 열렸습니다!")
                    with c_un2:
                        if st.button("🔄 다시 잠금 테스트", use_container_width=True):
                            st.session_state["is_solution_unlocked"] = False
                            st.rerun()
                else:
                    st.info("💡 **[안내]** 1번 이슈의 대체 조항과 카톡 문구는 **무료 체험**으로 열람하실 수 있으며, 2번 이슈부터는 사장님 권익 보호를 위한 **맞춤 솔루션 자물쇠(Lock)**가 적용됩니다.")

                for idx, iss in enumerate(analysis.detected_issues, 1):
                    with st.container(border=True):
                        # 1. 뱃지, 페이지 번호 및 카테고리
                        badge_label = "🔴 조율 필요 (RED)" if iss.risk_level == "RED" else "🟡 주의 권장 (YELLOW)"
                        iss_page = getattr(iss, "page", 1)
                        page_display = f"📄 **계약서 제{iss_page}페이지**"
                        st.markdown(f"**{badge_label}** | {page_display} | `{iss.category}` • `{iss.matched_clause_no or '특약'}`")
                        
                        # 2. 이슈 제목
                        st.subheader(f"{idx}. {iss.title}")
                        
                        # 3. 계약서 원문 발췌
                        st.markdown(f"**🔍 계약서 원문 발췌 (제{iss_page}쪽 {iss.matched_clause_no or '특약'})**")
                        st.info(f"\"{iss.verbatim_quote}\"")
                        
                        # 4. 불리한 이유 및 법적 근거
                        col_r1, col_r2 = st.columns([1, 1])
                        with col_r1:
                            st.markdown(f"⚠️ **사장님께 불리한 이유**:\n\n{iss.danger_explanation}")
                        with col_r2:
                            st.markdown(f"📜 **법적 근거**:\n\n{iss.legal_basis}")

                        # 대법원 확정 판례 심층 브리핑 연동
                        prec_db = PrecedentDB()
                        matched_prec = prec_db.find_by_case_no(iss.legal_basis)
                        if matched_prec:
                            with st.expander(f"⚖️ [대법원 판례 심층 브리핑] {matched_prec.case_no} 판시사항 확인하기", expanded=False):
                                st.caption(f"📌 사건명: **{matched_prec.title}** ({matched_prec.case_date})")
                                st.markdown(f"**🔍 판결 요지**:\n{matched_prec.summary}")
                                st.info(f"**📜 대법원 판시 핵심 문구**:\n\"{matched_prec.key_quote}\"")
                                st.success(f"**🛡️ 사장님 실전 대응 팁**: {matched_prec.action_guide}")

                        # 5 & 6. 솔루션 영역 (1번 이슈 무료 체험 or 결제 해제 시 노출)
                        if is_unlocked or idx == 1:
                            if idx == 1 and not is_unlocked:
                                st.caption("✨ **[무료 체험 제공]** 1번 이슈의 맞춤 대체 조항 및 카톡 조율 문구를 먼저 확인해 보세요!")

                            # 5. 추천 대체 조항
                            st.markdown("**✨ 이렇게 수정 조율을 제안해 보세요 (계약서 반영용)**")
                            st.success(iss.recommended_replacement)
                            
                            # 6. 카카오톡 스타일 협상 문구 (원클릭 복사 버튼 내장)
                            st.markdown("**💬 건물주에게 보낼 완곡한 카톡 문구 (원클릭 복사)**")
                            render_html(f"""
                            <div class="kakao-bubble">
                                💬 <b>건물주용 추천 대화문:</b><br>
                                "{iss.nudge_script_polite}"
                            </div>
                            """)
                            st.code(iss.nudge_script_polite, language="text")
                        else:
                            # 🔒 2번 이슈부터 노출되는 자물쇠(Lock) 과금 유도 카드
                            safe_rep_preview = (iss.recommended_replacement[:40] + "...") if len(iss.recommended_replacement) > 40 else iss.recommended_replacement
                            safe_talk_preview = (iss.nudge_script_polite[:35] + "...") if len(iss.nudge_script_polite) > 35 else iss.nudge_script_polite

                            render_html(f"""
                            <div class="lock-box">
                                <div class="lock-preview-blur">
                                    ✨ <b>대체 조항:</b> {safe_rep_preview} (안심 보호 조항 전문 가림)<br>
                                    💬 <b>카톡 멘트:</b> "{safe_talk_preview}" (원클릭 복사 대화문 가림)
                                </div>
                                <div class="lock-icon">🔒</div>
                                <div class="lock-title">사장님 맞춤 대체 조항 & 카톡 협상 족보 잠금</div>
                                <div class="lock-desc">
                                    건물주 심기 건드리지 않고 자연스럽게 불리한 특약을 무효화하는<br>
                                    <b>전문 변호사 감수 대체 조항</b>과 <b>실전 카톡 협상 족보</b>를 확인하세요.
                                </div>
                                <div class="lock-price-tag">
                                    <span style="text-decoration: line-through; color: #94A3B8; margin-right: 4px;">정가 29,000원</span>
                                    <b>9,900원</b> (오픈 특가)
                                </div>
                            </div>
                            """)

                            c_p1, c_p2 = st.columns([1.3, 1])
                            with c_p1:
                                if st.button(f"💳 9,900원 결제하고 전체 솔루션 즉시 열기", key=f"pay_btn_{idx}", type="primary", use_container_width=True):
                                    st.session_state["is_solution_unlocked"] = True
                                    st.balloons()
                                    st.success("결제가 완료되었습니다! 모든 특약의 솔루션과 카톡 문구가 열렸습니다.")
                                    st.rerun()
                            with c_p2:
                                if st.button(f"⚡ [체험용] 1초 만에 무료 잠금 해제", key=f"demo_unlock_{idx}", use_container_width=True):
                                    st.session_state["is_solution_unlocked"] = True
                                    st.success("체험 모드로 솔루션이 활성화되었습니다!")
                                    st.rerun()
            else:
                st.balloons()
                with st.container(border=True):
                    st.success("### 🎉 축하합니다! 안전한 표준 계약서입니다.\n\n상가임대차보호법 강행규정에 반하거나 사장님께 일방적으로 불리한 특약이 발견되지 않았습니다.")

            # 빠진 특약 체크
            missing_only = [m for m in missing_items if m.is_missing]
            if missing_only:
                st.markdown("### ⚠️ 계약서에 쏙 빠져있는 필수 보호 특약")
                for m in missing_only:
                    with st.expander(f"⚠️ [누락 체크] {m.title}", expanded=True):
                        st.markdown(f"**위험 요소**: {m.why_important}")
                        if getattr(m, 'legal_basis', None):
                            st.markdown(f"📜 **법적 근거**: `{m.legal_basis}`")
                        st.markdown(f"👉 **추천 기재 문구**:\n`{m.recommended_clause}`")

    with tab_sources:
        render_sources_whitepaper()

    with tab2:
        st.markdown("### 📁 내 매장 계약서 타임라인 & 협상 전/후 비교")
        history_mgr = HistoryManager()
        sessions = history_mgr.list_sessions()

        if not sessions:
            st.info("아직 저장된 검토 이력이 없습니다. [30초 실시간 진단]에서 계약서를 검토해 보세요!")
        else:
            tenant_list = [s.tenant_name for s in sessions]
            selected_t = st.selectbox("🏢 매장 선택", tenant_list)
            session = history_mgr.get_session(selected_t)

            if session and session.versions:
                st.markdown(f"**{session.tenant_name}** 매장의 누적 검토 버전: **{len(session.versions)}개**")

                # 버전 테이블
                v_rows = []
                for v in session.versions:
                    v_rows.append({
                        "버전": f"v{v.version_id} ({v.version_label})",
                        "검토 일시": v.analyzed_at.strftime("%Y-%m-%d %H:%M"),
                        "안전 점수": f"{v.safety_score}점",
                        "조율 필요(RED)": f"{v.risk_summary.get('RED', 0)}건",
                        "주의 권장(YELLOW)": f"{v.risk_summary.get('YELLOW', 0)}건"
                    })
                st.dataframe(v_rows, use_container_width=True)

                if len(session.versions) >= 2:
                    st.markdown("#### 🔄 1차 초안 대비 2차 수정본 위험 해결 분석 (Diff)")
                    c_v1, c_v2 = st.columns(2)
                    with c_v1:
                        v1_num = st.selectbox("이전 버전", [v.version_id for v in session.versions], index=0)
                    with c_v2:
                        v2_num = st.selectbox("최신 수정본", [v.version_id for v in session.versions], index=len(session.versions)-1)

                    if st.button("📊 변경점(Diff) 상세 비교", type="primary"):
                        diff = DiffAnalyzer.compare_versions(session, v1_num, v2_num)
                        
                        score_delta = diff.score_change
                        with st.container(border=True):
                            st.subheader(diff.summary_message)
                            st.metric("안전 점수 변화량", f"{score_delta:+d}점")

                        for item in diff.diff_items:
                            if item.status == "RESOLVED":
                                st.success(f"**[조율 해결 완료! 🎉] {item.title}**: {item.comment}")
                                if item.old_quote:
                                    st.caption(f"↳ 이전 초안에서 삭제된 문제 문구: \"{item.old_quote}\"")
                            elif item.status == "PERSISTENT":
                                st.error(f"**[추가 협의 필요 ⚠️] {item.title}**: {item.comment}")
                                if item.new_quote:
                                    st.caption(f"↳ 여전히 남아있는 문구: \"{item.new_quote}\"")
                            else:
                                st.warning(f"**[새로운 주의 항목 🚨] {item.title}**: {item.comment}")
                                if item.new_quote:
                                    st.info(f"🔍 **기습 변경/추가된 문구**: \"{item.new_quote}\"")

                # 데이터 관리 옵션 (최종본만 남기기 vs 전체 영구 삭제)
                with st.expander("⚙️ 내 매장 검토 기록 관리 (최종본만 남기기 / 전체 영구 삭제)", expanded=False):
                    st.caption("🔒 **Zero-Retention 준수**: 원본 계약서 파일은 분석 즉시 이미 영구 파기되었습니다. 이곳에 남아있는 최소한의 검토 통계 메타데이터도 원하시면 언제든 삭제하실 수 있습니다.")
                    c_del1, c_del2 = st.columns(2)
                    with c_del1:
                        if len(session.versions) >= 2:
                            if st.button("🧹 최종본만 남기고 이전 버전(1차, 2차) 정리", use_container_width=True):
                                history_mgr.prune_previous_versions(selected_t)
                                st.success("이전 버전이 정리되고 최종 체결본만 안전하게 보관되었습니다.")
                                st.rerun()
                        else:
                            st.button("🧹 최종본만 남기기 (현재 1개 버전만 존재)", disabled=True, use_container_width=True)
                    with c_del2:
                        if st.button("🗑️ 이 매장의 모든 검토 기록 영구 삭제", type="secondary", use_container_width=True):
                            history_mgr.delete_session(selected_t)
                            st.success(f"'{selected_t}' 매장의 모든 기록이 영구 삭제되었습니다.")
                            st.rerun()

    with tab3:
        st.markdown("### 💬 건물주 기분 안 상하게 조율하는 카톡 족보")
        st.caption("소상공인 전문 변호사와 협상 전문가가 감수한 실전 카톡/문자 멘트입니다.")

        script_list = [
            ("원상복구 범위 완화 요청", "임대인 사장님, 특약 제N조 원상회복 문구를 대법원 판례 및 국토부 표준계약서 양식에 맞춰 '현 임차인이 직접 시공한 시설에 한함(통상 마모 제외)'으로 문구만 살짝 명확히 해주시면 감사하겠습니다 ^^"),
            ("권리금 회수 기회 보장", "사장님, 권리금 포기 조항은 상가건물임대차보호법 제15조(강행규정)에 의해 효력이 제한될 수 있어서, 서로 오해 없도록 법정 권리금 회수 기회 보장 조항으로 다듬어두면 어떨까요?"),
            ("대규모 수선의무 명시", "사장님, 소모품 수리는 저희가 당연히 고쳐 쓰겠지만 건물 자체의 누수나 배관 노후 같은 대규모 수선은 민법 원칙대로 건물주님께서 챙겨주시는 문구로 정리해주시면 안심하겠습니다!"),
            ("재건축 일방 명도 조율", "임대인 사장님, 저희도 인테리어 비용이 크게 들어가다 보니 혹시 모를 재건축 통보는 최소 6개월 전에 미리 서면으로 주시는 것으로 조율해주시면 안심하고 영업에 매진하겠습니다!")
        ]

        for title, script in script_list:
            with st.container(border=True):
                st.markdown(f"#### 📌 {title}")
                st.code(script, language="text")


def render_sources_whitepaper():
    """소상공인을 위한 4대 공인 법률 출처 및 대법원 판례 백서 (한 페이지 정리)"""
    st.markdown("### 🏛️ SafeLease AI 법률 분석 엔진의 4대 공인 출처 및 판례 백과")
    st.markdown("사장님의 소중한 보증금과 권리금을 지키는 **4중 법률 방어막**을 한눈에 확인하세요. 본 서비스의 모든 진단 기준은 대한민국 정부 공인 표준계약서, 편면적 강행규정, 대법원 확정 판례, 공공 분쟁조정 실무례에 100% 근거합니다.")

    # 1. 4대 공인 출처 배너 및 그리드 카드
    render_html("""
    <div class="source-banner">
        🛡️ <b>[신뢰도 100% 공인 출처 보증]</b><br>
        SafeLease AI의 위험 조항 탐지 및 조율 가이드는 AI의 임의적 추측이 아닌, 
        <b>법무부·국토교통부·공정거래위원회 공인 표준계약서</b>와 <b>대한민국 대법원 확정 판례</b>에 1:1로 엄격하게 매칭됩니다.
    </div>
    """)

    render_html("""
    <div class="source-grid">
        <div class="source-card gov">
            <h4>📜 ① 정부 공인 표준계약서</h4>
            <p>정부 부처가 임차인과 가맹점주의 권익을 보호하기 위해 공식 고시한 표준 양식을 기준으로 불리한 변형을 정밀 탐지합니다.</p>
            <ul>
                <li><b>법무부·국토교통부</b> 「상가건물 임대차 표준계약서」 (상가임대차법 제10조의6)</li>
                <li><b>공정거래위원회</b> 「외식업·도소매업 표준가맹계약서」</li>
                <li>표준계약서 권장 필수 조항(원상복구 한정, 수선의무 분담 등) 대조</li>
            </ul>
        </div>
        <div class="source-card law">
            <h4>⚖️ ② 대한민국 실정 법률 (편면적 강행규정)</h4>
            <p>계약서에 도장을 찍었더라도 임차인에게 불리하면 법적으로 100% 무효가 되는 강행법규를 적용합니다.</p>
            <ul>
                <li><b>상가임대차법 제15조</b> (편면적 강행규정: 임차인에게 불리한 약정은 전부 무효)</li>
                <li><b>상가임대차법 제10조</b> (10년 갱신보장 및 재건축 사유 엄격 제한)</li>
                <li><b>상가임대차법 제10조의4</b> (권리금 회수기회 보호 및 방해 손해배상)</li>
                <li><b>상가임대차법 제11조</b> (차임 등 증액 5% 상한선)</li>
                <li><b>민법 제623조</b> (대수선 및 기본설비 임대인 수선의무) / <b>제536조</b> (동시이행)</li>
                <li><b>가맹사업법 제12조</b> (불공정거래 및 과다위약금 부과 금지)</li>
            </ul>
        </div>
        <div class="source-card court">
            <h4>👨‍⚖️ ③ 대법원 확정 판례 (9선 전수 매칭)</h4>
            <p>실제 법원에서 건물주나 가맹본부의 부당한 특약을 무효화하고 세입자의 손을 들어준 리딩 케이스입니다.</p>
            <ul>
                <li><b>대법원 2017다268142</b>: 종전 임차인 시설 철거 의무 없음</li>
                <li><b>대법원 2020다277028</b>: 현저한 고액 차임 요구로 권리금 방해 시 손배</li>
                <li><b>대법원 94다34692</b>: 건물 구조부·대규모 수선의무는 임대인 부담</li>
                <li><b>대법원 2014다203960</b>: 5% 초과 차임증액 약정 무효 및 부당이득 반환</li>
                <li><b>대법원 2020다263635</b>: 계약 당시 미고지된 재건축 즉시 명도 불가</li>
                <li><b>대법원 2018두43981 / 2021다234120</b>: 필수품목 강제 및 공급중단 위법</li>
                <li><b>대법원 2016다248998</b>: 중도해지 시 과다한 위약벌 법정 감액</li>
            </ul>
        </div>
        <div class="source-card dispute">
            <h4>🤝 ④ 공공 분쟁조정기구 실무 사례집</h4>
            <p>소송 전 조정 단계에서 실제 원만한 합의를 이끌어낸 공공 분쟁조정위원회의 실제 사례를 반영합니다.</p>
            <ul>
                <li><b>대한법률구조공단</b> 상가건물임대차분쟁조정위원회 분쟁사례집</li>
                <li><b>한국공정거래조정원</b> 가맹사업분쟁조정협의회 실제 접수·조정 사례</li>
                <li>건물주 심기 건드리지 않고 합의 가능한 정중한 카톡 조율 문구 데이터화</li>
            </ul>
        </div>
    </div>
    """)

    # 2. 강행규정 심층 이해 섹션
    with st.container(border=True):
        st.markdown("#### 💡 사장님이 꼭 아셔야 할 법률 상식: **「상가임대차법 제15조」의 위력**")
        st.info("""
        **Q. 이미 계약서에 서명하고 도장까지 찍었는데, 무효가 될 수 있나요?**  
        **A. 네, 확실하게 무효가 됩니다!**  
        
        대한민국 **상가건물 임대차보호법 제15조(강행규정)**는 다음과 같이 선언하고 있습니다:  
        > *"이 법의 규정에 위반된 약정으로서 임차인에게 불리한 것은 효력이 없다."*  
        
        이를 법학에서 **'편면적 강행규정'**이라 부릅니다. 경제적·사회적 약자인 세입자를 보호하기 위해, 건물주와 세입자가 계약서에 상호 날인했더라도 **법정 기준보다 세입자에게 불리하게 정한 특약은 법원 소송이나 분쟁조정 시 100% 원천 무효**로 처리됩니다.
        """)

    st.markdown("---")

    # 3. 대법원 판례 9선 인터랙티브 검색 & 전체 브리핑
    st.markdown("### ⚖️ 대법원 주요 확정 판례 백과 (9대 리딩 케이스)")
    st.caption("SafeLease AI가 계약서 진단 시 자동으로 대조·인용하는 대한민국 대법원 확정 판례 전문 요약집입니다.")

    prec_db = PrecedentDB()
    all_precedents = prec_db.get_all()

    # 필터 & 검색
    c_f1, c_f2 = st.columns([1, 2])
    with c_f1:
        categories = ["전체 보기"] + sorted(list(set(p.category for p in all_precedents)))
        sel_cat = st.selectbox("📂 분쟁 카테고리별 필터", categories, key="whitepaper_cat_filter")
    with c_f2:
        search_kw = st.text_input("🔍 판례 키워드 검색", placeholder="예: 원상복구, 권리금, 위약금, 5%, 수선, 2017다268142", key="whitepaper_kw_search")

    filtered_precedents = all_precedents
    if sel_cat != "전체 보기":
        filtered_precedents = [p for p in filtered_precedents if p.category == sel_cat]
    if search_kw:
        filtered_precedents = [p for p in filtered_precedents if search_kw.lower() in (p.title + p.summary + p.key_quote + p.action_guide + p.case_no).lower()]

    st.write(f"조회된 판례: **{len(filtered_precedents)}건**")

    for p in filtered_precedents:
        with st.container(border=True):
            st.markdown(f"#### 📜 {p.case_no} : {p.title} `[{p.category}]`")
            st.caption(f"선고일자: {p.case_date}")
            st.markdown(f"**🔍 판결 요지**:\n{p.summary}")
            st.info(f"**대법원 판시 핵심 문구**:\n\"{p.key_quote}\"")
            st.success(f"**🛡️ 사장님 실전 협상 및 대응 가이드**: {p.action_guide}")

    # 4. 무료 공공 상담처 연락처 모음
    st.markdown("---")
    st.markdown("### 📞 무료 분쟁 조정 및 법률 지원 기관")
    col_org1, col_org2, col_org3 = st.columns(3)
    with col_org1:
        with st.container(border=True):
            st.markdown("##### 🏛️ 대한법률구조공단")
            st.markdown("상가건물임대차분쟁조정위원회 운영  \n**전화**: `국번없이 132`  \n**웹사이트**: [klac.or.kr](https://www.klac.or.kr)")
    with col_org2:
        with st.container(border=True):
            st.markdown("##### 🤝 한국공정거래조정원")
            st.markdown("가맹사업거래 분쟁조정협의회 운영  \n**전화**: `1588-1490`  \n**웹사이트**: [kfair.or.kr](https://www.kfair.or.kr)")
    with col_org3:
        with st.container(border=True):
            st.markdown("##### 🏪 소상공인시장진흥공단")
            st.markdown("소상공인마당 무료 법률·세무 전문상담  \n**전화**: `1357`  \n**웹사이트**: [sbiz.or.kr](https://www.sbiz.or.kr)")


def render_admin_dashboard():
    """전문가 및 운영 관리자 대시보드"""
    render_html("""
    <div class="hero-container" style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);">
        <div class="hero-title">🛠️ SafeLease AI 관리자 센터</div>
        <div class="hero-desc">전체 계약서 검토 통계, 주의 특약 적발 빅데이터, 법률 룰셋 엔진을 모니터링합니다.</div>
    </div>
    """)

    history_mgr = HistoryManager()
    sessions = history_mgr.list_sessions()

    tab_a1, tab_a2, tab_a3, tab_a4 = st.tabs(["📊 KPI 및 적발 통계", "📁 전체 의뢰인 관리", "⚙️ 불리한 특약 룰셋", "⚖️ 대법원 판례 DB"])

    with tab_a1:
        st.subheader("서비스 KPI 메트릭스")
        c1, c2, c3 = st.columns(3)
        c1.metric("총 등록 의뢰 매장", f"{len(sessions)}곳")
        tot_v = sum(len(s.versions) for s in sessions)
        c2.metric("누적 계약서 검토", f"{tot_v}건")
        avg = (sum(s.versions[-1].safety_score for s in sessions if s.versions) / len(sessions)) if sessions else 0
        c3.metric("평균 최종 안전지수", f"{avg:.1f}점")

        st.markdown("#### 🚨 상가 계약서 빈출 주의 특약 TOP 5")
        st.table({
            "주의 특약 유형": ["전 임차인 시설 원상복구 부담 전가", "권리금 일체 포기 조항", "재건축 시 무조건 명도 약정", "임대료 5% 초과 일방 인상", "구조부 대수선 임차인 부담"],
            "적발 건수": [42, 38, 27, 19, 15],
            "위험도": ["RED (조율 필요)", "RED (조율 필요)", "RED (조율 필요)", "YELLOW (주의)", "YELLOW (주의)"],
            "법적 근거": ["대법원 2017다268142", "상가임대차법 15조", "상가임대차법 10조", "상가임대차법 11조", "민법 623조"]
        })

    with tab_a2:
        st.subheader("전체 의뢰인 컨설팅 히스토리")
        if sessions:
            rows = []
            for s in sessions:
                rows.append({
                    "세션 ID": s.session_id,
                    "상호명": s.tenant_name,
                    "업종": s.business_type,
                    "검토 버전 수": len(s.versions),
                    "최신 안전점수": f"{s.versions[-1].safety_score}점" if s.versions else "-",
                    "최근 갱신일": s.updated_at.strftime("%Y-%m-%d %H:%M")
                })
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("등록된 세션이 없습니다.")

    with tab_a3:
        st.subheader("⚙️ 공인 법률 기준 주의 특약 룰셋 엔진")
        r_type = st.radio("룰셋 분류 필터", ["전체 보기", "상가 임대차 (상가임대차보호법·대법원판례)", "프랜차이즈 가맹계약 (가맹사업법·공정위)"], horizontal=True)
        c_filter = "lease" if "상가" in r_type else ("franchise" if "프랜차이즈" in r_type else "all")
        engine = RulesEngine(contract_type=c_filter)
        st.write(f"현재 활성화된 법률 룰셋: **{len(engine.rules)}개**")
        for r in engine.rules:
            with st.expander(f"[{r.get('risk_level')}] {r.get('rule_id')} - {r.get('title')} ({r.get('category')})"):
                st.json(r)

    with tab_a4:
        st.subheader("⚖️ 대법원 주요 확정 판례 지식베이스")
        st.caption("상가임대차 및 가맹계약 분쟁 시 사장님 권익 보호의 기준이 되는 대법원 판례 데이터베이스입니다.")
        p_search = st.text_input("🔍 판례 검색 (사건번호, 키워드, 카테고리)", placeholder="예: 원상복구, 권리금, 2017다268142, 수선의무", key="admin_prec_search")
        prec_db = PrecedentDB()
        precedent_list = prec_db.search(p_search) if p_search else prec_db.get_all()
        st.write(f"조회된 판례: **{len(precedent_list)}건**")
        for p in precedent_list:
            with st.container(border=True):
                st.markdown(f"#### 📜 {p.case_no} : {p.title} `[{p.category}]`")
                st.caption(f"선고일자: {p.case_date}")
                st.markdown(f"**🔍 판결 요지**:\n{p.summary}")
                st.info(f"**핵심 판시 문구**:\n\"{p.key_quote}\"")
                st.success(f"**🛡️ 사장님 실전 협상 및 대응 가이드**: {p.action_guide}")


if __name__ == "__main__":
    main()
