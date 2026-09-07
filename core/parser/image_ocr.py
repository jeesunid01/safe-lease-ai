"""
SafeLease AI - 스마트폰 사진 및 이미지 OCR 파서
스마트폰 촬영 계약서 사진(JPG, PNG 등)에서 텍스트를 인식하고 왜곡/품질을 체크합니다.
"""

from pathlib import Path
from core.parser.base_parser import BaseParser, ContractDocument
from config import GEMINI_API_KEY


class ImageParser(BaseParser):
    """이미지 및 스마트폰 촬영본 파서"""

    def parse(self, file_path: Path | str) -> ContractDocument:
        path = Path(file_path)
        extracted_text = ""
        
        # 1. 이미지 무결성 및 해상도 기본 검증
        try:
            from PIL import Image
            with Image.open(str(path)) as img:
                width, height = img.size
                if width < 300 or height < 300:
                    extracted_text = "⚠️ [품질 경고] 이미지 해상도가 너무 낮아 계약서 특약 글씨를 정확히 판별하기 어렵습니다. 밝은 곳에서 선명하게 재촬영해 주세요."
        except ImportError:
            extracted_text = "[이미지 처리를 위해 pillow 라이브러리 설치가 필요합니다: pip install pillow]"
        except Exception as e:
            extracted_text = f"[이미지 파일 로드 실패: {e}]"

        # 2. Vision AI (Gemini) 연동 시도
        if not extracted_text and GEMINI_API_KEY:
            try:
                # Gemini Vision API 호출 시도
                from google import genai
                client = genai.Client(api_key=GEMINI_API_KEY)
                with open(str(path), "rb") as f:
                    image_bytes = f.read()
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        "당신은 리걸테크 OCR 전문가입니다. 이 계약서 이미지에서 조항(제N조, 특약사항 등)을 누락 없이 그대로 전사(Transcribe)해 주세요.",
                        image_bytes
                    ]
                )
                extracted_text = response.text or ""
            except Exception as e:
                extracted_text = f"[Vision OCR 처리 중 오류 발생: {e}. 명확한 텍스트 확인을 위해 PDF 또는 텍스트 문서를 권장합니다.]"

        if not extracted_text:
            extracted_text = "[이미지 OCR 처리를 위해 GEMINI_API_KEY 설정이 필요하거나, 텍스트/PDF 업로드를 권장합니다.]"

        masked_text, masked_count = self.apply_security(extracted_text)
        clauses = self.extract_clauses(masked_text)

        return ContractDocument(
            filename=path.name,
            file_type=path.suffix.lower().replace(".", ""),
            raw_text=masked_text,
            clauses=clauses,
            masked_items_count=masked_count,
            char_count=len(masked_text)
        )
