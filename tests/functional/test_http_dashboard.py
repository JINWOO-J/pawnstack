#!/usr/bin/env python3
"""
HTTP 대시보드 Sparkline 테스트 스크립트

개선된 대시보드 기능 테스트:
- 응답 시간 sparkline 히스토그램
- 상태 추이 sparkline
- 실시간 통계 업데이트
"""

import asyncio
import sys
import os
import time
from typing import List

# PawnStack 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text

from pawnstack.monitoring.http_monitor import HTTPMonitor, HTTPMonitorConfig


def create_test_configs() -> List[HTTPMonitorConfig]:
    """테스트용 HTTP 엔드포인트 설정 생성"""
    configs = [
        # 빠른 응답 (일반적으로 성공)
        HTTPMonitorConfig(
            url="https://httpbin.org/delay/0",
            name="httpbin-fast",
            interval=1.0,
            timeout=5.0,
            success_criteria=["status_code==200", "response_time<2.0"]
        ),
        
        # 중간 속도 응답
        HTTPMonitorConfig(
            url="https://httpbin.org/delay/1",
            name="httpbin-normal",
            interval=1.5,
            timeout=5.0,
            success_criteria=["status_code==200", "response_time<3.0"]
        ),
        
        # 느린 응답
        HTTPMonitorConfig(
            url="https://httpbin.org/delay/2",
            name="httpbin-slow",
            interval=2.0,
            timeout=5.0,
            success_criteria=["status_code==200", "response_time<5.0"]
        ),
        
        # 구글 (매우 빠름)
        HTTPMonitorConfig(
            url="https://www.google.com",
            name="Google",
            interval=1.0,
            timeout=5.0,
            success_criteria=["status_code==200", "response_time<1.0"]
        ),
        
        # GitHub API
        HTTPMonitorConfig(
            url="https://api.github.com",
            name="GitHub API",
            interval=1.5,
            timeout=5.0,
            success_criteria=["status_code==200"]
        ),
    ]
    
    return configs


async def test_dashboard_with_sparkline():
    """Sparkline이 포함된 대시보드 테스트"""
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🍀 HTTP 대시보드 Sparkline 테스트[/bold cyan]\n"
        "[yellow]응답 시간과 상태 추이를 시각화합니다[/yellow]",
        border_style="cyan"
    ))
    
    # HTTP 모니터 생성
    monitor = HTTPMonitor(console=console)
    
    # 테스트 엔드포인트 추가
    configs = create_test_configs()
    for config in configs:
        monitor.add_endpoint(config)
    
    console.print(f"\n✅ {len(configs)}개 엔드포인트 추가 완료")
    console.print("📊 대시보드를 시작합니다...")
    console.print("[dim]Ctrl+C를 눌러 종료하세요[/dim]\n")
    
    try:
        # 대시보드 모드로 모니터링 시작
        await monitor.start_monitoring(dashboard=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]모니터링이 중단되었습니다.[/yellow]")
    finally:
        await monitor.stop_monitoring()
        
        # 최종 통계 출력
        console.print("\n[bold cyan]📈 최종 통계[/bold cyan]")
        for name, stats in monitor.statistics.items():
            console.print(f"\n[cyan]{name}:[/cyan]")
            console.print(f"  총 요청: {stats['total_requests']}")
            console.print(f"  성공률: {stats['uptime_percentage']:.1f}%")
            console.print(f"  평균 응답시간: {stats['avg_response_time']:.3f}s")
            console.print(f"  최소/최대: {stats['min_response_time']:.3f}s / {stats['max_response_time']:.3f}s")


