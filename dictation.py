"""
Dictation Tool com IA — Groq
Transcreve sua fala e corrige gramática automaticamente.
Modelo: Whisper large-v3 + Llama 3.3 70B (Groq)

Requisitos:
    pip install sounddevice numpy scipy keyboard pyperclip pyautogui groq python-dotenv
"""

import os
import sys
import threading
import tempfile
import time

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write as wav_write
import keyboard
import pyperclip
import pyautogui
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ─────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "SUA_CHAVE_GROQ")
HOTKEY        = "ctrl+windows"  # ⚠️ A tecla Windows pode ser bloqueada pelo SO.
                                # Se não funcionar, troque por: "ctrl+alt+d", "f9", etc.
SAMPLE_RATE   = 16000           # Hz — ideal para Whisper
MAX_DURATION  = 30              # Segundos máximos de gravação
LANGUAGE      = "pt"            # Idioma da transcrição

CORRECTION_PROMPT = (
    "Corrija o texto abaixo: "
    "1) corrija erros gramaticais e adicione pontuação adequada; "
    "2) remova vícios de linguagem (né, aí, tipo, então, sei lá, cara); "
    "3) formate em parágrafo limpo e coeso. "
    "Mantenha o sentido original. Retorne APENAS o texto corrigido, sem explicações."
    "\n\nTexto: "
)

client = Groq(api_key=GROQ_API_KEY)


# ─────────────────────────────────────────
# GRAVAÇÃO DE ÁUDIO
# ─────────────────────────────────────────
def record_audio() -> np.ndarray:
    """Grava enquanto o atalho estiver pressionado."""
    frames = []
    print("  🔴 Gravando...", end="", flush=True)

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback):
        start = time.time()
        while keyboard.is_pressed(HOTKEY):
            if time.time() - start > MAX_DURATION:
                print(" [limite máximo atingido]", end="")
                break
            time.sleep(0.05)

    print(" ✅")
    if not frames:
        return np.array([], dtype="float32")
    return np.concatenate(frames, axis=0)


def audio_to_wav_file(audio: np.ndarray) -> str:
    """Salva o áudio em arquivo .wav temporário."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_int16 = (audio * 32767).astype(np.int16)
    wav_write(tmp.name, SAMPLE_RATE, audio_int16)
    return tmp.name


# ─────────────────────────────────────────
# TRANSCRIÇÃO + CORREÇÃO (Groq)
# ─────────────────────────────────────────
def process(audio: np.ndarray) -> str:
    wav_path = audio_to_wav_file(audio)
    try:
        print("  📡 Transcrevendo com Whisper large-v3...", end="", flush=True)
        with open(wav_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language=LANGUAGE,
                response_format="text",
            )
        raw_text = transcription.strip()
        print(f" ✅\n  📝 Bruto: {raw_text}")

        print("  🤖 Corrigindo com Llama 3.3 70B...", end="", flush=True)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": CORRECTION_PROMPT + raw_text}],
            max_tokens=1000,
        )
        corrected = response.choices[0].message.content.strip()
        print(" ✅")
        return corrected
    finally:
        os.unlink(wav_path)


# ─────────────────────────────────────────
# INJEÇÃO DE TEXTO NO CAMPO ATIVO
# ─────────────────────────────────────────
def type_text(text: str):
    """Cola o texto no campo de texto atualmente em foco."""
    pyperclip.copy(text + " ")
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "v")
    print(f"  ✍️  Colado: {text}\n")


# ─────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────
def main():
    print("\n" + "═" * 45)
    print("  🎙  DICTATION TOOL — GROQ")
    print("═" * 45)
    print(f"  Segure [{HOTKEY.upper()}] para gravar")
    print(f"  Solte para transcrever e colar")
    print(f"  CTRL+C para sair")
    print("═" * 45 + "\n")

    try:
        while True:
            keyboard.wait(HOTKEY)

            # Debounce — ignora tecla solta imediatamente
            time.sleep(0.05)
            if not keyboard.is_pressed(HOTKEY):
                continue

            audio = record_audio()

            if audio.size < SAMPLE_RATE * 0.5:
                print("  ⚠️  Áudio muito curto, ignorado.\n")
                continue

            def run():
                try:
                    corrected = process(audio)
                    type_text(corrected)
                except Exception as e:
                    print(f"  ❌ Erro: {e}\n")

            threading.Thread(target=run, daemon=True).start()

    except KeyboardInterrupt:
        print("\n  👋 Encerrando. Até mais!")
        sys.exit(0)


if __name__ == "__main__":
    main()
