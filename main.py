"""
Entry point único para o executável PyInstaller.

Modo de uso:
  DictationTool.exe              → ícone na bandeja (padrão)
  DictationTool.exe --dictation  → gravação/transcrição
  DictationTool.exe --overlay    → janela pill animada
"""
import sys

if __name__ == '__main__':
    if '--overlay' in sys.argv:
        from overlay import Overlay
        Overlay()

    elif '--dictation' in sys.argv:
        import dictation
        dictation.run()

    else:
        import tray
        tray.run_tray()
