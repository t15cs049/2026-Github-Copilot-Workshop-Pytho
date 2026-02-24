"""
Pomodoro Timer App with Visual Feedback Enhancement
視覚的フィードバック強化機能を持つポモドーロタイマー
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

if __name__ == '__main__':
    # 開発環境でのみデバッグモードを使用
    # 本番環境では debug=False に設定してください
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
