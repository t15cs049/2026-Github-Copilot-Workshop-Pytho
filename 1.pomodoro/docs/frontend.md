# フロントエンド仕様

## 概要

ポモドーロタイマーのフロントエンドは、シンプルなHTML/CSS/JavaScriptで構築されています。現在は基本的なUI構造のみが実装されており、タイマーロジックは将来実装予定です。

## UIコンポーネント

### メインレイアウト（index.html）

#### 構造
````html
<div id="app">
  <h1>ポモドーロタイマー</h1>
  <div id="timer-display">00:00</div>
  <div id="timer-controls">
    <button disabled>スタート</button>
    <button disabled>ストップ</button>
    <button disabled>リセット</button>
  </div>
</div>
````

#### コンポーネント説明

**1. アプリケーションコンテナ (`#app`)**
- 最大幅: 400px
- センタリング配置
- 白い背景、角丸ボーダー
- ドロップシャドウによる立体感

**2. タイマー表示 (`#timer-display`)**
- フォントサイズ: 3rem
- デフォルト表示: "00:00"
- 文字間隔: 0.1em
- 将来、残り時間を動的に更新予定

**3. コントロールボタン (`#timer-controls`)**
- 3つのボタン: スタート、ストップ、リセット
- 現在の状態: すべて無効化（`disabled`属性）
- ボタン間のマージン: 8px

## スタイリング（style.css）

### デザインコンセプト
- **シンプル**: ミニマルで直感的なUI
- **日本語フォント対応**: ヒラギノ角ゴ、Meiryoなど
- **レスポンシブ**: 各種デバイスに対応
- **視覚的階層**: 適切な余白とシャドウ

### カラースキーム
- **背景色**: `#f7f7f7` (薄いグレー)
- **カードの背景**: `#fff` (白)
- **ボタンの背景**: `#e0e0e0` (グレー、無効状態)
- **テキスト**: `#333` (ダークグレー)

### タイポグラフィ
````css
font-family: 'Segoe UI', 'ヒラギノ角ゴ ProN', 'Meiryo', sans-serif;
````

### レイアウト詳細

**アプリケーションカード**
````css
#app {
  max-width: 400px;
  margin: 40px auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 32px 24px;
  text-align: center;
}
````

**タイマー表示**
````css
#timer-display {
  font-size: 3rem;
  margin: 24px 0;
  letter-spacing: 0.1em;
}
````

**ボタン**
````css
#timer-controls button {
  margin: 0 8px;
  padding: 8px 20px;
  font-size: 1rem;
  border-radius: 6px;
  border: none;
  background: #e0e0e0;
  color: #333;
  cursor: not-allowed;
}
````

## JavaScript（timer.js）

### 現在の実装状態
````javascript
// タイマー処理は後続ステップで実装予定
````

**ステータス**: 未実装

### 将来の実装予定機能

#### 1. タイマーコアロジック
- カウントダウン処理
- 作業時間/休憩時間の管理
- タイマー状態管理（停止中、実行中、一時停止）

#### 2. UI更新
- `#timer-display`への残り時間表示
- ボタンの有効/無効切り替え
- 視覚的フィードバック（色の変化など）

#### 3. イベントハンドリング
````javascript
// 将来実装予定の例
document.querySelector('button:nth-child(1)').addEventListener('click', startTimer);
document.querySelector('button:nth-child(2)').addEventListener('click', stopTimer);
document.querySelector('button:nth-child(3)').addEventListener('click', resetTimer);
````

#### 4. 通知機能
- タイマー終了時のアラート
- ブラウザ通知（Notification API）
- 音声アラート（オプション）

## ユーザーインタラクション

### 現在の動作
- ページ読み込み時: タイマー表示は "00:00"
- すべてのボタンが無効化されている
- 静的な表示のみ

### 将来の動作フロー

1. **初期表示**
   - タイマーは25分（作業時間）に設定
   - スタートボタンのみ有効

2. **スタートボタンクリック**
   - タイマー開始
   - 1秒ごとに`#timer-display`が更新
   - ストップボタンとリセットボタンが有効化

3. **ストップボタンクリック**
   - タイマー一時停止
   - スタートボタンで再開可能

4. **リセットボタンクリック**
   - タイマーを初期値にリセット
   - 停止状態に戻る

5. **タイマー終了**
   - 通知を表示
   - 休憩時間に自動切り替え（オプション）

## アクセシビリティ

### 現在の対応
- セマンティックHTML
- 日本語の適切なlang属性（`<html lang="ja">`）
- ビューポート設定（レスポンシブ対応）

### 将来の改善予定
- ARIAラベルの追加
- キーボードナビゲーション対応
- スクリーンリーダー対応
- フォーカス管理

## 開発者向けメモ

### デバッグ
ブラウザの開発者ツールのコンソールでデバッグ可能です。

### ファイル構造
````
static/
├── css/
│   └── style.css    # すべてのスタイル定義
└── js/
    └── timer.js     # 将来のタイマーロジック
````

### 依存関係
- 外部ライブラリなし（Vanilla JavaScript）
- CDNの使用なし
- フレームワークの使用なし

すべてネイティブのWeb技術のみで実装されています。
