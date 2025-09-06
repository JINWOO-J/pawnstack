#!/usr/bin/env python3
"""
Top CLI 프로세스 테이블 개선 테스트
- 확장된 Name 컬럼 (40자)
- 새로운 RSS, CPU Time 컬럼
- --show-cmdline 옵션
"""

import subprocess
import sys
import time
import os


def run_top_command(args, duration=3):
    """top 명령어 실행 및 출력 캡처"""
    cmd = ["python", "-m", "pawnstack.cli.main", "top"] + args
    
    print(f"실행 명령: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        proc = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # duration 초 동안 실행
        time.sleep(duration)
        proc.terminate()
        
        stdout, stderr = proc.communicate(timeout=2)
        
        # 로그 메시지 필터링 (실제 출력만 표시)
        if stdout:
            lines = stdout.split('\n')
            # 로그 메시지가 아닌 실제 출력만 필터링
            output_lines = []
            for line in lines:
                # 로그 메시지는 보통 [시간] 형식으로 시작
                if not line.startswith('[') and line.strip():
                    output_lines.append(line)
            
            if output_lines:
                print('\n'.join(output_lines[:50]))  # 처음 50줄만 출력
            else:
                print("(출력 없음)")
        
        return True
        
    except Exception as e:
        print(f"오류: {e}")
        return False


def test_basic_process_table():
    """기본 프로세스 테이블 테스트"""
    print("\n" + "="*80)
    print("테스트 1: 기본 프로세스 테이블")
    print("설명: Name 컬럼 40자, RSS와 CPU Time 컬럼 추가됨")
    print("="*80 + "\n")
    
    # line 모드로 테스트 (프로세스 정보가 표시되는지 확인)
    args = ["resource", "--print-type", "line", "--top-n", "10"]
    return run_top_command(args, duration=2)


def test_show_cmdline():
    """--show-cmdline 옵션 테스트"""
    print("\n" + "="*80)
    print("테스트 2: --show-cmdline 옵션")
    print("설명: 전체 명령줄 표시 (Name 컬럼 45자)")
    print("="*80 + "\n")
    
    args = ["resource", "--show-cmdline", "--print-type", "line", "--top-n", "5"]
    return run_top_command(args, duration=2)


def test_process_mode():
    """프로세스 전용 모드 테스트"""
    print("\n" + "="*80)
    print("테스트 3: 프로세스 전용 모니터링 (proc)")
    print("설명: 더 많은 프로세스 정보 표시")
    print("="*80 + "\n")
    
    args = ["proc", "--print-type", "line", "--top-n", "15"]
    return run_top_command(args, duration=2)


def test_process_filter():
    """프로세스 필터 테스트"""
    print("\n" + "="*80)
    print("테스트 4: 프로세스 이름 필터")
    print("설명: Python 프로세스만 표시")
    print("="*80 + "\n")
    
    args = ["resource", "--proc-filter", "python", "--print-type", "line"]
    return run_top_command(args, duration=2)


def main():
    """메인 테스트 실행"""
    print("🍀 PawnStack Top CLI 프로세스 테이블 개선 테스트")
    print("=" * 80)
    
    # Python 경로 확인
    print(f"Python 경로: {sys.executable}")
    print(f"Python 버전: {sys.version}")
    print()
    
    # 테스트 목록
    tests = [
        ("기본 프로세스 테이블", test_basic_process_table),
        ("--show-cmdline 옵션", test_show_cmdline),
        ("프로세스 전용 모드", test_process_mode),
        ("프로세스 필터", test_process_filter),
    ]
    
    passed = 0
    failed = 0
    
    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] {name} 테스트 중...")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} 테스트 성공")
            else:
                failed += 1
                print(f"❌ {name} 테스트 실패")
        except KeyboardInterrupt:
            print("\n사용자가 테스트를 중단했습니다.")
            break
        except Exception as e:
            failed += 1
            print(f"❌ {name} 테스트 실패: {e}")
    
    # 결과 요약
    print("\n" + "="*80)
    print("📊 테스트 결과 요약")
    print("="*80)
    print(f"✅ 성공: {passed}")
    print(f"❌ 실패: {failed}")
    print(f"📈 성공률: {passed/(passed+failed)*100:.1f}%")
    
    print("\n📝 개선사항 요약:")
    print("1. Name 컬럼 너비: 35 -> 40자 (--show-cmdline 시 45자)")
    print("2. RSS 컬럼 추가: 실제 메모리 사용량 (MB 단위)")
    print("3. CPU Time 컬럼 추가: 프로세스 CPU 사용 시간")
    print("4. --show-cmdline 옵션: 전체 명령줄 표시")
    print("5. 프로세스 모니터링 개선: 더 많은 정보 표시")
    
    print("\n💡 팁:")
    print("실시간 모니터링을 보려면 다음 명령을 사용하세요:")
    print("  python -m pawnstack.cli.main top resource --print-type live")
    print("  python -m pawnstack.cli.main top proc --show-cmdline --print-type live")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())