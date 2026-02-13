# 💱 Conversor de Moedas Pro

Conversor de moedas profissional com interface gráfica, CLI moderna, persistência em banco de dados e múltiplas fontes de dados.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)

## ✨ Funcionalidades

### 🖥️ Interfaces

- **GUI (Tkinter)** - Interface gráfica moderna e intuitiva
- **CLI (Rich)** - Terminal colorido com tabelas e progress bars
- **API** - Use como biblioteca em seus projetos

### 💰 Conversão

- 🔄 Conversão entre 150+ moedas mundiais
- 📊 Conversão múltipla (uma origem → vários destinos)
- 💹 Taxas em tempo real com cache inteligente
- 🔄 Fallback automático entre APIs

### 💾 Persistência

- 🗄️ Banco de dados SQLite com SQLAlchemy
- 📜 Histórico completo de conversões
- 📈 Estatísticas e análises
- 🔍 Filtros avançados

### 📤 Exportação

- 📊 Excel (.xlsx)
- 📄 PDF
- 📋 JSON/CSV

### 📊 Visualização

- 📈 Gráficos de evolução de taxas
- 📊 Comparativos entre moedas
- 📉 Tendências

## 🚀 Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/conversor-moedas.git
cd conversor-moedas

# Crie o ambiente virtual
python -m venv venv

# Ative (Windows)
venv\Scripts\activate
# Ative (Linux/Mac)
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure (opcional - já vem com API gratuita)
cp .env.example .env
```

## 💻 Como Usar

### Interface Gráfica (GUI)

```bash
python -m src.gui
# ou
python gui.py
```

### Linha de Comando (CLI)

```bash
# Modo interativo
python -m src.cli

# Comando rápido
python -m src.cli convert 100 USD BRL

# Múltiplas moedas
python -m src.cli convert 100 USD --to BRL,EUR,GBP

# Listar moedas
python -m src.cli list

# Histórico
python -m src.cli history --limit 10

# Estatísticas
python -m src.cli stats

# Exportar
python -m src.cli export --format excel --output historico.xlsx
```

### Como Biblioteca

```python
from src.core import ConversorMoedas

conversor = ConversorMoedas()

# Conversão simples
resultado = conversor.converter(100, "USD", "BRL")
print(f"100 USD = {resultado.valor_convertido:.2f} BRL")

# Conversão múltipla
resultados = conversor.converter_multiplo(100, "USD", ["BRL", "EUR", "GBP"])

# Estatísticas
stats = conversor.obter_estatisticas("USD", "BRL", dias=30)
```

## 🏗️ Arquitetura

```
conversor-moedas/
├── src/
│   ├── core/              # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── conversor.py   # Classe principal
│   │   ├── models.py      # Modelos Pydantic
│   │   └── cache.py       # Sistema de cache
│   │
│   ├── api/               # Clientes de API
│   │   ├── __init__.py
│   │   ├── base.py        # Classe base
│   │   ├── frankfurter.py # API Frankfurter
│   │   ├── exchangerate.py# API ExchangeRate
│   │   └── manager.py     # Gerenciador com fallback
│   │
│   ├── database/          # Persistência
│   │   ├── __init__.py
│   │   ├── db.py          # Conexão SQLAlchemy
│   │   ├── models.py      # Modelos ORM
│   │   └── repository.py  # Repositório de dados
│   │
│   ├── services/          # Serviços
│   │   ├── __init__.py
│   │   ├── export.py      # Exportação
│   │   ├── charts.py      # Gráficos
│   │   └── stats.py       # Estatísticas
│   │
│   ├── cli/               # Interface CLI
│   │   ├── __init__.py
│   │   └── app.py         # CLI com Rich
│   │
│   ├── gui/               # Interface Gráfica
│   │   ├── __init__.py
│   │   └── app.py         # Tkinter app
│   │
│   └── utils/             # Utilitários
│       ├── __init__.py
│       ├── formatters.py  # Formatação
│       └── validators.py  # Validação
│
├── tests/                 # Testes
├── docs/                  # Documentação
├── docker/                # Docker
└── scripts/               # Scripts auxiliares
```

## 🛠️ Configuração

Edite o arquivo `.env`:

```env
# APIs (ordem de prioridade)
API_PRIMARY=frankfurter
API_SECONDARY=exchangerate
API_EXCHANGERATE_KEY=sua_chave_aqui

# Banco de dados
DATABASE_URL=sqlite:///data/conversor.db

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 🧪 Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_conversor.py -v
```

## 🐳 Docker

```bash
# Build
docker build -t conversor-moedas .

# Run CLI
docker run -it conversor-moedas cli

# Run GUI (requer X11)
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix conversor-moedas gui
```

## 📸 Screenshots

### CLI com Rich

```
💱 CONVERSOR DE MOEDAS PRO
═══════════════════════════════════════════════════

┌─────────┬──────────────┬─────────────────┬────────────┐
│ Moeda   │ Valor        │ Taxa            │ Atualizado │
├─────────┼──────────────┼─────────────────┼────────────┤
│ BRL     │ R$ 507,45    │ 1 USD = 5,0745  │ 14:30:22   │
│ EUR     │ € 92,15      │ 1 USD = 0,9215  │ 14:30:22   │
│ GBP     │ £ 78,90      │ 1 USD = 0,7890  │ 14:30:22   │
└─────────┴──────────────┴─────────────────┴────────────┘
```

### GUI

# Run usando GUI

python main.py --gui

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit (`git commit -m 'Adiciona nova feature'`)
4. Push (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📫 Autor

<div align="center">

**Hiann Alexander Mendes de Oliveira** *Desenvolvedor Backend & Entusiasta de IA*

<a href="https://www.linkedin.com/in/hiann-alexander" target="_blank">
  <img src="https://img.shields.io/badge/LinkedIn-Conectar-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge">
</a>
<a href="https://github.com/Hiann" target="_blank">
  <img src="https://img.shields.io/badge/GitHub-Ver_Perfil-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Badge">
</a>

</div
