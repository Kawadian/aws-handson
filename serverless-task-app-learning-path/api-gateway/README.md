# API Gateway ハンズオン

Lambda 関数を HTTP API として公開し、ブラウザや curl から呼び出す教材です。

## ゴール

- API Gateway で HTTP API を作成する
- Lambda 関数と統合する
- エンドポイントを呼び出してレスポンスを確認する

## 前提条件

- [Lambda ハンズオン](../lambda/README.md) で `handson-hello-lambda` を作成済み

## 手順

### 1. HTTP API を作成する

1. API Gateway コンソールを開く
2. **HTTP API を構築** を選ぶ
3. 統合先に `handson-hello-lambda` を選ぶ
4. ルートは `GET /hello` を設定する
5. ステージ名は `dev` にする

### 2. 動作確認する

作成完了後に表示された URL を使ってアクセスします。

```bash
curl "https://<api-id>.execute-api.<region>.amazonaws.com/dev/hello"
```

名前を変えて試す場合は、クエリ文字列を付ける代わりに Lambda 側で固定値を返しても構いません。まずは「HTTP で Lambda を呼べる」ことを確認するのが目的です。

### 3. API と Lambda の連携を観察する

1. API Gateway の **ステージ** で invoke URL を確認する
2. Lambda の **モニタリング** で呼び出し回数が増えることを確認する
3. CloudWatch Logs に API 経由のイベントが渡っていることを確認する

## 発展課題

- `POST /hello` を追加し、リクエストボディを受け取る
- CORS を有効化してブラウザ JavaScript から呼び出す

## 片付け

- 作成した HTTP API を削除する

## 学べるポイント

- API Gateway は Lambda を HTTP インターフェースとして公開できる
- ステージ URL を通すことでブラウザや curl から簡単に検証できる
- 本番では認証や CORS、エラーハンドリング設計も重要になる
