"""
SafeLease AI - 보안 및 마스킹 단위 테스트
"""

from core.security.anonymizer import mask_pii
from core.security.file_purger import safe_temp_file, purge_file
from pathlib import Path


def test_mask_pii():
    sample = "임차인 홍길동 (주민번호: 900101-1234567, 전화: 010-1234-5678, 계좌: 110-123-456789, 메일: test@example.com)"
    masked, count = mask_pii(sample)

    assert count >= 3
    assert "900101-1234567" not in masked
    assert "900101-*******" in masked
    assert "010-****-5678" in masked
    assert "test@example.com" not in masked


def test_safe_temp_file():
    test_content = b"Super Sensitive Contract Data"
    filename = "temp_contract.tmp"

    created_path = None
    with safe_temp_file(filename, test_content) as path:
        created_path = path
        assert path.exists()
        assert path.read_bytes() == test_content

    # 컨텍스트 종료 후 파일이 즉시 영구 삭제되었는지 확인
    assert not created_path.exists()
