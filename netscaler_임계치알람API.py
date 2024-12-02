import requests
from datetime import datetime

# 상수 선언: 유지보수성을 위해 경고 임계값 설정
ALERT_THRESHOLDS = {
    "mgmtcpuusagepcnt": 90,
    "memusagepcnt": 80,
    "disk0perusage": 90,
    "disk1perusage": 90,
}

def fetch_ns_stats(ip, username, password):
    """NetScaler 상태 정보 가져오기"""
    url = f"http://{ip}/nitro/v1/stat/ns"
    params = {
        "attrs": "rxmbitsrate,txmbitsrate,mgmtcpuusagepcnt,memusagepcnt,disk0perusage,disk1perusage"
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, auth=(username, password), headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stats: {e}")
        return None

def detect_issues(stats):
    """상태 정보에서 문제 탐지"""
    issues = []
    if not stats or "ns" not in stats:
        return issues

    ns_stats = stats["ns"]
    for key, threshold in ALERT_THRESHOLDS.items():
        value = ns_stats.get(key, 0)
        if value > threshold:
            issues.append(f"{key.replace('pcnt', '').capitalize()} usage high: {value}% (Threshold: {threshold}%)")
    return issues

def alert_issues(issues):
    """문제 경고 출력 및 알림"""
    if issues:
        print("ALERT: The following issues were detected:")
        for issue in issues:
            print(f"- {issue}")
        # 추가 알림 구현 (예: Slack, Email 등)
    else:
        print(f"{datetime.now()}: No issues detected.")

if __name__ == "__main__":
    # 사용자 입력 변수
    adc_ip = ""
    username = "nsroot"
    password = ""

    stats = fetch_ns_stats(adc_ip, username, password)
    if stats:
        issues = detect_issues(stats)
        alert_issues(issues)
    else:
        print(f"{datetime.now()}: Failed to retrieve stats.")
