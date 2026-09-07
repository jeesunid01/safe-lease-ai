"""
SafeLease AI - 대법원 핵심 판례 매처 및 지식베이스 모듈
계약서 독소조항 검토 시 관련 대법원 판례의 요약 및 핵심 판시사항을 제공합니다.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from config import BASE_DIR

PRECEDENTS_FILE = BASE_DIR / "data" / "precedents" / "supreme_court_precedents.json"


class PrecedentItem:
    def __init__(self, data: dict):
        self.precedent_id: str = data.get("precedent_id", "")
        self.case_no: str = data.get("case_no", "")
        self.case_date: str = data.get("case_date", "")
        self.title: str = data.get("title", "")
        self.category: str = data.get("category", "")
        self.summary: str = data.get("summary", "")
        self.key_quote: str = data.get("key_quote", "")
        self.action_guide: str = data.get("action_guide", "")


class PrecedentDB:
    """대법원 판례 검색 및 조회 엔진"""

    def __init__(self, file_path: Optional[Path | str] = None):
        self.file_path = Path(file_path) if file_path else PRECEDENTS_FILE
        self.precedents: List[PrecedentItem] = self._load()

    def _load(self) -> List[PrecedentItem]:
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
                return [PrecedentItem(item) for item in raw_list]
        except Exception as e:
            print(f"[PrecedentDB] 로드 실패: {e}")
            return []

    def get_all(self) -> List[PrecedentItem]:
        return self.precedents

    def find_by_case_no(self, case_query: str) -> Optional[PrecedentItem]:
        """사건번호(예: 2017다268142)로 판례 매칭"""
        clean_q = case_query.replace(" ", "").replace("판결", "").replace("선고", "")
        for p in self.precedents:
            clean_case = p.case_no.replace(" ", "")
            if clean_q in clean_case or any(num in clean_case for num in clean_q.split("다") if num.isdigit()):
                return p
        return None

    def search(self, query: str) -> List[PrecedentItem]:
        """키워드 검색"""
        results = []
        q_lower = query.lower().strip()
        for p in self.precedents:
            searchable = f"{p.case_no} {p.title} {p.summary} {p.category}".lower()
            if q_lower in searchable:
                results.append(p)
        return results
