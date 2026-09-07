"""
SafeLease AI - 필수 누락 조항 역추적 검사기 (Missing Clauses Checker)
계약서에 반드시 기재되어 있어야 하지만 빠져 있는 소상공인 핵심 보호 특약을 점검합니다.
"""

from typing import List
from pydantic import BaseModel, Field
from core.parser.base_parser import ContractDocument


class MissingCheckItem(BaseModel):
    check_id: str
    category: str
    title: str
    why_important: str
    legal_basis: str = Field(..., description="관련 법령 및 표준계약서 규정")
    recommended_clause: str
    is_missing: bool = True


# 필수 점검 항목 표준 리스트
ESSENTIAL_CHECKLIST = [
    {
        "check_id": "MISSING-01",
        "category": "관리비 투명성",
        "title": "관리비 부과 내역 및 정산 기준 명시",
        "keywords": ["관리비", "정산", "부과 내역", "실비"],
        "why_important": "관리비 산정 기준이 없으면 임대료 인상 규제를 피해 '깜깜이 관리비'를 과다 청구할 때 대항하기 어렵습니다.",
        "legal_basis": "국토교통부 고시 상가건물임대차표준계약서 제4조 및 집합건물의 소유 및 관리에 관한 법률 제26조(관리비용 징수 기준)",
        "recommended_clause": "임대인은 관리비의 산출 근거 및 영수증을 임차인에게 매월 투명하게 공개하며, 실비를 초과하여 징수하지 아니한다."
    },
    {
        "check_id": "MISSING-02",
        "category": "시설/영업환경",
        "title": "외부 간판 설치 위치 및 닥트/환기구 허용 특약",
        "keywords": ["간판", "환기구", "닥트", "설치 위치", "외벽"],
        "why_important": "구두로 약속받았어도 계약서에 없으면 건물주나 타 상가 입주민의 민원으로 간판/환기 시설을 철거해야 할 수 있습니다.",
        "legal_basis": "옥외광고물 등의 관리와 옥외광고산업 진흥에 관한 법률 시행령 제5조 및 민법 제623조(목적물 사용·수익 유지의무)",
        "recommended_clause": "임대인은 임차인의 정상적인 영업을 위하여 지정된 외벽 위치에 상호 간판 및 환기덕트 배관의 설치를 무상으로 허용한다."
    },
    {
        "check_id": "MISSING-03",
        "category": "주차/편의",
        "title": "임차인 및 고객 무료 주차 대수 보장",
        "keywords": ["주차", "주차 대수", "주차권", "방문객"],
        "why_important": "주차 가능 여부는 요식업/서비스업 매출에 직결되며, 약속과 달리 유료 전환되거나 제한될 위험이 있습니다.",
        "legal_basis": "주차장법 제19조(부설주차장의 설치·지정) 및 법무부 표준계약서 제6조(특약사항 권장)",
        "recommended_clause": "임대인은 임차인 영업 차량 N대의 무료 주차 및 방문 고객을 위한 주차 편의(또는 할인권)를 제공한다."
    },
    {
        "check_id": "MISSING-04",
        "category": "보증금 반환",
        "title": "명도와 보증금 반환의 동시이행 및 지연이자 약정",
        "keywords": ["보증금 반환", "동시이행", "퇴거 즉시", "명도와 동시"],
        "why_important": "'다음 세입자 들어오면 보증금 준다'는 건물주의 횡포를 막기 위해 명도 당일 반환 원칙이 기재되어야 합니다.",
        "legal_basis": "민법 제536조(동시이행의 항변권), 민법 제379조 및 상법 제54조(상사 법정이율 연 6%)",
        "recommended_clause": "임대인은 임차인이 목적물을 인도(명도)함과 동시에 보증금 전액을 반환하여야 하며, 지연 시 연 5%의 지연손해금을 가산하여 지급한다."
    }
]


class MissingChecker:
    """누락 조항 점검기"""

    def check(self, doc: ContractDocument) -> List[MissingCheckItem]:
        results: List[MissingCheckItem] = []
        full_text = doc.raw_text

        for item in ESSENTIAL_CHECKLIST:
            keywords = item["keywords"]
            # 본문에 키워드가 하나라도 언급되어 있는지 확인
            found = any(kw in full_text for kw in keywords)

            results.append(MissingCheckItem(
                check_id=item["check_id"],
                category=item["category"],
                title=item["title"],
                why_important=item["why_important"],
                recommended_clause=item["recommended_clause"],
                legal_basis=item.get("legal_basis", "국토교통부 표준계약서 및 민법 임대차 규정"),
                is_missing=(not found)
            ))

        return results
