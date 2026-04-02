# CloudFront + S3 + EC2 ハンズオン

CloudFront のオリジンとビヘイビアで通信を振り分けたあとに、次の 2 点を体験できるようにするための資材です。

- **S3 のコンテンツが CloudFront でキャッシュされること**
- **EC2 のアプリケーションが状態を保持し、サーバー側で処理していること**

このフォルダには、S3 に置く静的ファイルと、EC2 で動かすシンプルな Python サーバーをまとめています。

## フォルダ構成

```text
cloudfront-s3-ec2/
├── README.md
├── ec2-origin/
│   └── server.py
└── s3-origin/
    ├── index.html
    └── static/
        ├── app.js
        ├── cache-demo.txt
        └── style.css
```

## ゴール

このハンズオンが完了すると、CloudFront 配下で次のようにアクセスできる状態になります。

- `https://<CloudFrontのドメイン>/` → **S3 オリジン**の画面
- `https://<CloudFrontのドメイン>/static/cache-demo.txt` → **S3 オリジン**のキャッシュ確認用ファイル
- `https://<CloudFrontのドメイン>/api/state` → **EC2 オリジン**の状態確認 API
- `https://<CloudFrontのドメイン>/api/memos` → **EC2 オリジン**のメモ保存 API
- `https://<CloudFrontのドメイン>/api/calculate` → **EC2 オリジン**のサーバー側計算 API

## 事前準備

- CloudFront ディストリビューションを 1 つ作成済み
- S3 バケットを 1 つ作成済み
- Amazon Linux 2023 / Ubuntu などの EC2 を 1 台起動済み
- EC2 に `python3` がインストール済み
- CloudFront から S3/EC2 へアクセスできる状態になっている

## 1. S3 用ファイルをアップロードする

S3 オリジンに使うファイルは `s3-origin/` 配下です。

### 手動でアップロードする場合

S3 バケットに次のように配置してください。

- `s3-origin/index.html` → `index.html`
- `s3-origin/static/app.js` → `static/app.js`
- `s3-origin/static/style.css` → `static/style.css`
- `s3-origin/static/cache-demo.txt` → `static/cache-demo.txt`

### AWS CLI でアップロードする場合

`<YOUR_BUCKET_NAME>` を実際のバケット名に置き換えて実行します。

```bash
aws s3 cp /path/to/cloudfront-s3-ec2/s3-origin/index.html s3://<YOUR_BUCKET_NAME>/index.html \
  --content-type text/html \
  --cache-control no-cache

aws s3 cp /path/to/cloudfront-s3-ec2/s3-origin/static s3://<YOUR_BUCKET_NAME>/static/ \
  --recursive \
  --cache-control public,max-age=300
```

### S3 側で確認したいこと

- `index.html` は更新を反映しやすいように `no-cache`
- `static/cache-demo.txt` は `max-age=300` を付けて、CloudFront のキャッシュヒットを観察しやすくする

## 2. EC2 にサーバーを配置する

EC2 オリジンに使うファイルは `ec2-origin/server.py` です。外部ライブラリは不要で、`python3` だけで動きます。

### 配置例

```bash
scp /path/to/cloudfront-s3-ec2/ec2-origin/server.py ec2-user@<EC2のIP>:/home/ec2-user/server.py
```

### 起動例

```bash
python3 server.py --host 0.0.0.0 --port 8080
```

起動後に次のようなエンドポイントが使えます。

- `GET /health`
- `GET /api/state`
- `POST /api/memos`
- `POST /api/calculate`

### EC2 サーバーで体験できること

- サーバー起動時刻とアップタイムを返す
- 保存したメモを**サーバーメモリ上に保持**する
- 送信した数値配列の合計値と平均値を**サーバー側で計算**する
- ホスト名・PID・総リクエスト数を返す

> メモはプロセスのメモリに保存されます。`server.py` を再起動すると消えるため、「EC2 で状態を持っている」ことを確認しやすくなっています。

