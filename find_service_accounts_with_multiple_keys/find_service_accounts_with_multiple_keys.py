import subprocess
import json

def run_gcloud_command(command_args):
    """gcloudコマンドを実行し、その結果をJSONとして返す"""
    try:
        result = subprocess.run(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e.stderr.decode()}")
        return None

def get_service_accounts(project_id):
    """指定したプロジェクトのサービスアカウントを取得する"""
    return run_gcloud_command([
        'gcloud', 'iam', 'service-accounts', 'list', 
        f'--project={project_id}', '--format=json'
    ])

def has_tmp_in_name_or_display_name(account):
    """サービスアカウント名や表示名に'tmp'が含まれているか確認する"""
    return 'tmp' in account['name'] or 'tmp' in account.get('displayName', '')

def get_service_account_keys(account_name):
    """サービスアカウントのキーリストを取得する"""
    return run_gcloud_command([
        'gcloud', 'iam', 'service-accounts', 'keys', 'list', 
        f'--iam-account={account_name}', '--format=json'
    ])

def filter_service_accounts(accounts):
    """条件に一致するサービスアカウントをフィルタリングする"""
    filtered_accounts = []
    
    for account in accounts:
        account_name = account['name']

        if has_tmp_in_name_or_display_name(account):
            filtered_accounts.append(account_name)
        else:
            keys = get_service_account_keys(account_name)
            if keys and len(keys) > 1:
                filtered_accounts.append(account_name)
    
    return filtered_accounts

def get_filtered_service_accounts(project_id):
    """条件に一致するサービスアカウントのリストを取得する"""
    service_accounts = get_service_accounts(project_id)
    if service_accounts is not None:
        return filter_service_accounts(service_accounts)
    else:
        return []

# 使用方法
project_id = 'your-project-id'
filtered_service_accounts = get_filtered_service_accounts(project_id)
if filtered_service_accounts:
    for account in filtered_service_accounts:
        print(f"条件に一致したサービスアカウント: {account}")
