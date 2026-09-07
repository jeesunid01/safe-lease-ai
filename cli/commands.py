"""
SafeLease AI - CLI 서브커맨드 구현 모듈
"""

from pathlib import Path
from core.parser import parse_contract
from core.analyzer.rules_engine import RulesEngine
from core.analyzer.missing_checker import MissingChecker
from core.exporter.console_view import render_analysis_result, print_banner
from core.exporter.markdown_report import generate_markdown_report, save_markdown_report
from core.history.history_manager import HistoryManager
from core.history.diff_analyzer import DiffAnalyzer
from rich.console import Console
from rich.table import Table

console = Console()


def run_analyze(file_path: str, output: str = None, session_id: str = None, tenant_name: str = None, label: str = "초안", contract_type: str = "all"):
    """계약서 독소조항 분석 실행"""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]오류: 파일을 찾을 수 없습니다: {file_path}[/bold red]")
        return

    # 1. 파싱 & 마스킹
    doc = parse_contract(path)

    # 2. 분석
    engine = RulesEngine(contract_type=contract_type)
    analysis = engine.analyze(doc)

    # 3. 필수 누락 조항 점검
    checker = MissingChecker()
    missing_items = checker.check(doc)

    # 4. 터미널 신호등 출력
    render_analysis_result(analysis, missing_items)

    # 5. 파일 저장 요청 시 마크다운 리포트 저장
    if output:
        md_content = generate_markdown_report(analysis, missing_items)
        save_markdown_report(md_content, output)
        console.print(f"[bold green]📄 마크다운 리포트가 저장되었습니다: {output}[/bold green]")

    # 6. 히스토리 세션 저장 (지정된 경우)
    if session_id and tenant_name:
        mgr = HistoryManager()
        mgr.create_or_get_session(session_id, tenant_name)
        mgr.save_version(session_id, label, analysis)
        console.print(f"[dim]💾 컨설팅 히스토리에 '{label}'(으)로 저장되었습니다. (Session: {session_id})[/dim]")


def run_check_missing(file_path: str):
    """필수 누락 조항만 집중 점검"""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]오류: 파일을 찾을 수 없습니다: {file_path}[/bold red]")
        return

    doc = parse_contract(path)
    checker = MissingChecker()
    items = checker.check(doc)

    print_banner()
    console.print(f"\n[bold]대상 파일:[/bold] {doc.filename}")
    table = Table(title="📋 필수 보호 특약 누락 검사 결과", header_style="bold cyan")
    table.add_column("상태", width=10)
    table.add_column("항목", width=20)
    table.add_column("누락 시 위험", width=35)
    table.add_column("추천 보완 특약", width=35)

    for item in items:
        status = "[bold red]❌ 누락[/bold red]" if item.is_missing else "[bold green]✅ 기재됨[/bold green]"
        table.add_row(status, item.title, item.why_important, item.recommended_clause)

    console.print(table)


def run_history_list():
    """저장된 컨설팅 히스토리 목록 조회"""
    mgr = HistoryManager()
    sessions = mgr.list_sessions()

    print_banner()
    if not sessions:
        console.print("[yellow]저장된 컨설팅 히스토리가 없습니다.[/yellow]")
        return

    table = Table(title="📁 저장된 컨설팅 히스토리 목록", header_style="bold blue")
    table.add_column("세션 ID", width=18)
    table.add_column("상호/의뢰인", width=15)
    table.add_column("업종", width=12)
    table.add_column("버전 수", width=8)
    table.add_column("최신 안전점수", width=12)
    table.add_column("최근 갱신일", width=18)

    for s in sessions:
        latest_score = f"{s.versions[-1].safety_score}점" if s.versions else "-"
        table.add_row(
            s.session_id,
            s.tenant_name,
            s.business_type,
            f"{len(s.versions)}개",
            latest_score,
            s.updated_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)


def run_history_diff(session_id: str, v1: int = 1, v2: int = 2):
    """계약서 초안과 수정본 간 Diff 비교"""
    mgr = HistoryManager()
    session = mgr.get_session(session_id)
    if not session:
        console.print(f"[bold red]세션을 찾을 수 없습니다: {session_id}[/bold red]")
        return

    try:
        diff = DiffAnalyzer.compare_versions(session, v1, v2)
    except Exception as e:
        console.print(f"[bold red]비교 오류: {e}[/bold red]")
        return

    print_banner()
    console.print(f"[bold cyan]🔍 [{session.tenant_name}] 계약서 버전 비교 (v{v1} ➔ v{v2})[/bold cyan]\n")
    console.print(f"📊 안전 점수 변화: [bold]{diff.score_change:+d}점[/bold]")
    console.print(f"💬 총평: {diff.summary_message}\n")

    table = Table(title="독소조항 해결 및 변경 내역", header_style="bold magenta")
    table.add_column("조항", width=25)
    table.add_column("상태", width=14)
    table.add_column("상세 내용", width=50)

    for item in diff.diff_items:
        if item.status == "RESOLVED":
            status = "[bold green]✅ 해결 완료[/bold green]"
        elif item.status == "PERSISTENT":
            status = "[bold red]⚠️ 미해결[/bold red]"
        else:
            status = "[bold yellow]🚨 신규 위험[/bold yellow]"

        table.add_row(item.title, status, item.comment)

    console.print(table)
