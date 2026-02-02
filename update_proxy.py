import re
import requests
import yaml
from typing import List, Dict, Any

# 1. 국가 매핑 정보
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

def get_info_from_name(name: str):
    """이름에서 국가코드와 한국어 이름을 추출"""
    name_upper = name.upper()
    
    for keyword, kor_name in COUNTRY_MAP.items():
        if keyword in name_upper:
            # 대표 코드 설정
            code_mapping = {'홍콩':'HK', '싱가포르':'SG', '일본':'JP', '한국':'KR', '대만':'TW', '미국':'US', '네덜란드':'NL'}
            code = code_mapping.get(kor_name, keyword[:2])
            return code, kor_name
            
    match = re.search(r'([A-Z]{2,3})', name_upper)
    if match:
        code = match.group(1)
        return code, COUNTRY_MAP.get(code, code)

    return 'N/A', '알수없음'

def extract_ip_port_country_code_yaml(url: str) -> List[str]:
    """YAML에서 프록시 추출 (도메인/중국어 완벽 지원)"""
    extracted_data = []
    try:
        response = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        config_data = yaml.safe_load(response.text)
        
        if not config_data or 'proxies' not in config_data:
            print("데이터를 찾을 수 없습니다.")
            return []

        for proxy in config_data['proxies']:
            server = str(proxy.get('server', ''))
            port = proxy.get('port', '')
            name = proxy.get('name', '')
            if not server or not port: continue

            # 국가 정보 추출
            raw_code, kor_name = get_info_from_name(name)

            # 최적화 노드(CF, 优选 등) 특수 처리
            if any(keyword in name for keyword in ['优选', 'CF', 'Tg', '频道', '群组']):
                raw_code = 'HK'
                kor_name = 'SPEED'

            # 정렬 키 생성
            try:
                sort_key = list(map(int, server.split('.')))
            except:
                sort_key = [999, 999, 999, 999] # 도메인/IPv6는 하단 정렬

            entry_str = f"{server}:{port}#{raw_code} {kor_name} {port}"
            
            if not any(e['string'] == entry_str for e in extracted_data):
                extracted_data.append({'sort_key': sort_key, 'string': entry_str})

        # IP 기준 정렬
        extracted_data.sort(key=lambda x: (len(x['sort_key']) != 4, x['sort_key']))
        return [e['string'] for e in extracted_data]

    except Exception as e:
        print(f"오류 발생: {e}")
        return []

# --- 실행 부분 (함수 이름 일치 완료) ---
REAL_TARGET_URL = "https://api.subcsub.com/sub?target=clash&url=https%3A%2F%2Fcm.soso.edu.kg%2Fsub%3Fpassword%3Daaa%26security%3Dtls%26type%3Dws%26host%3Daaaa%26sni%3Daaa%26path%3D%252Fproxyip%253DProxyIP.JP.CMLiussss.Net%26encryption%3Dnone%26allowInsecure%3D1%7Chttps%3A%2F%2Fsub.cmliussss.net%2Fsub%3Fpassword%3Daaa%26security%3Dtls%26type%3Dws%26host%3Daaaa%26sni%3Daaa%26path%3D%252Fproxyip%253DProxyIP.JP.CMLiussss.Net%26encryption%3Dnone%26allowInsecure%3D1&insert=false"

if __name__ == "__main__":
    print("프록시 목록 다운로드 및 변환 시작...")
    extracted_list = extract_ip_port_country_code_yaml(REAL_TARGET_URL)

    if extracted_list:
        OUTPUT_FILE = "cfproxy.txt"
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for item in extracted_list:
                f.write(item + "\n")
        print(f"변환 완료: 총 {len(extracted_list)}개의 항목이 {OUTPUT_FILE}에 저장되었습니다.")
    else:
        print("유효한 프록시 항목이 추출되지 않았습니다.")
