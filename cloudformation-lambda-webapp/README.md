# CloudFormation + Lambda + API Gateway + DynamoDB + S3 ハンズオン

CloudFormation を使ってサーバーレスなタスク管理 Web アプリを一括デプロイするハンズオン教材です。  
コンソールから 1 つの YAML ファイルをデプロイするだけで、フロントエンドからバックエンドまで一気に構築できます。

## アーキテクチャ

```text
ブラウザ
  │
  ├─[HTML/CSS/JS]──▶ S3 (静的ウェブサイトホスティング)
  │
  └─[REST API]──▶ Amazon API Gateway (prod ステージ)
                        │
                        ▼ Lambda Proxy Integration
                  AWS Lambda (Python 3.12)
                        │
                        ▼
                  Amazon DynamoDB (タスクテーブル)
```

| サービス | 役割 | Free Tier |
|----------|------|-----------|
| Amazon S3 | フロントエンド（HTML）の静的ホスティング | 5 GB / 月、GET 20,000 回 / 月 |
| Amazon API Gateway | REST API エンドポイントの提供 | 100 万 API コール / 月 |
| AWS Lambda | CRUD ロジックの実行 | 100 万リクエスト / 月 |
| Amazon DynamoDB | タスクデータの永続化 | 25 GB、25 WCU / 25 RCU / 月 |
| AWS IAM | Lambda 実行ロールの管理 | 常時無料 |
| AWS CloudFormation | インフラ一括管理（IaC） | 常時無料 |

## API 仕様

| メソッド | パス | 説明 |
|----------|------|------|
| `GET` | `/tasks` | タスク一覧を取得 |
| `POST` | `/tasks` | タスクを新規作成 |
| `PUT` | `/tasks/{id}` | タスクの完了状態を切り替え |
| `DELETE` | `/tasks/{id}` | タスクを削除 |

## フォルダ構成

```text
cloudformation-lambda-webapp/
├── README.md           ← この手順書
├── template.yaml       ← CloudFormation テンプレート（インフラ一式）
└── frontend/
    └── index.html      ← タスク管理 SPA（S3 にアップロードするファイル）
```

## ゴール

このハンズオンが完了すると、次の状態になります。

- CloudFormation スタックがデプロイされ、DynamoDB / Lambda / API Gateway / S3 がすべて作成される
- ブラウザから `http://<S3ウェブサイトURL>/index.html` を開いてタスクを CRUD 操作できる
- API 呼び出しが画面のログエリアにリアルタイムで表示される

## 前提条件

- AWS アカウント（Free Tier 利用推奨）
- AWS コンソールへのログイン権限
- 以下の操作権限を持つ IAM ユーザー / ロール
  - CloudFormation: `CreateStack`, `DescribeStacks`, `DeleteStack`
  - IAM: `CreateRole`, `AttachRolePolicy`, `PutRolePolicy`
  - Lambda: `CreateFunction`, `UpdateFunctionCode`
  - DynamoDB: `CreateTable`
  - API Gateway: フル権限
  - S3: `CreateBucket`, `PutBucketPolicy`, `PutObject`

---

## 手順

### 1. CloudFormation スタックをデプロイする

#### 1-1. テンプレートを確認する

`template.yaml` を開き、作成されるリソースを確認してください。

**主なリソース**

| 論理 ID | タイプ | 内容 |
|---------|--------|------|
| `TasksTable` | `AWS::DynamoDB::Table` | タスクを保存する DynamoDB テーブル |
| `LambdaRole` | `AWS::IAM::Role` | Lambda が DynamoDB と CloudWatch Logs にアクセスするためのロール |
| `TasksFunction` | `AWS::Lambda::Function` | CRUD ロジックを処理する Python 3.12 関数 |
| `TasksApi` | `AWS::ApiGateway::RestApi` | REST API のルートリソース |
| `ApiStage` | `AWS::ApiGateway::Stage` | `prod` ステージ（デプロイ単位） |
| `FrontendBucket` | `AWS::S3::Bucket` | フロントエンドを公開する S3 バケット |

#### 1-2. AWS コンソールからデプロイする

