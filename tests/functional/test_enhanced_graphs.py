#!/usr/bin/env python3
"""
향상된 HTTP 대시보드 그래프 테스트 스크립트

멀티라인 ASCII 그래프와 개선된 가시성 테스트
"""

import asyncio
import sys
import os
import random
import time
import math
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
from rich.columns import Columns
from rich import box


class EnhancedGraphTester:
    """향상된 그래프 테스트 클래스"""
    
    def __init__(self):
        self.console = Console()
        
    def create_ascii_graph(self, data: List[float], width: int = 60, height: int = 8, label: str = "") -> str:
        """멀티라인 ASCII 그래프 생성 - 높은 가시성"""
        if not data or height < 2:
            return "데이터 없음"
        
        # 데이터 샘플링
        if len(data) > width:
            step = len(data) / width
            sampled = []
            for i in range(width):
                idx = int(i * step)
                sampled.append(data[idx])
            data = sampled
        elif len(data) < width:
            # 데이터가 너비보다 적으면 선형 보간
            if len(data) > 1:
                interpolated = []
                for i in range(width):
                    t = i / (width - 1) * (len(data) - 1)
                    idx1 = int(t)
                    idx2 = min(idx1 + 1, len(data) - 1)
                    weight = t - idx1
                    val = data[idx1] * (1 - weight) + data[idx2] * weight
                    interpolated.append(val)
                data = interpolated
            else:
                data = data * width
        
        # 최소/최대값 계산
        min_val = min(data) if data else 0
        max_val = max(data) if data else 0
        
        if max_val == min_val:
            max_val = min_val + 1
        
        # 그래프 문자 팔레트
        blocks = ["░", "▒", "▓", "█"]
        
        # 그래프 생성
        graph_lines = []
        
        # 제목
        if label:
            graph_lines.append(f"  [bold cyan]{label}[/bold cyan]")
            graph_lines.append("")
        
        # Y축 라벨과 그래프 생성
        for h in range(height, 0, -1):
            line = ""
            
            # Y축 라벨 (더 정밀한 표시)
            y_val = min_val + (max_val - min_val) * (h - 0.5) / height
            if h == height:
                y_label = f"[dim]{max_val:6.2f}s[/dim]│"
            elif h == 1:
                y_label = f"[dim]{min_val:6.2f}s[/dim]│"
            elif h == height // 2 + 1:
                mid_val = (max_val + min_val) / 2
                y_label = f"[dim]{mid_val:6.2f}s[/dim]│"
            else:
                y_label = "        │"
            
            line = y_label
            
            # 데이터 포인트 그리기
            for i, val in enumerate(data):
                # 정규화된 높이 계산
                normalized_val = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
                bar_height = normalized_val * height
                
                # 현재 행에 그릴지 결정
                if bar_height >= h - 0.5:
                    # 그라데이션 효과
                    intensity = min(1.0, bar_height - (h - 1))
                    block_idx = int(intensity * (len(blocks) - 1))
                    
                    # 색상 결정
                    if val < 0.5:
                        color = "green"
                    elif val < 1.0:
                        color = "bright_green"
                    elif val < 1.5:
                        color = "yellow"
                    elif val < 2.0:
                        color = "bright_yellow"
                    else:
                        color = "red"
                    
                    line += f"[{color}]{blocks[block_idx]}[/{color}]"
                else:
                    # 그리드 라인
                    if h == 1:
                        line += "─"
                    elif i % 10 == 0:
                        line += "·"
                    else:
                        line += " "
            
            graph_lines.append(line)
        
        # X축 그리기
        graph_lines.append("        └" + "─" * width + "→ Time")
        
        # X축 라벨
        if len(data) > 0:
            x_labels = f"         0s" + " " * (width - 20) + f"{len(data)}개 샘플"
            graph_lines.append(x_labels)
        
        return "\n".join(graph_lines)
    
    def create_enhanced_sparkline(self, data: List[float], width: int = 60) -> str:
        """향상된 sparkline - 더 많은 단계"""
        if not data:
            return "─" * width
        
        # 확장된 블록 문자 세트
        blocks = " ▁▂▃▄▅▆▇█"
        
        # 데이터 샘플링
        if len(data) > width:
            step = len(data) / width
            sampled = [data[int(i * step)] for i in range(width)]
        else:
            sampled = data + [data[-1]] * (width - len(data)) if data else []
        
        # 정규화
        min_val = min(sampled)
        max_val = max(sampled)
        range_val = max_val - min_val if max_val > min_val else 1
        
        sparkline = ""
        for val in sampled:
            normalized = (val - min_val) / range_val
            block_idx = int(normalized * (len(blocks) - 1))
            
            # 색상 적용
            if val < 1.0:
                sparkline += f"[green]{blocks[block_idx]}[/green]"
            elif val < 2.0:
                sparkline += f"[yellow]{blocks[block_idx]}[/yellow]"
            else:
                sparkline += f"[red]{blocks[block_idx]}[/red]"
        
        return sparkline
    
    def create_dual_axis_graph(self, data1: List[float], data2: List[float], 
                              width: int = 60, height: int = 10,
                              label1: str = "응답시간", label2: str = "성공률") -> str:
        """이중 축 그래프 - 두 개의 메트릭을 동시에 표시"""
        if not data1 or not data2:
            return "데이터 수집 중..."
        
        # 데이터 샘플링
        def sample_data(data, target_width):
            if len(data) > target_width:
                step = len(data) / target_width
                return [data[int(i * step)] for i in range(target_width)]
            elif len(data) < target_width:
                return data + [data[-1]] * (target_width - len(data))
            return data
        
        data1 = sample_data(data1, width)
        data2 = sample_data(data2, width)
        
        # 각 데이터의 범위 계산
        min1, max1 = min(data1), max(data1)
        min2, max2 = min(data2), max(data2)
        
        if max1 == min1:
            max1 = min1 + 1
        if max2 == min2:
            max2 = min2 + 1
        
        lines = []
        
        # 제목
        lines.append(f"  [bold cyan]Dual Metrics Graph[/bold cyan]")
        lines.append("")
        
        # 그래프 그리기
        for h in range(height, 0, -1):
            line = ""
            
            # 왼쪽 Y축 (data1)
            if h == height:
                line += f"[blue]{max1:5.2f}[/blue]│"
            elif h == 1:
                line += f"[blue]{min1:5.2f}[/blue]│"
            else:
                line += "      │"
            
            # 데이터 그리기
            for i in range(width):
                val1_norm = (data1[i] - min1) / (max1 - min1) * height
                val2_norm = (data2[i] - min2) / (max2 - min2) * height
                
                if val1_norm >= h - 0.5 and val2_norm >= h - 0.5:
                    # 두 데이터가 겹침
                    line += "[magenta]▓[/magenta]"
                elif val1_norm >= h - 0.5:
                    # data1만
                    if data1[i] < 1.0:
                        line += "[green]█[/green]"
                    elif data1[i] < 2.0:
                        line += "[yellow]█[/yellow]"
                    else:
                        line += "[red]█[/red]"
                elif val2_norm >= h - 0.5:
                    # data2만
                    if data2[i] > 0.95:
                        line += "[cyan]▒[/cyan]"
                    else:
                        line += "[blue]▒[/blue]"
                else:
                    line += " "
            
            # 오른쪽 Y축 (data2)
            if h == height:
                line += f"│[cyan]{max2*100:5.1f}%[/cyan]"
            elif h == 1:
                line += f"│[cyan]{min2*100:5.1f}%[/cyan]"
            else:
                line += "│"
            
            lines.append(line)
        
        # X축
        lines.append("      └" + "─" * width + "┘")
        lines.append(f"       [blue]{label1}[/blue]: █  [cyan]{label2}[/cyan]: ▒")
        
        return "\n".join(lines)
    
    async def demonstrate_graphs(self):
        """다양한 그래프 시연"""
        self.console.print(Panel.fit(
            "[bold cyan]🍀 향상된 그래프 시각화 데모[/bold cyan]\n"
            "[yellow]다양한 그래프 유형을 보여드립니다[/yellow]",
            border_style="cyan"
        ))
        
        # 테스트 데이터 생성
        # 1. 정상적인 응답 패턴
        normal_data = []
        for i in range(60):
            base = 0.5
            noise = random.gauss(0, 0.1)
            spike = 1.5 if i % 15 == 0 else 0  # 주기적 스파이크
            normal_data.append(max(0.1, base + noise + spike))
        
        # 2. 점진적 악화 패턴
        degrading_data = []
        for i in range(60):
            base = 0.3 + (i / 60) * 2.0  # 0.3초에서 2.3초로 증가
            noise = random.gauss(0, 0.1)
            degrading_data.append(max(0.1, base + noise))
        
        # 3. 주기적 패턴
        periodic_data = []
        for i in range(60):
            base = 1.0 + math.sin(i / 5) * 0.8
            noise = random.gauss(0, 0.05)
            periodic_data.append(max(0.1, base + noise))
        
        # 4. 성공률 데이터
        success_data = []
        for i in range(60):
            if i < 20:
                rate = 0.99 + random.gauss(0, 0.01)
            elif i < 40:
                rate = 0.95 + random.gauss(0, 0.02)
            else:
                rate = 0.85 + random.gauss(0, 0.05)
            success_data.append(max(0, min(1, rate)))
        
        # 그래프 표시
        self.console.print("\n[bold]1. 기본 Sparkline (1줄)[/bold]")
        sparkline = self.create_enhanced_sparkline(normal_data)
        self.console.print(f"  {sparkline}")
        self.console.print(f"  [dim]최소: {min(normal_data):.2f}s | 최대: {max(normal_data):.2f}s[/dim]\n")
        
        self.console.print("[bold]2. ASCII 그래프 - 정상 패턴 (8줄)[/bold]")
        graph1 = self.create_ascii_graph(normal_data, width=60, height=8, label="정상 응답 패턴")
        self.console.print(graph1)
        
        self.console.print("\n[bold]3. ASCII 그래프 - 악화 패턴 (8줄)[/bold]")
        graph2 = self.create_ascii_graph(degrading_data, width=60, height=8, label="점진적 성능 악화")
        self.console.print(graph2)
        
        self.console.print("\n[bold]4. ASCII 그래프 - 주기적 패턴 (10줄)[/bold]")
        graph3 = self.create_ascii_graph(periodic_data, width=60, height=10, label="주기적 변동")
        self.console.print(graph3)
        
        self.console.print("\n[bold]5. 이중 축 그래프 - 응답시간 & 성공률 (10줄)[/bold]")
        dual_graph = self.create_dual_axis_graph(
            periodic_data, success_data,
            width=60, height=10,
            label1="응답시간", label2="성공률"
        )
        self.console.print(dual_graph)
        
        # 실시간 업데이트 시뮬레이션
        self.console.print("\n[bold]6. 실시간 업데이트 시뮬레이션 (5초)[/bold]")
        await self.run_live_simulation()
    
    async def run_live_simulation(self):
        """실시간 그래프 업데이트 시뮬레이션"""
        data = deque(maxlen=60)
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="graph", size=12),
            Layout(name="stats", size=3)
        )
        
        with Live(layout, refresh_per_second=2, screen=False) as live:
            for _ in range(10):  # 5초 동안
                # 새 데이터 추가
                new_value = 0.5 + random.gauss(0, 0.2) + (random.random() < 0.1) * 1.5
                data.append(max(0.1, new_value))
                
                # 헤더 업데이트
                layout["header"].update(Panel(
                    f"[bold cyan]실시간 그래프 업데이트[/bold cyan] | "
                    f"데이터 포인트: {len(data)} | "
                    f"시간: {datetime.now().strftime('%H:%M:%S')}",
                    style="cyan"
                ))
                
                # 그래프 업데이트
                if len(data) > 1:
                    graph = self.create_ascii_graph(
                        list(data), width=70, height=10,
                        label="실시간 응답 시간 모니터링"
                    )
                    layout["graph"].update(Panel(
                        Text.from_markup(graph),
                        title="Performance Graph",
                        border_style="green"
                    ))
                
                # 통계 업데이트
                if data:
                    stats_text = (
                        f"현재: [cyan]{data[-1]:.3f}s[/cyan] | "
                        f"평균: {sum(data)/len(data):.3f}s | "
                        f"최소: {min(data):.3f}s | "
                        f"최대: {max(data):.3f}s"
                    )
                    layout["stats"].update(Panel(
                        stats_text,
                        title="Statistics",
                        border_style="yellow"
                    ))
                
                await asyncio.sleep(0.5)


