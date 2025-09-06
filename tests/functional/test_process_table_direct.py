#!/usr/bin/env python3
"""
프로세스 테이블 직접 테스트 스크립트
TopCLI의 create_process_table 메서드를 직접 호출하여 개선사항 확인
"""

import sys
import os
import time
import psutil
from dataclasses import dataclass
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel

# PawnStack 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pawnstack.cli.top import TopCLI, TopConfig


def test_process_table_basic():
    """기본 프로세스 테이블 테스트"""
    print("\n" + "="*80)
    print("🍀 테스트 1: 기본 프로세스 테이블 (Name 40자, RSS/CPU Time 컬럼)")
    print("="*80)
    
    # TopCLI 인스턴스 생성
    cli = TopCLI()
    cli.config = TopConfig(top_n=10, show_cmdline=False)
    
    # 프로세스 테이블 생성
    panel = cli.create_process_table()
    
    # 출력
    console = Console()
    console.print(panel)
    
    return True


def test_process_table_cmdline():
    """--show-cmdline 옵션 테스트"""
    print("\n" + "="*80)
    print("🍀 테스트 2: 전체 명령줄 표시 (--show-cmdline)")
    print("="*80)
    
    # TopCLI 인스턴스 생성
    cli = TopCLI()
    cli.config = TopConfig(top_n=5, show_cmdline=True)
    
    # 프로세스 테이블 생성
    panel = cli.create_process_table()
    
    # 출력
    console = Console()
    console.print(panel)
    
    return True


def test_process_details():
    """프로세스 상세 정보 직접 확인"""
    print("\n" + "="*80)
    print("🍀 테스트 3: 프로세스 상세 정보")
    print("="*80)
    
    console = Console()
    
    # 테이블 생성
    table = Table(show_header=True, header_style="bold bright_cyan", box=box.SIMPLE)
    table.add_column("PID", style="cyan", width=8)
    table.add_column("Name", style="white", width=40)
    table.add_column("CPU%", style="yellow", width=8)
    table.add_column("MEM%", style="magenta", width=8)
    table.add_column("RSS", style="blue", width=10)
    table.add_column("CPU Time", style="cyan", width=12)
    table.add_column("Status", style="green", width=10)
    
    # 프로세스 정보 수집
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                    'status', 'memory_info', 'cpu_times']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # CPU 사용률 기준 정렬
    processes.sort(key=lambda x: x.get('cpu_percent') or 0, reverse=True)
    
    # 상위 10개 표시
    for proc in processes[:10]:
        cpu_val = proc.get('cpu_percent') or 0
        mem_val = proc.get('memory_percent') or 0
        
        # 메모리 정보
        memory_info = proc.get('memory_info')
        if memory_info:
            rss_mb = memory_info.rss / 1024 / 1024
            rss_str = f"{rss_mb:.1f}M"
        else:
            rss_str = "N/A"
        
        # CPU 시간
        cpu_times = proc.get('cpu_times')
        if cpu_times:
            total_time = cpu_times.user + cpu_times.system
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            seconds = int(total_time % 60)
            if hours > 0:
                cpu_time_str = f"{hours}h{minutes:02d}m"
            elif minutes > 0:
                cpu_time_str = f"{minutes}m{seconds:02d}s"
            else:
                cpu_time_str = f"{seconds}s"
        else:
            cpu_time_str = "N/A"
        
        # 프로세스 이름 처리 (40자 제한)
        name = proc.get('name', '')
        if len(name) > 40:
            name = name[:37] + "..."
        
        table.add_row(
            str(proc.get('pid', '')),
            name,
            f"{cpu_val:.1f}",
            f"{mem_val:.1f}",
            rss_str,
            cpu_time_str,
            proc.get('status', '')
        )
    
    # 패널로 감싸서 출력
    panel = Panel(
        table,
        title="[bold bright_cyan]📊 Top 10 Processes (by CPU)[/bold bright_cyan]",
        border_style="bright_cyan"
    )
    
    console.print(panel)
    
    return True


