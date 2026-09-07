"""
SafeLease AI - LLM 프롬프트 템플릿 및 Gemini 연동 모듈 (2차 하이브리드 추론)
독소조항 심층 해석 및 사장님 맞춤 협상 스크립트를 정밀하게 생성합니다.
"""

from typing import Optional
from config import GEMINI_API_KEY


SYSTEM_PROMPT = """당신은 대한민국 최고 수준의 상가건물임대차 및 가맹계약 전문 법률 AI 비서 'SafeLease AI'입니다.
당신의 사명은 소상공인·자영업자가 건물주나 가맹본사와의 계약에서 억울한 피해를 입지 않도록 돕는 것입니다.

[원칙]
1. 변호사법 제109조를 준수하며, 확정적 법률 유권해석이 아닌 정부 표준계약서 및 대법원 판례 대조 정보를 제공합니다.
2. 계약서 원문의 문장을 왜곡 없이 정확하게 인용합니다.
3. 건물주의 기분을 상하게 하지 않고 자연스럽게 수용할 수 있는 '완곡하고 세련된 대체 문구(Nudge Script)'를 작성합니다.
"""

DEEP_ANALYSIS_PROMPT_TEMPLATE = """
[검토 대상 계약서 조항]
{clause_text}

[질문 및 요청사항]
1. 위 조항이 대한민국 「상가건물 임대차보호법」 제15조(강행규정) 또는 대법원 판례에 비추어 임차인에게 일방적으로 불리한 독소조항인지 판단해 주세요.
2. 위험도(🔴 RED: 위험, 🟡 YELLOW: 주의, 🟢 GREEN: 안전)를 판정해 주세요.
3. 소상공인 사장님이 건물주에게 카톡/문자로 보낼 수 있는 '공손하고 완곡한 협상 대화문'과 '논리적인 객관적 대화문'을 2가지 버전으로 작성해 주세요.
"""


def generate_deep_explanation(clause_text: str, tone: str = "polite") -> Optional[str]:
    """Gemini API가 설정되어 있을 경우 심층 해설 및 협상 문구를 동적으로 생성합니다."""
    if not GEMINI_API_KEY:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = DEEP_ANALYSIS_PROMPT_TEMPLATE.format(clause_text=clause_text)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[SYSTEM_PROMPT, prompt]
        )
        return response.text
    except Exception as e:
        print(f"[LLM 추론 실패] {e}")
        return None
