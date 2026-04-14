import requests
from typing import Dict

# 국가 매핑 딕셔너리
COUNTRY_MAP: Dict[str, str] = {
    'HK': '홍콩', 'HKG': '홍콩', '香港': '홍콩',
    'SG': '싱가포르', 'SGP': '싱가포르', '新加坡': '싱가포르',
    'JP': '일본', 'JPN': '일본', '日本': '일본',
    'KR': '한국', 'KOR': '한국', '韩国': '한국',
    'TW': '대만', 'TWN': '대만', '台湾': '대만',
    'US': '미국', 'USA': '미국', '美国': '미국',
    'GB': '영국', 'GBR': '영국', '英': '영국',
    'FR': '프랑스', 'FRA': '프랑스', '法国': '프랑스',
    'DE': '독일', 'DEU': '독일', '德': '독일',
    'NL': '네덜란드', 'NLD': '네덜란드', '荷兰': '네덜란드',
    'CF': 'SPEED'
}

def save_transformed_ip(url: str, output_filename: str):
    try:
        # 1. 데이터 가져오기
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        
        # 2. 파일 쓰기 모드로 열기
        with open(output_filename, 'w', encoding='utf-8') as f:
            for line in lines:
                line = line.strip()
                if not line or '#' not in line:
                    continue
                
                # 주소와 태그 분리
                address, tag_content = line.split('#', 1)
                port = address.split(':')[-1]
                
                # 국가 코드 추출
                raw_country = tag_content.split('_')[0].upper()
                
                # 국가명 매핑 (없으면 원본 유지)
                country_name = COUNTRY_MAP.get(raw_country, raw_country)
                
                # 새로운 형식 구성
                new_line = f"{address}#{raw_country} {country_name} {port}\n"
                
                # 파일에 쓰기
                f.write(new_line)
        
        print(f"성공: '{output_filename}' 파일이 생성되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

# 실행
target_url = "https://raw.githubusercontent.com/rxsweet/cfip/refs/heads/main/aliveip.txt"
save_transformed_ip(target_url, "aliveip.txt")
