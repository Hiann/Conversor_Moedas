# 📚 Exemplos de Uso

## CLI (Linha de Comando)

### Modo Interativo
```bash
python -m src.cli
# ou
python main.py
```

### Conversão Simples
```bash
python -m src.cli convert 100 USD BRL
```

Saída:
```
💰 Resultado da Conversão
────────────────────────────────────────
100.00 USD = 507.45 BRL

Taxa: 1 USD = 5.0745 BRL
Inverso: 1 BRL = 0.1971 USD
Data: 15/01/2024 14:30:22
```

### Conversão Múltipla
```bash
python -m src.cli multi 100 USD --to BRL,EUR,GBP
```

Saída:
```
💱 Conversão Múltipla: 100 USD

┌────────┬──────────────────┬────────────┐
│ Moeda  │ Valor Convertido │ Taxa       │
├────────┼──────────────────┼────────────┤
│ BRL    │ 507.45           │ 5.0745     │
│ EUR    │ 92.15            │ 0.9215     │
│ GBP    │ 78.90            │ 0.7890     │
└────────┴──────────────────┴────────────┘
```

### Listar Moedas
```bash
# Todas as moedas
python -m src.cli list

# Apenas populares
python -m src.cli list --popular

# Buscar
python -m src.cli list --search "dolar"
```

### Histórico
```bash
# Últimas 10 conversões
python -m src.cli history

# Com filtros
python -m src.cli history --limit 20 --moeda USD --from-date 2024-01-01
```

### Estatísticas
```bash
python -m src.cli stats USD BRL --dias 30
```

### Exportar
```bash
# Excel
python -m src.cli export --format excel --output historico.xlsx

# PDF
python -m src.cli export --format pdf --output historico.pdf

# CSV
python -m src.cli export --format csv --output historico.csv

# JSON
python -m src.cli export --format json --output historico.json
```

### Gráficos
```bash
python -m src.cli chart USD BRL --dias 30 --output grafico.png
```

### Status do Sistema
```bash
python -m src.cli status
```

---

## Interface Gráfica (GUI)

```bash
python -m src.gui
# ou
python main.py --gui
```

---

## Como Biblioteca Python

```python
from src.core import ConversorMoedas
from src.core.models import HistoricoFiltro
from decimal import Decimal

# Inicializa
conversor = ConversorMoedas()

# Conversão simples
resultado = conversor.converter(100, "USD", "BRL")
print(f"{resultado.valor_original} {resultado.moeda_origem} = "
      f"{resultado.valor_convertido} {resultado.moeda_destino}")

# Conversão múltipla
resultados = conversor.converter_multiplo(
    100, "USD", ["BRL", "EUR", "GBP", "JPY"]
)
for conv in resultados.conversoes:
    print(f"{conv.moeda_destino}: {conv.valor_convertido}")

# Listar moedas
moedas = conversor.listar_moedas(apenas_populares=True)
for codigo, nome in moedas.items():
    print(f"{codigo}: {nome}")

# Buscar moeda
resultados = conversor.buscar_moeda("euro")
print(resultados)  # {'EUR': 'Euro'}

# Histórico com filtros
filtro = HistoricoFiltro(
    moeda_origem="USD",
    moeda_destino="BRL",
    limit=10
)
conversoes, total = conversor.obter_historico(filtro)
print(f"Total: {total}")
for conv in conversoes:
    print(conv.formatar("simples"))

# Estatísticas
stats = conversor.obter_estatisticas("USD", "BRL", dias=30)
print(f"Taxa média: {stats.taxa_media}")
print(f"Taxa mínima: {stats.taxa_minima}")
print(f"Taxa máxima: {stats.taxa_maxima}")

# Comparar moedas
comparacao = conversor.comparar_moedas(
    ["BRL", "EUR", "GBP", "JPY"],
    valor_base=1,
    moeda_referencia="USD"
)
for moeda, valor in comparacao.items():
    print(f"1 USD = {valor} {moeda}")

# Status do sistema
status = conversor.get_status()
print(status)
```

---

## Exportação Programática

```python
from src.core import ConversorMoedas
from src.core.models import HistoricoFiltro, ExportacaoConfig
from src.services.export import ExportService

conversor = ConversorMoedas()
export_service = ExportService()

# Busca dados
filtro = HistoricoFiltro(limit=100)
conversoes, _ = conversor.obter_historico(filtro)

# Exporta
config = ExportacaoConfig(
    formato="excel",
    arquivo="meu_historico.xlsx"
)
arquivo = export_service.exportar(conversoes, config)
print(f"Exportado: {arquivo}")
```

---

## Gráficos Programáticos

```python
from src.core import ConversorMoedas
from src.core.models import HistoricoFiltro
from src.services.charts import ChartService

conversor = ConversorMoedas()
chart_service = ChartService()

# Busca dados
filtro = HistoricoFiltro(
    moeda_origem="USD",
    moeda_destino="BRL",
    limit=100
)
conversoes, _ = conversor.obter_historico(filtro)

# Gráfico de histórico
arquivo = chart_service.criar_grafico_historico(
    conversoes, "USD", "BRL", "meu_grafico.png"
)

# Gráfico comparativo
dados = {"BRL": 5.07, "EUR": 0.92, "GBP": 0.79}
arquivo = chart_service.criar_grafico_comparativo(
    dados, "USD", "comparativo.png"
)

# Dashboard completo
stats = conversor.obter_estatisticas("USD", "BRL")
arquivo = chart_service.criar_dashboard(
    stats, conversoes, "dashboard.png"
)
```

---

## Docker

```bash
# Build
make docker-build

# Run CLI
make docker-run

# Run GUI (Linux)
make docker-gui

# Docker Compose
cd docker
docker-compose up conversor
```

---

## Makefile

```bash
# Instalar dependências
make install

# Executar testes
make test

# Linting
make lint

# Formatar código
make format

# Limpar
make clean

# Iniciar GUI
make gui

# Iniciar CLI
make cli
```
