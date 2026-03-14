# Enforce-RJ

Protótipo de dashboard para centralização dos casos de crédito em RJ.

## O que já tem

- Frontend em `HTML + CSS + JavaScript`
- Backend em `Python + Flask`
- Casos mocados para demonstração
- Filtros de pendência:
  - documento faltando
  - sem data AGC
  - AM atrasado
- Modal com campos financeiros e operacionais do caso
- Lista de AGCs do próximo mês

## Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/)
- pip (já incluído no Python)

## Como rodar

### 1. Clone o repositório (se ainda não tiver feito)

```bash
git clone <url-do-repositorio>
cd Enforce-RJ
```

### 2. Crie e ative o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> O ambiente virtual isola as dependências do projeto. Você saberá que está ativo quando o terminal mostrar `(.venv)` no início da linha.

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o servidor

```bash
python app.py
```

Saída esperada:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!
```

### 5. Acesse no navegador

```
http://127.0.0.1:5000
```

> O servidor roda em modo debug, então qualquer alteração no código é aplicada automaticamente sem precisar reiniciar.

## Estrutura do projeto

```
Enforce-RJ/
├── app.py                  # API Flask e dados mocados
├── requirements.txt        # Dependências Python
├── templates/
│   └── index.html          # Estrutura da página (frontend)
└── static/
    ├── styles.css          # Layout visual
    └── app.js              # Renderização, filtros e modal
```
