# API リファレンス

## 概要

現在、ポモドーロタイマーアプリケーションはREST APIを提供していません。すべての機能はフロントエンドのみで動作する予定です。

## 現在のエンドポイント

### `GET /`
メインページを表示します。

**レスポンス**
- **ステータスコード**: 200 OK
- **Content-Type**: text/html; charset=utf-8
- **ボディ**: index.htmlのHTMLコンテンツ

**説明**  
ポモドーロタイマーのUIを含むHTMLページをレンダリングします。

**例**
````bash
curl http://localhost:5000/
````

## 静的ファイルエンドポイント

Flaskの静的ファイル配信機能により、以下のリソースが提供されます：

### `GET /static/css/style.css`
スタイルシートファイルを取得します。

### `GET /static/js/timer.js`
タイマーロジックのJavaScriptファイルを取得します（現在は空）。

## 将来のAPI拡張計画

以下のAPIエンドポイントが将来追加される予定です：

### タイマー設定API（予定）
- `GET /api/settings` - タイマー設定の取得
- `POST /api/settings` - タイマー設定の保存

### タイマー履歴API（予定）
- `GET /api/history` - ポモドーロセッション履歴の取得
- `POST /api/history` - 新しいセッションの記録

### タイマー制御API（予定）
- `POST /api/timer/start` - タイマー開始
- `POST /api/timer/stop` - タイマー停止
- `POST /api/timer/reset` - タイマーリセット
- `GET /api/timer/status` - 現在のタイマー状態取得

**注意**: 上記のAPIは計画段階であり、実装されていません。
