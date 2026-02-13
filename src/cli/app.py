#!/usr/bin/env python3
"""
Interface de linha de comando moderna com Rich.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import box

from src.core import ConversorMoedas, Configuracao
from src.core.models import HistoricoFiltro, ExportacaoConfig
from src.services.export import ExportService
from src.services.charts import ChartService


console = Console()


def get_conversor() -> ConversorMoedas:
    """Obtém instância do conversor."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task("Inicializando conversor...", total=None)
        return ConversorMoedas()


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """💱 Conversor de Moedas Pro - CLI"""
    pass


@cli.command()
@click.argument('valor', type=float)
@click.argument('de_moeda')
@click.argument('para_moeda')
@click.option('--save/--no-save', default=True, help='Salvar no histórico')
def convert(valor: float, de_moeda: str, para_moeda: str, save: bool):
    """Converte valor entre duas moedas."""
    try:
        conversor = get_conversor()
        
        with console.status("[bold blue]Obtendo taxa de câmbio..."):
            resultado = conversor.converter(valor, de_moeda, para_moeda, salvar=save)
        
        # Exibe resultado
        console.print()
        console.print(Panel(
            f"[bold green]{float(resultado.valor_original):,.2f} {resultado.moeda_origem}[/bold green] = "
            f"[bold yellow]{float(resultado.valor_convertido):,.2f} {resultado.moeda_destino}[/bold yellow]",
            title="💰 Resultado da Conversão",
            border_style="green"
        ))
        
        # Tabela com detalhes
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("Taxa", f"1 {resultado.moeda_origem} = {float(resultado.taxa):,.6f} {resultado.moeda_destino}")
        table.add_row("Inverso", f"1 {resultado.moeda_destino} = {float(resultado.taxa_inversa):,.6f} {resultado.moeda_origem}")
        table.add_row("Data", resultado.timestamp.strftime("%d/%m/%Y %H:%M:%S"))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")
        raise click.Abort()


@cli.command()
@click.argument('valor', type=float)
@click.argument('de_moeda')
@click.option('--to', 'para_moedas', help='Moedas de destino separadas por vírgula')
def multi(valor: float, de_moeda: str, para_moedas: str):
    """Converte para múltiplas moedas."""
    try:
        conversor = get_conversor()
        
        moedas = [m.strip().upper() for m in para_moedas.split(',')]
        
        with console.status(f"[bold blue]Convertendo {valor} {de_moeda} para {len(moedas)} moedas..."):
            resultado = conversor.converter_multiplo(valor, de_moeda, moedas)
        
        # Tabela de resultados
        table = Table(
            title=f"💱 Conversão Múltipla: {valor} {de_moeda}",
            box=box.ROUNDED
        )
        table.add_column("Moeda", style="cyan", justify="center")
        table.add_column("Valor Convertido", style="green", justify="right")
        table.add_column("Taxa", style="yellow", justify="right")
        
        for conv in resultado.conversoes:
            table.add_row(
                conv.moeda_destino,
                f"{float(conv.valor_convertido):,.2f}",
                f"{float(conv.taxa):,.6f}"
            )
        
        console.print()
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")
        raise click.Abort()


@cli.command()
@click.option('--popular', is_flag=True, help='Mostrar apenas moedas populares')
@click.option('--search', help='Buscar moeda por termo')
def list(popular: bool, search: Optional[str]):
    """Lista moedas disponíveis."""
    try:
        conversor = get_conversor()
        
        if search:
            moedas = conversor.buscar_moeda(search)
            title = f"🔍 Resultados para '{search}'"
        else:
            moedas = conversor.listar_moedas(apenas_populares=popular)
            title = "⭐ Moedas Populares" if popular else "📋 Todas as Moedas"
        
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Código", style="cyan", justify="center")
        table.add_column("Nome", style="white")
        table.add_column("Símbolo", style="yellow", justify="center")
        
        simbolos = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
            'BRL': 'R$', 'CAD': 'C$', 'AUD': 'A$', 'CHF': 'Fr'
        }
        
        for codigo, nome in sorted(moedas.items()):
            simbolo = simbolos.get(codigo, '-')
            popular_marker = "⭐" if codigo in conversor.MOEDAS_POPULARES else ""
            table.add_row(codigo, f"{nome} {popular_marker}", simbolo)
        
        console.print()
        console.print(table)
        console.print(f"\n[dim]Total: {len(moedas)} moedas[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")


