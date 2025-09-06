#!/usr/bin/env python3
"""
PawnStack 레거시 호환 전역 설정 사용 예제

레거시 pawnlib.config.globalconfig와 동일한 형태로 사용하는 방법을 보여줍니다.
"""

import os
from pawnstack.config.global_config import (
    PawnStackConfig,
    ConfigHandler,
    NestedNamespace,
    pawnstack_config,
    pawn,
    pconf,
    global_verbose
)


def demo_legacy_basic_usage():
    """레거시 기본 사용법 데모"""
    print("=== 레거시 기본 사용법 데모 ===")
    
    # 레거시 스타일 설정
    pawn.set(
        PAWN_DEBUG=True,
        PAWN_VERBOSE=2,
        PAWN_TIMEOUT=5000,
        app_name="Legacy Demo App"
    )
    
    print(f"Debug Mode: {pawn.get('PAWN_DEBUG')}")
    print(f"Verbose Level: {pawn.get('PAWN_VERBOSE')}")
    print(f"Timeout: {pawn.get('PAWN_TIMEOUT')}")
    print(f"App Name: {pawn.get('app_name')}")
    
    # 레거시 스타일 콘솔 로그 (시간 포맷 포함)
    pawn.console.log("레거시 스타일 콘솔 로그 출력")
    
    print()


def demo_time_format():
    """시간 포맷 데모 (레거시 호환)"""
    print("=== 시간 포맷 데모 ===")
    
    # 기본 시간 포맷 (레거시 스타일: [HH:MM:SS,fff])
    pawn.console.log("기본 시간 포맷: [HH:MM:SS,fff]")
    
    # 커스텀 시간 포맷 설정
    pawn.set(PAWN_CONSOLE={'log_time_format': '%Y-%m-%d %H:%M:%S.%f'})
    pawn.console.log("커스텀 시간 포맷: [YYYY-MM-DD HH:MM:SS.fff]")
    
    # 다른 시간 포맷
    pawn.set(PAWN_CONSOLE={'log_time_format': '%H:%M:%S'})
    pawn.console.log("간단한 시간 포맷: [HH:MM:SS]")
    
    # 기본 포맷으로 복원
    pawn.set(PAWN_CONSOLE={'log_time_format': '%H:%M:%S.%f'})
    pawn.console.log("기본 포맷으로 복원")
    
    print()


def demo_counter_operations():
    """카운터 연산 데모 (레거시 기능)"""
    print("=== 카운터 연산 데모 ===")
    
    # 설정값 증가/감소 (레거시 기능)
    pawn.set(counter=0)
    pawn.console.log(f"초기 카운터: {pawn.get('counter')}")
    
    pawn.increase(counter=10)
    pawn.console.log(f"10 증가 후: {pawn.get('counter')}")
    
    pawn.increase(counter=5)
    pawn.console.log(f"5 더 증가 후: {pawn.get('counter')}")
    
    pawn.decrease(counter=3)
    pawn.console.log(f"3 감소 후: {pawn.get('counter')}")
    
    print()


def demo_list_operations():
    """리스트 연산 데모 (레거시 기능)"""
    print("=== 리스트 연산 데모 ===")
    
    # 리스트 연산 (레거시 기능)
    pawn.set(items=[])
    pawn.console.log(f"초기 리스트: {pawn.get('items')}")
    
    pawn.append_list(items="item1")
    pawn.console.log(f"item1 추가 후: {pawn.get('items')}")
    
    pawn.append_list(items="item2")
    pawn.console.log(f"item2 추가 후: {pawn.get('items')}")
    
    pawn.append_list(items="item3")
    pawn.console.log(f"item3 추가 후: {pawn.get('items')}")
    
    pawn.remove_list(items="item2")
    pawn.console.log(f"item2 제거 후: {pawn.get('items')}")
    
    print()


def demo_namespace_access():
    """네임스페이스 접근 데모 (레거시 스타일)"""
    print("=== 네임스페이스 접근 데모 ===")
    
    # 데이터 네임스페이스 설정
    pawn.set(data={
        "user": {
            "name": "홍길동",
            "email": "hong@example.com",
            "preferences": {
                "theme": "dark",
                "language": "ko"
            }
        },
        "system": {
            "version": "1.0.0",
            "debug": True
        }
    })
    
    # 전역 설정을 네임스페이스로 접근 (레거시 스타일)
    conf = pawn.conf()
    pawn.console.log(f"App Name: {conf.app_name}")
    pawn.console.log(f"User Name: {pawn.data.user.name}")
    pawn.console.log(f"User Email: {pawn.data.user.email}")
    pawn.console.log(f"Theme: {pawn.data.user.preferences.theme}")
    pawn.console.log(f"Language: {pawn.data.user.preferences.language}")
    
    # pconf 함수 사용 (레거시 호환)
    config_ns = pconf()
    pawn.console.log(f"pconf()로 접근한 앱 이름: {config_ns.app_name}")
    
    print()


