import requests
from typing import Dict

# 국가 코드 -> 한국어 국가명 매핑
COUNTRY_MAP: Dict[str, str] = {
    'HK': '홍콩', 'SG': '싱가포르', 'JP': '일본', 'KR': '한국',
    'TW': '대만', 'US': '미국', 'GB': '영국', 'FR': '프랑스',
    'DE': '독일', 'NL': '네덜란드', 'CA': '캐나다', 'CN': '중국',
    'RU': '러시아', 'IN': '인도', 'AU': '호주', 'BR': '브라질',
    'ID': '인도네시아', 'VN': '베트남', 'TH': '태국', 'MY': '말레이시아',
    'PH': '필리핀', 'IT': '이탈리아', 'ES': '스페인', 'CH': '스위스',
    'SE': '스웨덴', 'NO': '노르웨이', 'FI': '핀란드', 'DK': '덴마크',
    'PL': '폴란드', 'TR': '터키', 'AE': '아랍에미리트', 'SA': '사우디아라비아',
    'ZA': '남아프리카공화국', 'MX': '멕시코', 'AR': '아르헨티나', 'UA': '우크라이나',
    'IE': '아일랜드', 'BE': '벨기에', 'AT': '오스트리아', 'PT': '포르투갈',
    'NZ': '뉴질랜드', 'IL': '이스라엘', 'EG': '이집트', 'KH': '캄보디아',
    'LA': '라오스', 'MM': '미얀마', 'MO': '마카오', 'BD': '방글라데시',
    'PK': '파키스탄', 'IR': '이란', 'IQ': '이라크', 'MN': '몽골',
    'CZ': '체코', 'RO': '루마니아', 'HU': '헝가리', 'GR': '그리스',
    'BG': '불가리아', 'LU': '룩셈부르크',
}


def country_code_to_emoji(code: str) -> str:
    """2자리 국가 코드를 국기 이모지로 변환 (예: 'KR' -> '🇰🇷')"""
    code = code.strip().upper()
    if len(code) != 2 or not code.isalpha():
        return ''
    return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in code)


def save_transformed_ip(url: str, output_filename: str):
    try:
        # 1. 데이터 가져오기
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()

        result_lines = []

        for line in lines:
            line = line.strip()
            if not line or '#' not in line:
                continue

            # 주소와 태그 분리
            address, tag_content = line.split('#', 1)
            address = address.strip()

            # '|' 로 구분된 필드 분리
            # 형식: ip:port#불필요 | 불필요 | 국가코드 | 불필요
            fields = [f.strip() for f in tag_content.split('|')]

            # 국가코드 필드(index=2)가 없는 라인(공지/헤더성 라인)은 스킵
            if len(fields) < 3:
                continue

            country_code = fields[2].upper()

            # 유효한 국가코드(영문 2자리)인지 확인
            if len(country_code) != 2 or not country_code.isalpha():
                continue

            # 포트 추출
            port = address.split(':')[-1]

            # 국기 이모지 생성
            emoji = country_code_to_emoji(country_code)

            # 국가코드 -> 한국어 국가명 (매핑에 없으면 원본 코드 유지)
            country_name = COUNTRY_MAP.get(country_code, country_code)

            # 새로운 형식 구성: ip:port#국가이모지 국가명(한국어) port
            new_line = f"{address}#{emoji} {country_name} {port} 신규"
            result_lines.append(new_line)

        # 2. 파일 쓰기
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result_lines) + '\n')

        print(f"성공: '{output_filename}' 파일이 생성되었습니다. (총 {len(result_lines)}개)")

    except Exception as e:
        print(f"오류 발생: {e}")


# 실행
target_url = "https://bestcf.pages.dev/tiancheng/all.txt"
save_transformed_ip(target_url, "tiancheng.txt")