@cli.command()
@click.option('--limit', '-l', default=10, help='Número de registros')
@click.option('--moeda', '-m', help='Filtrar por moeda de origem')
@click.option('--from-date', help='Data inicial (YYYY-MM-DD)')
@click.option('--to-date', help='Data final (YYYY-MM-DD)')
def history(limit: int, moeda: Optional[str], from_date: Optional[str], to_date: Optional[str]):
    """Mostra histórico de conversões."""
    try:
        conversor = get_conversor()
        
        filtro = HistoricoFiltro(limit=limit)
        
        if moeda:
            filtro.moeda_origem = moeda.upper()
        if from_date:
            filtro.data_inicio = datetime.strptime(from_date, "%Y-%m-%d").date()
        if to_date:
            filtro.data_fim = datetime.strptime(to_date, "%Y-%m-%d").date()
        
        conversoes, total = conversor.obter_historico(filtro)
        
        if not conversoes:
            console.print("[yellow]📭 Nenhuma conversão encontrada.[/yellow]")
            return
        
        table = Table(
            title=f"📜 Histórico de Conversões (Total: {total})",
            box=box.ROUNDED
        )
        table.add_column("ID", style="dim", justify="right")
        table.add_column("Data", style="cyan")
        table.add_column("Origem", style="green", justify="right")
        table.add_column("→", style="dim", justify="center")
        table.add_column("Destino", style="yellow", justify="right")
        table.add_column("Taxa", style="blue")
        
        for conv in conversoes:
            table.add_row(
                str(conv.id),
                conv.timestamp.strftime("%d/%m/%Y %H:%M") if conv.timestamp else "-",
                f"{float(conv.valor_original):,.2f} {conv.moeda_origem}",
                "→",
                f"{float(conv.valor_convertido):,.2f} {conv.moeda_destino}",
                f"{float(conv.taxa):,.4f}"
            )
        
        console.print()
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")


