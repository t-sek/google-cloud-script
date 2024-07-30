import subprocess
import json

def get_used_services(project_id, start_time, end_time):
    try:
        # gcloud コマンドを実行して、ログエントリを取得
        result = subprocess.run(
            [
                'gcloud', 'logging', 'read', 
                f'timestamp>="{start_time}" AND timestamp<="{end_time}"',
                f'--project={project_id}', '--format=json'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        # 結果をパース
        entries = json.loads(result.stdout)
        used_services = set()
        
        for entry in entries:
            if 'protoPayload' in entry:
                service_name = entry['protoPayload'].get('serviceName')
                if service_name:
                    used_services.add(service_name)
        
        return used_services
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e.stderr.decode()}")
        return None

project_id = 'YOUR_PROJECT_ID'
start_time = '2023-07-01T00:00:00Z'
end_time = '2023-07-30T23:59:59Z'

used_services = get_used_services(project_id, start_time, end_time)
if used_services:
    print("実際に使用されているサービス:", used_services)
else:
    print("サービスが見つかりませんでした。")
