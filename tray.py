import os
import sys
import threading
import subprocess
from PIL import Image
import pystray

BASE_DIR  = (sys._MEIPASS
             if getattr(sys, 'frozen', False)
             else os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(BASE_DIR, "Assets", "ICON.ico")

_dictation_process = None
_stop_event        = threading.Event()


def load_icon() -> Image.Image:
    if os.path.exists(ICON_PATH):
        return Image.open(ICON_PATH)
    from PIL import ImageDraw
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill=(1, 254, 195))
    return img


def start_dictation():
    global _dictation_process
    if _dictation_process and _dictation_process.poll() is None:
        return
    if getattr(sys, 'frozen', False):
        cmd = [sys.executable, '--dictation']
    else:
        cmd = [sys.executable, os.path.join(BASE_DIR, 'dictation.py')]
    _dictation_process = subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )


def stop_dictation():
    global _dictation_process
    if _dictation_process:
        _dictation_process.terminate()
        _dictation_process = None


def on_quit(icon, item):
    stop_dictation()
    _stop_event.set()
    icon.stop()


def build_menu():
    return pystray.Menu(
        pystray.MenuItem("🎙 Dictation Tool", lambda *_: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Encerrar", on_quit),
    )


def run_tray():
    icon = pystray.Icon(
        "DictationTool",
        load_icon(),
        "Dictation Tool",
        menu=build_menu(),
    )
    start_dictation()
    icon.run()


if __name__ == "__main__":
    run_tray()
