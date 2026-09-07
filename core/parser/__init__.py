"""
SafeLease AI - Parser Module Factory
"""

from pathlib import Path
from core.parser.base_parser import BaseParser, ContractDocument, ClauseItem
from core.parser.txt_parser import TxtParser
from core.parser.pdf_parser import PdfParser
from core.parser.docx_parser import DocxParser
from core.parser.hwp_parser import HwpParser
from core.parser.image_ocr import ImageParser


def get_parser(file_path: Path | str) -> BaseParser:
    """
    파일 확장자에 맞는 최적의 파서 인스턴스를 반환합니다.
    """
    ext = Path(file_path).suffix.lower()

    if ext in [".txt", ".md"]:
        return TxtParser()
    elif ext == ".pdf":
        return PdfParser()
    elif ext in [".docx", ".doc"]:
        return DocxParser()
    elif ext in [".hwp", ".hwpx"]:
        return HwpParser()
    elif ext in [".jpg", ".jpeg", ".png", ".heic", ".webp"]:
        return ImageParser()
    else:
        # 알 수 없는 확장자는 텍스트 파서로 기본 시도
        return TxtParser()


def parse_contract(file_path: Path | str) -> ContractDocument:
    """단일 진입점으로 파일 경로를 받아 파싱 및 마스킹 수행"""
    parser = get_parser(file_path)
    return parser.parse(file_path)


__all__ = ["BaseParser", "ContractDocument", "ClauseItem", "get_parser", "parse_contract"]
