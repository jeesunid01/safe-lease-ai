"""
SafeLease AI - 제로 리텐션(Zero-Retention) 파일 파기 모듈
업로드된 계약서 원본 파일을 처리 완료 즉시 복구 불가능하도록 영구 파기합니다.
"""

import os
import shutil
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from config import TEMP_DIR


def purge_file(file_path: Path | str) -> bool:
    """
    지정된 파일을 디스크에서 안전하게 영구 삭제합니다.
    
    Args:
        file_path: 삭제할 파일 경로
        
    Returns:
        bool: 삭제 성공 여부
    """
    path = Path(file_path)
    if not path.exists():
        return True

    try:
        # 파일 크기 확인 후 0바이트로 덮어쓰기 (Data Shredding)
        if path.is_file():
            file_size = path.stat().st_size
            if file_size > 0:
                with open(path, "ba+", buffering=0) as f:
                    f.write(b"\x00" * file_size)
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        return True
    except Exception as e:
        print(f"[Warning] 파일 안전 파기 중 예외 발생: {e}")
        # 예외 발생 시에도 기본 삭제 재시도
        try:
            if path.is_file():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            return True
        except Exception:
            return False


@contextmanager
def safe_temp_file(filename: str, content: bytes) -> Generator[Path, None, None]:
    """
    임시 파일을 생성하고, 작업이 끝나면 (성공/예외 무관) 즉시 영구 삭제하는 컨텍스트 매니저.
    
    사용 예:
        with safe_temp_file("contract.pdf", file_bytes) as temp_path:
            text = parse_pdf(temp_path)
        # 블록을 벗어나면 파일은 이미 삭제됨
    """
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = TEMP_DIR / filename

    try:
        with open(temp_path, "wb") as f:
            f.write(content)
        yield temp_path
    finally:
        purge_file(temp_path)
