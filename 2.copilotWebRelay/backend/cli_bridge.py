"""
Copilot Web Relay - CLI Bridge

Copilot CLI プロセスを PTY で管理し、非同期 I/O を提供するモジュール。
pexpect を使用して PTY を作成し、asyncio と統合する。
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional

import pexpect

from config import config

logger = logging.getLogger(__name__)


class CLIBridge:
    """
    Copilot CLI プロセスの管理クラス。

    PTY（疑似端末）を介して copilot コマンドを起動・管理し、
    非同期 I/O によるストリーミング入出力を提供する。
    """

    def __init__(self) -> None:
        self._process: Optional[pexpect.spawn] = None
        self._output_queue: asyncio.Queue[str] = asyncio.Queue()
        self._read_task: Optional[asyncio.Task] = None
        self._running: bool = False

    async def start(self, cols: int = 120, rows: int = 40) -> bool:
        """
        PTY を作成して copilot プロセスを起動する。

        Args:
            cols: ターミナルの幅（デフォルト: 120）
            rows: ターミナルの高さ（デフォルト: 40）

        Returns:
            bool: 起動成功時 True、失敗時 False
        """
        if self._running:
            logger.warning("CLIBridge: プロセスは既に実行中です")
            return True

        try:
            # pexpect.spawn で copilot コマンドを PTY 付きで起動
            self._process = pexpect.spawn(
                config.cli.command,
                encoding=config.cli.encoding,
                dimensions=(rows, cols),
                timeout=None,  # タイムアウトなし（手動で管理）
            )
            self._running = True
            logger.info(f"CLIBridge: copilot プロセスを起動しました (cols={cols}, rows={rows})")

            # 出力読み取りタスクを開始
            self._read_task = asyncio.create_task(self._async_expect_loop())

            return True

        except pexpect.exceptions.ExceptionPexpect as e:
            logger.error(f"CLIBridge: プロセス起動に失敗しました: {e}")
            self._running = False
            self._process = None
            return False
        except FileNotFoundError:
            logger.error(f"CLIBridge: コマンド '{config.cli.command}' が見つかりません")
            self._running = False
            self._process = None
            return False
        except Exception as e:
            logger.error(f"CLIBridge: 予期しないエラー: {e}")
            self._running = False
            self._process = None
            return False

    async def stop(self) -> None:
        """プロセスを終了する。"""
        if not self._running:
            return

        self._running = False

        # 読み取りタスクをキャンセル
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None

        # プロセスを終了
        if self._process is not None:
            try:
                self._process.terminate(force=True)
                logger.info("CLIBridge: プロセスを終了しました")
            except Exception as e:
                logger.warning(f"CLIBridge: プロセス終了時にエラー: {e}")
            finally:
                self._process = None

        # キューをクリア
        while not self._output_queue.empty():
            try:
                self._output_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def write(self, data: str) -> None:
        """
        PTY の stdin に書き込む。

        Args:
            data: 書き込む文字列
        """
        if not self._running or self._process is None:
            logger.warning("CLIBridge: プロセスが実行されていないため書き込みできません")
            return

        loop = asyncio.get_event_loop()
        try:
            # ブロッキング I/O を run_in_executor で非同期化
            await loop.run_in_executor(None, self._process.send, data)
        except Exception as e:
            logger.error(f"CLIBridge: 書き込みエラー: {e}")

    async def resize(self, cols: int, rows: int) -> None:
        """
        PTY のサイズを変更する。

        Args:
            cols: 新しいターミナル幅
            rows: 新しいターミナル高さ
        """
        if not self._running or self._process is None:
            logger.warning("CLIBridge: プロセスが実行されていないためリサイズできません")
            return

        try:
            self._process.setwinsize(rows, cols)
            logger.debug(f"CLIBridge: ターミナルサイズを変更しました (cols={cols}, rows={rows})")
        except Exception as e:
            logger.error(f"CLIBridge: リサイズエラー: {e}")

    async def read_output(self) -> AsyncGenerator[str, None]:
        """
        PTY の stdout から出力を読み取る非同期ジェネレータ。

        Yields:
            str: 出力文字列
        """
        while self._running:
            try:
                # タイムアウト付きでキューから取得
                output = await asyncio.wait_for(
                    self._output_queue.get(),
                    timeout=0.5
                )
                yield output
            except asyncio.TimeoutError:
                # タイムアウト時は継続（running チェックのため）
                continue
            except asyncio.CancelledError:
                break

    @property
    def is_running(self) -> bool:
        """プロセスが実行中かどうかを返す。"""
        return self._running and self._process is not None

    async def _async_expect_loop(self) -> None:
        """
        PTY の出力を監視し、キューに格納する非同期ループ。

        run_in_executor でブロッキング read をラップし、
        出力を asyncio.Queue に push する。
        """
        loop = asyncio.get_event_loop()

        while self._running and self._process is not None:
            try:
                # ブロッキング read を run_in_executor で非同期化
                # read_nonblocking は即座に返るが、出力がない場合は空文字
                output = await loop.run_in_executor(
                    None,
                    self._read_output_blocking
                )

                if output:
                    await self._output_queue.put(output)

                # CPU 使用率を抑えるための短い待機
                await asyncio.sleep(0.01)

            except pexpect.exceptions.EOF:
                logger.info("CLIBridge: プロセスが終了しました (EOF)")
                self._running = False
                break
            except pexpect.exceptions.TIMEOUT:
                # タイムアウトは正常（出力がないだけ）
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._running:  # 意図的な停止でなければログ出力
                    logger.error(f"CLIBridge: 読み取りエラー: {e}")
                break

    def _read_output_blocking(self) -> str:
        """
        ブロッキングで PTY から出力を読み取る。

        Returns:
            str: 読み取った出力（出力がない場合は空文字）
        """
        if self._process is None:
            return ""

        try:
            # read_nonblocking で最大 4096 バイトを読み取り
            # タイムアウト 0.1 秒で出力がなければ空文字を返す
            return self._process.read_nonblocking(size=4096, timeout=0.1)
        except pexpect.exceptions.TIMEOUT:
            return ""
        except pexpect.exceptions.EOF:
            raise
