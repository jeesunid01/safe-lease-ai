"""
SafeLease AI - 대법원 판례 DB 모듈 검증 테스트
"""

from core.analyzer.precedent_matcher import PrecedentDB


def test_precedent_db_loading():
    db = PrecedentDB()
    all_precedents = db.get_all()
    assert len(all_precedents) >= 5

    # 1. 2017다268142 원상회복 판례 검색
    p1 = db.find_by_case_no("2017다268142")
    assert p1 is not None
    assert "원상회복" in p1.title or "원상복구" in p1.category
    assert "전 임차인" in p1.key_quote or "원상회복" in p1.key_quote

    # 2. 94다34692 대수선 판례 검색
    p2 = db.find_by_case_no("94다34692")
    assert p2 is not None
    assert "수선의무" in p2.title or "시설수선" in p2.category

    # 3. 키워드 검색
    results = db.search("권리금")
    assert len(results) >= 1
    assert any("2020다277028" in r.case_no for r in results)
