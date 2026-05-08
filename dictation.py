import sys
import os

# ── Caminho base para arquivos de dados ───────────────────────────────────────
# frozen: sys._MEIPASS aponta para _internal/ onde ficam .env, Assets/, etc.
# dev:    mesma pasta do script
BASE_DIR = (sys._MEIPASS
            if getattr(sys, 'frozen', False)
            else os.path.dirname(os.path.abspath(__file__)))


def _pause_on_error(msg: str) -> None:
    if getattr(sys, 'frozen', False):
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "Dictation Tool — Erro", 0x10)
    else:
        print(f"\n❌ ERRO: {msg}")
        print("\nPressione Enter para fechar...")
        input()
    sys.exit(1)

# Verificar dependências antes de importar tudo
try:
    import io
    import time
    import subprocess
    import threading
    import traceback
    import datetime
    import numpy as np
    import sounddevice as sd
    import scipy.io.wavfile as wav
    import pyperclip
    import pyautogui
    import keyboard
    from groq import Groq
    from dotenv import load_dotenv
except ImportError as e:
    _pause_on_error(
        f"Dependência não instalada: {e}\n\n"
        "Execute no terminal:\n"
        "  pip install sounddevice numpy scipy keyboard pyperclip pyautogui groq python-dotenv pystray pillow"
    )

load_dotenv(os.path.join(BASE_DIR, '.env'))

# ── Configuração ──────────────────────────────────────────────────────────────
HOTKEY        = "ctrl+windows"
SAMPLE_RATE   = 16000
MAX_DURATION  = 59       # segundos (limite da API Whisper Groq)
LANGUAGE      = "pt"
CORRECTION_PROMPT = (
    "Você é um corretor gramatical. Corrija ortografia e pontuação do texto "
    "abaixo mantendo exatamente o sentido original. Retorne APENAS o texto "
    "corrigido, sem explicações, sem aspas, sem prefixos."
)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    _pause_on_error(
        "GROQ_API_KEY não encontrada.\n\n"
        "Crie um arquivo .env na pasta do projeto com:\n"
        "  GROQ_API_KEY=gsk_...\n\n"
        "Obtenha sua chave gratuita em: https://console.groq.com/keys"
    )

client = Groq(api_key=api_key)

# ── Estado global ─────────────────────────────────────────────────────────────
recording      = False
audio_chunks   = []
record_lock    = threading.Lock()
_hotkey_lock   = threading.Lock()   # garante atomicidade na troca de estado
_status_lines  = 0                  # linhas impressas no último status


def _print_status(msg: str) -> None:
    """Imprime msg apagando o status anterior no terminal (no-op se sem console)."""
    global _status_lines
    try:
        if _status_lines:
            print(f'\033[{_status_lines}A\033[J', end='', flush=True)
        print(msg, flush=True)
        _status_lines = msg.count('\n') + 1
    except Exception:
        pass

# ── Overlay ───────────────────────────────────────────────────────────────────
_overlay_proc: subprocess.Popen | None = None
_smooth_amp   = 0.0
_last_amp_t   = 0.0


def _overlay_send(cmd: str) -> None:
    if _overlay_proc and _overlay_proc.poll() is None:
        try:
            _overlay_proc.stdin.write(cmd + '\n')
            _overlay_proc.stdin.flush()
        except Exception:
            pass


def _overlay_start() -> None:
    global _overlay_proc
    if getattr(sys, 'frozen', False):
        cmd = [sys.executable, '--overlay']          # .exe se spawna com flag
    else:
        script = os.path.join(BASE_DIR, 'overlay.py')
        if not os.path.exists(script):
            return
        cmd = [sys.executable, script]
    try:
        _overlay_proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
        )
    except Exception:
        _overlay_proc = None


def _overlay_stop() -> None:
    _overlay_send('quit')


def log_error(context: str, error: Exception) -> None:
    logs_dir = os.path.join(os.path.dirname(__file__), "logs", "errors")
    os.makedirs(logs_dir, exist_ok=True)
    date_str   = datetime.date.today().isoformat()
    error_name = type(error).__name__
    filename   = f"{date_str}_{error_name}.md"
    filepath   = os.path.join(logs_dir, filename)
    content = (
        f"# {error_name} — {datetime.datetime.now().strftime('%H:%M:%S')}\n\n"
        f"**Contexto:** {context}\n\n"
        f"**Mensagem:** {error}\n\n"
        f"```\n{traceback.format_exc()}\n```\n"
    )
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content + "\n---\n")
    print(f"⚠️  Erro registrado em logs/errors/{filename}")


