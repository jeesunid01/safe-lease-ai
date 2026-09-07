"""
SafeLease AI - 독소조항 분석 엔진 검증 테스트
"""

from pathlib import Path
from core.parser import parse_contract
from core.analyzer.rules_engine import RulesEngine
from core.analyzer.missing_checker import MissingChecker
from config import TESTS_DIR


def test_toxic_contract_detection():
    toxic_file = TESTS_DIR / "sample_contracts" / "sample_toxic_lease.txt"
    assert toxic_file.exists()

    # 1. 파싱 및 PII 마스킹 검증
    doc = parse_contract(toxic_file)
    assert doc.masked_items_count > 0
    assert "880512-1234567" not in doc.raw_text

    # 2. 독소조항 검출 검증
    engine = RulesEngine()
    result = engine.analyze(doc)

    assert result.has_critical_toxic is True
    assert result.risk_summary.get("RED", 0) >= 2
    assert result.safety_score < 60  # 위험 점수 하락

    # 탐지된 룰 ID 확인
    detected_rules = [iss.rule_id for iss in result.detected_issues]
    assert "TOXIC-001" in detected_rules  # 전 임차인 원상복구
    assert "TOXIC-002" in detected_rules  # 권리금 포기
    assert "TOXIC-003" in detected_rules  # 재건축 무조건 명도


def test_normal_contract_clean():
    normal_file = TESTS_DIR / "sample_contracts" / "sample_normal_lease.txt"
    assert normal_file.exists()

    doc = parse_contract(normal_file)
    engine = RulesEngine()
    result = engine.analyze(doc)

    assert result.has_critical_toxic is False
    assert result.risk_summary.get("RED", 0) == 0
    assert result.safety_score >= 90


def test_franchise_contract_detection():
    franchise_file = TESTS_DIR / "sample_contracts" / "sample_toxic_franchise.txt"
    assert franchise_file.exists()

    doc = parse_contract(franchise_file)
    assert doc.masked_items_count > 0
    assert "890315-1928374" not in doc.raw_text

    engine = RulesEngine(contract_type="franchise")
    result = engine.analyze(doc)

    assert result.risk_summary.get("RED", 0) >= 3
    assert result.safety_score < 50

    detected_rules = [iss.rule_id for iss in result.detected_issues]
    assert "FRAN-001" in detected_rules  # 중도해지 위약금
    assert "FRAN-002" in detected_rules  # 필수품목 강제
    assert "FRAN-004" in detected_rules  # 인테리어 리뉴얼
    assert "FRAN-005" in detected_rules  # 영업지역 침해
    
    # 페이지 번호 검증 (2페이지 특약에 위치)
    for iss in result.detected_issues:
        assert iss.page == 2


def test_a4_html_report_generation():
    from core.exporter.html_report import generate_a4_html_report
    toxic_file = TESTS_DIR / "sample_contracts" / "sample_toxic_lease.txt"
    doc = parse_contract(toxic_file)
    engine = RulesEngine()
    analysis = engine.analyze(doc)
    checker = MissingChecker()
    missing_items = checker.check(doc)

    html_out = generate_a4_html_report(
        analysis=analysis,
        missing_items=missing_items,
        tenant_name="성수 베이커리 1호점",
        version_label="1차 초안 검토본"
    )

    assert "<!DOCTYPE html>" in html_out
    assert "상가건물 임대차 계약 사전 법률 진단 의견서" in html_out
    assert "성수 베이커리 1호점" in html_out
    assert "@page" in html_out
    assert "A4 portrait" in html_out
    assert "TOXIC-001" not in html_out or "원상회복" in html_out
    assert "window.print()" in html_out
