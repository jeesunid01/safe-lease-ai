"""
SafeLease AI - PDF 문서 파서
PyPDF 및 pdfplumber를 활용하여 PDF에서 텍스트와 레이아웃을 안전하게 추출합니다.
"""

from pathlib import Path
from core.parser.base_parser import BaseParser, ContractDocument, ClauseItem


class PdfParser(BaseParser):
    """PDF 파일 파서"""

    def parse(self, file_path: Path | str) -> ContractDocument:
        path = Path(file_path)
        extracted_pages = []

        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                extracted_pages.append(text)
        except Exception as e:
            # pdfplumber 폴백 시도
            try:
                import pdfplumber
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text() or ""
                        extracted_pages.append(text)
            except Exception as e2:
                extracted_pages = [f"[PDF 파싱 오류: {e} / {e2}]"]

        full_raw_text = "\n\n".join(extracted_pages)
        masked_text, masked_count = self.apply_security(full_raw_text)

        clauses = []
        for page_idx, page_text in enumerate(extracted_pages, 1):
            masked_p_text, _ = self.apply_security(page_text)
            p_clauses = self.extract_clauses(masked_p_text, default_page=page_idx)
            clauses.extend(p_clauses)

        return ContractDocument(
            filename=path.name,
            file_type="pdf",
            raw_text=masked_text,
            clauses=clauses,
            masked_items_count=masked_count,
            char_count=len(masked_text)
        )