def demo_environment_variables():
    """환경변수 데모 (레거시 호환)"""
    print("=== 환경변수 데모 ===")
    
    # 환경변수 설정 시뮬레이션
    os.environ['PAWN_DEBUG'] = 'true'
    os.environ['PAWN_VERBOSE'] = '3'
    os.environ['PAWN_TIME_FORMAT'] = '%H:%M:%S.%f'
    os.environ['PAWN_TIMEOUT'] = '8000'
    
    # 환경변수에서 설정 로드
    pawn.fill_config_from_environment()
    
    pawn.console.log(f"환경변수에서 로드된 DEBUG: {pawn.get('PAWN_DEBUG')}")
    pawn.console.log(f"환경변수에서 로드된 VERBOSE: {pawn.get('PAWN_VERBOSE')}")
    pawn.console.log(f"환경변수에서 로드된 TIME_FORMAT: {pawn.get('PAWN_TIME_FORMAT')}")
    pawn.console.log(f"환경변수에서 로드된 TIMEOUT: {pawn.get('PAWN_TIMEOUT')}")
    
    # 환경변수 우선순위 테스트
    pawn.set(PAWN_DEBUG=False)  # 환경변수가 우선
    pawn.console.log(f"환경변수 우선순위 테스트 - DEBUG: {pawn.get('PAWN_DEBUG')}")
    
    print()


def demo_config_handler():
    """ConfigHandler 사용 데모 (레거시 호환)"""
    print("=== ConfigHandler 데모 ===")
    
    # 환경변수 설정
    os.environ['PAWN_APP_NAME'] = 'ConfigHandler Demo'
    os.environ['PAWN_PORT'] = '8080'
    
    # ConfigHandler 생성 (레거시 스타일)
    handler = ConfigHandler(
        env_prefix='pawn_',
        defaults={
            'host': '0.0.0.0',
            'workers': 4,
            'log_level': 'INFO'
        }
    )
    
    pawn.console.log(f"App Name: {handler.get('app_name')}")
    pawn.console.log(f"Port: {handler.get('port')}")
    pawn.console.log(f"Host: {handler.get('host')}")
    pawn.console.log(f"Workers: {handler.get('workers')}")
    pawn.console.log(f"Log Level: {handler.get('log_level')}")
    
    # 설정 테이블 출력
    try:
        handler.print_config(pawn.console)
    except Exception as e:
        pawn.console.log(f"설정 테이블 출력 오류: {e}")
    
    print()


def demo_inspect_feature():
    """Rich inspect 기능 데모"""
    print("=== Rich Inspect 데모 ===")
    
    # 복잡한 데이터 구조
    sample_data = {
        "config": {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "****"
                }
            },
            "cache": {
                "redis": {
                    "host": "redis.example.com",
                    "port": 6379
                }
            }
        },
        "features": ["auth", "logging", "monitoring", "caching"],
        "metadata": {
            "version": "1.0.0",
            "build_date": "2025-09-05",
            "environment": "production"
        }
    }
    
    pawn.console.print("[yellow]Rich Inspect으로 데이터 구조 분석:[/yellow]")
    PawnStackConfig.inspect(sample_data, title="복잡한 설정 데이터")
    
    print()


def demo_legacy_patterns():
    """레거시 패턴 데모"""
    print("=== 레거시 패턴 데모 ===")
    
    # 레거시 스타일 로거 설정 (시뮬레이션)
    pawn.set(
        PAWN_LOGGER={
            "app_name": "Legacy Logger Demo",
            "log_level": "DEBUG",
            "stdout": True
        }
    )
    
    # 레거시 스타일 콘솔 설정
    pawn.set(
        PAWN_CONSOLE={
            "log_time_format": "%Y-%m-%d %H:%M:%S.%f",
            "record": True,
            "soft_wrap": False
        }
    )
    
    pawn.console.log("레거시 스타일 로거 및 콘솔 설정 완료")
    
    # 전역 verbose 레벨 확인
    pawn.console.log(f"Global verbose level: {global_verbose}")
    
    # 설정 요약 출력
    pawn.console.log(f"전체 설정 요약: {len(pawn.to_dict())}개 설정 항목")
    
    print()


def main():
    """메인 데모 함수"""
    print("🐍 PawnStack 레거시 호환 Global Config Demo\n")
    
    demo_legacy_basic_usage()
    demo_time_format()
    demo_counter_operations()
    demo_list_operations()
    demo_namespace_access()
    demo_environment_variables()
    demo_config_handler()
    demo_inspect_feature()
    demo_legacy_patterns()
    
    print("✅ 모든 레거시 호환 데모 완료!")
    print(f"📊 최종 설정 상태: {pawn}")


if __name__ == "__main__":
    main()