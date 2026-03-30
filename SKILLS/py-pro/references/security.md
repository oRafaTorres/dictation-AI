# Segurança — Checklist Expandido

## APIs e Credenciais

- [ ] Todas as keys carregadas via `os.getenv()` + `python-dotenv`
- [ ] `.env` no `.gitignore` antes do primeiro commit
- [ ] `.env.example` com todas as variáveis sem valores
- [ ] Nenhuma key em logs, prints de debug, ou mensagens de erro expostas ao usuário
- [ ] Rotacionar keys se houver suspeita de exposição

## Requisições HTTP

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "MyApp/1.0"})
    return session
```

- [ ] Sempre usar HTTPS
- [ ] Timeout explícito em todas as requisições (`timeout=30`)
- [ ] Nunca logar o corpo completo de requests com credenciais

## Arquivos Temporários

```python
import tempfile
import os

tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
try:
    # usar tmp.name
    ...
finally:
    os.unlink(tmp.name)  # Sempre limpar
```

## Dados do Usuário

- [ ] Nunca persistir áudio ou texto do usuário sem consentimento explícito
- [ ] Arquivos temporários deletados após processamento
- [ ] Logs não devem conter conteúdo sensível do usuário

## Requirements

```bash
# Fixar versões exatas para reproducibilidade e segurança
pip freeze > requirements.txt

# Verificar vulnerabilidades conhecidas
pip install pip-audit
pip-audit
```
