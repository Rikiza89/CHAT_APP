# 💬 ChatApp - リアルタイムメッセージングプラットフォーム

WebSocketによるインスタントメッセージング、ブログ機能、ユーザー通知を備えたDjangoベースのチャットアプリケーション。

## 仕組み

**アーキテクチャ:**
- DjangoがHTTPリクエスト（Webページ、API、認証）を処理
- Django ChannelsがリアルタイムチャットのWebSocket接続を管理
- PostgreSQL/SQLiteが全データ（ユーザー、メッセージ、投稿）を保存
- インメモリチャネルレイヤーがWebSocketメッセージのブロードキャストを処理

**フロー:**
1. ユーザー登録/ログイン → Djangoがセッション作成
2. チャットルームへアクセス → WebSocket接続確立
3. メッセージ送信 → データベースに保存 + WebSocket経由でルームメンバーにブロードキャスト
4. イベント発生時にDjangoシグナル経由で通知トリガー

## 機能

✅ **リアルタイムチャット** - タイピングインジケーター、既読表示付きWebSocketメッセージング  
✅ **ダイレクト＆グループチャット** - 1対1および複数ユーザーの会話  
✅ **ブログシステム** - コメント、いいね、閲覧数トラッキング付き投稿  
✅ **通知機能** - メッセージ、コメント、いいね、プロフィール閲覧の通知  
✅ **ユーザープロフィール** - アバター、ステータスメッセージ、プライバシー設定  
✅ **REST API** - モバイルアプリ用JWT認証  
✅ **レスポンシブUI** - モバイルフレンドリーデザイン

## クイックセットアップ

```bash
# クローンとインストール
git clone <repo-url>
cd chatapp
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 設定（簡単のためSQLiteを使用）
cp .env.example .env

# データベースセットアップ
python manage.py migrate
python manage.py createsuperuser

# 実行
python manage.py runserver 0.0.0.0:8000
```

アクセス: `http://your-ip:8000`

## ローカルサーバーデプロイ（自宅/オフィス）

### オプション1: シンプルなrunserver（クイック）

```bash
# 起動時実行 - Linux/Mac
crontab -e
# 追加: @reboot cd /path/to/chatapp && /path/to/venv/bin/python manage.py runserver 0.0.0.0:8000

# 起動時実行 - Windows
# startup.batを作成:
cd C:\path\to\chatapp
venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
# ショートカットを配置: shell:startup
```

**メリット:** シンプル、設定不要  
**デメリット:** シングルスレッド、本番環境向けではない

### オプション2: 本番環境対応（推奨）

```bash
# インストール
pip install gunicorn

# 実行
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 2
```

**systemdサービス作成** `/etc/systemd/system/chatapp.service`:
```ini
[Unit]
Description=ChatApp
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/chatapp
Environment="PATH=/path/to/chatapp/venv/bin"
ExecStart=/path/to/chatapp/venv/bin/gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable chatapp
sudo systemctl start chatapp
```

## Raspberry Piデプロイ

### 1. Pi準備
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql nginx -y
```

### 2. データベースセットアップ
```bash
sudo -u postgres psql
CREATE DATABASE chatapp;
CREATE USER chatapp WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatapp TO chatapp;
\q
```

### 3. アプリデプロイ
```bash
cd /home/pi
git clone <repo-url> chatapp
cd chatapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 設定
nano .env
# 設定:
# DB_NAME=chatapp
# DB_USER=chatapp
# DB_PASSWORD=your_password
# DB_HOST=localhost

# 初期化
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. サービス作成
`sudo nano /etc/systemd/system/chatapp.service`:
```ini
[Unit]
Description=ChatApp
After=network.target postgresql.service

[Service]
User=pi
WorkingDirectory=/home/pi/chatapp
Environment="PATH=/home/pi/chatapp/venv/bin"
ExecStart=/home/pi/chatapp/venv/bin/gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --workers 2

[Install]
WantedBy=multi-user.target
```

### 5. Nginx設定
`sudo nano /etc/nginx/sites-available/chatapp`:
```nginx
server {
    listen 80;
    server_name _;
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/pi/chatapp/staticfiles/;
    }

    location /media/ {
        alias /home/pi/chatapp/media/;
    }
}
```

### 6. 全て起動
```bash
# サービス有効化
sudo systemctl enable chatapp
sudo systemctl start chatapp

# Nginx設定
sudo ln -s /etc/nginx/sites-available/chatapp /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # デフォルト削除
sudo systemctl restart nginx

# ステータス確認
sudo systemctl status chatapp
sudo systemctl status nginx
```

**アクセス:** `http://raspberry-pi-ip`

### 7. メンテナンスコマンド
```bash
# ログ表示
sudo journalctl -u chatapp -f

# 変更後の再起動
cd /home/pi/chatapp
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart chatapp

# エラー確認
sudo systemctl status chatapp
```

## パフォーマンスのヒント（Raspberry Pi）

```python
# config/settings.py - ワーカーメモリを削減
# Gunicorn: --workers 1 (Pi Zero/1用)
# Gunicorn: --workers 2 (Pi 3/4用)

# 接続プーリング有効化
DATABASES = {
    'default': {
        # ... 他の設定 ...
        'CONN_MAX_AGE': 600,
    }
}
```

## アクセスポイント

- **Web UI:** `http://your-ip`
- **管理画面:** `http://your-ip/admin`
- **API:** `http://your-ip/api/v1/`
- **通知:** `http://your-ip/accounts/notifications/`

## トラブルシューティング

**他のデバイスからアクセスできない:**
```bash
# ファイアウォール確認
sudo ufw allow 80
sudo ufw allow 8000

# settings.pyのALLOWED_HOSTSを確認
ALLOWED_HOSTS = ['*']  # テスト用
```

**WebSocketが動作しない:**
- Djangoのrunserverではなく、uvicornワーカー付き`gunicorn`を使用していることを確認
- ブラウザコンソールで接続エラーを確認

**静的ファイルが読み込まれない:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

**Piの動作が遅い:**
```bash
# ワーカーを1に削減
# PostgreSQLの代わりにSQLiteを使用
# デバッグモード無効化: DEBUG=False
```

## アップデート

```bash
cd /home/pi/chatapp
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart chatapp
```
