# 🎙 Dictation Tool com IA

Transcreve sua fala, corrige gramática e cola automaticamente em qualquer campo de texto ativo.  
Desenvolvido no **Antigravity IDE** com a extensão **Claude Code**.

---

## Modelo disponível

| # | Transcrição       | Correção gramatical | Custo         |
|---|-------------------|---------------------|---------------|
| 1 | Whisper (Groq)    | Llama 3.3 70B       | Gratuito*     |

*Dentro dos limites de rate limit gratuitos.

---

## Estrutura do projeto

```
dictation_tool/
├── .env                  # Chaves de API (nunca commitar)
├── .env.example          # Template de variáveis sem valores reais
├── .gitignore            # Inclui .env, __pycache__, logs/
├── requirements.txt      # Dependências fixadas com versão
├── dictation.py          # Script principal
├── logs/
│   └── errors/           # Erros registrados em .md (gerado automaticamente)
└── README.md             # Este arquivo
```

---

## Bibliotecas e Dependências

Lista completa das bibliotecas necessárias para o funcionamento do app, com descrição detalhada de cada uma. **Instale todas antes de executar o projeto.**

### Instalação rápida

```bash
pip install sounddevice numpy scipy keyboard pyperclip pyautogui groq python-dotenv
```

---

### Detalhamento de cada biblioteca

| Biblioteca | Versão | Comando de instalação |
|---|---|---|
| `sounddevice` | 0.5.5 | `pip install sounddevice==0.5.5` |
| `numpy` | 2.4.3 | `pip install numpy==2.4.3` |
| `scipy` | 1.17.1 | `pip install scipy==1.17.1` |
| `keyboard` | 0.13.5 | `pip install keyboard==0.13.5` |
| `pyperclip` | 1.11.0 | `pip install pyperclip==1.11.0` |
| `PyAutoGUI` | 0.9.54 | `pip install PyAutoGUI==0.9.54` |
| `groq` | 1.1.2 | `pip install groq==1.1.2` |
| `python-dotenv` | 1.2.2 | `pip install python-dotenv==1.2.2` |

---

#### `sounddevice` — Captura de áudio do microfone
Acessa o microfone do sistema e grava o áudio enquanto o hotkey está pressionado. Retorna os dados de áudio como array NumPy. Depende do **PortAudio** instalado no sistema.
- Requisito de sistema no Windows: se falhar, instale o PortAudio com `pip install sounddevice --pre` ou baixe o binário manualmente.

#### `numpy` — Processamento de arrays de áudio
Manipula os dados brutos de áudio capturados pelo `sounddevice`. Converte e concatena os chunks de áudio gravados em um único array antes de salvar o arquivo WAV.

#### `scipy` — Escrita de arquivos WAV
Usa `scipy.io.wavfile.write` para serializar o array NumPy em um arquivo `.wav` temporário. Esse arquivo é enviado para a API de transcrição (Groq/Whisper).

#### `keyboard` — Detecção de hotkey global
Registra e monitora combinações de teclas globais (ex: `Ctrl+Windows`, `Ctrl+Alt+D`, `F9`) mesmo quando o app está em background. Dispara os callbacks de início e fim de gravação.
- **Importante:** no Windows, requer execução como administrador para interceptar a tecla Windows.

#### `pyperclip` — Manipulação da área de transferência
Copia o texto transcrito e corrigido para o clipboard do sistema operacional. Funciona de forma cross-platform (Windows, macOS, Linux).

#### `PyAutoGUI` — Simulação de teclas (paste automático)
Simula o atalho `Ctrl+V` para colar o texto no campo de texto ativo após copiá-lo para o clipboard com `pyperclip`. Garante que o texto seja inserido na aplicação que estava em foco no momento.

#### `groq` — Transcrição e correção via Groq
SDK oficial da Groq. Usado no Modelo 3 para:
1. Transcrever áudio via **Whisper** (endpoint de áudio da Groq)
2. Corrigir gramática via **Llama 3.3 70B**
Requer a variável de ambiente `GROQ_API_KEY`. Disponível gratuitamente dentro dos limites de rate limit.

