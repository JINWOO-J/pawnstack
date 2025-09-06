"""파일 I/O 유틸리티"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, Union, Optional

from pawnstack.core.mixins import LoggerMixin


class FileHandler(LoggerMixin):
    """파일 처리 유틸리티 클래스"""
    
    def __init__(self):
        super().__init__()
    
    def write_file(self, filename: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
        """텍스트 파일 쓰기"""
        try:
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            
            self.logger.debug(f"파일 쓰기 완료: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"파일 쓰기 실패 {filename}: {e}")
            return False
    
    def write_json(self, filename: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> bool:
        """JSON 파일 쓰기"""
        try:
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            self.logger.debug(f"JSON 파일 쓰기 완료: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"JSON 파일 쓰기 실패 {filename}: {e}")
            return False
    
    def write_yaml(self, filename: Union[str, Path], data: Dict[str, Any]) -> bool:
        """YAML 파일 쓰기"""
        try:
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.debug(f"YAML 파일 쓰기 완료: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"YAML 파일 쓰기 실패 {filename}: {e}")
            return False
    
    def read_file(self, filename: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
        """텍스트 파일 읽기"""
        try:
            filepath = Path(filename)
            
            if not filepath.exists():
                self.logger.warning(f"파일이 존재하지 않음: {filepath}")
                return None
            
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            
            self.logger.debug(f"파일 읽기 완료: {filepath}")
            return content
            
        except Exception as e:
            self.logger.error(f"파일 읽기 실패 {filename}: {e}")
            return None
    
    def read_json(self, filename: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """JSON 파일 읽기"""
        try:
            filepath = Path(filename)
            
            if not filepath.exists():
                self.logger.warning(f"JSON 파일이 존재하지 않음: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"JSON 파일 읽기 완료: {filepath}")
            return data
            
        except Exception as e:
            self.logger.error(f"JSON 파일 읽기 실패 {filename}: {e}")
            return None
    
    def read_yaml(self, filename: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """YAML 파일 읽기"""
        try:
            filepath = Path(filename)
            
            if not filepath.exists():
                self.logger.warning(f"YAML 파일이 존재하지 않음: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.logger.debug(f"YAML 파일 읽기 완료: {filepath}")
            return data
            
        except Exception as e:
            self.logger.error(f"YAML 파일 읽기 실패 {filename}: {e}")
            return None
    
    def is_file(self, filename: Union[str, Path]) -> bool:
        """파일 존재 여부 확인"""
        return Path(filename).is_file()
    
    def is_directory(self, dirname: Union[str, Path]) -> bool:
        """디렉토리 존재 여부 확인"""
        return Path(dirname).is_dir()
    
    def get_file_size(self, filename: Union[str, Path]) -> Optional[int]:
        """파일 크기 조회 (바이트)"""
        try:
            filepath = Path(filename)
            if filepath.exists():
                return filepath.stat().st_size
            return None
        except Exception as e:
            self.logger.error(f"파일 크기 조회 실패 {filename}: {e}")
            return None


# 전역 인스턴스
file_handler = FileHandler()

# 편의 함수들
def write_file(filename: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
    """텍스트 파일 쓰기"""
    return file_handler.write_file(filename, content, encoding)

def write_json(filename: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> bool:
    """JSON 파일 쓰기"""
    return file_handler.write_json(filename, data, indent)

def write_yaml(filename: Union[str, Path], data: Dict[str, Any]) -> bool:
    """YAML 파일 쓰기"""
    return file_handler.write_yaml(filename, data)

def read_file(filename: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
    """텍스트 파일 읽기"""
    return file_handler.read_file(filename, encoding)

def read_json(filename: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """JSON 파일 읽기"""
    return file_handler.read_json(filename)

def read_yaml(filename: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """YAML 파일 읽기"""
    return file_handler.read_yaml(filename)

def is_file(filename: Union[str, Path]) -> bool:
    """파일 존재 여부 확인"""
    return file_handler.is_file(filename)

def is_directory(dirname: Union[str, Path]) -> bool:
    """디렉토리 존재 여부 확인"""
    return file_handler.is_directory(dirname)