## 3. CloudFront のオリジンとビヘイビアを設定する

おすすめ構成は次のとおりです。

### オリジン

1. **S3 origin**
   - S3 バケットを指定
2. **EC2 origin**
   - EC2 のパブリック DNS または Elastic IP を指定
   - `HTTP only` でも可
   - `Origin protocol policy`: HTTP Only
   - ポートは `8080`（`server.py` を 8080 で起動した場合）

### ビヘイビア

1. **Default behavior (`*`)**
   - Origin: S3
2. **`/api/*` behavior**
   - Origin: EC2
   - Allowed methods: `GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE` のうち最低でも `GET, HEAD, OPTIONS, POST`
   - Cache policy: 動的 API と分かるもの（例: CachingDisabled）

これで `/` や `/static/*` は S3、`/api/*` は EC2 へ振り分けられます。

## 4. 動作確認する

### 4-1. S3 キャッシュの確認

1. `https://<CloudFrontのドメイン>/` を開く
2. **「S3 キャッシュ情報を取得」** を押す
3. 画面上に次のような情報が表示されることを確認する
   - `x-cache`
   - `age`
   - `etag`
   - `last-modified`
4. 同じボタンを数回押し、`x-cache: Hit from cloudfront` が出ることを確認する
5. S3 上の `static/cache-demo.txt` を書き換える
6. すぐに再度 CloudFront 経由で取得し、古い内容のままなら CloudFront キャッシュが効いている
7. S3 へ直接アクセスした内容と比較して差が出れば、キャッシュの効果を体感できる

#### すぐに変化を見たいとき

- TTL を短くする
- CloudFront の invalidation を実行する
- `cache-demo.txt` のファイル名を変えて再配置する

### 4-2. EC2 の状態保持を確認

1. 画面下部の **「サーバー状態を更新」** を押す
2. `hostname`, `pid`, `bootTime`, `requestCount` が表示される
3. メモ欄に文章を入れて **「メモを保存」** を押す
4. 再度 **「サーバー状態を更新」** を押す
5. 保存したメモが残っていれば、EC2 側プロセスが状態を保持している
6. `server.py` を再起動してもう一度確認し、メモが消えることを確かめる

### 4-3. EC2 のサーバー側処理を確認

1. 数値入力欄に `10, 20, 35` のように入力する
2. **「サーバーで計算する」** を押す
3. EC2 から返ってくる `sum`, `average`, `count` を確認する
4. ブラウザではなくサーバー側で計算した結果が返るので、CloudFront の振り分け先が EC2 であることを実感できる

## 5. トラブルシュート

### `/api/*` が 403 / 502 になる

- CloudFront の `/api/*` ビヘイビアが EC2 オリジンを向いているか確認する
- EC2 のセキュリティグループで 8080 番ポートが許可されているか確認する
- EC2 上で `python3 server.py --host 0.0.0.0 --port 8080` が起動しているか確認する

### `x-cache` が増えない

- ブラウザキャッシュではなく CloudFront を見たいので、画面のボタンから再取得する
- `cache-demo.txt` に `Cache-Control` が設定されているか確認する
- CloudFront の cache policy が極端に短くなっていないか確認する

### メモが保存されない

- `/api/memos` が EC2 に到達しているか確認する
- EC2 のプロセスを再起動していないか確認する
- 文字数制限（120 文字）を超えていないか確認する

## 6. 学べるポイント

- **CloudFront + S3**: 静的ファイル配信とキャッシュ
- **CloudFront + EC2**: パスベースルーティングによる動的処理
- **EC2 の状態保持**: アプリケーションプロセスがメモリ上にデータを持つ感覚
- **サーバー側処理**: API が計算結果を返す流れ

まずはこの構成で「S3 は静的配信とキャッシュ」「EC2 は動的処理と状態保持」という役割分担を体験するのがおすすめです。
