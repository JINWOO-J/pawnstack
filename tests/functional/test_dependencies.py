#!/usr/bin/env python3
"""
의존성 시스템 테스트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 간단한 콘솔 출력을 위한 Mock 클래스
class MockConsole:
    def log(self, message):
        print(f"LOG: {message}")

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

class MockPawn:
    def __init__(self):
        self.console = MockConsole()

    def get(self, key):
        return False

# Mock 글로벌 설정
sys.modules['pawnstack.config.global_config'] = type('MockModule', (), {'pawn': MockPawn()})()

# 의존성 시스템 import
from pawnstack.cli.dependencies import DependencyChecker, print_installation_guide

def test_dependency_checker():
    """의존성 검사 시스템 테스트"""
    print("=== PawnStack 의존성 시스템 테스트 ===\n")

    # 사용 가능한 extras 확인
    print("1. 사용 가능한 extras:")
    available = DependencyChecker.get_available_extras()
    for extra in available:
        print(f"   - {extra}")
    print()

    # 설치된 extras 확인
    print("2. 설치된 extras:")
    installed = DependencyChecker.get_installed_extras()
    for extra in installed:
        print(f"   ✓ {extra}")
    print()

    # 누락된 extras 확인
    print("3. 누락된 extras:")
    missing = DependencyChecker.get_missing_extras()
    for extra in missing:
        print(f"   ✗ {extra}")
    print()

    # 특정 의존성 테스트
    print("4. 개별 의존성 테스트:")
    test_extras = ['blockchain', 'aws', 'docker']

    for extra in test_extras:
        result = DependencyChecker.check_dependencies([extra])
        status = "✓ 사용 가능" if result else "✗ 누락"
        print(f"   {extra}: {status}")
    print()

    # 명령어별 의존성 확인
    print("5. 명령어별 의존성:")
    test_commands = ['wallet', 'aws', 'docker', 'info', 'deps']

    for command in test_commands:
        deps = DependencyChecker.get_command_dependencies(command)
        deps_str = ', '.join(deps) if deps else '없음'
        print(f"   {command}: {deps_str}")
    print()

    # 의존성 상태 출력
    print("6. 전체 의존성 상태:")
    DependencyChecker.print_dependency_status()
    print()

    print("=== 테스트 완료 ===")

if __name__ == '__main__':
    test_dependency_checker()
