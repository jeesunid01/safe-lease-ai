"""
SafeLease AI - 텍스트/마크다운 파일 파서
"""

from pathlib import Path
from core.parser.base_parser import BaseParser, ContractDocument


class TxtParser(BaseParser):
    """텍스트(.txt, .md) 파일 파서"""

    def parse(self, file_path: Path | str) -> ContractDocument:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw_content = f.read()

        masked_text, masked_count = self.apply_security(raw_content)
        clauses = self.extract_clauses(masked_text)

        return ContractDocument(
            filename=path.name,
            file_type=path.suffix.lower().replace(".", ""),
            raw_text=masked_text,
            clauses=clauses,
            masked_items_count=masked_count,
            char_count=len(masked_text)
        )
