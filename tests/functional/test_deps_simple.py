#!/usr/bin/env python3
"""
의존성 시스템 간단 테스트
"""

import importlib
import sys
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class DependencyInfo:
    """의존성 정보 클래스"""
    module_name: str
    package_name: str
    version_check: str = None
    import_error_hint: str = None

class SimpleDependencyChecker:
    """간단한 의존성 검사기"""

    EXTRAS_DEPENDENCIES = {
        'blockchain': [
            DependencyInfo('eth_keyfile', 'eth-keyfile', '__version__', 'ICON 지갑 관리에 필요'),
            DependencyInfo('coincurve', 'coincurve', '__version__', '암호화 서명에 필요'),
        ],
        'aws': [
            DependencyInfo('boto3', 'boto3', '__version__', 'AWS 서비스 연동에 필요'),
            DependencyInfo('aioboto3', 'aioboto3', '__version__', '비동기 AWS 작업에 필요'),
        ],
        'docker': [
            DependencyInfo('aiodocker', 'aiodocker', '__version__', '비동기 Docker 작업에 필요'),
            DependencyInfo('docker', 'docker', '__version__', 'Docker 관리에 필요'),
        ],
        'redis': [
            DependencyInfo('redis', 'redis', '__version__', 'Redis 연동에 필요'),
            DependencyInfo('aioredis', 'aioredis', '__version__', '비동기 Redis 작업에 필요'),
        ]
    }

    @classmethod
    def check_single_dependency(cls, dep_info: DependencyInfo) -> bool:
        """단일 의존성 검사"""
        try:
            module = importlib.import_module(dep_info.module_name)
            if dep_info.version_check:
                version = getattr(module, dep_info.version_check, 'unknown')
                print(f"  ✓ {dep_info.package_name} v{version}")
            else:
                print(f"  ✓ {dep_info.package_name}")
            return True
        except ImportError:
            print(f"  ✗ {dep_info.package_name} - {dep_info.import_error_hint}")
            return False

    @classmethod
    def check_dependencies(cls, extras: List[str]) -> bool:
        """의존성 검사"""
        all_available = True

        for extra in extras:
            print(f"\n[{extra}] 의존성 검사:")
            if extra not in cls.EXTRAS_DEPENDENCIES:
                print(f"  ⚠️  알 수 없는 extra: {extra}")
                continue

            for dep_info in cls.EXTRAS_DEPENDENCIES[extra]:
                if not cls.check_single_dependency(dep_info):
                    all_available = False

        return all_available

    @classmethod
    def get_available_extras(cls) -> List[str]:
        """사용 가능한 extras 목록"""
        return list(cls.EXTRAS_DEPENDENCIES.keys())

    @classmethod
    def get_installed_extras(cls) -> List[str]:
        """설치된 extras 목록"""
        installed = []
        for extra in cls.EXTRAS_DEPENDENCIES:
            all_deps_available = True
            for dep_info in cls.EXTRAS_DEPENDENCIES[extra]:
                if not cls.check_single_dependency_silent(dep_info):
                    all_deps_available = False
                    break
            if all_deps_available:
                installed.append(extra)
        return installed

    @classmethod
    def check_single_dependency_silent(cls, dep_info: DependencyInfo) -> bool:
        """조용한 의존성 검사"""
        try:
            importlib.import_module(dep_info.module_name)
            return True
        except ImportError:
            return False

def main():
    """메인 테스트 함수"""
    print("=== PawnStack 의존성 시스템 테스트 ===\n")

    checker = SimpleDependencyChecker()

    # 1. 사용 가능한 extras
    print("1. 사용 가능한 extras:")
    available = checker.get_available_extras()
    for extra in available:
        print(f"   - {extra}")

    # 2. 설치된 extras
    print("\n2. 설치된 extras:")
    installed = checker.get_installed_extras()
    if installed:
        for extra in installed:
            print(f"   ✓ {extra}")
    else:
        print("   (설치된 선택적 의존성 없음)")

    # 3. 각 extra별 상세 검사
    print("\n3. 상세 의존성 검사:")
    for extra in available:
        result = checker.check_dependencies([extra])
        status = "✓ 모두 사용 가능" if result else "✗ 일부 누락"
        print(f"\n{extra}: {status}")

    # 4. 설치 가이드
    missing = set(available) - set(installed)
    if missing:
        print(f"\n4. 설치 가이드:")
        print(f"   누락된 기능을 설치하려면:")
        missing_str = ','.join(missing)
        print(f"   pip install pawnstack[{missing_str}]")
        print(f"   또는 모든 기능: pip install pawnstack[full]")
    else:
        print(f"\n4. 모든 선택적 의존성이 설치되어 있습니다! 🎉")

    print("\n=== 테스트 완료 ===")

if __name__ == '__main__':
    main()
