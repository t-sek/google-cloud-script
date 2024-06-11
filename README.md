# google-cloud-script

## GCPサービスアカウント基本ロールチェックツール

このスクリプトは、指定されたGoogle Cloud Platform（GCP）プロジェクト内のサービスアカウントに基本ロール（Owner、Editor、Viewer）が割り当てられているかどうかを確認します。

### 前提条件

- Python 3.6以上
- `gcloud` CLIがインストールされ、設定されていること

### インストール

1. **リポジトリをクローン（またはスクリプトをダウンロード）します:**

    ```sh
    git clone https://github.com/your-repo/gcp-service-account-roles-checker.git
    cd gcp-service-account-roles-checker
    ```

2. **必要なPythonパッケージをインストールします:**

    このスクリプトには追加のPythonパッケージは必要ありません。

### 設定

1. **`gcloud` CLIがインストールされ、初期化されていることを確認します:**

    ```sh
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
    gcloud init
    ```

### 使用方法

1. **GCPプロジェクトIDを引数としてスクリプトを実行します:**

    ```sh
    python check_service_account_roles.py [YOUR_PROJECT_ID]
    ```

    `[YOUR_PROJECT_ID]`を実際のGCPプロジェクトIDに置き換えてください。

### 使用例

プロジェクトIDが `my-gcp-project` の場合、以下のコマンドを使用してサービスアカウントをチェックします:

```sh
python check_service_account_roles.py my-gcp-project
```
