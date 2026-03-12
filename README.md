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

## Como rodar
1. Criar ambiente virtual (opcional):
   - `python -m venv .venv`
   - `\.venv\Scripts\activate`
2. Instalar dependências:
   - `pip install -r requirements.txt`
3. Executar:
   - `python app.py`
4. Abrir no navegador:
   - `http://127.0.0.1:5000`

## Estrutura
- `app.py`: API e dados mocados
- `templates/index.html`: estrutura da página
- `static/styles.css`: layout visual
- `static/app.js`: renderização, filtros e modal