async def test_sparkline_visualization():
    """Sparkline 시각화 기능 단독 테스트"""
    console = Console()
    monitor = HTTPMonitor()
    
    console.print(Panel.fit(
        "[bold magenta]📊 Sparkline 시각화 테스트[/bold magenta]",
        border_style="magenta"
    ))
    
    # 테스트 데이터 생성
    test_data = [
        0.5, 0.7, 0.9, 1.2, 1.5, 1.8, 2.1, 2.5, 2.2, 1.9,
        1.6, 1.3, 1.0, 0.8, 0.6, 0.5, 0.4, 0.5, 0.7, 1.0,
        1.3, 1.6, 1.9, 2.2, 2.5, 2.3, 2.0, 1.7, 1.4, 1.1
    ]
    
    # Sparkline 생성
    sparkline = monitor.create_sparkline(test_data, width=40)
    console.print(f"\n응답 시간 Sparkline (30개 데이터 포인트):")
    console.print(f"  {sparkline}")
    console.print(f"  최소: {min(test_data):.1f}s | 최대: {max(test_data):.1f}s | 평균: {sum(test_data)/len(test_data):.1f}s")
    
    # 상태 sparkline 테스트
    status_data = [1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 
                   1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
    
    status_sparkline = monitor.create_status_sparkline(status_data, width=30)
    success_rate = (sum(status_data) / len(status_data)) * 100
    
    console.print(f"\n상태 추이 Sparkline (성공: 녹색 █, 실패: 빨간색 ▁):")
    console.print(f"  {status_sparkline}")
    console.print(f"  성공률: {success_rate:.1f}%")


async def test_command_line():
    """명령줄 실행 테스트"""
    console = Console()
    
    console.print(Panel.fit(
        "[bold green]🚀 명령줄 테스트[/bold green]\n"
        "실제 CLI 명령어 사용 예시",
        border_style="green"
    ))
    
    examples = [
        "# 기본 대시보드 모드",
        "python -m pawnstack.cli.main http https://httpbin.org/delay/1 --dashboard",
        "",
        "# 여러 URL 모니터링 (설정 파일 사용)",
        "python -m pawnstack.cli.main http -c http_config.ini --dashboard",
        "",
        "# 간격 조정",
        "python -m pawnstack.cli.main http https://api.github.com --dashboard --interval 2",
        "",
        "# 벤치마크 모드",
        "python -m pawnstack.cli.main http https://httpbin.org/get --benchmark --benchmark-requests 50",
        "",
        "# SSL 무시 옵션",
        "python -m pawnstack.cli.main http https://localhost:8443 --dashboard --ignore-ssl",
    ]
    
    for line in examples:
        if line.startswith("#"):
            console.print(f"[cyan]{line}[/cyan]")
        elif line:
            console.print(f"  [yellow]$ {line}[/yellow]")
        else:
            console.print()


async def main():
    """메인 함수"""
    console = Console()
    
    console.print("="*80)
    console.print("[bold cyan]🍀 PawnStack HTTP 대시보드 Sparkline 테스트[/bold cyan]")
    console.print("="*80)
    console.print()
    
    # 테스트 선택 메뉴
    console.print("[bold]테스트 옵션:[/bold]")
    console.print("  1. 대시보드 with Sparkline (실시간)")
    console.print("  2. Sparkline 시각화 테스트")
    console.print("  3. 명령줄 사용 예시")
    console.print("  4. 전체 테스트")
    console.print()
    console.print(f"[dim]사용법: python {sys.argv[0]} [1-4][/dim]")
    console.print()
    
    try:
        # 명령줄 인수로 선택 받기
        if len(sys.argv) > 1:
            choice = sys.argv[1]
        else:
            choice = "2"  # 기본값: Sparkline 시각화 테스트
        
        if choice == "1":
            await test_dashboard_with_sparkline()
        elif choice == "2":
            await test_sparkline_visualization()
        elif choice == "3":
            await test_command_line()
        elif choice == "4":
            # 전체 테스트
            await test_sparkline_visualization()
            console.print("\n" + "="*40 + "\n")
            await test_command_line()
            console.print("\n" + "="*40 + "\n")
            console.print("[yellow]이제 실시간 대시보드를 시작합니다...[/yellow]")
            await asyncio.sleep(2)
            await test_dashboard_with_sparkline()
        else:
            console.print("[red]잘못된 선택입니다.[/red]")
            return 1
            
    except KeyboardInterrupt:
        console.print("\n[yellow]테스트가 중단되었습니다.[/yellow]")
        return 0
    except Exception as e:
        console.print(f"\n[red]오류 발생: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1
    
    console.print("\n" + "="*80)
    console.print("[bold green]✨ 테스트 완료![/bold green]")
    console.print("="*80)
    console.print()
    console.print("[bold cyan]📊 개선된 기능:[/bold cyan]")
    console.print("  1. ✅ 응답 시간 Sparkline 히스토그램")
    console.print("  2. ✅ 상태 추이 시각화 (성공/실패)")
    console.print("  3. ✅ 실시간 통계 업데이트")
    console.print("  4. ✅ 색상 코딩 (녹색: 좋음, 노랑: 보통, 빨강: 나쁨)")
    console.print("  5. ✅ 최대 60개 데이터 포인트 히스토리")
    console.print()
    console.print("[bold yellow]💡 사용 팁:[/bold yellow]")
    console.print("  - 대시보드는 2초마다 자동 갱신됩니다")
    console.print("  - Sparkline은 최근 60개 데이터를 표시합니다")
    console.print("  - 응답 시간이 1초 미만이면 녹색, 2초 이상이면 빨간색으로 표시됩니다")
    console.print("  - 성공률이 99% 이상이면 녹색, 95% 미만이면 빨간색으로 표시됩니다")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))