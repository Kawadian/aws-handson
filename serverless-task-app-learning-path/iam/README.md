# IAM ハンズオン

Lambda ハンズオンで使うための最小権限ロールを作りながら、IAM の基本要素を体験する教材です。

## ゴール

- IAM の **Principal / Action / Resource** の考え方を理解する
- Lambda 実行ロールを作成する
- CloudWatch Logs への出力に必要な権限を確認する

## 作るもの

- `handson-lambda-execution-role`
- `handson-lambda-logs-policy`

## 手順

### 1. ポリシーを作成する

1. IAM コンソールを開く
2. **アクセス管理 > ポリシー > ポリシーの作成** を開く
3. JSON タブで次の内容を入力する

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

4. ポリシー名を `handson-lambda-logs-policy` にして保存する

### 2. Lambda 実行ロールを作成する

1. **アクセス管理 > ロール > ロールを作成** を開く
2. 信頼されたエンティティタイプで **AWS のサービス** を選ぶ
3. ユースケースで **Lambda** を選ぶ
4. 先ほど作成した `handson-lambda-logs-policy` をアタッチする
5. ロール名を `handson-lambda-execution-role` にして保存する

### 3. 信頼ポリシーを確認する

ロールの **信頼関係** タブで、`lambda.amazonaws.com` が引き受け元になっていることを確認します。

### 4. ポリシーシミュレータで試す

1. `handson-lambda-execution-role` を開く
2. **ポリシーをシミュレート** を開く
3. `logs:PutLogEvents` は許可、`dynamodb:DeleteTable` は未許可になることを確認する

## 片付け

- ロール `handson-lambda-execution-role` を削除する
- ポリシー `handson-lambda-logs-policy` を削除する

## 学べるポイント

- IAM ロールは「誰が引き受けるか」と「何ができるか」の組み合わせ
- 最初から広い権限を与えず、必要最低限から始めるのが基本
- Lambda や ECS などの AWS サービスでも IAM が土台になる
