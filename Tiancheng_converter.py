import requests
from typing import Dict, List, Union

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
    'BG': '불가리아', 'LU': '룩셈부르크', 'KZ': '카자흐스탄',
}


def country_code_to_emoji(code: str) -> str:
    """2자리 국가 코드를 국기 이모지로 변환 (예: 'KR' -> '🇰🇷')"""
    code = code.strip().upper()
    if len(code) != 2 or not code.isalpha():
        return ''
    return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in code)


def _process_lines(lines: List[str]) -> List[str]:
    """한 URL에서 받은 텍스트(라인 목록)를 변환된 라인 목록으로 가공"""
    result_lines = []
    for line in lines:
        line = line.strip()
        if not line or '#' not in line:
            continue

        # 주소와 태그 분리
        address, tag_content = line.split('#', 1)
        address = address.strip()

        # '|' 로 구분된 필드 분리
        # 형식 예시 1 (tiancheng): 불필요 | 불필요 | 국가코드 | 불필요
        # 형식 예시 2 (cmliu):     불필요 | 국가명(중문) 국가코드 | 불필요
        fields = [f.strip() for f in tag_content.split('|')]

        # 각 필드의 마지막 토큰 중에서 영문 2자리 국가코드를 탐색
        country_code = None
        for field in fields:
            tokens = field.split()
            if not tokens:
                continue
            candidate = tokens[-1].strip().upper()
            if len(candidate) == 2 and candidate.isascii() and candidate.isalpha():
                country_code = candidate
                break

        # 국가코드를 찾지 못한 라인(공지/헤더성 라인)은 스킵
        if not country_code:
            continue

        # 포트 추출
        port = address.split(':')[-1]

        # 국가코드 -> 한국어 국가명 (매핑에 없으면 원본 코드 유지)
        country_name = COUNTRY_MAP.get(country_code, country_code)

        # 새로운 형식 구성: ip:port#영어국가코드 한글국가명 port
        new_line = f"{address}#{country_code} {country_name} {port} 신규"
        result_lines.append(new_line)

    return result_lines


def save_transformed_ip(urls: Union[str, List[str]], output_filename: str):
    """
    urls: 문자열 1개(기존 방식) 또는 문자열 리스트(여러 URL).
    여러 URL을 주면 모두 가져와서 처리한 뒤, 하나의 output_filename 에 합쳐서 저장합니다.
    """
    # 문자열 1개만 들어와도 동작하도록 리스트로 통일
    if isinstance(urls, str):
        urls = [urls]

    all_result_lines: List[str] = []

    for url in urls:
        try:
            # 1. 데이터 가져오기
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            lines = response.text.splitlines()

            processed = _process_lines(lines)
            all_result_lines.extend(processed)

            print(f"  - '{url}' 처리 완료: {len(processed)}개")

        except Exception as e:
            print(f"  - '{url}' 처리 중 오류 발생: {e}")
            continue

    # 2. 파일 쓰기 (모든 URL 결과를 합쳐서 1개 파일로 저장)
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_result_lines) + '\n')
        print(f"성공: '{output_filename}' 파일이 생성되었습니다. (총 {len(all_result_lines)}개, URL {len(urls)}개)")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")


# 실행
# URL을 1개만 쓰고 싶으면 리스트에 1개만, 2개/3개/4개... 쓰고 싶으면 그만큼 추가하면 됩니다.
target_urls = [
    "https://raw.githubusercontent.com/cmliu/WorkerVless2sub/refs/heads/main/addressesapi.txt",
    #"https://bestcf.pages.dev/cmliu/all.txt",
    #"https://bestcf.pages.dev/cmliu2/all.txt",
    # "https://example.com/yet-another.txt",
]

save_transformed_ip(target_urls, "tiancheng.txt")
