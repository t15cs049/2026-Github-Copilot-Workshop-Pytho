"""
Copilot Web Relay - FastAPI アプリケーションエントリポイント

WebSocket を通じて Copilot CLI とブラウザを接続する。
"""
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import config
from websocket_handler import WebSocketHandler

app = FastAPI(
    title="Copilot Web Relay",
    description="GitHub Copilot CLI をブラウザからアクセス可能にする Web Relay",
    version="0.1.0",
)

# CORS 設定（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ヘルスチェック用エンドポイント"""
    return {"status": "ok", "message": "Copilot Web Relay is running"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket エンドポイント

    WebSocketHandler を使用してメッセージをルーティングし、
    CLI Bridge との接続を管理する。
    """
    await websocket.accept()
    handler = WebSocketHandler(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handler.handle_message(message)
            except json.JSONDecodeError:
                await handler.send_status("Invalid JSON message", "error")
    except WebSocketDisconnect:
        # クライアントが切断した場合、セッションをクリーンアップ
        if handler.cli_bridge is not None:
            try:
                await handler.cli_bridge.stop()
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
    )
