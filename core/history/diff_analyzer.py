"""
SafeLease AI - 계약서 버전 간 전/후 비교(Diff) 분석기
1차 초안과 2차 수정본 간의 독소조항 해결 여부 및 안전 점수 개선율을 산출합니다.
"""

from core.history.models import ConsultingSession, VersionDiffResult, DiffItem


class DiffAnalyzer:
    """계약서 버전 간 비교 분석기"""

    @staticmethod
    def compare_versions(session: ConsultingSession, base_v_id: int, compare_v_id: int) -> VersionDiffResult:
        v_map = {v.version_id: v for v in session.versions}
        base_v = v_map.get(base_v_id)
        comp_v = v_map.get(compare_v_id)

        if not base_v or not comp_v:
            raise ValueError("비교할 버전이 세션에 존재하지 않습니다.")

        diff_items = []
        base_issues_map = {iss.rule_id: iss for iss in base_v.issues}
        comp_issues_map = {iss.rule_id: iss for iss in comp_v.issues}

        # 1. 이전 버전 이슈 점검 (해결되었거나 여전히 존속)
        for rule_id, old_iss in base_issues_map.items():
            if rule_id not in comp_issues_map:
                # 해결됨!
                diff_items.append(DiffItem(
                    rule_id=rule_id,
                    title=old_iss.title,
                    status="RESOLVED",
                    old_risk=old_iss.risk_level,
                    new_risk=None,
                    comment="수정본에서 해당 독소조항이 성공적으로 삭제/완화되었습니다! 🎉",
                    old_quote=getattr(old_iss, "verbatim_quote", None),
                    new_quote=None
                ))
            else:
                new_iss = comp_issues_map[rule_id]
                diff_items.append(DiffItem(
                    rule_id=rule_id,
                    title=old_iss.title,
                    status="PERSISTENT",
                    old_risk=old_iss.risk_level,
                    new_risk=new_iss.risk_level,
                    comment="아직 수정본에 해당 독소조항이 그대로 남아있어 추가 조율이 필요합니다.",
                    old_quote=getattr(old_iss, "verbatim_quote", None),
                    new_quote=getattr(new_iss, "verbatim_quote", None)
                ))

        # 2. 새 버전에 새로 추가된 이슈 점검 (건물주가 다른 조항을 기습 변경/추가한 경우!)
        for rule_id, new_iss in comp_issues_map.items():
            if rule_id not in base_issues_map:
                diff_items.append(DiffItem(
                    rule_id=rule_id,
                    title=new_iss.title,
                    status="NEW",
                    old_risk=None,
                    new_risk=new_iss.risk_level,
                    comment="수정본에서 새로 발견된 불리한 특약입니다! 다른 조항이 기습적으로 변경/추가되었는지 확인하세요.",
                    old_quote=None,
                    new_quote=getattr(new_iss, "verbatim_quote", None)
                ))

        score_change = comp_v.safety_score - base_v.safety_score
        resolved_count = sum(1 for d in diff_items if d.status == "RESOLVED")

        if score_change > 0:
            summary = f"축하합니다! 이전 초안 대비 독소조항 {resolved_count}건이 해결되어 안전 점수가 {score_change}점 대폭 상승했습니다."
        elif score_change == 0:
            summary = "이전 버전과 비교하여 위험도에 큰 변동이 없습니다."
        else:
            summary = f"주의: 새로운 위험 조항이 유입되어 안전 점수가 {abs(score_change)}점 하락했습니다."

        return VersionDiffResult(
            session_id=session.session_id,
            base_version_id=base_v_id,
            compare_version_id=compare_v_id,
            score_change=score_change,
            diff_items=diff_items,
            summary_message=summary
        )
