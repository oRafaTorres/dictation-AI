---
name: py-pro
description: >
  Agente expert e profissional em desenvolvimento backend com Python. Use esta skill
  SEMPRE que o projeto envolver Python — scripts, APIs, automações, integrações com
  serviços externos, ou qualquer lógica de servidor. O agente aplica boas práticas de
  segurança automaticamente (variáveis de ambiente, .env, .gitignore), registra erros
  em arquivos .md estruturados dentro de uma pasta de logs para aprendizado contínuo,
  e usa esses logs como referência ao depurar problemas semelhantes em outros projetos.
  Acione esta skill também quando o usuário mencionar: bug Python, API key, variável
  de ambiente, requirements.txt, erro de importação, exceção, traceback, ou qualquer
  falha em script Python.
---

# py-pro — Expert Python Backend Agent

## Identidade do Agente

Você é um engenheiro Python sênior. Seu trabalho é escrever código limpo, seguro e
sustentável — e quando algo quebra, documentar o ocorrido de forma que sirva de
aprendizado para projetos futuros do mesmo estilo.

---

## 1. Estrutura de Projeto Padrão

Ao iniciar ou organizar qualquer projeto Python, adote esta estrutura:

```
projeto/
├── .env                  # Chaves e segredos (NUNCA commitar)
├── .env.example          # Template sem valores reais (commitar este)
├── .gitignore            # Sempre incluir .env, __pycache__, *.pyc, logs/
├── requirements.txt      # Dependências fixadas com versão (pip freeze)
├── main.py               # Ponto de entrada principal
├── config.py             # Carregamento centralizado de variáveis de ambiente
├── logs/
│   └── errors/           # Arquivos .md de erros registrados
└── src/                  # Módulos do projeto
```

---

## 2. Segurança — API Keys e Variáveis de Ambiente

### Regra absoluta
**Nunca escrever API keys, senhas ou tokens diretamente no código.**

### Fluxo obrigatório ao detectar qualquer credencial no projeto:

**Passo 1 — Criar `.env`**
```dotenv
# .env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql://user:pass@host:5432/db
```

**Passo 2 — Criar `.env.example`** (sem valores reais)
```dotenv
# .env.example — copie este arquivo para .env e preencha os valores
OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
DATABASE_URL=
```

**Passo 3 — Criar `config.py`**
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

def get(key: str, required: bool = True) -> str:
    value = os.getenv(key)
    if required and not value:
        raise EnvironmentError(
            f"Variável de ambiente '{key}' não encontrada. "
            f"Verifique o arquivo .env (use .env.example como base)."
        )
    return value

# Expõe as chaves como constantes tipadas
OPENAI_API_KEY  = get("OPENAI_API_KEY")
GEMINI_API_KEY  = get("GEMINI_API_KEY", required=False)
GROQ_API_KEY    = get("GROQ_API_KEY",   required=False)
```

**Passo 4 — Criar `.gitignore` mínimo**
```gitignore
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
.venv/
venv/
logs/errors/
*.log
```

**Passo 5 — Instalar dependência**
```bash
pip install python-dotenv
pip freeze > requirements.txt
```

### Checklist de segurança antes de qualquer commit
- [ ] `.env` está no `.gitignore`?
- [ ] Nenhuma key hardcoded no código?
- [ ] `.env.example` existe e está atualizado?
- [ ] `requirements.txt` está atualizado?

---

## 3. Registro de Erros — Sistema de Logs em Markdown

### Quando registrar
Registre um `.md` de erro sempre que ocorrer:
- Exceção não tratada em produção ou durante desenvolvimento
- Falha de integração com API externa
- Bug que levou mais de 10 min para depurar
- Comportamento inesperado que pode se repetir

### Caminho padrão
```
logs/errors/YYYY-MM-DD_nome-do-erro.md
```

### Template do arquivo de log
```markdown
# Erro: [Nome curto e descritivo]

**Data:** YYYY-MM-DD HH:MM  
**Projeto:** [nome do projeto]  
**Arquivo:** [caminho/arquivo.py, linha X]  
**Categoria:** [ImportError | APIError | AuthError | NetworkError | LogicError | etc.]

---

## Traceback completo

```
[cole aqui o traceback completo]
```

## Contexto

O que estava acontecendo quando o erro ocorreu:
- [descrição do contexto]
- [variáveis relevantes no momento do erro]

## Causa raiz

[Explicação clara do porquê o erro aconteceu]

## Solução aplicada

```python
# Código antes (com bug)

# Código depois (corrigido)
```

## Prevenção futura

- [O que mudar na arquitetura ou no fluxo para evitar recorrência]
- [Validações que devem ser adicionadas]

## Aplicável a projetos similares?

- **Sim** — [descreva em quais contextos este erro pode aparecer novamente]
- Padrão de projeto afetado: [ex: "qualquer projeto que use Whisper + pyaudio no Windows"]
```

### Função auxiliar de logging
Adicione ao projeto quando relevante:

```python
# utils/error_logger.py
import os
import traceback
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path("logs/errors")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log_error(
    title: str,
    context: str,
    cause: str,
    solution: str,
    prevention: str,
    project: str = "este projeto",
    category: str = "RuntimeError",
    applies_to: str = "",
) -> str:
    """Registra um erro estruturado como arquivo .md em logs/errors/"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    slug = title.lower().replace(" ", "-")[:40]
    filename = LOGS_DIR / f"{date_str}_{slug}.md"

    tb = traceback.format_exc()

    content = f"""# Erro: {title}

**Data:** {date_str} {time_str}  
**Projeto:** {project}  
**Categoria:** {category}

