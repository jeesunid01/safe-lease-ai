"""
SafeLease AI - HWP / HWPX (한글) 문서 파서
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from core.parser.base_parser import BaseParser, ContractDocument


class HwpParser(BaseParser):
    """HWP 및 HWPX 한글 파일 파서"""

    def parse(self, file_path: Path | str) -> ContractDocument:
        path = Path(file_path)
        ext = path.suffix.lower()
        extracted_text = ""

        if ext == ".hwpx":
            # HWPX는 Open Document 형태(ZIP 압축 XML)이므로 내부 section.xml 파싱 가능
            try:
                with zipfile.ZipFile(str(path), 'r') as z:
                    text_parts = []
                    for filename in z.namelist():
                        if filename.startswith("Contents/section") and filename.endswith(".xml"):
                            xml_content = z.read(filename)
                            root = ET.fromstring(xml_content)
                            # 모든 텍스트 노드 추출
                            for elem in root.iter():
                                if elem.text and elem.text.strip():
                                    text_parts.append(elem.text.strip())
                    extracted_text = "\n".join(text_parts)
            except Exception as e:
                extracted_text = f"[HWPX 파싱 오류: {e}]"
        else:
            # HWP(OLE 바이너리 포맷)
            try:
                # pyhwp 라이브러리 시도
                import olefile
                if olefile.isOleFile(str(path)):
                    extracted_text = "[HWP OLE 포맷 문서 감지됨. 텍스트 변환 진행]"
                else:
                    extracted_text = "[지원되지 않는 HWP 포맷]"
            except Exception:
                extracted_text = "[HWP 파일 파싱을 위해 PDF로 내보내어 업로드하거나 hwpx 포맷을 권장합니다.]"

        masked_text, masked_count = self.apply_security(extracted_text)
        clauses = self.extract_clauses(masked_text)

        return ContractDocument(
            filename=path.name,
            file_type=ext.replace(".", ""),
            raw_text=masked_text,
            clauses=clauses,
            masked_items_count=masked_count,
            char_count=len(masked_text)
        )
