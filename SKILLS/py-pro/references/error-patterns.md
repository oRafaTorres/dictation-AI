# Catálogo de Erros Comuns por Categoria

## Projetos de IA / APIs de Voz

### AuthenticationError (OpenAI/Groq)
**Causa:** Key inválida, expirada, ou carregada antes do `load_dotenv()`  
**Solução:** Garantir que `load_dotenv()` é chamado antes de instanciar o cliente  
**Padrão afetado:** Qualquer projeto que instancia cliente de API no escopo global do módulo

### sounddevice — PortAudio não encontrado
**Causa:** PortAudio não instalado no sistema operacional  
**Solução Windows:** `pip install sounddevice --pre` ou instalar binário do PortAudio  
**Solução Linux:** `sudo apt install libportaudio2`

### Whisper — CUDA out of memory
**Causa:** Modelo grande demais para a VRAM disponível  
**Solução:** Trocar `whisper.load_model("large")` por `"base"` ou `"small"`; adicionar `fp16=False` em CPU

### pyautogui — caracteres especiais não colados corretamente
**Causa:** `typewrite()` não suporta Unicode/acentos  
**Solução:** Usar `pyperclip.copy()` + `pyautogui.hotkey("ctrl", "v")`

---

## Projetos de Integração com Webhooks / n8n

### CORS — requisição bloqueada
**Causa:** Header `Access-Control-Allow-Origin` ausente na resposta  
**Solução:** Adicionar middleware CORS ou configurar no gateway

### ngrok — URL expirada
**Causa:** Sessão ngrok encerrada ou URL mudou  
**Solução:** Usar domínio fixo ngrok ou atualizar URL no cliente automaticamente

---

## Projetos com Supabase / Banco de Dados

### RPC retorna null inesperadamente
**Causa:** Parâmetro com nome errado na chamada RPC  
**Solução:** Conferir assinatura da função no Supabase SQL Editor

### Connection pool esgotado
**Causa:** Muitas conexões simultâneas sem fechar  
**Solução:** Usar connection pooling (PgBouncer) ou `with` statement para fechar conexões
