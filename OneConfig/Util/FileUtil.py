import sys
from pathlib import Path
from ..Const import STORE_APPROOT_TEMPLATE


def get_app_path() -> str:
    return str(Path(getattr(sys, '_MEIPASS', Path.cwd())))


def expand_approot(s: str) -> str:
    return s.replace(STORE_APPROOT_TEMPLATE, get_app_path())