import re
import requests
import yaml
from typing import List, Dict, Any

# 국가 매핑 정보 (중국어 간체 및 영어 코드 통합)
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
    'NL': '네덜란드', 'NLD': '네덜란드', '荷兰': '네덜란드'
}

def get_info_from_name(name: str):
    """이름에서 국가코드와 한국어 이름을 추출 (중국어 우선순위)"""
    name_upper = name.upper()
    
    # 1. 매핑 테이블에 있는 키워드(중국어/영어)가 이름에 포함되어 있는지 확인
    for keyword, kor_name in COUNTRY_MAP.items():
        if keyword in name_upper:
            # 코드 변환 (3자리 -> 2자리 혹은 중국어 -> 영어코드)
            code = 'HK' if kor_name == '홍콩' else \
                   'SG' if kor_name == '싱가포르' else \
                   'JP' if kor_name == '일본' else \
                   'KR' if kor_name == '한국' else \
                   'TW' if kor_name == '대만' else \
                   'US' if kor_name == '미국' else \
                   'GB' if kor_name == '영국' else \
                   'FR' if kor_name == '프랑스' else \
                   'DE' if kor_name == '독일' else \
                   'NL' if kor_name == '네덜란드' else keyword[:2]
            return code, kor_name
            
    # 2. 못 찾았다면 정규식으로 영어 2~3글자 추출 시도
    match = re.search(r'([A-Z]{2,3})', name_upper)
    if match:
        code = match.group(1)
        return code, COUNTRY_MAP.get(code, code)

    return 'N/A', '알수없음'

def extract_all_proxies(url: str) -> List[str]:
    extracted_data = []
    try:
        response = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        config_data = yaml.safe_load(response.text)
        
        if not config_data or 'proxies' not in config_data:
            return []

        for proxy in config_data['proxies']:
            server = str(proxy.get('server', ''))
            port = proxy.get('port', '')
            name = proxy.get('name', '')
            if not server or not port: continue

            # 국가 정보 추출
            raw_code, kor_name = get_info_from_name(name)

            # CF优选/移动优选 등 특수 처리
            if any(keyword in name for keyword in ['优选', 'CF', 'Tg里的']):
                raw_code = 'HK'
                kor_name = 'SPEED'

            # 정렬용 키 생성 (IP는 숫자 리스트, 도메인은 문자열로 처리하여 에러 방지)
            try:
                # IPv4인 경우 숫자 리스트로 변환하여 자연스러운 정렬 지원
                sort_key = list(map(int, server.split('.')))
            except (ValueError, AttributeError):
                # 도메인이나 IPv6인 경우 정렬 시 에러 방지를 위해 큰 값 부여
                sort_key = [999, 999, 999, 999]

            entry_str = f"{server}:{port}#{raw_code} {kor_name} {port}"
            
            # 중복 제거 (이미 저장된 문자열인지 확인)
            if not any(e['string'] == entry_str for e in extracted_data):
                extracted_data.append({'sort_key': sort_key, 'string': entry_str})

        # 정렬 (IP 순서대로, 도메인은 뒤로)
        extracted_data.sort(key=lambda x: (isinstance(x['sort_key'], list), x['sort_key']))
        
        return [e['string'] for e in extracted_data]

    except Exception as e:
        print(f"오류 발생: {e}")
        return []
        
# URL
#REAL_TARGET_URL = "https://api.subcsub.com/sub?target=clash&url=https%3A%2F%2Fcm.soso.edu.kg%2Fsub%3Fpassword%3Daaa%26security%3Dtls%26type%3Dws%26host%3Daaaa%26sni%3Daaa%26path%3D%252Fproxyip%253DProxyIP.JP.CMLiussss.Net%26encryption%3Dnone%26allowInsecure%3D1&insert=false&config=https%3A%2F%2Fraw.githubusercontent.com%2Fcmliu%2FACL4SSR%2Fmain%2FClash%2Fconfig%2FACL4SSR_Online.ini&emoji=true&list=true&xudp=false&udp=false&tfo=false&expand=true&scv=false&fdn=false&new_name=true"
REAL_TARGET_URL = "https://api.subcsub.com/sub?target=clash&url=https%3A%2F%2Fcm.soso.edu.kg%2Fsub%3Fpassword%3Daaa%26security%3Dtls%26type%3Dws%26host%3Daaaa%26sni%3Daaa%26path%3D%252Fproxyip%253DProxyIP.JP.CMLiussss.Net%26encryption%3Dnone%26allowInsecure%3D1%7Chttps%3A%2F%2Fsub.cmliussss.net%2Fsub%3Fpassword%3Daaa%26security%3Dtls%26type%3Dws%26host%3Daaaa%26sni%3Daaa%26path%3D%252Fproxyip%253DProxyIP.JP.CMLiussss.Net%26encryption%3Dnone%26allowInsecure%3D1&insert=false"
if __name__ == "__main__":
    print("프록시 목록 다운로드 및 변환 시작...")
    extracted_list = extract_ip_port_country_code_yaml(REAL_TARGET_URL)

    # cfproxy.txt 파일로 저장
    if extracted_list:
        OUTPUT_FILE = "cfproxy.txt"
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for item in extracted_list:
                f.write(item + "\n")
        print(f"변환 완료: 총 {len(extracted_list)}개의 항목이 {OUTPUT_FILE}에 저장되었습니다.")
    else:
        print("유효한 프록시 항목이 추출되지 않았습니다. 파일이 저장되지 않았습니다.")
