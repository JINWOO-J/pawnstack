#!/usr/bin/env python3
"""
Inspect CLI 테스트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.getcwd())

def test_inspect_cli():
    """Inspect CLI 기본 테스트"""
    try:
        # 기본 import 테스트
        from pawnstack.cli.inspect import InspectCLI
        print("✅ InspectCLI import 성공")

        # 클래스 인스턴스 생성 테스트
        cli = InspectCLI()
        print("✅ InspectCLI 인스턴스 생성 성공")

        # 기본 속성 확인
        print(f"✅ 명령어 이름: {cli.command_name}")
        print(f"✅ 설명: {cli.description}")

        # 인수 파서 테스트
        from argparse import ArgumentParser
        parser = ArgumentParser()
        cli.get_arguments(parser)
        print("✅ 인수 파서 설정 성공")

        # 도움말 출력 테스트
        print("\n=== 도움말 출력 테스트 ===")
        parser.print_help()

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_inspect_cli()
    sys.exit(0 if success else 1)
