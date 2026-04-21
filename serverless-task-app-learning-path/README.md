# サーバーレスタスクアプリ学習パス

CloudFormation のワンクリック構築に入る前に、タスクアプリを構成する各 AWS サービスを小さく体験しながら学ぶための学習パスです。

## 学習の進め方

1. IAM で権限の考え方を理解する
2. Lambda でコードを実行する
3. API Gateway で Lambda を HTTP API として公開する
4. DynamoDB でデータを保存する
5. Cognito でユーザー認証を追加する
6. SQS で非同期処理を切り出す
7. SNS で通知を送る
8. CloudWatch でログ・メトリクス・アラームを見る
9. CloudFormation で全体をまとめて構築する

## フォルダ構成

```text
serverless-task-app-learning-path/
├── README.md
├── iam/
│   └── README.md
├── lambda/
│   └── README.md
├── api-gateway/
│   └── README.md
├── dynamodb/
│   └── README.md
├── cognito/
│   └── README.md
├── sqs/
│   └── README.md
├── sns/
│   └── README.md
├── cloudwatch/
│   └── README.md
└── cloudformation-lambda-webapp/
    ├── README.md
    ├── template.yaml
    └── frontend/
        └── index.html
```

## ハンズオン一覧

| 順番 | サービス | フォルダ | 体験すること |
|------|----------|----------|--------------|
| 1 | IAM | [iam](./iam/README.md) | 最小権限のロールを作り、Lambda 実行権限の考え方を理解する |
| 2 | Lambda | [lambda](./lambda/README.md) | 関数を作成し、テストイベント実行とログ確認を行う |
| 3 | API Gateway | [api-gateway](./api-gateway/README.md) | Lambda を HTTP API として公開し、ブラウザや curl で呼び出す |
| 4 | DynamoDB | [dynamodb](./dynamodb/README.md) | キー設計・項目追加・Query を体験する |
| 5 | Cognito | [cognito](./cognito/README.md) | ユーザー登録・確認・ログインの流れを体験する |
| 6 | SQS | [sqs](./sqs/README.md) | キュー投入・受信・DLQ の基本動作を確認する |
| 7 | SNS | [sns](./sns/README.md) | トピックとサブスクリプションを作り、通知を受け取る |
| 8 | CloudWatch | [cloudwatch](./cloudwatch/README.md) | Lambda のログ・メトリクス・アラームを確認する |
| 9 | CloudFormation | [cloudformation-lambda-webapp](./cloudformation-lambda-webapp/README.md) | ここまでの要素をまとめたフルスタック構成を一括デプロイする |

## 使い方のコツ

- まずは各サービス単体のハンズオンを順番に進める
- そのあとで `cloudformation-lambda-webapp` を開くと、各リソースが全体の中でどう組み合わさるか理解しやすい
- 各ハンズオンの後片付けを行い、不要な課金を避ける
