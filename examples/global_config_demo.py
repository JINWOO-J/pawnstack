#!/usr/bin/env python3

import common
"""
PawnStack 전역 설정 사용 예제

레거시 pawnlib.config.globalconfig에서 마이그레이션된 기능들의 사용법을 보여줍니다.
"""

import os
from pawnstack.config.global_config import (
    PawnStackConfig,
    ConfigHandler,
    NestedNamespace,
    pawnstack_config,
    pawn
)


def demo_nested_namespace():
    """NestedNamespace 사용 예제"""
    print("=== NestedNamespace 데모 ===")

    # 중첩된 딕셔너리 생성
    data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "secret"
            }
        },
        "features": ["auth", "logging", "monitoring"],
        "debug": True
    }

    # NestedNamespace로 변환
    config = NestedNamespace(**data)

    # 점 표기법으로 접근
    print(f"Database Host: {config.database.host}")
    print(f"Database Port: {config.database.port}")
    print(f"Username: {config.database.credentials.username}")
    print(f"Features: {config.features}")
    print(f"Debug Mode: {config.debug}")

    # 중첩된 값 검색
    username = config.get_nested(['database', 'credentials', 'username'])
    print(f"Nested Username: {username}")

    # 딕셔너리로 다시 변환
    as_dict = config.as_dict()
    print(f"As Dict: {as_dict['database']['host']}")
    print()


def demo_config_handler():
    """ConfigHandler 사용 예제"""
    print("=== ConfigHandler 데모 ===")

    # 환경변수 설정 (시뮬레이션)
    os.environ['PAWN_DEBUG'] = 'true'
    os.environ['PAWN_TIMEOUT'] = '5000'
    os.environ['APP_NAME'] = 'demo_app'

    # ConfigHandler 생성
    handler = ConfigHandler(
        env_prefix='pawn_',
        allowed_env_keys=['app_name'],
        defaults={
            'log_level': 'INFO',
            'max_connections': 100
        }
    )

    # 값 가져오기
    print(f"Debug: {handler.get('debug')}")
    print(f"Timeout: {handler.get('timeout')}")
    print(f"App Name: {handler.get('app_name')}")
    print(f"Log Level: {handler.get('log_level')}")
    print(f"Max Connections: {handler.get('max_connections')}")

    # 설정 업데이트
    handler.set('new_setting', 'new_value')
    print(f"New Setting: {handler.get('new_setting')}")

    # 네임스페이스로 변환
    ns = handler.as_namespace()
    print(f"As Namespace - Debug: {ns.debug}")

    # 설정 테이블 출력 (Rich Console 필요)
    try:
        handler.print_config()
    except Exception as e:
        print(f"Config table display error: {e}")

    print()


def demo_pawnstack_config():
    """PawnStackConfig 사용 예제"""
    print("=== PawnStackConfig 데모 ===")

    # 전역 설정 인스턴스 사용
    config = PawnStackConfig()

    # 기본 설정
    config.set(
        app_name="PawnStack Demo",
        version="1.0.0",
        debug=True,
        max_workers=4
    )

    print(f"App Name: {config.get('app_name')}")
    print(f"Version: {config.get('version')}")
    print(f"Debug: {config.get('debug')}")
    print(f"Max Workers: {config.get('max_workers')}")

    # 숫자 증가/감소
    config.set(counter=10)
    config.increase(counter=5)
    print(f"Counter after increase: {config.get('counter')}")

    config.decrease(counter=3)
    print(f"Counter after decrease: {config.get('counter')}")

    # 리스트 연산
    config.set(tasks=[])
    config.append_list(tasks="task1")
    config.append_list(tasks="task2")
    config.append_list(tasks="task3")
    print(f"Tasks: {config.get('tasks')}")

    config.remove_list(tasks="task2")
    print(f"Tasks after removal: {config.get('tasks')}")

    # 데이터 네임스페이스
    config.set(data={
        "user": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    })

    print(f"User Name: {config.data.user.name}")
    print(f"User Email: {config.data.user.email}")
    print(f"Theme: {config.data.settings.theme}")

    # 전체 설정을 네임스페이스로
    conf = config.conf()
    print(f"Config as namespace - App Name: {conf.app_name}")

    print()


def demo_global_instance():
    """전역 인스턴스 사용 예제"""
    print("=== 전역 인스턴스 데모 ===")

    # 전역 설정 사용
    pawn.set(
        service_name="Global Service",
        port=8080,
        host="0.0.0.0"
    )

    print(f"Service Name: {pawn.get('service_name')}")
    print(f"Port: {pawn.get('port')}")
    print(f"Host: {pawn.get('host')}")

    # pawnstack_config와 pawn은 같은 인스턴스
    print(f"Same instance: {pawn is pawnstack_config}")

    # 다른 모듈에서도 접근 가능
    print(f"From pawnstack_config: {pawnstack_config.get('service_name')}")

    print()