@cli.command()
@click.argument('moeda_origem')
@click.argument('moeda_destino')
@click.option('--dias', '-d', default=30, help='Período em dias')
def stats(moeda_origem: str, moeda_destino: str, dias: int):
    """Mostra estatísticas de conversões."""
    try:
        conversor = get_conversor()
        
        with console.status("[bold blue]Calculando estatísticas..."):
            estatisticas = conversor.obter_estatisticas(moeda_origem, moeda_destino, dias)
        
        if not estatisticas:
            console.print(f"[yellow]📭 Nenhuma estatística disponível para {moeda_origem} → {moeda_destino}[/yellow]")
            return
        
        # Painel de estatísticas
        content = f"""
[bold]Período:[/bold] Últimos {dias} dias

[bold cyan]Total de Conversões:[/bold cyan] {estatisticas.total_conversoes}
[bold cyan]Volume Total:[/bold cyan] {float(estatisticas.valor_total_origem):,.2f} {estatisticas.moeda_origem}
                              {float(estatisticas.valor_total_destino):,.2f} {estatisticas.moeda_destino}

[bold green]Taxa Média:[/bold green] {float(estatisticas.taxa_media):,.6f}
[bold yellow]Taxa Mínima:[/bold yellow] {float(estatisticas.taxa_minima):,.6f}
[bold red]Taxa Máxima:[/bold red] {float(estatisticas.taxa_maxima):,.6f}

[bold magenta]Variação:[/bold magenta] {float(estatisticas.variacao_percentual or 0):,.2f}%
        """
        
        console.print()
        console.print(Panel(
            content,
            title=f"📊 Estatísticas: {moeda_origem} → {moeda_destino}",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")


@cli.command()
@click.option('--format', 'formato', type=click.Choice(['excel', 'csv', 'json', 'pdf']), required=True)
@click.option('--output', '-o', required=True, help='Arquivo de saída')
@click.option('--limit', '-l', default=1000, help='Limite de registros')
def export(formato: str, output: str, limit: int):
    """Exporta histórico para arquivo."""
    try:
        conversor = get_conversor()
        
        with console.status("[bold blue]Buscando dados..."):
            filtro = HistoricoFiltro(limit=limit)
            conversoes, total = conversor.obter_historico(filtro)
        
        if not conversoes:
            console.print("[yellow]📭 Nenhum dado para exportar.[/yellow]")
            return
        
        config = ExportacaoConfig(formato=formato, arquivo=output)
        service = ExportService()
        
        with console.status(f"[bold blue]Exportando para {formato.upper()}..."):
            arquivo = service.exportar(conversoes, config)
        
        console.print(f"[bold green]✅ Exportado com sucesso:[/bold green] {arquivo}")
        console.print(f"[dim]Total de registros: {len(conversoes)}[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")


@cli.command()
@click.argument('moeda_origem')
@click.argument('moeda_destino')
@click.option('--dias', '-d', default=30, help='Período em dias')
@click.option('--output', '-o', help='Arquivo de saída')
def chart(moeda_origem: str, moeda_destino: str, dias: int, output: Optional[str]):
    """Gera gráfico de histórico."""
    try:
        conversor = get_conversor()
        
        with console.status("[bold blue]Buscando dados..."):
            filtro = HistoricoFiltro(
                moeda_origem=moeda_origem,
                moeda_destino=moeda_destino,
                limit=1000
            )
            conversoes, _ = conversor.obter_historico(filtro)
        
        if not conversoes:
            console.print("[yellow]📭 Dados insuficientes para gerar gráfico.[/yellow]")
            return
        
        service = ChartService()
        
        arquivo = Path(output) if output else None
        
        with console.status("[bold blue]Gerando gráfico..."):
            arquivo = service.criar_grafico_historico(
                conversoes, moeda_origem, moeda_destino, arquivo
            )
        
        console.print(f"[bold green]✅ Gráfico gerado:[/bold green] {arquivo}")
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")


@cli.command()
def status():
    """Mostra status do sistema."""
    try:
        conversor = get_conversor()
        status_info = conversor.get_status()
        
        console.print()
        console.print(Panel("[bold]Status do Sistema[/bold]", border_style="blue"))
        
        # APIs
        api_table = Table(title="🌐 APIs", box=box.SIMPLE)
        api_table.add_column("API", style="cyan")
        api_table.add_column("Status", style="green")
        
        for api, status in status_info['apis'].items():
            color = "green" if status == "online" else "red"
            api_table.add_row(api, f"[{color}]{status}[/{color}]")
        
        console.print(api_table)
        
        # Cache
        cache = status_info['cache']
        console.print(f"\n[bold]💾 Cache:[/bold]")
        console.print(f"  Itens em memória: {cache['memory_items']}")
        console.print(f"  Itens em disco: {cache['disk_items']}")
        console.print(f"  TTL: {cache['ttl_seconds']}s")
        
        # Database
        console.print(f"\n[bold]🗄️  Banco de Dados:[/bold] {status_info['database']}")
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")


@cli.command()
def interactive():
    """Modo interativo."""
    conversor = get_conversor()
    
    console.print(Panel.fit(
        "[bold green]💱 Conversor de Moedas Pro - Modo Interativo[/bold green]\n"
        "[dim]Digite 'sair' para encerrar[/dim]",
        border_style="green"
    ))
    
    while True:
        console.print()
        
        valor = Prompt.ask("[cyan]Valor[/cyan] (ou 'sair')")
        if valor.lower() in ('sair', 'exit', 'quit'):
            break
        
        try:
            valor = float(valor)
        except ValueError:
            console.print("[red]Valor inválido![/red]")
            continue
        
        de_moeda = Prompt.ask("[cyan]De moeda[/cyan]", default="USD").upper()
        para_moeda = Prompt.ask("[cyan]Para moeda[/cyan]", default="BRL").upper()
        
        try:
            with console.status("[bold blue]Convertendo..."):
                resultado = conversor.converter(valor, de_moeda, para_moeda)
            
            console.print(f"\n[bold green]✅ {float(resultado.valor_original):,.2f} {resultado.moeda_origem} = "
                         f"{float(resultado.valor_convertido):,.2f} {resultado.moeda_destino}[/bold green]")
            console.print(f"[dim]Taxa: 1 {resultado.moeda_origem} = {float(resultado.taxa):,.6f} {resultado.moeda_destino}[/dim]")
            
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")
    
    console.print("\n[green]👋 Até logo![/green]")


if __name__ == '__main__':
    cli()
