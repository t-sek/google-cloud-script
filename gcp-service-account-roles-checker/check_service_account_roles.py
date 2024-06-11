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

def check_roles(iam_policy, roles_to_check, role_type):
    """指定されたロールが付与されているサービスアカウントをチェック"""
    found = False
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        members = binding['members']
        if role in roles_to_check:
            for member in members:
                if member.startswith('serviceAccount:'):
                    print(f'Service Account {member} has {role_type} role: {role}')
                    found = True
    if not found:
        print(f"No service accounts with {role_type} roles found.")

def check_service_account_user_role(iam_policy):
    """サービスアカウントユーザーロールの確認"""
    sa_user_role = 'roles/iam.serviceAccountUser'
    found = False

    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        members = binding['members']
        if role == sa_user_role:
            found = True
            print(f'{role} assigned to: {members}')
            if not any('serviceAccount:' in member for member in members):
                print(f"Warning: {sa_user_role} should not be assigned at project level for least privilege.")
    
    if not found:
        print("No service account user roles found.")
    else:
        print(f"Check completed for {sa_user_role}.")

def list_service_account_roles(iam_policy, service_account_name):
    """特定のサービスアカウントに対するロールを一覧表示"""
    roles = {}
    for binding in iam_policy.get('bindings', []):
        role = binding['role']
        members = [member for member in binding['members'] if member.startswith(f'serviceAccount:{service_account_name}')]
        if members:
            roles[role] = members
    
    if not roles:
        print(f"No roles found for service account {service_account_name}.")
    else:
        print(f"Roles for service account {service_account_name}:")
        for role, members in roles.items():
            print(f"  Role: {role}")
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
    service_account_name = ''

    check_roles(iam_policy, basic_roles, "basic")
    check_roles(iam_policy, [admin_role], "admin")
    check_service_account_user_role(iam_policy)
    list_service_account_roles(iam_policy, service_account_name)

if __name__ == "__main__":
    main()