async def main():
    """메인 함수"""
    console = Console()
    
    console.print("="*80)
    console.print("[bold cyan]🍀 Enhanced Graph Visualization Test[/bold cyan]")
    console.print("="*80)
    console.print()
    
    # 테스터 생성
    tester = EnhancedGraphTester()
    
    try:
        # 그래프 데모 실행
        await tester.demonstrate_graphs()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]테스트가 중단되었습니다.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]오류: {e}[/red]")
        import traceback
        traceback.print_exc()
    
    console.print("\n" + "="*80)
    console.print("[bold green]✨ 테스트 완료![/bold green]")
    console.print("="*80)
    console.print()
    console.print("[bold cyan]📊 주요 개선사항:[/bold cyan]")
    console.print("  1. ✅ 멀티라인 ASCII 그래프 (6-10줄 높이)")
    console.print("  2. ✅ 그라데이션 효과로 더 정밀한 표현")
    console.print("  3. ✅ Y축 라벨과 격자선 표시")
    console.print("  4. ✅ 색상 코딩 (녹색→노랑→빨강)")
    console.print("  5. ✅ 이중 축 그래프 지원")
    console.print("  6. ✅ 실시간 업데이트 애니메이션")
    console.print()
    console.print("[bold yellow]💡 사용 방법:[/bold yellow]")
    console.print("  pawns http https://naver.com --dashboard")
    console.print("  # 더 높은 가시성의 그래프로 모니터링")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))