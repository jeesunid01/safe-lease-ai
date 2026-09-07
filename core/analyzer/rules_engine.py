"""
SafeLease AI - 독소조항 탐지 룰셋 엔진 (1차 하이브리드 파이프라인)
4대 공인 기준(상가임대차법, 표준계약서, 대법원 판례, 약관규제법) 룰셋을 기반으로 계약서 조항을 검사합니다.
"""

import json
import re
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from core.parser.base_parser import ContractDocument, ClauseItem
from config import RULESET_DIR


class DetectedIssue(BaseModel):
    """탐지된 독소조항 이슈 모델"""
    rule_id: str
    category: str
    risk_level: str = Field(..., description="RED (위험) | YELLOW (주의) | GREEN (안전)")
    title: str
    matched_clause_no: Optional[str] = None
    page: int = Field(1, description="계약서 내 발견된 페이지 번호")
    verbatim_quote: str = Field(..., description="계약서 원문 글자 그대로 발췌")
    legal_basis: str = Field(..., description="관련 법률 조항 및 대법원 판례")
    danger_explanation: str = Field(..., description="왜 사장님에게 불리한지에 대한 설명")
    recommended_replacement: str = Field(..., description="추천 대체 조항 문구")
    nudge_script_polite: str = Field(..., description="건물주용 완곡/공손한 협상 대화문")
    nudge_script_logical: str = Field(..., description="법인/본사용 객관적/논리적 협상 대화문")


class AnalysisResult(BaseModel):
    """계약서 전체 분석 결과 모델"""
    document_name: str
    total_clauses: int
    safety_score: int = Field(..., ge=0, le=100, description="계약서 안전 점수 (0~100점)")
    risk_summary: dict = Field(default_factory=dict, description="RED/YELLOW/GREEN 건수 요약")
    detected_issues: List[DetectedIssue] = Field(default_factory=list)
    has_critical_toxic: bool = Field(False, description="치명적 독소조항 포함 여부")


class RulesEngine:
    """독소조항 규칙 매칭 엔진"""

    def __init__(self, ruleset_path: Optional[Path | str] = None, contract_type: str = "all"):
        self.ruleset_path = Path(ruleset_path) if ruleset_path else None
        self.contract_type = contract_type
        self.rules = self._load_rules()

    def _load_rules(self) -> list:
        if self.ruleset_path and self.ruleset_path.exists():
            try:
                with open(self.ruleset_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[RulesEngine] 룰셋 로드 실패 ({self.ruleset_path}): {e}")
                return []

        # contract_type에 따른 룰셋 로드
        rules = []
        files_to_load = []
        if self.contract_type == "lease":
            files_to_load.append(RULESET_DIR / "lease_toxic_rules.json")
        elif self.contract_type == "franchise":
            files_to_load.append(RULESET_DIR / "franchise_toxic_rules.json")
        else:
            # "all" 또는 자동
            files_to_load.extend(sorted(RULESET_DIR.glob("*toxic_rules.json")))

        for r_file in files_to_load:
            if r_file.exists():
                try:
                    with open(r_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            rules.extend(data)
                except Exception as e:
                    print(f"[RulesEngine] 룰셋 로드 실패 ({r_file}): {e}")

        return rules

    def analyze(self, doc: ContractDocument) -> AnalysisResult:
        """
        ContractDocument의 모든 조항을 순회하며 독소조항을 탐지하고 안전 점수를 산출합니다.
        """
        detected_issues: List[DetectedIssue] = []

        # 각 조항별로 룰셋 검사
        for clause in doc.clauses:
            clause_text = clause.content
            if not clause_text or len(clause_text.strip()) < 5:
                continue

            for rule in self.rules:
                is_matched = False
                matched_snippet = ""

                # 1. 정규식 패턴 검사
                patterns = rule.get("patterns", [])
                for pat in patterns:
                    match = re.search(pat, clause_text, re.IGNORECASE)
                    if match:
                        is_matched = True
                        matched_snippet = match.group(0)
                        break

                # 2. 키워드 교차 검사 (정규식 미매칭 시)
                if not is_matched:
                    keywords = rule.get("keywords", [])
                    matched_kw = [kw for kw in keywords if kw in clause_text]
                    if len(matched_kw) >= 2: # 최소 2개 이상 키워드 동시 출현
                        is_matched = True
                        matched_snippet = f"키워드 포착: {', '.join(matched_kw)}"

                if is_matched:
                    # 중복 방지 (동일 조항에서 같은 룰 중복 방지)
                    if not any(iss.rule_id == rule["rule_id"] and iss.matched_clause_no == clause.article_no for iss in detected_issues):
                        detected_issues.append(DetectedIssue(
                            rule_id=rule["rule_id"],
                            category=rule.get("category", "일반"),
                            risk_level=rule.get("risk_level", "YELLOW"),
                            title=rule.get("title", ""),
                            matched_clause_no=clause.article_no,
                            page=clause.page,
                            verbatim_quote=clause_text.strip()[:200] + ("..." if len(clause_text.strip()) > 200 else ""),
                            legal_basis=rule.get("legal_basis", ""),
                            danger_explanation=rule.get("danger_explanation", ""),
                            recommended_replacement=rule.get("recommended_replacement", ""),
                            nudge_script_polite=rule.get("nudge_script_polite", "").replace("제N조", clause.article_no or "해당 조항"),
                            nudge_script_logical=rule.get("nudge_script_logical", "").replace("제N조", clause.article_no or "해당 조항")
                        ))

        # 안전 점수 계산 (기본 100점에서 RED -25점, YELLOW -10점)
        red_count = sum(1 for iss in detected_issues if iss.risk_level == "RED")
        yellow_count = sum(1 for iss in detected_issues if iss.risk_level == "YELLOW")
        green_count = max(0, len(doc.clauses) - len(detected_issues))

        score = max(0, 100 - (red_count * 25) - (yellow_count * 10))

        return AnalysisResult(
            document_name=doc.filename,
            total_clauses=len(doc.clauses),
            safety_score=score,
            risk_summary={
                "RED": red_count,
                "YELLOW": yellow_count,
                "GREEN": green_count
            },
            detected_issues=detected_issues,
            has_critical_toxic=(red_count > 0)
        )
