"""
SafeLease AI - 컨설팅 히스토리 및 Diff 비교 검증 테스트
"""

from pathlib import Path
from core.parser import parse_contract
from core.analyzer.rules_engine import RulesEngine
from core.history.history_manager import HistoryManager
from core.history.diff_analyzer import DiffAnalyzer
from config import TESTS_DIR, HISTORY_DIR


def test_history_and_diff():
    db_test_path = HISTORY_DIR / "test_history.db"
    if db_test_path.exists():
        db_test_path.unlink()

    history_mgr = HistoryManager(db_path=db_test_path)
    session_id = "test-cafe-session"
    history_mgr.create_or_get_session(session_id, "테스트 카페", "카페/베이커리")

    toxic_file = TESTS_DIR / "sample_contracts" / "sample_toxic_lease.txt"
    normal_file = TESTS_DIR / "sample_contracts" / "sample_normal_lease.txt"

    engine = RulesEngine()

    # 1. 1차 초안(독소조항 가득) 저장
    doc_v1 = parse_contract(toxic_file)
    analysis_v1 = engine.analyze(doc_v1)
    v1 = history_mgr.save_version(session_id, "1차 초안", analysis_v1)
    assert v1.version_id == 1
    assert v1.safety_score < 60

    # 2. 2차 수정본(독소조항 해소) 저장
    doc_v2 = parse_contract(normal_file)
    analysis_v2 = engine.analyze(doc_v2)
    v2 = history_mgr.save_version(session_id, "2차 협상 수정본", analysis_v2)
    assert v2.version_id == 2
    assert v2.safety_score >= 90

    # 3. Diff 비교 검증
    session = history_mgr.get_session(session_id)
    diff = DiffAnalyzer.compare_versions(session, 1, 2)

    assert diff.score_change > 0
    resolved_items = [d for d in diff.diff_items if d.status == "RESOLVED"]
    assert len(resolved_items) >= 2

    # 4. 버전 가지치기 (최종본만 남기기) 검증
    history_mgr.prune_previous_versions(session_id)
    session_pruned = history_mgr.get_session(session_id)
    assert len(session_pruned.versions) == 1
    assert session_pruned.versions[0].version_id == 2

    # 5. 세션 영구 삭제 검증
    history_mgr.delete_session(session_id)
    assert history_mgr.get_session(session_id) is None

    # 뒷정리
    if db_test_path.exists():
        db_test_path.unlink()