def demo_environment_integration():
    """환경변수 통합 예제"""
    print("=== 환경변수 통합 데모 ===")

    # 환경변수 설정
    os.environ['PAWN_DEBUG'] = 'true'
    os.environ['PAWN_TIMEOUT'] = '10000'
    os.environ['PAWN_SSL_CHECK'] = 'false'

    # 새로운 설정 인스턴스 생성 (환경변수 로드)
    config = PawnStackConfig()
    config.fill_config_from_environment()

    print(f"Debug from env: {config.get('PAWN_DEBUG')}")
    print(f"Timeout from env: {config.get('PAWN_TIMEOUT')}")
    print(f"SSL Check from env: {config.get('PAWN_SSL_CHECK')}")

    # 환경변수 우선순위 테스트
    config.set(PAWN_DEBUG=False)  # 환경변수가 우선
    print(f"Debug after set (env wins): {config.get('PAWN_DEBUG')}")

    print()


def demo_rich_integration():
    """Rich 통합 예제"""
    print("=== Rich 통합 데모 ===")

    # Rich Console 사용
    if pawn.console:
        pawn.console.print("[bold green]PawnStack Config Demo[/bold green]")
        pawn.console.print("[blue]Rich Console is working![/blue]")

        # Rich inspect 사용
        sample_data = {"key": "value", "number": 42}
        pawn.console.print("\n[yellow]Rich Inspect Demo:[/yellow]")
        PawnStackConfig.inspect(sample_data, title="Sample Data")
    else:
        print("Rich Console not available")

    print()


def main():
    """메인 데모 함수"""
    print("🐍 PawnStack Global Config Demo\n")

    demo_nested_namespace()
    demo_config_handler()
    demo_pawnstack_config()
    demo_global_instance()
    demo_environment_integration()
    demo_rich_integration()

    print("✅ 모든 데모 완료!")


if __name__ == "__main__":
    main()

def demo_legacy_compatibility():
    """레거시 호환성 데모"""
    print("=== 레거시 호환성 데모 ===")
    
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
    
    # 레거시 스타일 콘솔 로그
    pawn.console.log("레거시 스타일 콘솔 로그 출력")
    
    # 설정값 증가/감소 (레거시 기능)
    pawn.set(counter=0)
    pawn.increase(counter=10)
    pawn.console.log(f"Counter increased: {pawn.get('counter')}")
    
    pawn.decrease(counter=3)
    pawn.console.log(f"Counter decreased: {pawn.get('counter')}")
    
    # 리스트 연산 (레거시 기능)
    pawn.set(items=[])
    pawn.append_list(items="item1")
    pawn.append_list(items="item2")
    pawn.console.log(f"Items: {pawn.get('items')}")
    
    # 전역 설정을 네임스페이스로 접근 (레거시 스타일)
    conf = pawn.conf()
    pawn.console.log(f"Config namespace access: {conf.app_name}")
    
    print()


def demo_time_format():
    """시간 포맷 데모 (레거시 호환)"""
    print("=== 시간 포맷 데모 ===")
    
    # 기본 시간 포맷 (레거시 스타일)
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


def demo_environment_variables():
    """환경변수 데모 (레거시 호환)"""
    print("=== 환경변수 데모 ===")
    
    # 환경변수 설정 시뮬레이션
    os.environ['PAWN_DEBUG'] = 'true'
    os.environ['PAWN_VERBOSE'] = '3'
    os.environ['PAWN_TIME_FORMAT'] = '%H:%M:%S.%f'
    
    # 환경변수에서 설정 로드
    pawn.fill_config_from_environment()
    
    pawn.console.log(f"환경변수에서 로드된 DEBUG: {pawn.get('PAWN_DEBUG')}")
    pawn.console.log(f"환경변수에서 로드된 VERBOSE: {pawn.get('PAWN_VERBOSE')}")
    pawn.console.log(f"환경변수에서 로드된 TIME_FORMAT: {pawn.get('PAWN_TIME_FORMAT')}")
    
    # 환경변수 우선순위 테스트
    pawn.set(PAWN_DEBUG=False)  # 환경변수가 우선
    pawn.console.log(f"환경변수 우선순위 테스트 - DEBUG: {pawn.get('PAWN_DEBUG')}")
    
    print()


if __name__ == "__main__":
    print("🐍 PawnStack Global Config Demo (레거시 호환)\n")
    
    demo_nested_namespace()
    demo_config_handler()
    demo_pawnstack_config()
    demo_global_instance()
    demo_legacy_compatibility()
    demo_time_format()
    demo_environment_variables()
    demo_rich_integration()
    
    print("✅ 모든 데모 완료!")