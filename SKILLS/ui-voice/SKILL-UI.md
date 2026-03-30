---
name: ui-voice
description: >
  Skill de UI & UX design para interfaces de aplicativos de voz e ditado — clean,
  fluída e minimalista. Use esta skill SEMPRE que o projeto envolver uma interface
  gráfica para captura de voz, microfone, transcrição, ou qualquer app de áudio.
  A prioridade são animações dinâmicas com a biblioteca LottieFiles para representar
  espectro de voz, ondas sonoras, e estados do microfone. Acione também quando o
  usuário mencionar: tray icon, UI do dictation tool, animação de microfone, espectro
  de áudio, waveform, visualização de voz, interface de gravação, ou quiser deixar
  o app mais bonito e moderno.
---

# ui-voice — UI & UX para Apps de Voz

## Filosofia de Design

**Princípios inegociáveis:**
1. **Menos é mais** — cada elemento na tela deve ter uma razão de existir
2. **O microfone é o protagonista** — a animação de voz é o centro visual
3. **Estados claros** — idle / gravando / processando / erro — sempre visível
4. **Zero friction** — o usuário nunca deve se perguntar "está funcionando?"

**Paleta padrão (dark, ajustável):**
```css
--bg:          #0d0d0f;   /* fundo quase preto */
--surface:     #16161a;   /* cards e painéis */
--border:      #2a2a30;   /* bordas sutis */
--accent:      #7f5af0;   /* roxo elétrico — ação principal */
--accent-glow: #7f5af033; /* glow do accent */
--text:        #fffffe;   /* texto principal */
--text-muted:  #94a1b2;   /* texto secundário */
--success:     #2cb67d;   /* verde — sucesso / texto colado */
--error:       #ef4565;   /* vermelho — erro */
--recording:   #ef4565;   /* vermelho pulsante — gravando */
```

---

## 1. Animações Lottie — Guia de Uso

### Importação (HTML/JS)
```html
<!-- Via CDN — sempre usar a versão mais recente estável -->
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>

<!-- Player básico -->
<lottie-player
  id="voice-anim"
  src="https://assets.lottiefiles.com/packages/lf20_..."
  background="transparent"
  speed="1"
  loop
  autoplay
  style="width: 120px; height: 120px;"
></lottie-player>
```

### Importação (Python + webview / tkinter + HTML)
```python
# Para apps desktop com interface HTML embutida (pywebview, customtkinter + webview)
LOTTIE_CDN = "https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"
```

### Animações recomendadas por estado

| Estado | Lottie sugerido | Comportamento |
|--------|----------------|---------------|
| **Idle** | Onda suave pulsando devagar | `loop`, velocidade 0.5 |
| **Gravando** | Espectro de voz / waveform ativo | `loop`, velocidade 1.2 |
| **Processando** | Spinner ou ondas circulares | `loop`, velocidade 1.0 |
| **Sucesso** | Check mark animado | `loop: false`, uma vez |
| **Erro** | X ou shake | `loop: false`, uma vez |

### Busca de animações gratuitas
URL base: `https://lottiefiles.com/search?q=`
- `voice+waveform` — espectros de voz
- `sound+wave` — ondas sonoras
- `microphone` — ícones de microfone animados
- `audio+equalizer` — equalizadores
- `recording` — estados de gravação

### Controle dinâmico por estado
```javascript
const player = document.getElementById("voice-anim");

const ANIMATIONS = {
  idle:       "https://assets.lottiefiles.com/packages/lf20_idle.json",
  recording:  "https://assets.lottiefiles.com/packages/lf20_recording.json",
  processing: "https://assets.lottiefiles.com/packages/lf20_processing.json",
  success:    "https://assets.lottiefiles.com/packages/lf20_success.json",
  error:      "https://assets.lottiefiles.com/packages/lf20_error.json",
};

function setState(state) {
  const anim = ANIMATIONS[state];
  if (!anim) return;

  player.load(anim);
  player.setSpeed(state === "idle" ? 0.5 : state === "recording" ? 1.2 : 1.0);
  player.setLooping(["idle", "recording", "processing"].includes(state));
  player.play();

  // Atualiza classe CSS para mudar cores de acordo com o estado
  document.body.dataset.state = state;
}
```

---

## 2. Espectro de Voz em Canvas (fallback sem Lottie)

Use quando quiser animação reativa ao volume real do microfone:

