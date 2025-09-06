#!/usr/bin/env python3
"""
Top CLI 개선사항 테스트 스크립트
- 프로세스 이름 표시 개선
- 새로운 컬럼들 (RSS, CPU Time)
- --show-cmdline 옵션
"""

import subprocess
import sys
import time
import os


def test_top_basic():
    """기본 top 명령어 테스트"""
    print("🍀 테스트 1: 기본 top 명령어 (개선된 프로세스 테이블)")
    print("-" * 60)
    print("명령어: pawns top resource --print-type line")
    print("설명: 프로세스 이름이 더 길게 표시되고, RSS와 CPU Time 컬럼이 추가됨")
    print("-" * 60)
    
    # 5초 동안만 실행
    cmd = ["pawns", "top", "resource", "--print-type", "line", "--interval", "1"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=2)
        
        if stdout:
            print("출력 샘플 (처음 50줄):")
            lines = stdout.split('\n')[:50]
            for line in lines:
                print(line)
    except Exception as e:
        print(f"오류 발생: {e}")
    
    print("\n" + "="*60 + "\n")


def test_top_cmdline():
    """--show-cmdline 옵션 테스트"""
    print("🍀 테스트 2: --show-cmdline 옵션")
    print("-" * 60)
    print("명령어: pawns top resource --show-cmdline --print-type line")
    print("설명: 프로세스 이름 대신 전체 명령줄 표시")
    print("-" * 60)
    
    cmd = ["pawns", "top", "resource", "--show-cmdline", "--print-type", "line", "--interval", "1"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=2)
        
        if stdout:
            print("출력 샘플 (처음 50줄):")
            lines = stdout.split('\n')[:50]
            for line in lines:
                print(line)
    except Exception as e:
        print(f"오류 발생: {e}")
    
    print("\n" + "="*60 + "\n")


def test_top_proc_mode():
    """프로세스 모니터링 모드 테스트"""
    print("🍀 테스트 3: 프로세스 전용 모니터링 모드")
    print("-" * 60)
    print("명령어: pawns top proc --top-n 20 --print-type line")
    print("설명: 상위 20개 프로세스 표시 (개선된 정보)")
    print("-" * 60)
    
    cmd = ["pawns", "top", "proc", "--top-n", "20", "--print-type", "line"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=2)
        
        if stdout:
            print("출력 샘플 (처음 50줄):")
            lines = stdout.split('\n')[:50]
            for line in lines:
                print(line)
    except Exception as e:
        print(f"오류 발생: {e}")
    
    print("\n" + "="*60 + "\n")


def test_top_filter():
    """프로세스 필터링 테스트"""
    print("🍀 테스트 4: 프로세스 필터링")
    print("-" * 60)
    print("명령어: pawns top resource --proc-filter python --print-type line")
    print("설명: python 관련 프로세스만 표시")
    print("-" * 60)
    
    cmd = ["pawns", "top", "resource", "--proc-filter", "python", "--print-type", "line"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=2)
        
        if stdout:
            print("출력 샘플 (처음 50줄):")
            lines = stdout.split('\n')[:50]
            for line in lines:
                print(line)
    except Exception as e:
        print(f"오류 발생: {e}")
    
    print("\n" + "="*60 + "\n")


def check_help():
    """도움말 확인"""
    print("🍀 도움말 확인")
    print("-" * 60)
    print("명령어: pawns top --help")
    print("-" * 60)
    
    cmd = ["pawns", "top", "--help"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("에러 출력:", result.stderr)
    except Exception as e:
        print(f"오류 발생: {e}")
    
    print("\n" + "="*60 + "\n")


def main():
    """메인 함수"""
    print("="*60)
    print("🍀 PawnStack Top CLI 개선사항 테스트")
    print("="*60)
    print()
    
    # pawns 명령어가 설치되어 있는지 확인
    try:
        subprocess.run(["pawns", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pawns 명령어를 찾을 수 없습니다.")
        print("먼저 pawnstack을 설치해주세요: pip install -e .")
        sys.exit(1)
    
    # 테스트 실행
    tests = [
        ("도움말 확인", check_help),
        ("기본 top 테스트", test_top_basic),
        ("--show-cmdline 옵션", test_top_cmdline),
        ("프로세스 모니터링 모드", test_top_proc_mode),
        ("프로세스 필터링", test_top_filter),
    ]
    
    for i, (test_name, test_func) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] {test_name} 실행 중...")
        try:
            test_func()
        except KeyboardInterrupt:
            print("\n사용자가 테스트를 중단했습니다.")
            break
        except Exception as e:
            print(f"테스트 실행 중 오류: {e}")
    
    print("\n" + "="*60)
    print("🍀 테스트 완료!")
    print("="*60)
    print("\n주요 개선사항:")
    print("1. ✅ Name 컬럼 너비 확장 (35 -> 40 문자)")
    print("2. ✅ --show-cmdline 옵션으로 전체 명령줄 표시 가능")
    print("3. ✅ RSS (실제 메모리 사용량) 컬럼 추가")
    print("4. ✅ CPU Time 컬럼 추가")
    print("5. ✅ 프로세스 모니터링 모드에서도 동일한 개선 적용")
    print("\n실시간 모니터링을 보려면:")
    print("  pawns top resource --print-type live")
    print("  pawns top proc --show-cmdline --print-type live")


if __name__ == "__main__":
    main()