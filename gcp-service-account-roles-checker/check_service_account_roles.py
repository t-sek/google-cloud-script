import json
import subprocess
import sys

def get_iam_policy(project_id):
    """プロジェクトのIAMポリシーを取得"""
    try:
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

def format_condition(condition):
    """条件の説明をフォーマット"""
    if condition:
        return f"with condition: {condition['title']} ({condition['description']})"
    else:
        return "with no condition"

def categorize_roles(iam_policy, roles_to_check):
    """ロールをテンポラリアクセスとそれ以外に分類"""
    permanent_roles = {}
    temporary_roles = {}
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        members = binding['members']
        if role in roles_to_check:
            condition = binding.get('condition')
            service_accounts = [member for member in members if member.startswith('serviceAccount:')]
            if service_accounts:
                if condition:
                    temporary_roles[role] = service_accounts
                else:
                    permanent_roles[role] = service_accounts
    return permanent_roles, temporary_roles

def print_roles(roles, header):
    """ロールの情報を出力"""
    print(header)
    if not roles:
        print("None")
    else:
        for role, members in roles.items():
            for member in members:
                print(f"{member} has role: {role}")

def check_roles(iam_policy, roles_to_check, role_type):
    """指定されたロールが付与されているサービスアカウントをチェック"""
    permanent_roles, temporary_roles = categorize_roles(iam_policy, roles_to_check)
    print_roles(permanent_roles, f"===== {role_type.capitalize()} roles =====")
    print_roles(temporary_roles, f"===== {role_type.capitalize()} temporary access roles =====")

def check_service_account_user_role(iam_policy):
    """サービスアカウントユーザーロールの確認"""
    sa_user_role = 'roles/iam.serviceAccountUser'
    permanent_roles, temporary_roles = categorize_roles(iam_policy, [sa_user_role])
    
    if sa_user_role in permanent_roles and not any('serviceAccount:' in member for member in permanent_roles[sa_user_role]):
        print(f"Warning: {sa_user_role} should not be assigned at project level for least privilege.")
    
    print_roles(permanent_roles, "===== Service Account User roles =====")
    print_roles(temporary_roles, "===== Service Account User temporary access roles =====")

def list_service_account_roles(iam_policy, service_account_name):
    """特定のサービスアカウントに対するロールを一覧表示"""
    roles = {}
    temporary_roles = {}
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        condition = binding.get('condition')
        members = [member for member in binding['members'] if member.startswith(f'serviceAccount:{service_account_name}')]
        if members:
            if condition:
                temporary_roles[role] = members
            else:
                roles[role] = members
    
    if not roles and not temporary_roles:
        print(f"No roles found for service account {service_account_name}.")
    else:
        print(f"Roles for service account {service_account_name}:")
        print_roles(roles, "===== Permanent roles =====")
        print_roles(temporary_roles, "===== Temporary access roles =====")

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_service_account_roles.py [PROJECT_ID]")
        return

    project_id = sys.argv[1]
    iam_policy = get_iam_policy(project_id)
    if not iam_policy:
        print("Failed to retrieve IAM policy. Exiting.")
        return

    basic_roles = ['roles/owner', 'roles/editor', 'roles/viewer']
    admin_role = f'roles/{project_id}.admin'
    service_account_name = ''  # ここに特定のサービスアカウント名を指定

    check_roles(iam_policy, basic_roles, "basic")
    check_roles(iam_policy, [admin_role], "admin")
    check_service_account_user_role(iam_policy)
    if service_account_name:
        list_service_account_roles(iam_policy, service_account_name)

if __name__ == "__main__":
    main()
