"""파일 유틸리티 테스트"""

import pytest
import tempfile
import shutil
from pathlib import Path

from pawnstack.utils.file import (
    write_file,
    write_json,
    write_yaml,
    read_file,
    read_json,
    read_yaml,
    is_file,
    is_directory,
)


@pytest.fixture
def temp_dir():
    """임시 디렉토리 픽스처"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


def test_write_and_read_text_file(temp_dir):
    """텍스트 파일 쓰기/읽기 테스트"""
    filename = temp_dir / "test.txt"
    content = "Hello, PawnStack!"
    
    # 파일 쓰기
    result = write_file(filename, content)
    assert result is True
    
    # 파일 읽기
    read_content = read_file(filename)
    assert content == read_content


def test_write_and_read_json_file(temp_dir):
    """JSON 파일 쓰기/읽기 테스트"""
    filename = temp_dir / "test.json"
    data = {"name": "PawnStack", "version": "1.0.0", "features": ["http", "system"]}
    
    # JSON 파일 쓰기
    result = write_json(filename, data)
    assert result is True
    
    # JSON 파일 읽기
    read_data = read_json(filename)
    assert data == read_data


def test_write_and_read_yaml_file(temp_dir):
    """YAML 파일 쓰기/읽기 테스트"""
    filename = temp_dir / "test.yaml"
    data = {"app": {"name": "PawnStack", "config": {"debug": True, "port": 8080}}}
    
    # YAML 파일 쓰기
    result = write_yaml(filename, data)
    assert result is True
    
    # YAML 파일 읽기
    read_data = read_yaml(filename)
    assert data == read_data


def test_file_existence_check(temp_dir):
    """파일 존재 여부 확인 테스트"""
    filename = temp_dir / "exists.txt"
    
    # 파일이 없을 때
    assert is_file(filename) is False
    
    # 파일 생성 후
    write_file(filename, "test")
    assert is_file(filename) is True


def test_directory_existence_check(temp_dir):
    """디렉토리 존재 여부 확인 테스트"""
    dirname = temp_dir / "subdir"
    
    # 디렉토리가 없을 때
    assert is_directory(dirname) is False
    
    # 디렉토리 생성 후
    dirname.mkdir()
    assert is_directory(dirname) is True


def test_nonexistent_file_read(temp_dir):
    """존재하지 않는 파일 읽기 테스트"""
    filename = temp_dir / "nonexistent.txt"
    
    result = read_file(filename)
    assert result is None
    
    result = read_json(filename)
    assert result is None
    
    result = read_yaml(filename)
    assert result is None