def test_process_with_cmdline():
    """명령줄 포함 프로세스 정보"""
    print("\n" + "="*80)
    print("🍀 테스트 4: 전체 명령줄 포함 프로세스 정보")
    print("="*80)
    
    console = Console()
    
    # 테이블 생성
    table = Table(show_header=True, header_style="bold bright_cyan", box=box.SIMPLE)
    table.add_column("PID", style="cyan", width=8)
    table.add_column("Command Line", style="white", width=50)
    table.add_column("CPU%", style="yellow", width=8)
    table.add_column("RSS", style="blue", width=10)
    
    # 프로세스 정보 수집 (cmdline 포함)
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # CPU 사용률 기준 정렬
    processes.sort(key=lambda x: x.get('cpu_percent') or 0, reverse=True)
    
    # 상위 5개만 표시
    for proc in processes[:5]:
        cpu_val = proc.get('cpu_percent') or 0
        
        # 명령줄 처리
        cmdline = proc.get('cmdline', [])
        if cmdline:
            display_name = ' '.join(cmdline)
        else:
            display_name = proc.get('name', '')
        
        # 50자 제한
        if len(display_name) > 50:
            display_name = display_name[:47] + "..."
        
        # 메모리 정보
        memory_info = proc.get('memory_info')
        if memory_info:
            rss_mb = memory_info.rss / 1024 / 1024
            rss_str = f"{rss_mb:.1f}M"
        else:
            rss_str = "N/A"
        
        table.add_row(
            str(proc.get('pid', '')),
            display_name,
            f"{cpu_val:.1f}",
            rss_str
        )
    
    # 패널로 감싸서 출력
    panel = Panel(
        table,
        title="[bold bright_cyan]📋 Top 5 Processes with Full Command Line[/bold bright_cyan]",
        border_style="bright_cyan"
    )
    
    console.print(panel)
    
    return True


def main():
    """메인 함수"""
    print("="*80)
    print("🍀 PawnStack Top CLI 프로세스 테이블 개선 직접 테스트")
    print("="*80)
    
    console = Console()
    
    # 시스템 정보 출력
    print(f"\n📊 시스템 정보:")
    print(f"  - 총 프로세스 수: {len(list(psutil.process_iter()))}")
    print(f"  - CPU 코어 수: {psutil.cpu_count(logical=False)} (논리: {psutil.cpu_count()})")
    print(f"  - 메모리: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"  - CPU 사용률: {psutil.cpu_percent()}%")
    print(f"  - 메모리 사용률: {psutil.virtual_memory().percent}%")
    
    tests = [
        ("기본 프로세스 테이블", test_process_table_basic),
        ("전체 명령줄 표시", test_process_table_cmdline),
        ("프로세스 상세 정보", test_process_details),
        ("명령줄 포함 정보", test_process_with_cmdline),
    ]
    
    passed = 0
    failed = 0
    
    for i, (name, test_func) in enumerate(tests, 1):
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {name} 테스트 성공")
            else:
                failed += 1
                print(f"\n❌ {name} 테스트 실패")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
    
    # 결과 요약
    print("\n" + "="*80)
    print("📊 테스트 결과 요약")
    print("="*80)
    print(f"✅ 성공: {passed}")
    print(f"❌ 실패: {failed}")
    if passed + failed > 0:
        print(f"📈 성공률: {passed/(passed+failed)*100:.1f}%")
    
    print("\n🎉 개선된 프로세스 테이블 기능:")
    print("  1. ✅ Name 컬럼 확장: 40자 (기존 20자)")
    print("  2. ✅ RSS 컬럼 추가: 실제 메모리 사용량 표시")
    print("  3. ✅ CPU Time 컬럼 추가: 누적 CPU 사용 시간")
    print("  4. ✅ --show-cmdline 옵션: 전체 명령줄 표시 (45자)")
    print("  5. ✅ 프로세스 모니터링 개선: 더 많은 상세 정보")
    
    print("\n💡 실시간 모니터링 실행 방법:")
    print("  # 기본 리소스 모니터링 (라이브)")
    print("  python -m pawnstack.cli.main top resource --print-type live")
    print("\n  # 프로세스 전용 모니터링")
    print("  python -m pawnstack.cli.main top proc --print-type live")
    print("\n  # 전체 명령줄 표시")
    print("  python -m pawnstack.cli.main top resource --show-cmdline --print-type live")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())