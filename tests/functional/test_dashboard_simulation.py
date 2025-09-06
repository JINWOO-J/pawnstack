#!/usr/bin/env python3
"""
HTTP 대시보드 시뮬레이션 테스트

실제 HTTP 요청 없이 대시보드 기능을 시뮬레이션합니다.
Sparkline 히스토그램과 실시간 업데이트를 테스트합니다.
"""

import asyncio
import sys
import os
import random
import time
from datetime import datetime
from collections import deque
from typing import List, Dict, Any

# PawnStack 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich import box


class MockHTTPMonitor:
    """대시보드 시뮬레이션을 위한 모의 HTTP 모니터"""
    
    def __init__(self):
        self.console = Console()
        self.endpoints = [
            {"name": "API Gateway", "url": "https://api.example.com/health", "base_time": 0.3},
            {"name": "Database API", "url": "https://db.example.com/status", "base_time": 0.5},
            {"name": "Auth Service", "url": "https://auth.example.com/ping", "base_time": 0.2},
            {"name": "Storage Service", "url": "https://storage.example.com/health", "base_time": 0.8},
            {"name": "Analytics API", "url": "https://analytics.example.com/status", "base_time": 1.2},
        ]
        
        # 각 엔드포인트별 히스토리
        self.response_times = {ep["name"]: deque(maxlen=60) for ep in self.endpoints}
        self.status_history = {ep["name"]: deque(maxlen=60) for ep in self.endpoints}
        self.statistics = {ep["name"]: {
            "total": 0,
            "success": 0,
            "failed": 0,
            "avg_time": 0,
            "min_time": float('inf'),
            "max_time": 0,
            "last_check": None
        } for ep in self.endpoints}
    
    def simulate_response(self, endpoint: Dict) -> Dict[str, Any]:
        """HTTP 응답 시뮬레이션"""
        # 랜덤 응답 시간 생성 (기본 시간에 변동 추가)
        base_time = endpoint["base_time"]
        variation = random.uniform(-0.3, 0.5)
        response_time = max(0.1, base_time + variation)
        
        # 가끔 실패 시뮬레이션 (5% 확률)
        if random.random() < 0.05:
            success = False
            status_code = random.choice([500, 503, 404])
        # 가끔 느린 응답 (10% 확률)
        elif random.random() < 0.1:
            response_time = base_time * 3
            success = response_time < 3.0  # 3초 이하면 성공
            status_code = 200
        else:
            success = True
            status_code = 200
        
        return {
            "response_time": response_time,
            "success": success,
            "status_code": status_code,
            "timestamp": datetime.now()
        }
    
    def update_statistics(self, name: str, response: Dict):
        """통계 업데이트"""
        stats = self.statistics[name]
        stats["total"] += 1
        stats["last_check"] = response["timestamp"]
        
        if response["success"]:
            stats["success"] += 1
        else:
            stats["failed"] += 1
        
        # 응답 시간 통계
        rt = response["response_time"]
        stats["min_time"] = min(stats["min_time"], rt)
        stats["max_time"] = max(stats["max_time"], rt)
        
        # 평균 계산
        times = list(self.response_times[name])
        if times:
            stats["avg_time"] = sum(times) / len(times)
    
    def create_sparkline(self, data: List[float], width: int = 40) -> str:
        """Sparkline 생성"""
        if not data or len(data) < 2:
            return "▁" * width
        
        blocks = " ▁▂▃▄▅▆▇█"
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val > min_val else 1
        
        # 리샘플링
        if len(data) > width:
            step = len(data) / width
            sampled = [data[int(i * step)] for i in range(width)]
        else:
            sampled = list(data) + [data[-1]] * (width - len(data))
        
        sparkline = ""
        for val in sampled:
            normalized = (val - min_val) / range_val if range_val > 0 else 0
            idx = int(normalized * (len(blocks) - 1))
            sparkline += blocks[idx]
        
        return sparkline
    
    def create_status_sparkline(self, data: List[int], width: int = 40) -> str:
        """상태 sparkline 생성"""
        if not data:
            return "[dim]" + "▁" * width + "[/dim]"
        
        # 리샘플링
        if len(data) > width:
            step = len(data) / width
            sampled = [data[int(i * step)] for i in range(width)]
        else:
            sampled = list(data) + [1] * (width - len(data))
        
        sparkline = ""
        for status in sampled:
            if status == 1:
                sparkline += "[green]█[/green]"
            else:
                sparkline += "[red]▁[/red]"
        
        return sparkline
    
    def create_dashboard_layout(self) -> Layout:
        """대시보드 레이아웃 생성"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=2),
            Layout(name="sparklines", size=15),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="endpoints"),
            Layout(name="statistics")
        )
        
        return layout
    
    def update_dashboard(self, layout: Layout):
        """대시보드 업데이트"""
        # 헤더
        layout["header"].update(
            Panel(
                f"[bold cyan]🍀 HTTP Monitoring Dashboard with Sparklines[/bold cyan] | "
                f"Time: {datetime.now().strftime('%H:%M:%S')} | "
                f"Endpoints: {len(self.endpoints)}",
                style="cyan"
            )
        )
        
        # 엔드포인트 상태 테이블
        endpoints_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        endpoints_table.add_column("Name", style="cyan", width=20)
        endpoints_table.add_column("Status", justify="center", width=10)
        endpoints_table.add_column("Response", justify="right", width=12)
        endpoints_table.add_column("Last Check", justify="center", width=10)
        
        for endpoint in self.endpoints:
            name = endpoint["name"]
            stats = self.statistics[name]
            
            if stats["last_check"]:
                times = list(self.response_times[name])
                if times:
                    latest = times[-1]
                    statuses = list(self.status_history[name])
                    if statuses and statuses[-1] == 1:
                        status = "[green]✅ OK[/green]"
                    else:
                        status = "[red]❌ FAIL[/red]"
                    
                    if latest < 1.0:
                        time_str = f"[green]{latest:.3f}s[/green]"
                    elif latest < 2.0:
                        time_str = f"[yellow]{latest:.3f}s[/yellow]"
                    else:
                        time_str = f"[red]{latest:.3f}s[/red]"
                    
                    last_check = stats["last_check"].strftime("%H:%M:%S")
                else:
                    status = "[dim]Waiting[/dim]"
                    time_str = "-"
                    last_check = "-"
            else:
                status = "[dim]Waiting[/dim]"
                time_str = "-"
                last_check = "-"
            
            endpoints_table.add_row(name, status, time_str, last_check)
        
        layout["endpoints"].update(Panel(endpoints_table, title="Endpoint Status"))
        
        # 통계 테이블
        stats_table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        stats_table.add_column("Endpoint", style="cyan", width=20)
        stats_table.add_column("Total", justify="right", width=8)
        stats_table.add_column("Success", justify="right", width=10)
        stats_table.add_column("Avg Time", justify="right", width=10)
        
        for endpoint in self.endpoints:
            name = endpoint["name"]
            stats = self.statistics[name]
            
            if stats["total"] > 0:
                success_rate = (stats["success"] / stats["total"]) * 100
                if success_rate >= 99:
                    rate_str = f"[green]{success_rate:.1f}%[/green]"
                elif success_rate >= 95:
                    rate_str = f"[yellow]{success_rate:.1f}%[/yellow]"
                else:
                    rate_str = f"[red]{success_rate:.1f}%[/red]"
                
                if stats["avg_time"] < 1.0:
                    avg_str = f"[green]{stats['avg_time']:.3f}s[/green]"
                else:
                    avg_str = f"[yellow]{stats['avg_time']:.3f}s[/yellow]"
                
                stats_table.add_row(
                    name,
                    str(stats["total"]),
                    rate_str,
                    avg_str
                )
        
        layout["statistics"].update(Panel(stats_table, title="Statistics"))
        
        # Sparklines 패널
        sparkline_lines = []
        for endpoint in self.endpoints:
            name = endpoint["name"]
            times = list(self.response_times[name])
            statuses = list(self.status_history[name])
            
            sparkline_lines.append(f"[bold cyan]{name}[/bold cyan]")
            
            if times:
                time_spark = self.create_sparkline(times, width=50)
                sparkline_lines.append(f"  Response: {time_spark}")
                
                latest = times[-1] if times else 0
                avg = sum(times) / len(times) if times else 0
                min_val = min(times) if times else 0
                max_val = max(times) if times else 0
                
                sparkline_lines.append(
                    f"  [dim]Current: {latest:.3f}s | Avg: {avg:.3f}s | "
                    f"Min: {min_val:.3f}s | Max: {max_val:.3f}s[/dim]"
                )
            
            if statuses:
                status_spark = self.create_status_sparkline(statuses, width=50)
                sparkline_lines.append(f"  Status:   {status_spark}")
                
                success_rate = (sum(statuses) / len(statuses)) * 100 if statuses else 0
                sparkline_lines.append(f"  [dim]Success Rate: {success_rate:.1f}%[/dim]")
            
            sparkline_lines.append("")
        
        sparkline_text = "\n".join(sparkline_lines) if sparkline_lines else "Collecting data..."
        layout["sparklines"].update(Panel(Text.from_markup(sparkline_text), title="Response Time Trends"))
        
        # 푸터
        layout["footer"].update(
            Panel(
                "[dim]Press Ctrl+C to stop monitoring | Sparklines show last 60 data points[/dim]",
                style="dim"
            )
        )
    
    async def run_simulation(self, duration: int = 30):
        """시뮬레이션 실행"""
        self.console.print(Panel.fit(
            "[bold cyan]🍀 Starting HTTP Dashboard Simulation[/bold cyan]\n"
            f"[yellow]Running for {duration} seconds with sparkline visualization[/yellow]",
            border_style="cyan"
        ))
        
        layout = self.create_dashboard_layout()
        
        with Live(layout, refresh_per_second=2, screen=True) as live:
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    # 각 엔드포인트에 대해 시뮬레이션 실행
                    for endpoint in self.endpoints:
                        # 랜덤하게 일부 엔드포인트만 업데이트 (실제 상황 시뮬레이션)
                        if random.random() < 0.7:  # 70% 확률로 업데이트
                            response = self.simulate_response(endpoint)
                            name = endpoint["name"]
                            
                            # 히스토리 업데이트
                            self.response_times[name].append(response["response_time"])
                            self.status_history[name].append(1 if response["success"] else 0)
                            
                            # 통계 업데이트
                            self.update_statistics(name, response)
                    
                    # 대시보드 업데이트
                    self.update_dashboard(layout)
                    
                    await asyncio.sleep(0.5)
                
                except KeyboardInterrupt:
                    break
        
        # 최종 통계 출력
        self.console.print("\n[bold cyan]📊 Final Statistics:[/bold cyan]")
        for endpoint in self.endpoints:
            name = endpoint["name"]
            stats = self.statistics[name]
            if stats["total"] > 0:
                success_rate = (stats["success"] / stats["total"]) * 100
                self.console.print(f"\n[cyan]{name}:[/cyan]")
                self.console.print(f"  Total Requests: {stats['total']}")
                self.console.print(f"  Success Rate: {success_rate:.1f}%")
                self.console.print(f"  Avg Response: {stats['avg_time']:.3f}s")
                self.console.print(f"  Min/Max: {stats['min_time']:.3f}s / {stats['max_time']:.3f}s")


async def main():
    """메인 함수"""
    console = Console()
    
    console.print("="*80)
    console.print("[bold cyan]🍀 HTTP Dashboard Simulation Test[/bold cyan]")
    console.print("="*80)
    console.print()
    
    # 시뮬레이션 시간 설정
    duration = 20  # 20초 동안 실행
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            console.print(f"[yellow]Invalid duration, using default: {duration} seconds[/yellow]")
    
    console.print(f"[green]Simulation will run for {duration} seconds[/green]")
    console.print("[dim]Sparklines will show response time trends and status history[/dim]\n")
    
    # 모의 모니터 생성 및 실행
    monitor = MockHTTPMonitor()
    
    try:
        await monitor.run_simulation(duration)
    except KeyboardInterrupt:
        console.print("\n[yellow]Simulation interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1
    
    console.print("\n" + "="*80)
    console.print("[bold green]✨ Simulation Complete![/bold green]")
    console.print("="*80)
    console.print()
    console.print("[bold cyan]Key Features Demonstrated:[/bold cyan]")
    console.print("  ✅ Real-time response time sparklines")
    console.print("  ✅ Status history visualization (green=success, red=failure)")
    console.print("  ✅ Live statistics updates")
    console.print("  ✅ Color-coded response times")
    console.print("  ✅ 60-point rolling history window")
    console.print()
    console.print("[bold yellow]Usage with real URLs:[/bold yellow]")
    console.print("  python -m pawnstack.cli.main http https://naver.com --dashboard")
    console.print("  python -m pawnstack.cli.main http https://google.com --dashboard --interval 2")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))