1. [AWS CloudFormation コンソール](https://console.aws.amazon.com/cloudformation/) を開く
2. **「スタックの作成」** → **「新しいリソースを使用 (標準)」** を選択する
3. **「テンプレートファイルのアップロード」** を選び、このリポジトリの `template.yaml` を選択する
4. **「次へ」** をクリックする
5. スタック名に任意の名前（例: `task-app-stack`）を入力する
6. パラメータ **`ProjectName`** はデフォルト（`task-app`）のままで問題ありません。変更する場合は小文字英数字とハイフンのみ使用できます
7. **「次へ」** → **「次へ」** とクリックし、確認画面で **「IAM リソースを作成することを承認します」** にチェックを入れる
8. **「スタックの作成」** をクリックする
9. ステータスが `CREATE_COMPLETE` になるまで待つ（約 1〜2 分）

#### 1-3. AWS CLI からデプロイする場合

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name task-app-stack \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-1
```

#### 1-4. スタック出力を確認する

デプロイ完了後、コンソールの **「出力」** タブを開き、以下の値をメモしておいてください。

| キー | 説明 |
|------|------|
| `ApiEndpoint` | API Gateway の URL（フロントエンドの設定に使用） |
| `WebsiteURL` | S3 静的ウェブサイトの URL |
| `FrontendBucketName` | フロントエンドファイルをアップロードする S3 バケット名 |

---

### 2. フロントエンドを S3 にアップロードする

#### コンソールから操作する場合

1. [S3 コンソール](https://s3.console.aws.amazon.com/s3/) を開く
2. `FrontendBucketName` に表示されたバケットを選択する
3. **「アップロード」** → **「ファイルを追加」** から `frontend/index.html` を選択する
4. **「アップロード」** をクリックする

#### AWS CLI からアップロードする場合

`<YOUR_BUCKET>` を `FrontendBucketName` の値に置き換えて実行します。

```bash
aws s3 cp frontend/index.html s3://<YOUR_BUCKET>/index.html \
  --content-type text/html \
  --cache-control no-cache
```

---

### 3. アプリを開いて API URL を設定する

1. ブラウザで `WebsiteURL` に表示された URL を開く  
   `http://<バケット名>.s3-website-<リージョン>.amazonaws.com/`
2. 画面右上の **「⚙️ API 設定」** ボタンをクリックする
3. `ApiEndpoint` の値（例: `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod`）を貼り付ける
4. **「保存して再読み込み」** をクリックする

---

### 4. 動作確認する

#### 4-1. タスクを追加する

1. テキストフォームにタスク名を入力し、**「追加」** を押す
2. タスク一覧に新しいタスクが表示されること、および画面下部の API ログに `POST /tasks → 201` が表示されることを確認する
3. ブラウザをリロードしてタスクが消えないことを確認する（DynamoDB に永続化されている）

#### 4-2. タスクを完了にする / 元に戻す

1. タスク左側の丸いボタンをクリックする
2. チェックマークが付いてタスクがグレーアウトし、API ログに `PUT /tasks/{id} → 200` が表示されることを確認する
3. もう一度クリックして未完了に戻せることを確認する

#### 4-3. タスクを削除する

1. タスクにカーソルを合わせてゴミ箱アイコンをクリックする
2. 確認ダイアログで「OK」を選ぶ
3. タスクが一覧から消え、API ログに `DELETE /tasks/{id} → 200` が表示されることを確認する

#### 4-4. Lambda のログを確認する（オプション）

1. [CloudWatch コンソール](https://console.aws.amazon.com/cloudwatch/) → **「ロググループ」** を開く
2. `/aws/lambda/task-app-handler` を選択する
3. 各 API 呼び出しのログが記録されていることを確認する

#### 4-5. DynamoDB のデータを確認する（オプション）

1. [DynamoDB コンソール](https://console.aws.amazon.com/dynamodb/) → **「テーブル」** を開く
2. `task-app-tasks` を選択し、**「項目の探索」** をクリックする
3. 追加したタスクが保存されていることを確認する

---

### 5. スタックを削除する（後片付け）

> ⚠️ S3 バケットにファイルが残っているとスタック削除が失敗します。先にバケットを空にしてください。

#### S3 バケットを空にする

```bash
aws s3 rm s3://<YOUR_BUCKET> --recursive
```

#### スタックを削除する（コンソール）

1. CloudFormation コンソールでスタックを選択する
2. **「削除」** → **「スタックの削除」** をクリックする

#### スタックを削除する（CLI）

```bash
aws cloudformation delete-stack --stack-name task-app-stack
```

---

## トラブルシュート

### `CREATE_FAILED` でスタックが失敗する

- イベントタブでエラーメッセージを確認する
- IAM の権限不足が最も多い原因です。`CAPABILITY_NAMED_IAM` を付けてデプロイしているか確認する

### API を呼び出すと `403 Forbidden` が返る

- API Gateway のステージ（`prod`）がデプロイされているか確認する  
  コンソール → API Gateway → API を選択 → 「ステージ」 → `prod` が存在するか確認する
- `ApiEndpoint` の末尾が `/prod` で終わっているか確認する

### API を呼び出すと `502 Bad Gateway` が返る

- Lambda 関数がエラーを返している可能性があります
- CloudWatch Logs (`/aws/lambda/task-app-handler`) でエラー内容を確認する
- DynamoDB テーブルが `ACTIVE` 状態か確認する

### CORS エラーがブラウザのコンソールに表示される

- API Gateway の OPTIONS メソッドが設定されているか確認する  
  コンソール → API Gateway → API を選択 → `/tasks` リソース → `OPTIONS` が存在するか確認する
- API Gateway を再デプロイする  
  コンソール → API Gateway → 「アクション」 → 「API のデプロイ」 → ステージ `prod` を選択する

### S3 の URL を開くと `403 Access Denied` が表示される

- `index.html` がアップロードされているか確認する
- バケットポリシーでパブリック読み取りが許可されているか確認する  
  コンソール → S3 → バケット → 「アクセス許可」 → 「バケットポリシー」を確認する
- バケットの「パブリックアクセスをすべてブロック」がオフになっているか確認する

---

## 学べるポイント

- **IaC (Infrastructure as Code)**: CloudFormation で AWS リソースをコードで管理する方法
- **サーバーレスアーキテクチャ**: Lambda + API Gateway によるサーバー管理不要のバックエンド
- **DynamoDB**: NoSQL データベースへの CRUD 操作と PAY_PER_REQUEST 課金モデル
- **Lambda Proxy Integration**: API Gateway がリクエストをそのまま Lambda に渡す仕組み
- **CORS 設定**: ブラウザからクロスオリジンの API を呼び出すための設定
- **S3 静的ウェブサイトホスティング**: S3 バケットを Web サーバーとして使う方法
- **IAM 最小権限の原則**: Lambda に必要な権限だけを付与するロール設計
