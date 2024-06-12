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
        return f" with condition: {condition['title']} ({condition['description']})"
    else:
        return " with no condition"

def print_roles_and_members(roles, role_type):
    """ロールとメンバーの情報を出力"""
    if not roles:
        print(f"No service accounts with {role_type} roles found.")
    else:
        for role, members_condition in roles.items():
            members, condition_desc = members_condition
            for member in members:
                print(f'Service Account {member} has {role_type} role: {role}{condition_desc}')

def check_roles(iam_policy, roles_to_check, role_type):
    """指定されたロールが付与されているサービスアカウントをチェック"""
    roles = {}
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        members = binding['members']
        if role in roles_to_check:
            condition_desc = format_condition(binding.get('condition'))
            service_accounts = [member for member in members if member.startswith('serviceAccount:')]
            if service_accounts:
                roles[role] = (service_accounts, condition_desc)
    print_roles_and_members(roles, role_type)

def check_service_account_user_role(iam_policy):
    """サービスアカウントユーザーロールの確認"""
    sa_user_role = 'roles/iam.serviceAccountUser'
    roles = {}
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        if role == sa_user_role:
            condition_desc = format_condition(binding.get('condition'))
            roles[role] = (binding['members'], condition_desc)
            if not any('serviceAccount:' in member for member in binding['members']):
                print(f"Warning: {sa_user_role} should not be assigned at project level for least privilege.")
    print_roles_and_members(roles, "serviceAccountUser")

def list_service_account_roles(iam_policy, service_account_name):
    """特定のサービスアカウントに対するロールを一覧表示"""
    roles = {}
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        members = [member for member in binding['members'] if member.startswith(f'serviceAccount:{service_account_name}')]
        if members:
            condition_desc = format_condition(binding.get('condition'))
            roles[role] = (members, condition_desc)
    
    if not roles:
        print(f"No roles found for service account {service_account_name}.")
    else:
        print(f"Roles for service account {service_account_name}:")
        for role, (members, condition_desc) in roles.items():
            print(f"  Role: {role}{condition_desc}")
            for member in members:
                print(f"    Member: {member}")

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
    list_service_account_roles(iam_policy, service_account_name)

if __name__ == "__main__":
    main()