```javascript
// Espectro de áudio em tempo real com Web Audio API
class VoiceSpectrum {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.analyser = null;
    this.animFrame = null;
  }

  async start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);
    this.analyser = audioCtx.createAnalyser();
    this.analyser.fftSize = 64;
    source.connect(this.analyser);
    this.draw();
  }

  draw() {
    const data = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(data);

    const { width, height } = this.canvas;
    this.ctx.clearRect(0, 0, width, height);

    const barW = width / data.length;
    data.forEach((val, i) => {
      const barH = (val / 255) * height;
      const hue = 260 + (i / data.length) * 60; // roxo → azul
      this.ctx.fillStyle = `hsla(${hue}, 80%, 65%, 0.9)`;
      this.ctx.beginPath();
      this.ctx.roundRect(
        i * barW + 1, height - barH,
        barW - 2, barH,
        [3, 3, 0, 0]
      );
      this.ctx.fill();
    });

    this.animFrame = requestAnimationFrame(() => this.draw());
  }

  stop() {
    if (this.animFrame) cancelAnimationFrame(this.animFrame);
  }
}
```

---

## 3. Layout Padrão — Dictation Tool

```html
<!-- Estrutura HTML semântica para o app de ditado -->
<div class="app">

  <!-- Indicador de estado superior -->
  <div class="status-bar">
    <span class="status-dot" data-state="idle"></span>
    <span class="status-label">Aguardando...</span>
  </div>

  <!-- Animação central — protagonista da UI -->
  <div class="voice-visual">
    <lottie-player id="voice-anim" ...></lottie-player>
  </div>

  <!-- Hotkey hint -->
  <div class="hotkey-hint">
    <kbd>Ctrl</kbd> + <kbd>⊞ Win</kbd>
    <span>para gravar</span>
  </div>

  <!-- Último texto colado -->
  <div class="last-output">
    <p class="output-label">Último texto</p>
    <p class="output-text" id="last-text">—</p>
  </div>

  <!-- Seletor de modelo (discreto, canto inferior) -->
  <div class="model-selector">
    <select id="model-select">
      <option value="openai">Whisper + GPT-4</option>
      <option value="gemini">Gemini 2.0</option>
      <option value="groq">Groq (grátis)</option>
    </select>
  </div>

</div>
```

---

## 4. CSS Essencial

```css
/* Reset e base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'DM Sans', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.app {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 32px;
  width: 320px;
}

/* Animação de estado do dot */
.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: background 0.3s;
}
.status-dot[data-state="recording"] {
  background: var(--recording);
  animation: pulse 0.8s ease-in-out infinite;
}
.status-dot[data-state="processing"] {
  background: var(--accent);
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(1.3); }
}

/* Área de animação Lottie */
.voice-visual {
  position: relative;
  width: 160px; height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Glow ao redor da animação quando gravando */
[data-state="recording"] .voice-visual::before {
  content: '';
  position: absolute;
  inset: -16px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--recording) 0%, transparent 70%);
  opacity: 0.2;
  animation: glow-pulse 0.8s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { transform: scale(1); opacity: 0.2; }
  50%       { transform: scale(1.1); opacity: 0.35; }
}

/* Hint de hotkey */
kbd {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
  font-family: monospace;
}

/* Output do último texto */
.output-text {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  max-width: 260px;
  line-height: 1.5;
  transition: color 0.3s;
}
[data-state="success"] .output-text { color: var(--success); }
```

---

## 5. Tray Icon (System Tray) — Boas Práticas

Para apps desktop com ícone na bandeja:

```python
# Usando pystray + PIL
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

def create_tray_icon(state: str) -> Image.Image:
    """Gera ícone colorido de acordo com o estado atual."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    colors = {
        "idle":       "#94a1b2",
        "recording":  "#ef4565",
        "processing": "#7f5af0",
    }
    color = colors.get(state, "#94a1b2")
    draw.ellipse([8, 8, 56, 56], fill=color)
    return img
```

**Tooltip do tray deve sempre indicar o estado:**
- 🎙 Dictation Tool — Aguardando
- 🔴 Dictation Tool — Gravando...
- ⏳ Dictation Tool — Processando...

---

## 6. Micro-interações Essenciais

| Evento | Feedback visual |
|--------|----------------|
| Tecla pressionada | Animação muda para `recording` + dot vermelho |
| Tecla solta | Animação muda para `processing` + dot roxo |
| Texto colado | Flash verde no output + animação `success` |
| Erro | Shake na animação + dot vermelho estático + mensagem |
| Áudio curto | Tooltip "gravação muito curta" por 2s |

---

## 7. Referências

- LottieFiles Player: https://developers.lottiefiles.com/docs/lottie-player/
- LottieFiles Free Animations: https://lottiefiles.com/free-animations
- DM Sans (fonte recomendada): https://fonts.google.com/specimen/DM+Sans
- Web Audio API (espectro): https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode
