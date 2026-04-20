# CloudFormation フルスタック会員制タスク管理アプリ ハンズオン

CloudFormation を使って **会員登録 / ログイン付きのタスク管理 Web アプリ** をワンクリックでデプロイするハンズオン教材です。
スタックを作成するだけでフロントエンドからバックエンド・データベースまで一気に構築され、**削除もボタン一つ** で完了します。

## アーキテクチャ

```text
            ブラウザ
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
CloudFront ──OAC──▶ S3 バケット          Cognito User Pool
(HTTPS)            (フロントエンド)        (会員登録 / ログイン)
    │                                         │
    │              JWT トークン                │
    └──────────────────┐  ┌───────────────────┘
                       ▼  ▼
                API Gateway (prod)
                 Cognito Authorizer
                       │
             ┌─────────┴──────────┐
             ▼                    ▼
     Lambda (App)           Lambda (Worker)
       │   │   │                  │
       ▼   ▼   ▼                  ▼
   DynamoDB DynamoDB SQS ────▶ SNS
   (タスク) (監査/プロフィール) (キュー)  (通知)
```

## リソース一覧（41 リソース）

| カテゴリ | サービス | リソース | 説明 |
|---------|----------|---------|------|
| **認証** | Cognito | UserPool, Client, Domain | 会員登録・ログイン・メール認証 |
| **API** | API Gateway | REST API, Authorizer, Methods ×9, Stage | Cognito 認証付き REST API |
| **処理** | Lambda | App, Worker, S3Deploy (計3関数) | ビジネスロジック・非同期処理・デプロイ |
| **ストレージ** | S3 | Bucket, BucketPolicy | フロントエンド配信（非公開） |
| **CDN** | CloudFront | Distribution, OAC | HTTPS フロントエンド配信 |
| **NoSQL** | DynamoDB | TasksTable, UserProfilesTable, AuditLogTable | タスク本体・プロフィール・監査ログ |
| **メッセージ** | SQS | Queue, DLQ | 非同期タスク処理キュー |
| **通知** | SNS | Topic | タスク操作通知 |
| **監視** | CloudWatch | Dashboard, Alarm ×2 | メトリクス可視化・エラーアラート |
| **権限** | IAM | Role ×3 | 最小権限の原則に基づくロール |
| **IaC** | CloudFormation | Custom Resource ×1 | S3 自動デプロイ / 自動クリーンアップ |

## API 仕様

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| `GET` | `/tasks` | Cognito | 自分のタスク一覧を取得 |
| `POST` | `/tasks` | Cognito | タスクを新規作成 |
| `PUT` | `/tasks/{id}` | Cognito | タスクの完了状態を切り替え |
| `DELETE` | `/tasks/{id}` | Cognito | タスクを削除 |
| `GET` | `/profile` | Cognito | プロフィールを取得（初回は自動作成） |
| `PUT` | `/profile` | Cognito | 表示名を更新 |

## フォルダ構成

```text
cloudformation-lambda-webapp/
├── README.md                ← この手順書
├── template.yaml            ← CloudFormation テンプレート（全リソース + 埋め込み HTML）
└── frontend/
    └── index.html           ← フロントエンド参照用（実際はテンプレートから自動デプロイ）
```

> **💡 ポイント**: `frontend/index.html` はリポジトリ上での参照用ファイルです。
> 実際のデプロイ時は CloudFormation テンプレート内の `S3DeployFunction` Lambda が
> 同等の HTML を **自動生成** し、API エンドポイントや Cognito の設定値を埋め込んで
> S3 バケットに配置します。手動アップロードは不要です。

## ゴール

- CloudFormation スタックをデプロイするだけで全リソースが構築される
- フロントエンドが CloudFront 経由で自動配信される（手動 S3 アップロード不要）
- ブラウザから会員登録 → メール認証 → ログイン → タスク管理が可能
- スタック削除時に S3 バケットが自動的に空になり、クリーンに削除される

## 前提条件

- AWS アカウント
- AWS コンソールへのログイン権限
- 以下のサービスへの操作権限を持つ IAM ユーザー / ロール
  - CloudFormation, IAM, Lambda, API Gateway, S3, CloudFront
  - Cognito, DynamoDB, SQS, SNS
  - CloudWatch

## コストについて

> ✅ **このテンプレートは Free Tier を意識して DynamoDB ベースに変更済みです。**

| サービス | 概算コスト |
|---------|-----------|
| CloudFront | 無料枠: 1TB/月、1,000万リクエスト/月 |
| Cognito | 無料枠: 50,000 MAU/月 |
| Lambda | 無料枠: 100万リクエスト/月 |
| API Gateway | 無料枠: 100万コール/月 |
| DynamoDB | 無料枠: 25GB、25WCU/25RCU |
| SQS | 無料枠: 100万リクエスト/月 |
| SNS | 無料枠: 100万パブリッシュ/月 |
| CloudWatch | ダッシュボード $3/月（3つまで無料） |

**ハンズオン後は必ずスタックを削除してください。**

---

## 手順

### 1. CloudFormation スタックをデプロイする

#### 1-1. テンプレートを確認する

`template.yaml` を開き、41 個のリソースの構成を確認してください。
Infrastructure Composer で開くと、アーキテクチャ図として視覚的に確認できます。

#### 1-2. AWS コンソールからデプロイする

