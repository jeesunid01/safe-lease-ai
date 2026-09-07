"""
SafeLease AI - 개인정보 비식별화(마스킹) 모듈
계약서 텍스트에서 주민등록번호, 계좌번호, 전화번호 등 민감정보를 정규식으로 감지하여 마스킹합니다.
"""

import re
from typing import Tuple

# 정규식 패턴 정의
# 1. 주민등록번호 (6자리-7자리 또는 13자리 연속)
RRN_PATTERN = re.compile(r'\b(\d{6})[- ]?([1-4]\d{6})\b')

# 2. 전화번호 (휴대폰 및 일반 유선전화)
PHONE_PATTERN = re.compile(r'\b(01[016789]|02|0[3-6][1-5])[- ]?(\d{3,4})[- ]?(\d{4})\b')

# 3. 계좌번호 (은행별 다양한 형식의 하이픈 숫자 패턴)
ACCOUNT_PATTERN = re.compile(r'\b(\d{3,6})[- ]?(\d{2,6})[- ]?(\d{3,8})\b')

# 4. 이메일 주소
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


def mask_pii(text: str) -> Tuple[str, int]:
    """
    텍스트 내 민감한 개인정보를 마스킹 처리합니다.
    
    Args:
        text: 원본 계약서 텍스트
        
    Returns:
        Tuple[str, int]: (마스킹된 텍스트, 마스킹된 총 항목 수)
    """
    if not text:
        return "", 0

    masked_count = 0

    # 1. 주민등록번호 마스킹 (생년월일만 남기고 뒷자리 마스킹: YYMMDD-*******)
    def rrn_sub(match):
        nonlocal masked_count
        masked_count += 1
        return f"{match.group(1)}-*******"

    text = RRN_PATTERN.sub(rrn_sub, text)

    # 2. 전화번호 마스킹 (가운데/뒷자리 마스킹: 010-****-1234 또는 010-****-****)
    def phone_sub(match):
        nonlocal masked_count
        masked_count += 1
        prefix = match.group(1)
        suffix = match.group(3)
        return f"{prefix}-****-{suffix}"

    text = PHONE_PATTERN.sub(phone_sub, text)

    # 3. 이메일 마스킹 (앞 2글자만 남기고 마스킹: ab***@domain.com)
    def email_sub(match):
        nonlocal masked_count
        masked_count += 1
        email = match.group(0)
        user, domain = email.split('@', 1)
        masked_user = user[:2] + "***" if len(user) > 2 else "***"
        return f"{masked_user}@{domain}"

    text = EMAIL_PATTERN.sub(email_sub, text)

    return text, masked_count
