"""
SafeLease AI - CLI 터미널 컬러 신호등 리포트 뷰어
Rich 라이브러리를 활용하여 직관적인 신호등 색상과 협상 대안 카드를 터미널에 렌더링합니다.
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from core.analyzer.rules_engine import AnalysisResult, DetectedIssue
from core.analyzer.missing_checker import MissingCheckItem

console = Console(legacy_windows=False)


def print_banner():
    """상단 로고 배너 출력"""
    console.print(Panel(
        "[bold cyan]🛡️ SafeLease AI (안심계약 AI)[/bold cyan]\n"
        "[dim]소상공인·자영업자 30초 계약서 독소조항 검토 & 완곡한 협상 비서[/dim]",
        border_style="cyan"
    ))


def render_analysis_result(analysis: AnalysisResult, missing_items: list[MissingCheckItem] = None):
    """분석 결과를 터미널에 컬러 신호등으로 출력"""
    print_banner()

    # 1. 종합 안전 점수 카드
    score = analysis.safety_score
    if score >= 80:
        score_color = "green"
        score_icon = "🟢 안전"
    elif score >= 50:
        score_color = "yellow"
        score_icon = "🟡 주의"
    else:
        score_color = "red"
        score_icon = "🔴 위험"

    summary_text = (
        f"[bold]계약서 파일:[/bold] {analysis.document_name}\n"
        f"[bold]전체 조항 수:[/bold] {analysis.total_clauses}개\n"
        f"[bold]종합 안전 지수:[/bold] [{score_color} bold]{score}점 ({score_icon})[/{score_color} bold]\n"
        f"[dim]위험(RED): {analysis.risk_summary.get('RED', 0)}건 | 주의(YELLOW): {analysis.risk_summary.get('YELLOW', 0)}건[/dim]"
    )
    console.print(Panel(summary_text, title="📊 계약서 종합 진단 결과", border_style=score_color))

    # 2. 발견된 독소조항 카드 리스트
    if not analysis.detected_issues:
        console.print(Panel("[bold green]🎉 축하합니다! 검토 결과 명백한 독소조항이 발견되지 않았습니다.[/bold green]", border_style="green"))
    else:
        console.print("\n[bold red]🚨 발견된 주의 조항 및 부드러운 협상 가이드[/bold red]")
        for idx, issue in enumerate(analysis.detected_issues, 1):
            border = "red" if issue.risk_level == "RED" else "yellow"
            badge = "[bold red]🔴 조율 필요[/bold red]" if issue.risk_level == "RED" else "[bold yellow]🟡 주의 권장[/bold yellow]"

            content = (
                f"{badge} [bold white]{issue.title}[/bold white] (위치: {issue.page}페이지 • {issue.matched_clause_no or '특약'})\n\n"
                f"[bold cyan]🔍 계약서 원문 발췌 (제{issue.page}쪽):[/bold cyan]\n[dim]\"{issue.verbatim_quote}\"[/dim]\n\n"
                f"[bold red]⚠️ 불리한 이유:[/bold red] {issue.danger_explanation}\n"
                f"[bold magenta]📜 법적 근거:[/bold magenta] {issue.legal_basis}\n\n"
                f"[bold green]✨ 추천 대체 조항:[/bold green]\n{issue.recommended_replacement}\n\n"
                f"[bold yellow]💬 건물주 전송용 협상 멘트 (복사해서 쓰세요):[/bold yellow]\n\"{issue.nudge_script_polite}\""
            )
            console.print(Panel(content, title=f"이슈 #{idx} [{issue.category}]", border_style=border))

    # 3. 필수 누락 조항 점검
    if missing_items:
        missing_list = [m for m in missing_items if m.is_missing]
        if missing_list:
            console.print("\n[bold yellow]⚠️ 빠져있어 분쟁이 우려되는 필수 특약 (누락 체크)[/bold yellow]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("항목", width=16)
            table.add_column("누락 시 위험", width=35)
            table.add_column("추천 보완 특약", width=35)

            for m in missing_list:
                table.add_row(m.title, m.why_important, m.recommended_clause)
            console.print(table)

    # 4. 법적 면책 고지
    console.print("\n[dim]⚖️ [Legal Disclaimer] 본 결과는 공개된 정부 표준계약서 및 대법원 판례와의 기계적 대조 참고자료이며, 변호사법상 개별 법률 자문이 아닙니다.[/dim]\n")