def audio_callback(indata, frames, time_info, status):
    global _smooth_amp, _last_amp_t
    if recording:
        audio_chunks.append(indata.copy())

        # Send smoothed amplitude to overlay at ~20 fps
        now = time.monotonic()
        if now - _last_amp_t >= 0.05:
            rms = float(np.sqrt(np.mean(indata ** 2)))
            _smooth_amp = 0.6 * _smooth_amp + 0.4 * rms
            _overlay_send(f'amplitude:{_smooth_amp:.4f}')
            _last_amp_t = now


def _deduplicate(text: str) -> str:
    """Remove repetições consecutivas que o Whisper às vezes alucina."""
    import re

    # 1. Repetição de frases separadas por pontuação: "Texto. Texto." → "Texto."
    parts = re.split(r'(?<=[.!?,;])\s+', text.strip())
    deduped = []
    for p in parts:
        if not deduped or p.strip().lower() != deduped[-1].strip().lower():
            deduped.append(p)
    text = ' '.join(deduped)

    # 2. Repetição do bloco de palavras (case-insensitive, ignora pontuação)
    # "Preciso de ajuda preciso de ajuda" → "Preciso de ajuda"
    words = text.split()
    n     = len(words)
    # normaliza cada palavra para comparação (sem pontuação, minúsculo)
    norm  = [re.sub(r'[^\w]', '', w).lower() for w in words]

    # busca em uma faixa ampla ao redor da metade
    for pivot in range(min(n // 2 + 4, n - 1), 0, -1):
        if norm[:pivot] == norm[pivot : pivot * 2]:
            text = ' '.join(words[:pivot])
            break

    return text


def transcribe(audio_int16: np.ndarray) -> str:
    import io as _io
    buf = _io.BytesIO()
    wav.write(buf, SAMPLE_RATE, audio_int16)
    buf.seek(0)
    buf.name = "audio.wav"
    response = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=buf,
        language=LANGUAGE,
    )
    return _deduplicate(response.text.strip())


def correct_grammar(text: str) -> str:
    if not text:
        return text
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": CORRECTION_PROMPT},
            {"role": "user",   "content": text},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


def paste_text(text: str) -> None:
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")


def process_recording() -> None:
    global audio_chunks

    with record_lock:
        chunks = audio_chunks[:]
        audio_chunks = []

    if not chunks:
        _overlay_send('hide')
        return

    audio_data = np.concatenate(chunks, axis=0).flatten().astype(np.float32)

    max_val = np.max(np.abs(audio_data))
    if max_val == 0:
        _overlay_send('hide')
        return

    audio_int16 = (audio_data / max_val * 32767).astype(np.int16)

    try:
        _print_status("🔄 Transcrevendo...")
        raw_text = transcribe(audio_int16)
        if not raw_text:
            _print_status("⚠️  Silêncio detectado.")
            _overlay_send('hide')
            return
        corrected = correct_grammar(raw_text)
        _print_status(f"✅ {corrected[:80]}{'...' if len(corrected) > 80 else ''}")
        paste_text(corrected)
    except Exception as e:
        log_error("process_recording", e)
    finally:
        _overlay_send('hide')


def on_hotkey_press() -> None:
    global recording, audio_chunks, _smooth_amp, _last_amp_t
    with _hotkey_lock:
        if recording:
            return
        recording = True
        audio_chunks = []
        _smooth_amp = 0.0
        _last_amp_t = 0.0
    _overlay_send('show')
    _print_status("🔴 Gravando... (solte para transcrever)")


def on_hotkey_release() -> None:
    global recording
    with _hotkey_lock:
        if not recording:
            return
        recording = False
    _overlay_send('processing')
    threading.Thread(target=process_recording, daemon=True).start()


def start_stream() -> None:
    _overlay_start()
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=audio_callback,
    ):
        keyboard.add_hotkey(HOTKEY, on_hotkey_press, suppress=False)
        keyboard.on_release_key(
            HOTKEY.split("+")[-1],
            lambda _: on_hotkey_release(),
            suppress=False,
        )
        _print_status(f"✅ Pronto! Segure [{HOTKEY}] para gravar.")
        stop_event = threading.Event()
        try:
            stop_event.wait()
        finally:
            _overlay_stop()


def run() -> None:
    """Entry point chamado por main.py (dev e .exe)."""
    try:
        start_stream()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_error("main", e)
        _pause_on_error(f"Erro inesperado: {e}\n\nDetalhes salvos em logs/errors/")


if __name__ == "__main__":
    run()
