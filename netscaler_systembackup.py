import requests
import datetime
#api 로 백업 생성 후 다운로드

# 새로운 백업 생성 함수
def create_backup(adc_ip, username, password):
    url = f"http://{adc_ip}/nitro/v1/config/systembackup?action=create"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.tgz"
    payload = {
        "systembackup": {
            "filename": filename,
            "level": "full",
            "includekernel": "NO",
            "comment": "Automated backup"
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-NITRO-USER": username,
        "X-NITRO-PASS": password
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    if response.status_code == 200:
        print(f"Backup created successfully: {filename}")
    else:
        print(f"Failed to create backup: {response.status_code}, {response.text}")
    return filename

# 백업 목록 조회 함수
def get_backup_list(adc_ip, username, password):
    url = f"http://{adc_ip}/nitro/v1/config/systembackup"
    headers = {
        "Content-Type": "application/json",
        "X-NITRO-USER": username,
        "X-NITRO-PASS": password
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            print("Backup List:")
            for backup in data["systembackup"]:
                print(f"Filename: {backup['filename']}, Created: {backup['creationtime']}, Size: {backup['size']} bytes")
            return data["systembackup"]
        else:
            print(f"Failed to get backup list: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred while getting backup list: {str(e)}")
        return None

# 백업 파일 다운로드 함수
def download_backup(adc_ip, username, password, filename):
    url = f"http://{adc_ip}/nitro/v1/config/systembackup/{filename}"
    headers = {
        "Content-Type": "application/json",
        "X-NITRO-USER": username,
        "X-NITRO-PASS": password
    }
    try:
        response = requests.get(url, headers=headers, verify=False, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Backup downloaded: {filename}")
        else:
            print(f"Failed to download backup: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error occurred while downloading backup: {str(e)}")

# 24시간 이내의 백업 확인 함수
def find_recent_backup(backup_list, hours=24):
    cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
    for backup in backup_list:
        # Convert creation time to datetime
        creation_time = datetime.datetime.strptime(backup["creationtime"], "%a %b %d %H:%M:%S %Y")
        if creation_time >= cutoff_time:
            print(f"Recent backup found: {backup['filename']} (Created: {backup['creationtime']})")
            return backup["filename"]
    print(f"No backups found within the last {hours} hours.")
    return None

# 메인 실행 부분
if __name__ == "__main__":
    # Citrix ADC 정보
    adc_ip = ""
    username = "nsroot"
    password = ""

    # 1. 새로운 백업 생성
    backup_name = create_backup(adc_ip, username, password)

    # 2. 백업 목록 조회
    backup_list = get_backup_list(adc_ip, username, password)

    # 3. 24시간 이내의 백업 파일 확인 및 다운로드
    if backup_list:
        recent_backup = find_recent_backup(backup_list, hours=24)
        if recent_backup:
            download_backup(adc_ip, username, password, recent_backup)