---

## Traceback

```
{tb}
```

## Contexto
{context}

## Causa raiz
{cause}

## Solução aplicada
{solution}

## Prevenção futura
{prevention}

## Aplicável a projetos similares?
{applies_to or "A ser avaliado."}
"""
    filename.write_text(content, encoding="utf-8")
    print(f"  📋 Erro registrado em: {filename}")
    return str(filename)
```

---

## 4. Uso dos Logs como Aprendizado

Antes de depurar qualquer erro em um novo projeto, **consulte a pasta `logs/errors/`**:

```python
# Busca rápida nos logs existentes
import os
from pathlib import Path

def search_logs(keyword: str):
    logs_dir = Path("logs/errors")
    if not logs_dir.exists():
        print("Nenhum log encontrado.")
        return
    for md_file in logs_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        if keyword.lower() in content.lower():
            print(f"📄 Relevante: {md_file.name}")
```

Ao encontrar um log relevante, leia a seção **"Solução aplicada"** e **"Aplicável a projetos similares?"** antes de iniciar a depuração.

---

## 5. Padrões de Código Python

### Tratamento de exceções
```python
# ❌ Nunca fazer
except:
    pass

# ✅ Sempre especificar e logar
except openai.AuthenticationError as e:
    log_error(title="Falha de autenticação OpenAI", ...)
    raise
```

### Tipagem
```python
# Sempre usar type hints em funções públicas
def process_audio(audio: np.ndarray, language: str = "pt") -> str:
    ...
```

### Variáveis de ambiente em runtime
```python
# Validar no início do script, não durante a execução
if __name__ == "__main__":
    from config import OPENAI_API_KEY  # Falha aqui se faltar, não no meio do processo
    main()
```

---

## 6. Padrões deste projeto — Dictation Tool

Esta seção documenta os padrões específicos do `dictation.py` para que o Claude Code
possa recriar, depurar ou expandir qualquer parte sem depender do arquivo original.

### Gravação de áudio com sounddevice

O app grava enquanto o atalho estiver pressionado, usando callback de stream:

```python
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000  # Hz — padrão Whisper
MAX_DURATION = 30    # segundos máximos de gravação

def record_audio() -> np.ndarray:
    frames = []

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback):
        while keyboard.is_pressed(HOTKEY):
            if time.time() - start > MAX_DURATION:
                break
            time.sleep(0.05)

    return np.concatenate(frames, axis=0) if frames else np.array([], dtype="float32")
```

**Conversão para .wav temporário** (necessário para envio às APIs):
```python
import tempfile
from scipy.io.wavfile import write as wav_write

def audio_to_wav_file(audio: np.ndarray) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_int16 = (audio * 32767).astype(np.int16)
    wav_write(tmp.name, SAMPLE_RATE, audio_int16)
    return tmp.name  # lembrar de os.unlink(path) depois de usar
```

---

### Modelo único — Groq

O app usa exclusivamente **Whisper large-v3** para transcrição e **Llama 3.3 70B** para
correção gramatical, ambos via Groq. Ao rodar, já entra direto no loop de gravação.

```python
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process(audio: np.ndarray) -> str:
    wav_path = audio_to_wav_file(audio)
    try:
        # 1. Transcrição
        with open(wav_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="pt",
                response_format="text",
            )
        raw_text = transcription.strip()

        # 2. Correção gramatical
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": CORRECTION_PROMPT + raw_text}],
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    finally:
        os.unlink(wav_path)
```

---

### Injeção de texto no campo ativo

**Nunca usar `pyautogui.typewrite()`** — não suporta acentos e caracteres especiais do PT-BR.

O padrão correto é sempre via clipboard:

```python
import pyperclip
import pyautogui
import time

def type_text(text: str):
    pyperclip.copy(text + " ")  # espaço final para separar da próxima palavra
    time.sleep(0.1)             # aguarda clipboard ser preenchido
    pyautogui.hotkey("ctrl", "v")
```

Isso funciona em qualquer campo de texto do Windows (Word, navegador, Notion, VS Code, etc.)
porque usa o mecanismo nativo de colar do sistema operacional.

---

### Atalho de teclado global

```python
HOTKEY = "ctrl+windows"  # ⚠️ Windows key pode ser bloqueada pelo SO
                         # Alternativas: "ctrl+alt+d", "f9", "scroll_lock"

# Loop principal — segura para gravar, solta para transcrever
keyboard.wait(HOTKEY)          # aguarda pressionar
while keyboard.is_pressed(HOTKEY):  # grava enquanto segurar
    record_audio()
# ao soltar → transcreve e cola
```

**Processamento em thread separada** para não travar o listener de teclado:
```python
import threading
threading.Thread(target=process_and_type, daemon=True).start()
```

---

### Prompt de correção gramatical

O mesmo prompt é enviado para os 3 modelos, garantindo comportamento consistente:

```python
CORRECTION_PROMPT = (
    "Corrija o texto abaixo: "
    "1) corrija erros gramaticais e adicione pontuação adequada; "
    "2) remova vícios de linguagem (né, aí, tipo, então, sei lá, cara); "
    "3) formate em parágrafo limpo e coeso. "
    "Mantenha o sentido original. Retorne APENAS o texto corrigido, sem explicações."
    "\n\nTexto: "
)
```

---

## 7. Referências adicionais

- `references/security.md` — Checklist expandido de segurança para APIs e web
- `references/error-patterns.md` — Catálogo de erros comuns por categoria de projeto

Leia esses arquivos quando o projeto envolver autenticação, deploy, ou padrões de erro
recorrentes em projetos de integração com IA.
