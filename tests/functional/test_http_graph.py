#!/usr/bin/env python3
"""
HTTP 모니터링 그래프 너비 테스트 스크립트
그래프가 터미널 너비에 맞게 제대로 확장되는지 테스트합니다.
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import random
import time

# PawnStack 모듈 임포트
from pawnstack.monitoring.http_monitor import HTTPMonitor, HTTPMonitorConfig


def generate_test_data(count: int = 50):
    """테스트용 응답 시간 데이터 생성"""
    data = []
    for i in range(count):
        # 다양한 패턴의 응답 시간 생성
        base = 0.5 + (i % 10) * 0.1
        noise = random.uniform(-0.2, 0.5)
        spike = 3.0 if i % 15 == 0 else 0  # 주기적인 스파이크
        data.append(max(0.1, base + noise + spike))
    return data


def test_graph_widths():
    """다양한 너비로 그래프 테스트"""
    console = Console()
    monitor = HTTPMonitor(console)
    
    # 테스트 데이터 생성
    test_data = generate_test_data(30)
    
    print("\n" + "=" * 100)
    print("HTTP Monitor Graph Width Test")
    print("=" * 100)
    
    # 터미널 너비 확인
    terminal_width = console.width
    print(f"\n터미널 너비: {terminal_width}")
    print(f"예상 그래프 너비: {int(terminal_width * 0.8)}")
    print("-" * terminal_width)
    
    # 다양한 너비로 테스트
    test_widths = [40, 60, 80, 100, 120]
    
    for width in test_widths:
        if width > terminal_width:
            continue
            
        print(f"\n\n{'='*width}")
        print(f"테스트 너비: {width}")
        print(f"{'='*width}")
        
        # ASCII 그래프 테스트
        print("\n[ASCII Graph]")
        ascii_graph = monitor.create_ascii_graph(
            test_data, 
            width=width, 
            height=8,
            label=f"Response Time (Width={width})"
        )
        print(ascii_graph)
        
        # Sparkline 테스트
        print("\n[Sparkline]")
        sparkline = monitor.create_sparkline(test_data, width=width)
        # Rich 마크업 제거하여 실제 길이 확인
        import re
        clean_sparkline = re.sub(r'\[.*?\]', '', sparkline)
        print(f"Sparkline ({len(clean_sparkline)} chars): {sparkline}")
        
        # 상태 바 그래프 테스트
        print("\n[Status Bar Graph]")
        status_data = [1 if random.random() > 0.1 else 0 for _ in range(30)]
        status_graph = monitor.create_status_bar_graph(
            status_data,
            width=width,
            height=4
        )
        print(status_graph)
        
        print(f"\n{'─'*width}")


async def test_live_monitoring():
    """실시간 모니터링 대시보드 테스트"""
    console = Console()
    
    # 가상의 엔드포인트 설정
    config = HTTPMonitorConfig(
        url="https://test.example.com/api",
        name="Test API",
        interval=1.0
    )
    
    monitor = HTTPMonitor(console)
    monitor.add_endpoint(config)
    
    # 테스트 데이터로 히스토리 채우기
    monitor.response_time_history[config.name] = generate_test_data(50)
    monitor.status_history[config.name] = [1 if random.random() > 0.05 else 0 for _ in range(50)]
    
    # 통계 데이터 설정
    monitor.statistics[config.name] = {
        'total_requests': 50,
        'successful_requests': 47,
        'failed_requests': 3,
        'uptime_percentage': 94.0,
        'avg_response_time': 0.85,
        'min_response_time': 0.12,
        'max_response_time': 3.45
    }
    
    # 터미널 너비 정보
    terminal_width = console.width
    graph_width = max(60, min(int(terminal_width * 0.8), 200))
    
    print("\n" + "=" * terminal_width)
    print(f"Live Dashboard Test - Terminal Width: {terminal_width}, Graph Width: {graph_width}")
    print("=" * terminal_width)
    
    # sparkline 패널 생성
    panel_content = monitor._create_sparkline_panel()
    
    # 패널 출력
    panel = Panel(
        Text.from_markup(panel_content),
        title="[bold cyan]📈 Performance Graphs Test[/bold cyan]",
        border_style="cyan"
    )
    
    console.print(panel)
    
    # 레이아웃 테스트
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", size=12),
        Layout(name="graphs", ratio=3),
        Layout(name="footer", size=2)
    )
    
    layout["header"].update(Panel("HTTP Monitor Dashboard Test", style="blue"))
    layout["main"].update(Panel("Main Content Area", style="green"))
    layout["graphs"].update(Panel(Text.from_markup(panel_content), title="Performance Graphs", border_style="cyan"))
    layout["footer"].update(Panel("Footer", style="dim"))
    
    print("\n[Layout Test]")
    console.print(layout)


def main():
    """메인 테스트 함수"""
    print("\n🚀 PawnStack HTTP Monitor Graph Width Test")
    
    # 1. 정적 그래프 너비 테스트
    test_graph_widths()
    
    # 2. 대시보드 모니터링 테스트
    print("\n\n" + "=" * 100)
    print("Testing Live Dashboard...")
    print("=" * 100)
    
    asyncio.run(test_live_monitoring())
    
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    main()