import re
import requests
import yaml
from typing import List, Dict, Any

# 1. 국가 키워드 매핑 (영어 및 중국어 포함)
COUNTRY_MAP: Dict[str, str] = {
    # 영어 코드
    'HK': '홍콩', 'HKG': '홍콩', 'SG': '싱가포르', 'SGP': '싱가포르', 
    'JP': '일본', 'JPN': '일본', 'KR': '한국', 'KOR': '한국', 
    'TW': '대만', 'TWN': '대만', 'CN': '중국', 'CHN': '중국',
    'US': '미국', 'USA': '미국',
    # 중국어 간체 (사용자 요청 반영)
    '香港': '홍콩', '日本': '일본', '新加坡': '싱가포르', '美国': '미국',
    '韩国': '한국', '台湾': '대만', '中国': '중국', '德': '독일', '英': '영국'
}

# 2. 통신사 및 기타 키워드 번역 (선택 사항)
ISP_MAP: Dict[str, str] = {
    '电信': '텔레콤', '联通': '유니콤', '移动': '이', '优选': '최적화'
}

def translate_name_to_info(name: str):
    """이름에서 국가 코드와 한국어 이름을 추출"""
    raw_code = 'N/A'
    kor_name = '알수없음'

    # 1. 중국어 키워드 우선 체크
    for cn_key, ko_val in COUNTRY_MAP.items():
        if cn_key in name:
            kor_name = ko_val
            # 출력 형식 유지를 위해 대표 코드 할당 (예: 홍콩 -> HK)
            reverse_map = {'홍콩': 'HK', '일본': 'JP', '싱가포르': 'SG', '미국': 'US', '한국': 'KR', '대만': 'TW', '중국': 'CN'}
            raw_code = reverse_map.get(ko_val, 'ETC')
            break
    
    # 2. 중국어가 없고 영어 코드가 있는 경우 (기존 로직)
    if raw_code == 'N/A':
        match = re.search(r'([A-Z]{2,3})', name.upper())
        if match:
            raw_code = match.group(1)
            # 기존 COUNTRY_MAP에서 한국어 이름 찾기
            kor_name = COUNTRY_MAP.get(raw_code, raw_code)

    return raw_code, kor_name

def extract_ip_port_country_code_yaml(url: str) -> List[str]:
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

            # 국가 정보 추출 (중국어/영어 통합 처리)
            raw_country_code, korean_name = translate_name_to_info(name)

            # --- CF(Cloudflare) 특수 처리 로직 ---
            if 'CF' in name.upper() or '优选' in name:
                raw_country_code = 'HK' 
                korean_name = 'SPEED'
            # ------------------------------------

            # IP 형식 확인 (IPv6 고려)
            is_ipv6 = '[' in server or ':' in server.replace('.', '')
            
            # 정렬을 위한 가중치 (IPv4는 숫자 리스트, IPv6/도메인은 문자열)
            try:
                ip_parts = list(map(int, server.split('.'))) if not is_ipv6 else [999, 999, 999, 999]
            except ValueError:
                ip_parts = [999, 999, 999, 999] # 도메인인 경우 맨 뒤로

            entry_str = f"{server}:{port}#{raw_country_code} {korean_name} {port}"
            
            if entry_str not in [e['string'] for e in extracted_data]:
                extracted_data.append({'ip_parts': ip_parts, 'string': entry_str})

        extracted_data.sort(key=lambda x: x['ip_parts'])
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