1. [CloudFormation コンソール](https://console.aws.amazon.com/cloudformation/) を開く
2. **「スタックの作成」** → **「新しいリソースを使用 (標準)」** を選択
3. **「テンプレートファイルのアップロード」** で `template.yaml` を選択
4. **「次へ」** をクリック
5. スタック名に任意の名前（例: `task-app-stack`）を入力
6. **ProjectName** はデフォルト `task-app` のまま、または変更可
7. **「次へ」** → **「次へ」** → 確認画面で以下にチェック:
   - ✅ **「IAM リソースを作成することを承認します」**
   - ✅ **「カスタム名の IAM リソースを作成する場合があることを承認します」**
8. **「スタックの作成」** をクリック
9. ステータスが `CREATE_COMPLETE` になるまで待つ（約 5〜10 分）

> ⏱️ DynamoDB 構成のため、従来の Aurora 構成より短時間で完了します。

#### 1-3. AWS CLI からデプロイする場合

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name task-app-stack \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-1
```

#### 1-4. スタック出力を確認する

デプロイ完了後、**「出力」** タブで以下を確認できます。

| キー | 説明 |
|------|------|
| `CloudFrontURL` | アプリケーションの URL（ブラウザで開く） |
| `ApiEndpoint` | API Gateway の URL（自動設定済み） |
| `CognitoUserPoolId` | Cognito User Pool ID |
| `CognitoClientId` | Cognito App Client ID |
| `TasksTableName` | タスク保存用 DynamoDB テーブル名 |
| `UserProfilesTableName` | プロフィール保存用 DynamoDB テーブル名 |
| `DashboardURL` | CloudWatch ダッシュボードへのリンク |

---

### 2. アプリを開く

1. **「出力」** タブの `CloudFrontURL` をクリックしてブラウザで開く
2. ログイン画面が表示される

> 💡 CloudFront の初回デプロイには数分かかる場合があります。
> 403 が表示された場合は数分待ってからリロードしてください。

---

### 3. 会員登録する

1. ログイン画面の **「新規登録」** リンクをクリック
2. メールアドレスとパスワード（8文字以上、大文字・小文字・数字を含む）を入力
3. **「登録する」** をクリック
4. 入力したメールアドレスに **確認コード** が届く
5. 確認コード（6桁の数字）を入力して **「確認する」** をクリック
6. 「登録完了！ログインしてください」と表示されたらログイン画面に戻る

---

### 4. ログインして動作確認する

#### 4-1. ログインする

1. メールアドレスとパスワードを入力して **「ログイン」**
2. ダッシュボードが表示される

#### 4-2. タスクを追加する

1. 「新しいタスクを入力…」フォームにタスク名を入力して **「追加」**
2. タスクが一覧に表示され、右サイドバーの統計が更新される
3. API ログに `POST /tasks → 201` が表示される

#### 4-3. タスクを完了 / 未完了にする

1. タスク左の丸いボタンをクリック
2. チェックマークが付き、統計の完了数・完了率が更新される

#### 4-4. タスクを削除する

1. タスクにカーソルを合わせてゴミ箱アイコンをクリック
2. 確認ダイアログで「OK」を選択

#### 4-5. プロフィールを更新する

1. 右サイドバーの「プロフィール」セクションで表示名を変更
2. **「保存」** をクリック

#### 4-6. CloudWatch ダッシュボードを確認する（オプション）

1. 出力タブの `DashboardURL` をクリック
2. Lambda、API Gateway、SQS、CloudFront、Cognito のメトリクスを確認

---

### 5. スタックを削除する（後片付け）

> ✅ **S3 バケットの手動削除は不要です！**
> Custom Resource Lambda がスタック削除時に S3 バケットを自動的に空にします。

#### コンソールから削除

1. [CloudFormation コンソール](https://console.aws.amazon.com/cloudformation/) を開く
2. スタックを選択 → **「削除」** → **「スタックの削除」**

#### CLI から削除

```bash
aws cloudformation delete-stack --stack-name task-app-stack
```

> ⏱️ 削除には数分かかります。`DELETE_COMPLETE` になれば完了です。

---

## トラブルシュート

### `CREATE_FAILED` でスタックが失敗する

- イベントタブでエラーメッセージを確認する
- IAM の権限不足が多い原因です。`CAPABILITY_NAMED_IAM` を付けてデプロイしているか確認
- `ProjectName` を変更した場合は、S3 バケット名や Cognito ドメイン名が一意になっているか確認

### CloudFront URL を開くと 403 が返る

- スタック作成直後は CloudFront の展開に数分かかります。しばらく待ってリロード
- S3DeployCustomResource がエラーになっていないかスタックイベントを確認

### ログインできない

- パスワードは **8文字以上、大文字・小文字・数字** を含む必要があります
- メール確認が完了しているか確認してください

### API を呼び出すと 401 が返る

- トークンの有効期限（1時間）が切れている可能性があります
- ログアウトして再ログインしてください

### API を呼び出すと 500 が返る

- DynamoDB テーブル名が Lambda 環境変数に正しく設定されているか確認してください
- CloudWatch Logs で Lambda のログを確認してください
- 必要に応じて `AppFunction` のログで `AccessDenied` や `ResourceNotFoundException` が出ていないか確認してください

---

## 学べるポイント

- **IaC (Infrastructure as Code)**: CloudFormation で 41 リソースを一括管理
- **認証**: Cognito User Pool による会員登録・ログイン・メール認証
- **NoSQL 設計**: DynamoDB によるタスク・プロフィール・監査ログ管理
- **CDN**: CloudFront + OAC による安全な S3 コンテンツ配信
- **サーバーレス**: Lambda + API Gateway によるバックエンド
- **非同期処理**: SQS + Lambda Worker パターン
- **通知**: SNS によるイベント通知
- **監査**: DynamoDB TTL による操作ログの自動期限管理
- **監視**: CloudWatch Dashboard / Alarm によるオブザーバビリティ
- **セキュリティ**: IAM 最小権限, OAC, Cognito 認証
- **自動化**: Custom Resource による S3 自動デプロイ / 自動クリーンアップ
