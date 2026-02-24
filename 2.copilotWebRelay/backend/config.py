"""
Copilot Web Relay - 設定管理

アプリケーション全体の設定を dataclass で一元管理する。
"""
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    """サーバー設定"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True  # 開発モード用


@dataclass
class CLIConfig:
    """Copilot CLI 設定"""
    command: str = "copilot"
    default_cols: int = 120
    default_rows: int = 40
    encoding: str = "utf-8"


@dataclass
class Config:
    """アプリケーション設定"""
    server: ServerConfig = field(default_factory=ServerConfig)
    cli: CLIConfig = field(default_factory=CLIConfig)


# シングルトンインスタンス
config = Config()
