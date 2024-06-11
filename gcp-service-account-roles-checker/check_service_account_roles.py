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

    check_roles(iam_policy, basic_roles, "basic")
    check_roles(iam_policy, [admin_role], "admin")

if __name__ == "__main__":
    main()
