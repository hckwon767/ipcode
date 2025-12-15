import re
import requests
import yaml # YAML 파서 라이브러리 (pip install pyyaml 필요)
from typing import List, Dict, Any

# 국가 코드 -> 한국어 국가명 매핑
# (기존 맵을 그대로 사용)
COUNTRY_CODE_TO_KOREAN: Dict[str, str] = {
    'HK': '홍콩', 'HKG': '홍콩', 'SG': '싱가포르', 'SGP': '싱가포르', 
    'JP': '일본', 'JPN': '일본', 'KR': '한국', 'KOR': '한국', 
    'TW': '대만', 'TWN': '대만', 'CN': '중국', 'CHN': '중국',
    'US': '미국', 'USA': '미국', 'GB': '영국', 'GBR': '영국',
    'FR': '프랑스', 'FRA': '프랑스', 'DE': '독일', 'DEU': '독일',
    'IT': '이탈리아', 'ITA': '이탈리아', 'ES': '스페인', 'ESP': '스페인',
}

# 정규식 패턴: 이름에서 2~3자리 국가 코드를 찾기 위함
# 예: 🚀US-Proxy -> US, HKG-Node -> HKG
NAME_COUNTRY_PATTERN = re.compile(r'(?P<country_code>[A-Z]{2,3})', re.IGNORECASE)


def get_korean_country_name(country_code: str) -> str:
    """국가 코드를 한국어 국가명으로 변환 및 3자리 -> 2자리 코드 처리"""
    if not country_code or country_code == 'N/A':
        return '알수없음'
    
    code_upper = country_code.upper()
    
    # 1. 맵에 직접 매칭 시도
    if code_upper in COUNTRY_CODE_TO_KOREAN:
        return COUNTRY_CODE_TO_KOREAN[code_upper]
    
    # 2. 3자리 코드인 경우 2자리로 잘라서 매칭 시도 (예: KOR -> KR)
    if len(code_upper) == 3:
        two_char_code = code_upper[:2]
        if two_char_code in COUNTRY_CODE_TO_KOREAN:
            return COUNTRY_CODE_TO_KOREAN[two_char_code]
    
    # 3. 매칭되는 이름이 없는 경우 원래 코드를 반환
    return code_upper


def extract_ip_port_country_code_yaml(url: str) -> List[str]:
    """
    URL에서 YAML 데이터를 가져와 PyYAML 파서로 파싱 후, 
    프록시 목록에서 IP, Port, 국가 코드를 추출하고 정렬하여 반환합니다.
    """
    extracted_data: List[Dict[str, Any]] = []
    
    try:
        # 1. 데이터 다운로드
        response = requests.get(
            url, 
            timeout=20, # 타임아웃을 20초로 늘려 안정성 확보
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response.raise_for_status() # HTTP 오류 발생 시 예외 처리
        
        # 2. YAML 파싱
        config_data = yaml.safe_load(response.text)
        
        if not isinstance(config_data, dict) or 'proxies' not in config_data:
            print("오류: 다운로드된 콘텐츠가 유효한 YAML 형식이거나 'proxies' 키를 포함하지 않습니다.")
            return []
            
        # 3. 프록시 목록 순회 및 추출
        for proxy in config_data['proxies']:
            # 필요한 키가 모두 있는지 확인
            server = proxy.get('server')
            port = proxy.get('port')
            name = proxy.get('name', '')
            
            if not server or not port:
                continue
            
            # 이름에서 국가 코드 추출 시도
            match = NAME_COUNTRY_PATTERN.search(name)
            raw_country_code = match.group('country_code').upper() if match else 'N/A'
            
            # 한국어 국가명 가져오기
            korean_name = get_korean_country_name(raw_country_code)
            
            # IP 주소 정렬을 위한 숫자 리스트 (try-except로 IP 형식 유효성 검사)
            try:
                ip_parts = list(map(int, server.split('.')))
                if len(ip_parts) != 4:
                     continue
            except ValueError:
                # IP 주소 형식이 잘못된 경우 (예: 도메인 이름) 건너뜀
                continue 
            
            entry = {
                'ip_parts': ip_parts,
                'string': f"{server}:{port}#{raw_country_code} {korean_name}"
            }
            
            # 중복 제거
            if entry['string'] not in [e['string'] for e in extracted_data]:
                extracted_data.append(entry)
        
        # 4. IP 주소 기준 정렬
        extracted_data.sort(key=lambda x: x['ip_parts'])
        
        return [entry['string'] for entry in extracted_data]
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류 또는 타임아웃 발생: {e}")
        return []
    except yaml.YAMLError as e:
        print(f"YAML 파싱 오류 발생: {e}")
        return []
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return []

# URL
REAL_TARGET_URL = "https://url.v1.mk/sub?target=clash&url=https%3A%2F%2Fcm.soso.edu.kg%2Fsub%3Fpassword%3Daaa%26security%3Dtls%26type%3Dws%26host%3Daaaa%26sni%3Daaa%26path%3D%252Fproxyip%253DProxyIP.JP.CMLiussss.Net%26encryption%3Dnone%26allowInsecure%3D1&insert=false&config=https%3A%2F%2Fraw.githubusercontent.com%2Fcmliu%2FACL4SSR%2Fmain%2FClash%2Fconfig%2FACL4SSR_Online.ini&emoji=true&list=true&xudp=false&udp=false&tfo=false&expand=true&scv=false&fdn=false&new_name=true"

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
