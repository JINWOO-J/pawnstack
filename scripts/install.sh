#!/bin/bash

# PawnStack 설치 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 배너 출력
print_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
    ██████╗  █████╗ ██╗    ██╗███╗   ██╗███████╗████████╗ █████╗  ██████╗██╗  ██╗
    ██╔══██╗██╔══██╗██║    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝
    ██████╔╝███████║██║ █╗ ██║██╔██╗ ██║███████╗   ██║   ███████║██║     █████╔╝ 
    ██╔═══╝ ██╔══██║██║███╗██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██╔═██╗ 
    ██║     ██║  ██║╚███╔███╔╝██║ ╚████║███████║   ██║   ██║  ██║╚██████╗██║  ██╗
    ╚═╝     ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
EOF
    echo -e "${NC}"
    echo -e "${GREEN}차세대 Infrastructure as Code (IaC) Python 라이브러리${NC}"
    echo ""
}

# Python 버전 확인
check_python() {
    log_info "Python 버전 확인 중..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3이 설치되어 있지 않습니다."
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    required_version="3.9"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
        log_success "Python $python_version 확인됨"
    else
        log_error "Python $required_version 이상이 필요합니다. 현재 버전: $python_version"
        exit 1
    fi
}

# pip 업그레이드
upgrade_pip() {
    log_info "pip 업그레이드 중..."
    python3 -m pip install --upgrade pip
    log_success "pip 업그레이드 완료"
}

# PawnStack 설치
install_pawnstack() {
    local install_type=$1
    
    case $install_type in
        "basic")
            log_info "PawnStack 기본 설치 중..."
            python3 -m pip install pawnstack
            ;;
        "full")
            log_info "PawnStack 전체 기능 설치 중..."
            python3 -m pip install "pawnstack[full]"
            ;;
        "dev")
            log_info "PawnStack 개발 환경 설치 중..."
            python3 -m pip install "pawnstack[dev,docs]"
            ;;
        *)
            log_error "알 수 없는 설치 타입: $install_type"
            exit 1
            ;;
    esac
    
    log_success "PawnStack 설치 완료"
}

# 설치 확인
verify_installation() {
    log_info "설치 확인 중..."
    
    if python3 -c "import pawnstack; print(f'PawnStack {pawnstack.__version__} 설치됨')" 2>/dev/null; then
        log_success "설치 확인 완료"
        
        # CLI 테스트
        if command -v pawnstack &> /dev/null; then
            log_success "CLI 명령어 사용 가능: pawnstack"
        else
            log_warning "CLI 명령어를 찾을 수 없습니다. PATH를 확인하세요."
        fi
    else
        log_error "설치 확인 실패"
        exit 1
    fi
}

# 사용법 출력
show_usage() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -t, --type TYPE    설치 타입 (basic|full|dev) [기본값: basic]"
    echo "  -h, --help         도움말 출력"
    echo ""
    echo "설치 타입:"
    echo "  basic    기본 기능만 설치"
    echo "  full     모든 선택적 기능 포함 설치"
    echo "  dev      개발 환경 설치"
    echo ""
    echo "예시:"
    echo "  $0                    # 기본 설치"
    echo "  $0 -t full           # 전체 기능 설치"
    echo "  $0 -t dev            # 개발 환경 설치"
}

# 메인 함수
main() {
    local install_type="basic"
    
    # 인수 파싱
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                install_type="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "알 수 없는 옵션: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # 설치 타입 검증
    if [[ ! "$install_type" =~ ^(basic|full|dev)$ ]]; then
        log_error "잘못된 설치 타입: $install_type"
        show_usage
        exit 1
    fi
    
    print_banner
    
    log_info "PawnStack 설치를 시작합니다..."
    log_info "설치 타입: $install_type"
    echo ""
    
    check_python
    upgrade_pip
    install_pawnstack "$install_type"
    verify_installation
    
    echo ""
    log_success "🎉 PawnStack 설치가 완료되었습니다!"
    echo ""
    echo "다음 명령어로 시작해보세요:"
    echo "  pawnstack --help"
    echo "  pawnstack info"
    echo "  pawnstack banner"
    echo ""
    echo "문서: https://pawnstack.readthedocs.io"
    echo "GitHub: https://github.com/jinwoo-j/pawnstack"
}

# 스크립트 실행
main "$@"