#### `python-dotenv` — Carregamento de variáveis de ambiente
Lê o arquivo `.env` na raiz do projeto e injeta a variável (`GROQ_API_KEY`) no ambiente antes da inicialização. Essencial para manter chaves de API fora do código-fonte.

---

## Instalação

```bash
pip install sounddevice numpy scipy keyboard pyperclip pyautogui
pip install openai google-generativeai groq python-dotenv
pip freeze > requirements.txt
```

### Dependência de sistema (Windows)
Se `sounddevice` falhar, instale o PortAudio:
```bash
pip install sounddevice --pre
```
Ou baixe o binário: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

---

## Configuração das chaves de API

Crie um arquivo `.env` na raiz do projeto (use `.env.example` como base):

```dotenv
# .env
GROQ_API_KEY=gsk_...
```

> ⚠️ Nunca commite o arquivo `.env`. Ele já está no `.gitignore`.

### Onde obter as chaves
- **Groq:** https://console.groq.com/keys (gratuito)

---

## Como usar

```bash
python dictation.py
```
1. Clique no campo de texto onde quer digitar (Word, navegador, Notion, etc.)
2. **Segure `Ctrl + Windows`** para gravar sua fala
3. **Solte `Ctrl + Windows`** — o texto é transcrito, corrigido e colado automaticamente

> ⚠️ A tecla Windows pode ser bloqueada pelo sistema operacional.  
> Se o atalho não responder, troque `HOTKEY` no topo do script por `"ctrl+alt+d"`, `"f9"`, etc.

---

## O que a IA corrige

- ✅ Erros ortográficos
- ✅ Pontuação (vírgulas, pontos, etc.)
- ✅ Vícios de linguagem (né, aí, tipo, então, sei lá, cara)
- ✅ Mantém o sentido original do que foi falado

---

## Fluxo interno

```
[Ctrl+Win segurado] → grava áudio via sounddevice
         ↓
[Ctrl+Win solto] → envia para API escolhida
         ↓
Modelo 3: Whisper (Groq) → Llama 3.3 70B corrige
         ↓
[Ctrl+V] → cola no campo de texto ativo
```

---

## Skills do projeto

Este projeto utiliza duas skills de agente desenvolvidas para o Antigravity + Claude Code:

### 🐍 `py-pro`
Agente expert em backend Python. Responsável por:
- Criar e manter `.env`, `.env.example`, `config.py` e `.gitignore` automaticamente
- Registrar erros em `logs/errors/YYYY-MM-DD_nome-erro.md` com template estruturado
- Consultar logs anteriores antes de depurar erros similares em novos projetos
- Aplicar boas práticas de segurança em toda integração com APIs externas

### 🎨 `ui-voice`
Skill de UI & UX para interfaces de voz. Responsável por:
- Design minimalista dark com animações por estado (idle / gravando / processando / sucesso / erro)
- Espectro de voz reativo ao microfone via Canvas + Web Audio API
- Micro-interações e feedback visual claro para cada estado do app
- Boas práticas para tray icon com ícone colorido por estado

---

## Personalização

| Variável            | Descrição                            | Padrão           |
|---------------------|--------------------------------------|------------------|
| `HOTKEY`            | Tecla de gravação                    | `ctrl+windows` ⚠️ |
| `MAX_DURATION`      | Tempo máximo de gravação (seg)       | `30`             |
| `LANGUAGE`          | Idioma da transcrição                | `pt`             |
| `CORRECTION_PROMPT` | Prompt de correção gramatical da IA  | (ver código)     |

---

## Próximos passos sugeridos

- [ ] Adicionar seleção de microfone (múltiplos dispositivos de entrada)
- [ ] Modo contínuo — grava em chunks automáticos sem segurar a tecla
- [ ] Interface gráfica com animação e espectro de voz
- [ ] Empacotar como `.exe` com PyInstaller para distribuição
