"""PawnStack 유틸리티 기능 데모"""

import tempfile
from pathlib import Path

from pawnstack.utils.file import write_json, read_json, write_yaml, read_yaml
from pawnstack.typing.validators import (
    is_valid_url, is_valid_email, is_valid_ipv4, 
    guess_type, is_hex, is_json
)


def demo_file_utils():
    """파일 유틸리티 데모"""
    print("🗂️  파일 유틸리티 데모")
    print("=" * 50)
    
    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # JSON 파일 처리
        json_file = temp_path / "config.json"
        config_data = {
            "app": {
                "name": "PawnStack",
                "version": "1.0.0",
                "debug": True
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "pawnstack_db"
            }
        }
        
        print(f"📝 JSON 파일 쓰기: {json_file}")
        write_json(json_file, config_data)
        
        print(f"📖 JSON 파일 읽기:")
        loaded_config = read_json(json_file)
        print(f"   앱 이름: {loaded_config['app']['name']}")
        print(f"   버전: {loaded_config['app']['version']}")
        
        # YAML 파일 처리
        yaml_file = temp_path / "settings.yaml"
        settings_data = {
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 4
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        print(f"\n📝 YAML 파일 쓰기: {yaml_file}")
        write_yaml(yaml_file, settings_data)
        
        print(f"📖 YAML 파일 읽기:")
        loaded_settings = read_yaml(yaml_file)
        print(f"   서버 포트: {loaded_settings['server']['port']}")
        print(f"   로그 레벨: {loaded_settings['logging']['level']}")


def demo_type_validators():
    """타입 검증 유틸리티 데모"""
    print("\n🔍 타입 검증 유틸리티 데모")
    print("=" * 50)
    
    # 테스트 데이터
    test_data = [
        ("https://pawnstack.dev", "URL"),
        ("admin@pawnstack.dev", "이메일"),
        ("192.168.1.100", "IPv4 주소"),
        ("0xFF00", "16진수"),
        ('{"name": "PawnStack"}', "JSON 문자열"),
        ("not-a-valid-email", "잘못된 이메일"),
        ("256.300.400.500", "잘못된 IP"),
        (42, "정수"),
        (3.14, "실수"),
        (["item1", "item2"], "배열"),
    ]
    
    print("📋 다양한 데이터 타입 검증:")
    for data, description in test_data:
        print(f"\n   데이터: {data}")
        print(f"   설명: {description}")
        print(f"   추측된 타입: {guess_type(data)}")
        
        # 구체적인 검증
        validations = []
        if isinstance(data, str):
            if is_valid_url(data):
                validations.append("✅ 유효한 URL")
            if is_valid_email(data):
                validations.append("✅ 유효한 이메일")
            if is_valid_ipv4(data):
                validations.append("✅ 유효한 IPv4")
            if is_hex(data):
                validations.append("✅ 16진수")
            if is_json(data):
                validations.append("✅ JSON 형식")
        
        if validations:
            print(f"   검증 결과: {', '.join(validations)}")
        else:
            print(f"   검증 결과: ❌ 특별한 형식 아님")


def demo_practical_usage():
    """실용적인 사용 예제"""
    print("\n🛠️  실용적인 사용 예제")
    print("=" * 50)
    
    # 설정 파일 검증 및 처리
    user_inputs = [
        "https://api.example.com",
        "admin@company.com", 
        "192.168.1.1",
        "invalid-url",
        "not-an-email"
    ]
    
    print("📝 사용자 입력 검증 및 분류:")
    
    urls = []
    emails = []
    ips = []
    invalid_inputs = []
    
    for user_input in user_inputs:
        print(f"\n   입력: {user_input}")
        
        if is_valid_url(user_input):
            urls.append(user_input)
            print(f"   → URL로 분류됨")
        elif is_valid_email(user_input):
            emails.append(user_input)
            print(f"   → 이메일로 분류됨")
        elif is_valid_ipv4(user_input):
            ips.append(user_input)
            print(f"   → IP 주소로 분류됨")
        else:
            invalid_inputs.append(user_input)
            print(f"   → ❌ 유효하지 않은 입력")
    
    # 분류 결과를 파일로 저장
    with tempfile.TemporaryDirectory() as temp_dir:
        result_file = Path(temp_dir) / "validation_results.json"
        
        results = {
            "urls": urls,
            "emails": emails,
            "ip_addresses": ips,
            "invalid_inputs": invalid_inputs,
            "summary": {
                "total_inputs": len(user_inputs),
                "valid_inputs": len(urls) + len(emails) + len(ips),
                "invalid_inputs": len(invalid_inputs)
            }
        }
        
        write_json(result_file, results)
        print(f"\n📊 검증 결과가 {result_file}에 저장되었습니다.")
        
        # 결과 요약 출력
        summary = results["summary"]
        print(f"\n📈 검증 요약:")
        print(f"   전체 입력: {summary['total_inputs']}개")
        print(f"   유효한 입력: {summary['valid_inputs']}개")
        print(f"   유효하지 않은 입력: {summary['invalid_inputs']}개")


def main():
    """메인 함수"""
    print("🏗️ PawnStack 유틸리티 기능 데모")
    print("=" * 60)
    
    try:
        demo_file_utils()
        demo_type_validators()
        demo_practical_usage()
        
        print("\n✅ 모든 데모가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    main()