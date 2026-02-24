"""
Copilot Web Relay - WebSocket ハンドラ

WebSocket メッセージのルーティングとステータス応答を管理する。
"""
import asyncio
import logging
from typing import Optional, TYPE_CHECKING

from fastapi import WebSocket

if TYPE_CHECKING:
    from cli_bridge import CLIBridge

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """WebSocket 接続を管理し、メッセージをルーティングするハンドラ"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.cli_bridge: Optional["CLIBridge"] = None
        self._output_task: Optional[asyncio.Task] = None

    async def handle_message(self, message: dict) -> None:
        """
        受信メッセージをタイプに応じてルーティング

        Args:
            message: パースされた JSON メッセージ
                - type: input → CLI の stdin に書き込み
                - type: resize → CLI のターミナルサイズ変更
                - type: session (action: start) → CLI プロセス起動
                - type: session (action: stop) → CLI プロセス終了
        """
        msg_type = message.get("type")

        if msg_type == "input":
            await self._handle_input(message)
        elif msg_type == "resize":
            await self._handle_resize(message)
        elif msg_type == "session":
            await self._handle_session(message)
        else:
            await self.send_status(f"Unknown message type: {msg_type}", "error")

    async def _handle_input(self, message: dict) -> None:
        """CLI の stdin に入力を書き込む"""
        payload = message.get("payload", "")
        if self.cli_bridge is not None:
            await self.cli_bridge.write(payload)
        else:
            await self.send_status("No active session", "error")

    async def _handle_resize(self, message: dict) -> None:
        """CLI のターミナルサイズを変更"""
        cols = message.get("cols", 120)
        rows = message.get("rows", 40)
        if self.cli_bridge is not None:
            await self.cli_bridge.resize(cols, rows)
        else:
            await self.send_status("No active session", "error")

    async def _handle_session(self, message: dict) -> None:
        """セッションの開始・停止を処理"""
        action = message.get("action")

        if action == "start":
            await self._start_session(message)
        elif action == "stop":
            await self._stop_session()
        else:
            await self.send_status(f"Unknown session action: {action}", "error")

    async def _start_session(self, message: dict) -> None:
        """CLI プロセスを起動してセッションを開始"""
        if self.cli_bridge is not None:
            await self.send_status("Session already running", "running")
            return

        cols = message.get("cols", 120)
        rows = message.get("rows", 40)

        try:
            # CLIBridge のインポートと起動
            from cli_bridge import CLIBridge

            self.cli_bridge = CLIBridge()
            success = await self.cli_bridge.start(cols=cols, rows=rows)

            if success:
                await self.send_status("Session started", "running")
                # 出力監視ループをバックグラウンドで開始
                self._output_task = asyncio.create_task(self._output_loop())
            else:
                await self.send_status("Failed to start CLI process", "error")
                self.cli_bridge = None
        except ImportError:
            await self.send_status("CLIBridge not implemented yet", "error")
            self.cli_bridge = None
        except Exception as e:
            await self.send_status(f"Failed to start session: {e}", "error")
            self.cli_bridge = None

    async def _stop_session(self) -> None:
        """CLI プロセスを終了してセッションを停止"""
        if self.cli_bridge is None:
            await self.send_status("No active session", "stopped")
            return

        try:
            # 出力監視タスクをキャンセル
            if self._output_task and not self._output_task.done():
                self._output_task.cancel()
                try:
                    await self._output_task
                except asyncio.CancelledError:
                    pass
                self._output_task = None

            await self.cli_bridge.stop()
        except Exception as e:
            await self.send_status(f"Error stopping session: {e}", "error")
        finally:
            self.cli_bridge = None
            await self.send_status("Session stopped", "stopped")

    async def _on_cli_exit(self) -> None:
        """CLI プロセスが終了したときのコールバック"""
        self.cli_bridge = None
        await self.send_status("CLI process exited", "stopped")

    async def _output_loop(self) -> None:
        """
        CLI Bridge からの出力を監視し、ブラウザに転送するループ。

        asyncio.create_task() でバックグラウンド実行される。
        """
        if self.cli_bridge is None:
            return

        try:
            async for output in self.cli_bridge.read_output():
                await self.send_output(output)
        except asyncio.CancelledError:
            logger.debug("Output loop cancelled")
        except Exception as e:
            logger.error(f"Output loop error: {e}")
        finally:
            # プロセスが終了した場合
            if self.cli_bridge is not None and not self.cli_bridge.is_running:
                await self._on_cli_exit()

    async def cleanup(self) -> None:
        """
        WebSocket 切断時のクリーンアップ処理。

        CLI プロセスも終了させる。
        """
        if self.cli_bridge is not None:
            # 出力監視タスクをキャンセル
            if self._output_task and not self._output_task.done():
                self._output_task.cancel()
                try:
                    await self._output_task
                except asyncio.CancelledError:
                    pass
                self._output_task = None

            await self.cli_bridge.stop()
            self.cli_bridge = None

    async def send_output(self, payload: str) -> None:
        """
        type: output メッセージを送信

        Args:
            payload: CLI からの出力文字列
        """
        await self.websocket.send_json({
            "type": "output",
            "payload": payload,
        })

    async def send_status(self, payload: str, state: str) -> None:
        """
        type: status メッセージを送信

        Args:
            payload: 人間向けメッセージ（例: "Session started"）
            state: セッション状態（running | stopped | error）
        """
        await self.websocket.send_json({
            "type": "status",
            "payload": payload,
            "state": state,
        })
