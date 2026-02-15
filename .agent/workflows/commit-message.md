---
description: Gitコミットメッセージの生成ルール
---

## コミットメッセージ形式

Conventional Commits 規約に従い、**日本語**でコミットメッセージを生成すること。

### フォーマット

```
<type>(<scope>): <日本語の要約>

<日本語の本文（任意）>
```

### type 一覧

| type | 用途 |
|---|---|
| `feat` | 新機能の追加 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `style` | コードの意味に影響しない変更（フォーマット等） |
| `refactor` | バグ修正でも機能追加でもないコード変更 |
| `perf` | パフォーマンス改善 |
| `test` | テストの追加・修正 |
| `ci` | CI 設定の変更 |
| `chore` | ビルドプロセスや補助ツールの変更 |

### scope の例

- `infra` — Terraform / AWS インフラ
- `backend` — バックエンド（FastAPI）
- `frontend` — フロントエンド（React）
- `docker` — Docker 関連
- `db` — データベース関連
- `api` — API エンドポイント

### ルール

1. **要約は日本語**で、簡潔に変更内容を記述する
2. **type は英語**のまま使用する
3. 要約は**50文字以内**を目安にする
4. 本文がある場合は、要約との間に**空行**を入れる
5. 本文では**変更の理由や影響**を説明する
6. 破壊的変更がある場合は `BREAKING CHANGE:` を本文に含める

### 良い例

```
feat(backend): ヘルスチェックエンドポイントを追加
```

```
feat(infra): Terraform AWS基盤構築

- networking: VPC, サブネット, IGW, NAT Gateway
- compute: EC2 (dev/staging), ECS Fargate (prod)
- database: RDS PostgreSQL
```

```
fix(api): 株価データ取得時のタイムゾーン変換エラーを修正
```

### 悪い例

```
update files          ← 具体性がない
Fixed bug             ← type がない、英語
feat: add new feature ← 英語で書いている
```
