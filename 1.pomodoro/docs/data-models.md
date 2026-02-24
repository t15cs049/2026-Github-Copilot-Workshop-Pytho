# データモデル仕様

## 概要

現在、ポモドーロタイマーアプリケーションにはデータ永続化機能が実装されていません。すべての状態はクライアント側（ブラウザ）で管理される予定です。

このドキュメントでは、将来実装される可能性のあるデータモデルについて記載しています。

## 現在の実装状態

**ステータス**: データモデル未実装

- データベースなし
- ORMなし
- データ永続化なし

すべての状態はメモリ上（JavaScriptの変数）で管理される予定です。

## 将来のデータモデル案

以下のデータモデルは、将来の拡張として検討されているものです。

### 1. TimerSettings（タイマー設定）

ユーザーのタイマー設定を保存するモデル。

**フィールド**

| フィールド名 | 型 | 説明 | デフォルト値 |
|------------|-----|------|------------|
| `work_duration` | integer | 作業時間（分） | 25 |
| `short_break_duration` | integer | 短い休憩時間（分） | 5 |
| `long_break_duration` | integer | 長い休憩時間（分） | 15 |
| `sessions_before_long_break` | integer | 長い休憩までのセッション数 | 4 |
| `auto_start_breaks` | boolean | 休憩自動開始 | false |
| `auto_start_sessions` | boolean | 作業自動開始 | false |
| `notification_enabled` | boolean | 通知有効化 | true |
| `sound_enabled` | boolean | サウンド有効化 | true |

**例（JSON形式）**
````json
{
  "work_duration": 25,
  "short_break_duration": 5,
  "long_break_duration": 15,
  "sessions_before_long_break": 4,
  "auto_start_breaks": false,
  "auto_start_sessions": false,
  "notification_enabled": true,
  "sound_enabled": true
}
````

### 2. TimerSession（タイマーセッション）

完了したポモドーロセッションの履歴を記録するモデル。

**フィールド**

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| `id` | integer | セッションID（主キー） |
| `session_type` | string | セッションタイプ（"work", "short_break", "long_break"） |
| `duration_minutes` | integer | セッションの長さ（分） |
| `started_at` | datetime | 開始日時 |
| `completed_at` | datetime | 完了日時 |
| `interrupted` | boolean | 中断されたか |

**例（JSON形式）**
````json
{
  "id": 1,
  "session_type": "work",
  "duration_minutes": 25,
  "started_at": "2026-02-24T10:00:00Z",
  "completed_at": "2026-02-24T10:25:00Z",
  "interrupted": false
}
````

### 3. TimerState（タイマー状態）

現在のタイマーの実行状態を表すモデル（クライアント側のみ）。

**フィールド**

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| `status` | string | 状態（"idle", "running", "paused"） |
| `session_type` | string | 現在のセッションタイプ |
| `remaining_seconds` | integer | 残り秒数 |
| `total_seconds` | integer | セッションの合計秒数 |
| `sessions_completed` | integer | 完了したセッション数 |

**例（JavaScript）**
````javascript
const timerState = {
  status: "running",
  session_type: "work",
  remaining_seconds: 1200,  // 20分
  total_seconds: 1500,      // 25分
  sessions_completed: 2
};
````

## データストレージ戦略

### フェーズ1: ローカルストレージ（現在）
- ブラウザのLocalStorageを使用
- 設定の保存のみ
- サーバー側の実装不要

**実装例**
````javascript
// 設定の保存
localStorage.setItem('timerSettings', JSON.stringify(settings));

// 設定の読み込み
const settings = JSON.parse(localStorage.getItem('timerSettings'));
````

### フェーズ2: サーバー側データベース（将来）
データベースを導入する場合の候補：

- **SQLite**: 開発環境、シンプルなデプロイ
- **PostgreSQL**: 本番環境、スケーラビリティ
- **MongoDB**: ドキュメント指向、柔軟なスキーマ

### フェーズ3: ユーザー認証（将来）
ユーザーごとのデータ管理：

**Userモデル追加案**

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| `id` | integer | ユーザーID（主キー） |
| `username` | string | ユーザー名 |
| `email` | string | メールアドレス |
| `password_hash` | string | パスワードハッシュ |
| `created_at` | datetime | 作成日時 |

リレーション:
- `User` 1対1 `TimerSettings`
- `User` 1対多 `TimerSession`

## データフロー

### 現在の設計（クライアント側のみ）

````
ユーザー操作
    ↓
JavaScriptイベントハンドラ
    ↓
タイマーロジック（timer.js）
    ↓
DOMの更新
````

### 将来の設計（サーバー側API追加時）

````
ユーザー操作
    ↓
JavaScriptイベントハンドラ
    ↓
Fetch API（REST APIコール）
    ↓
Flaskルート（/api/*）
    ↓
サービス層
    ↓
リポジトリ層
    ↓
データベース
````

## バリデーション

### 設定値のバリデーション（将来実装）

**work_duration（作業時間）**
- 型: 整数
- 範囲: 1〜60分
- デフォルト: 25分

**short_break_duration（短い休憩）**
- 型: 整数
- 範囲: 1〜30分
- デフォルト: 5分

**long_break_duration（長い休憩）**
- 型: 整数
- 範囲: 5〜60分
- デフォルト: 15分

**sessions_before_long_break**
- 型: 整数
- 範囲: 1〜10
- デフォルト: 4

## まとめ

現在のアプリケーションはデータモデルを持たず、すべてクライアント側で完結する設計です。将来の拡張に備えて、このドキュメントでは以下を定義しました：

- タイマー設定のデータ構造
- セッション履歴のデータ構造
- タイマー状態の管理方法
- データストレージ戦略

データ永続化が必要になった際は、このドキュメントを基に実装を進めることができます。
