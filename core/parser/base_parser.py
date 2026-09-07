"""
SafeLease AI - 문서 파서 공통 인터페이스 및 데이터 모델
모든 파일 포맷(PDF, 이미지, DOCX, HWP 등)의 파서는 이 인터페이스를 상속받습니다.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from core.security.anonymizer import mask_pii


class ClauseItem(BaseModel):
    """개별 계약 조항 모델"""
    article_no: Optional[str] = Field(None, description="제몇조 또는 특약 번호")
    title: Optional[str] = Field(None, description="조항 제목 (예: 원상회복의무)")
    content: str = Field(..., description="조항 원문 본문")
    page: int = Field(1, description="문서 내 페이지 번호")


class ContractDocument(BaseModel):
    """정규화된 계약서 전체 문서 모델"""
    filename: str = Field(..., description="원본 파일명")
    file_type: str = Field(..., description="파일 확장자/타입 (pdf, docx, hwp, img, txt)")
    raw_text: str = Field(..., description="전체 원문 텍스트 (마스킹 적용됨)")
    clauses: List[ClauseItem] = Field(default_factory=list, description="분리된 조항 목록")
    masked_items_count: int = Field(0, description="마스킹 처리된 민감정보 수")
    char_count: int = Field(0, description="총 글자 수")


class BaseParser(ABC):
    """추상 파서 기본 클래스"""

    @abstractmethod
    def parse(self, file_path: Path | str) -> ContractDocument:
        """
        파일을 읽어 표준 ContractDocument 규격으로 변환합니다.
        
        Args:
            file_path: 대상 파일 경로
            
        Returns:
            ContractDocument: 마스킹 처리된 계약서 데이터 객체
        """
        pass

    def extract_clauses(self, text: str, default_page: int = 1) -> List[ClauseItem]:
        """
        전체 텍스트에서 '제N조', '특약 N' 또는 페이지 마커를 기준으로 조항들을 분리하고 페이지 번호를 정확히 추적합니다.
        """
        import re
        page_marker_pattern = re.compile(r'(?:\[|\(|---|\s|^)(\d+)\s*(?:페이지|쪽|page)', re.IGNORECASE)
        clause_header_pattern = re.compile(r'^(제\s*\d+\s*조(?:\s*\[[^\]]+\]|\s*\([^\)]+\))?|특약\s*\d+[\.:\)]?|\[특약사항\]|\d+\.\s+[^\n]+)', re.MULTILINE)

        lines = text.splitlines()
        current_page = default_page
        clauses = []
        current_header = "전문/서두"
        current_page_of_clause = current_page
        current_body_lines = []

        for line in lines:
            line_str = line.strip()
            # 1. 페이지 마커 확인
            pm = page_marker_pattern.search(line_str)
            if pm:
                try:
                    current_page = int(pm.group(1))
                except ValueError:
                    pass
            elif "[특약사항]" in line_str:
                if current_page == 1:
                    current_page = 2

            # 2. 새로운 조항 시작 여부 확인
            hm = clause_header_pattern.match(line_str)
            if hm:
                # 이전 조항 저장
                if current_body_lines:
                    body_text = "\n".join(current_body_lines).strip()
                    if body_text:
                        clauses.append(ClauseItem(
                            article_no=current_header,
                            content=body_text,
                            page=current_page_of_clause
                        ))
                current_header = hm.group(1).strip()
                current_page_of_clause = current_page
                remainder = line_str[len(current_header):].strip()
                current_body_lines = [remainder] if remainder else []
            else:
                if line_str:
                    current_body_lines.append(line_str)

        # 마지막 조항 저장
        if current_body_lines:
            body_text = "\n".join(current_body_lines).strip()
            if body_text:
                clauses.append(ClauseItem(
                    article_no=current_header,
                    content=body_text,
                    page=current_page_of_clause
                ))

        return clauses

    def apply_security(self, raw_text: str) -> tuple[str, int]:
        """개인정보 마스킹을 적용합니다."""
        return mask_pii(raw_text)
