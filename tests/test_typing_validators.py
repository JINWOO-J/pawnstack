"""타입 검증 유틸리티 테스트"""

import pytest

from pawnstack.typing.validators import (
    is_json,
    is_int,
    is_float,
    is_number,
    is_hex,
    is_valid_ipv4,
    is_valid_ipv6,
    is_valid_url,
    is_valid_email,
    is_valid_phone,
    is_valid_postal_code,
    is_valid_credit_card,
    is_valid_html_tag,
    is_valid_slug,
    is_valid_date,
    is_valid_time,
    guess_type,
)


def test_is_json():
    """JSON 검증 테스트"""
    # 유효한 JSON
    assert is_json('{"key": "value"}') is True
    assert is_json('["item1", "item2"]') is True
    assert is_json({"key": "value"}) is True
    assert is_json(["item1", "item2"]) is True
    
    # 유효하지 않은 JSON
    assert is_json("not json") is False
    assert is_json("{'key': 'value'}") is False  # 단일 따옴표
    assert is_json(123) is False


def test_is_int():
    """정수 검증 테스트"""
    # 유효한 정수
    assert is_int(123) is True
    assert is_int("123") is True
    assert is_int("-123") is True
    
    # 유효하지 않은 정수
    assert is_int("01") is False  # 앞에 0이 있는 경우
    assert is_int("12.3") is False
    assert is_int("abc") is False
    assert is_int(True) is False  # bool은 제외


def test_is_float():
    """실수 검증 테스트"""
    # 유효한 실수
    assert is_float(12.3) is True
    assert is_float("12.3") is True
    assert is_float("-12.3") is True
    
    # 유효하지 않은 실수
    assert is_float(123) is False  # 정수
    assert is_float("123") is False  # 소수점 없는 문자열
    assert is_float("abc") is False


def test_is_hex():
    """16진수 검증 테스트"""
    # 유효한 16진수
    assert is_hex("0x123") is True
    assert is_hex("0xFF") is True
    assert is_hex("0X123") is True
    
    # 유효하지 않은 16진수
    assert is_hex("123") is False  # 0x 접두사 없음
    assert is_hex("0xGG") is False  # 잘못된 문자
    assert is_hex(123) is False


def test_is_valid_ipv4():
    """IPv4 주소 검증 테스트"""
    # 유효한 IPv4
    assert is_valid_ipv4("192.168.1.1") is True
    assert is_valid_ipv4("255.255.255.255") is True
    assert is_valid_ipv4("0.0.0.0") is True
    
    # 유효하지 않은 IPv4
    assert is_valid_ipv4("256.1.1.1") is False  # 범위 초과
    assert is_valid_ipv4("192.168.1") is False  # 옥텟 부족
    assert is_valid_ipv4("01.02.03.04") is False  # 앞에 0
    assert is_valid_ipv4("192.168.1.1.1") is False  # 옥텟 초과


def test_is_valid_url():
    """URL 검증 테스트"""
    # 유효한 URL
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://test.org/path") is True
    assert is_valid_url("ftp://files.example.com") is True
    
    # 유효하지 않은 URL
    assert is_valid_url("example.com") is False  # 스키마 없음
    assert is_valid_url("http://") is False  # 호스트 없음
    assert is_valid_url("not a url") is False


def test_is_valid_email():
    """이메일 검증 테스트"""
    # 유효한 이메일
    assert is_valid_email("test@example.com") is True
    assert is_valid_email("user.name+tag@domain.co.kr") is True
    
    # 유효하지 않은 이메일
    assert is_valid_email("test@") is False
    assert is_valid_email("@example.com") is False
    assert is_valid_email("test.example.com") is False


def test_is_valid_phone():
    """전화번호 검증 테스트"""
    # 유효한 전화번호
    assert is_valid_phone("+12345678901") is True
    assert is_valid_phone("+821012345678") is True
    
    # 유효하지 않은 전화번호
    assert is_valid_phone("12345") is False  # 너무 짧음
    assert is_valid_phone("01012345678") is False  # + 없음
    assert is_valid_phone("+0123456789") is False  # 0으로 시작


def test_is_valid_credit_card():
    """신용카드 번호 검증 테스트"""
    # 유효한 신용카드 번호 (테스트용)
    assert is_valid_credit_card("4111111111111111") is True  # Visa 테스트 번호
    
    # 유효하지 않은 신용카드 번호
    assert is_valid_credit_card("1234567890123456") is False  # Luhn 체크 실패
    assert is_valid_credit_card("123") is False  # 너무 짧음


def test_guess_type():
    """타입 추측 테스트"""
    assert guess_type(None) == "null"
    assert guess_type(True) == "boolean"
    assert guess_type(123) == "integer"
    assert guess_type(12.3) == "float"
    assert guess_type("hello") == "string"
    assert guess_type("0x123") == "hex_string"
    assert guess_type("https://example.com") == "url"
    assert guess_type("test@example.com") == "email"
    assert guess_type("192.168.1.1") == "ipv4"
    assert guess_type([1, 2, 3]) == "array"
    assert guess_type({"key": "value"}) == "object"


# 추가 테스트들
@pytest.mark.parametrize("value,expected", [
    ("192.168.0.1", True),
    ("255.255.255.255", True),
    ("0.0.0.0", True),
    ("172.16.254.1", True),
    ("256.100.100.100", False),
    ("-1.100.100.100", False),
    ("192.168.0", False),
    ("192.168.0.1.", False),
    ("192.abc.0.1", False),
    ("01.02.03.04", False),
    ("192.168.0.1.1", False),
    ("", False),
    ("    ", False),
    ("192..168.1", False),
    (" 192.168.0.1 ", False),
    ("999.999.999.999", False),
])
def test_ipv4_validation_comprehensive(value, expected):
    """포괄적인 IPv4 검증 테스트"""
    assert is_valid_ipv4(value) == expected


@pytest.mark.parametrize("email,expected", [
    ("example@test.com", True),
    ("user.name+tag@domain.co.kr", True),
    ("test123@example-site.org", True),
    ("example.com", False),
    ("@example.com", False),
    ("test@", False),
    ("test..test@example.com", False),
])
def test_email_validation_comprehensive(email, expected):
    """포괄적인 이메일 검증 테스트"""
    assert is_valid_email(email) == expected