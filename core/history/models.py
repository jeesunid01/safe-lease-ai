"""
SafeLease AI - 컨설팅 히스토리 & 버전 비교 데이터 모델
"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class IssueSnapshot(BaseModel):
    rule_id: str
    category: str
    risk_level: str
    title: str
    verbatim_quote: str
    page: int = 1
    resolved: bool = False


class VersionSnapshot(BaseModel):
    version_id: int = Field(..., description="버전 번호 (1, 2, 3...)")
    version_label: str = Field("초안", description="버전 라벨 (예: 1차 초안, 2차 수정본, 최종 체결본)")
    analyzed_at: datetime = Field(default_factory=datetime.now)
    safety_score: int
    risk_summary: Dict[str, int]
    issues: List[IssueSnapshot] = Field(default_factory=list)


class ConsultingSession(BaseModel):
    session_id: str = Field(..., description="고유 세션 ID (예: UUID 또는 상호-날짜)")
    tenant_name: str = Field(..., description="의뢰인 상호명 또는 닉네임")
    business_type: str = Field("일반상가", description="업종 (카페, 음식점, 학원 등)")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    versions: List[VersionSnapshot] = Field(default_factory=list)


class DiffItem(BaseModel):
    rule_id: str
    title: str
    status: str = Field(..., description="RESOLVED (해결됨) | PERSISTENT (여전히 존속) | NEW (새로 발생)")
    old_risk: Optional[str] = None
    new_risk: Optional[str] = None
    comment: str
    old_quote: Optional[str] = None
    new_quote: Optional[str] = None


class VersionDiffResult(BaseModel):
    session_id: str
    base_version_id: int
    compare_version_id: int
    score_change: int = Field(..., description="안전 점수 변화량 (예: +45점)")
    diff_items: List[DiffItem] = Field(default_factory=list)
    summary_message: str
