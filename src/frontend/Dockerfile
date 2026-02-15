# ベースイメージ
FROM node:20-slim

# 作業ディレクトリ
WORKDIR /app

# パッケージ定義をコピー
COPY package.json package-lock.json* ./

# 依存関係インストール
RUN npm install

# ソースコードをコピー
COPY . .

# 開発サーバー起動
CMD ["npm", "run", "dev", "--", "--host"]
