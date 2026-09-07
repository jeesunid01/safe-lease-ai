"""
SafeLease AI - CLI 메인 진입점
"""

import sys
from pathlib import Path

# workspace 루트를 sys.path에 등록하여 직접 실행(python cli/main.py) 지원
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import argparse
from cli.commands import (
    run_analyze,
    run_check_missing,
    run_history_list,
    run_history_diff
)


def main():
    parser = argparse.ArgumentParser(
        prog="safe-lease",
        description="SafeLease AI - 소상공인 상가/가맹 계약서 독소조항 검토 & 협상 비서"
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="실행할 서브커맨드")

    # 1. analyze 커맨드
    analyze_parser = subparsers.add_parser("analyze", help="계약서 독소조항 종합 분석 및 협상 가이드 출력")
    analyze_parser.add_argument("--file", "-f", required=True, help="분석할 계약서 파일 경로 (PDF, TXT, DOCX, HWP, 이미지)")
    analyze_parser.add_argument("--contract-type", "-c", choices=["all", "lease", "franchise"], default="all", help="계약서 유형 (기본: all, lease: 상가임대차, franchise: 가맹계약)")
    analyze_parser.add_argument("--output", "-o", help="결과를 저장할 마크다운 파일 경로 (예: report.md)")
    analyze_parser.add_argument("--session", "-s", help="저장할 컨설팅 세션 ID")
    analyze_parser.add_argument("--tenant", "-t", help="의뢰인 상호명")
    analyze_parser.add_argument("--label", "-l", default="초안", help="버전 라벨 (예: 1차 초안, 2차 수정본)")

    # 2. check-missing 커맨드
    missing_parser = subparsers.add_parser("check-missing", help="계약서 내 필수 보호 특약 누락 집중 검사")
    missing_parser.add_argument("--file", "-f", required=True, help="검사할 계약서 파일 경로")

    # 3. history 커맨드
    history_parser = subparsers.add_parser("history", help="컨설팅 히스토리 관리")
    history_sub = history_parser.add_subparsers(dest="history_action", help="히스토리 작업")

    # history list
    history_sub.add_parser("list", help="저장된 컨설팅 세션 목록 조회")

    # history diff
    diff_parser = history_sub.add_parser("diff", help="계약서 초안과 수정본 간 변경점 비교")
    diff_parser.add_argument("--session", "-s", required=True, help="비교할 세션 ID")
    diff_parser.add_argument("--v1", type=int, default=1, help="기준 버전 번호 (기본값: 1)")
    diff_parser.add_argument("--v2", type=int, default=2, help="비교 대상 버전 번호 (기본값: 2)")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "analyze":
        run_analyze(
            file_path=args.file,
            output=args.output,
            session_id=args.session,
            tenant_name=args.tenant,
            label=args.label,
            contract_type=args.contract_type
        )
    elif args.subcommand == "check-missing":
        run_check_missing(file_path=args.file)
    elif args.subcommand == "history":
        if args.history_action == "list":
            run_history_list()
        elif args.history_action == "diff":
            run_history_diff(session_id=args.session, v1=args.v1, v2=args.v2)
        else:
            history_parser.print_help()


if __name__ == "__main__":
    main()
