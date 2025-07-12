# raretech-bot

---

## ディレクトリ構成

```
├── app
│   └── main.py                # FastAPI アプリケーションのエントリーポイント
├── docker-compose.yml         # 開発用コンテナ構成（FastAPI 開発サーバー起動）
├── Dockerfile                 # 開発用 Dockerfile（リロード付き）
├── Dockerfile.prod            # 本番デプロイ用の Dockerfile（オプションで利用）
├── lambda_handler.py          # AWS Lambda 用のエントリーポイント
├── Makefile                   # よく使うコマンドの簡略化（build / up など）
├── README.md                  # このリポジトリの説明
├── requirements-dev.txt       # 開発用パッケージ（lint / dotenv など）
└── requirements.txt           # 本番環境用パッケージ
```