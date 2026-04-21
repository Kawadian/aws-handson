# Lambda ハンズオン

最小構成の Lambda 関数を作成し、テストイベント実行と CloudWatch Logs の確認を行う教材です。

## ゴール

- Lambda 関数を作成する
- テストイベントを使って実行する
- 実行ログを CloudWatch Logs で確認する

## 前提条件

- [IAM ハンズオン](../iam/README.md) で `handson-lambda-execution-role` を作成済み

## 手順

### 1. 関数を作成する

1. Lambda コンソールを開く
2. **関数の作成** を選ぶ
3. **一から作成** を選ぶ
4. 次の内容で作成する
   - 関数名: `handson-hello-lambda`
   - ランタイム: `Python 3.12`
   - 実行ロール: **既存のロールを使用する**
   - ロール名: `handson-lambda-execution-role`

### 2. コードを入力する

```python
import json


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    name = params.get("name") or event.get("name") or "AWS"
    message = f"Hello, {name}!"
    print({"receivedEvent": event, "message": message})
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": message
        }, ensure_ascii=False)
    }
```

### 3. テストイベントを実行する

1. **テスト** を押す
2. イベント名を `hello-event` にする
3. JSON に次を入力する

```json
{
  "name": "Lambda Hands-on"
}
```

4. 実行結果で `Hello, Lambda Hands-on!` が返ることを確認する

### 4. ログを確認する

1. **モニタリング** タブを開く
2. **CloudWatch Logs を表示** を選ぶ
3. `receivedEvent` と `message` が出力されていることを確認する

## 発展課題

- `event` に `tasks` 配列を渡して件数を返すように変更する
- 例外を投げたときに CloudWatch Logs へどう記録されるか確認する

## 片付け

- Lambda 関数 `handson-hello-lambda` を削除する

## 学べるポイント

- Lambda はサーバーを意識せずにコードを実行できる
- 入力イベントと返り値を明確に意識すると API 化しやすい
- ログ確認まで含めて 1 セットで理解するのが大切
