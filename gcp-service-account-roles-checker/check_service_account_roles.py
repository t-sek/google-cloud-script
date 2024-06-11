import json
import subprocess
import sys

def get_iam_policy(project_id):
    try:
        # IAMポリシーを取得
        result = subprocess.run(
            ['gcloud', 'projects', 'get-iam-policy', project_id, '--format=json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error getting IAM policy: {e.stderr.decode()}")
        return None

def check_basic_roles(iam_policy):
    # 基本ロールのリスト
    basic_roles = [
        'roles/owner',
        'roles/editor',
        'roles/viewer'
    ]

    found = False
    # 基本ロールが付与されているかどうかを確認
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        members = binding['members']
        if role in basic_roles:
            for member in members:
                if member.startswith('serviceAccount:'):
                    print(f'Service Account {member} has basic role: {role}')
                    found = True
    if not found:
        print("No service accounts with basic roles found.")

def main():
    # コマンドライン引数からプロジェクトIDを取得
    if len(sys.argv) != 2:
        print("Usage: python check_service_account_roles.py [PROJECT_ID]")
        return

    project_id = sys.argv[1]

    # IAMポリシーを取得
    iam_policy = get_iam_policy(project_id)
    if iam_policy:
        # 基本ロールの確認
        check_basic_roles(iam_policy)

if __name__ == "__main__":
    main()
