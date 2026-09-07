"""
SafeLease AI - SQLite 기반 컨설팅 히스토리 관리자
외부 DB 설치 없이 단일 파일(safe_lease.db)로 히스토리와 메타데이터를 저장 및 조회합니다.
"""

import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional
from core.analyzer.rules_engine import AnalysisResult
from core.history.models import ConsultingSession, VersionSnapshot, IssueSnapshot
from config import DB_PATH


class HistoryManager:
    """컨설팅 히스토리 SQLite 관리자"""

    def __init__(self, db_path: Optional[Path | str] = None):
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """테이블 스키마 생성"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. 세션 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    tenant_name TEXT NOT NULL,
                    business_type TEXT NOT NULL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            # 2. 버전 스냅샷 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    version_id INTEGER NOT NULL,
                    version_label TEXT NOT NULL,
                    analyzed_at TIMESTAMP,
                    safety_score INTEGER NOT NULL,
                    risk_summary_json TEXT NOT NULL,
                    issues_json TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            conn.commit()

    def create_or_get_session(self, session_id: str, tenant_name: str, business_type: str = "일반상가") -> ConsultingSession:
        now = datetime.now()
        now_str = now.isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT session_id, tenant_name, business_type, created_at, updated_at FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO sessions (session_id, tenant_name, business_type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (session_id, tenant_name, business_type, now_str, now_str)
                )
                conn.commit()
        return self.get_session(session_id)

    def save_version(self, session_id: str, version_label: str, analysis: AnalysisResult) -> VersionSnapshot:
        """분석 결과를 새 버전 스냅샷으로 저장"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")

        next_version_id = len(session.versions) + 1
        now = datetime.now()
        now_str = now.isoformat()

        # 이슈 변환
        issues_data = [
            {
                "rule_id": iss.rule_id,
                "category": iss.category,
                "risk_level": iss.risk_level,
                "title": iss.title,
                "verbatim_quote": iss.verbatim_quote,
                "page": getattr(iss, "page", 1),
                "resolved": False
            }
            for iss in analysis.detected_issues
        ]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO versions (session_id, version_id, version_label, analyzed_at, safety_score, risk_summary_json, issues_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    next_version_id,
                    version_label,
                    now_str,
                    analysis.safety_score,
                    json.dumps(analysis.risk_summary, ensure_ascii=False),
                    json.dumps(issues_data, ensure_ascii=False)
                )
            )
            # 세션 갱신일 업데이트
            cursor.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now_str, session_id))
            conn.commit()

        return VersionSnapshot(
            version_id=next_version_id,
            version_label=version_label,
            analyzed_at=now,
            safety_score=analysis.safety_score,
            risk_summary=analysis.risk_summary,
            issues=[IssueSnapshot(**i) for i in issues_data]
        )

    def get_session(self, session_id: str) -> Optional[ConsultingSession]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT session_id, tenant_name, business_type, created_at, updated_at FROM sessions WHERE session_id = ?", (session_id,))
            s_row = cursor.fetchone()
            if not s_row:
                return None

            cursor.execute("SELECT version_id, version_label, analyzed_at, safety_score, risk_summary_json, issues_json FROM versions WHERE session_id = ? ORDER BY version_id ASC", (session_id,))
            v_rows = cursor.fetchall()

            versions = []
            for v in v_rows:
                v_id, v_label, v_at, v_score, v_summary_str, v_issues_str = v
                versions.append(VersionSnapshot(
                    version_id=v_id,
                    version_label=v_label,
                    analyzed_at=datetime.fromisoformat(v_at) if isinstance(v_at, str) else v_at,
                    safety_score=v_score,
                    risk_summary=json.loads(v_summary_str),
                    issues=[IssueSnapshot(**i) for i in json.loads(v_issues_str)]
                ))

            return ConsultingSession(
                session_id=s_row[0],
                tenant_name=s_row[1],
                business_type=s_row[2],
                created_at=datetime.fromisoformat(s_row[3]) if isinstance(s_row[3], str) else s_row[3],
                updated_at=datetime.fromisoformat(s_row[4]) if isinstance(s_row[4], str) else s_row[4],
                versions=versions
            )

    def list_sessions(self) -> List[ConsultingSession]:
        """전체 세션 목록 반환"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT session_id FROM sessions ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return [self.get_session(r[0]) for r in rows if r[0]]

    def delete_session(self, session_id: str) -> bool:
        """세션 및 해당 세션의 모든 버전 스냅샷 영구 삭제"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM versions WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0

    def prune_previous_versions(self, session_id: str) -> bool:
        """최종본(최신 버전)만 유지하고 이전 초안(1차, 2차) 버전 영구 삭제"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(version_id) FROM versions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row[0]:
                max_vid = row[0]
                cursor.execute("DELETE FROM versions WHERE session_id = ? AND version_id < ?", (session_id, max_vid))
                conn.commit()
                return True
            return False
