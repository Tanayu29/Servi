import os
import sys
import yaml


def get_base_dir():
    """
    実行環境に応じたベースディレクトリを返す
    - python実行時: プロジェクトルート
    - exe実行時   : exeのあるディレクトリ
    """
    if getattr(sys, "frozen", False):
        # PyInstaller exe
        return os.path.dirname(sys.executable)
    else:
        # python
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, "config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.yaml not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
