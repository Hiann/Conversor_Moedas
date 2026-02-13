"""Serviço de gráficos e visualizações."""

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Dict

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure

from src.core.models import Conversao, Estatisticas


class ChartService:
    """Serviço para criar gráficos."""
    
    def __init__(self):
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def criar_grafico_historico(
        self,
        conversoes: List[Conversao],
        moeda_origem: str,
        moeda_destino: str,
        arquivo: Optional[Path] = None
    ) -> Path:
        """
        Cria gráfico de histórico de taxas.
        
        Args:
            conversoes: Lista de conversões
            moeda_origem: Moeda de origem
            moeda_destino: Moeda de destino
            arquivo: Caminho do arquivo (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        if not conversoes:
            raise ValueError("Nenhuma conversão fornecida")
        
        if arquivo is None:
            arquivo = Path(f"charts/historico_{moeda_origem}_{moeda_destino}.png")
        
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepara dados
        datas = [c.timestamp for c in conversoes if c.timestamp]
        taxas = [float(c.taxa) for c in conversoes]
        
        # Cria figura
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(datas, taxas, marker='o', linewidth=2, markersize=6, color='#366092')
        ax.fill_between(datas, taxas, alpha=0.3, color='#366092')
        
        # Configurações
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel(f'Taxa ({moeda_origem} → {moeda_destino})', fontsize=12)
        ax.set_title(f'Histórico de Taxas: {moeda_origem} → {moeda_destino}', fontsize=14, fontweight='bold')
        
        # Formatação do eixo X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(datas) // 10)))
        plt.xticks(rotation=45)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Estatísticas
        if taxas:
            media = sum(taxas) / len(taxas)
            ax.axhline(y=media, color='r', linestyle='--', alpha=0.7, label=f'Média: {media:.4f}')
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        plt.close()
        
        return arquivo
    
    def criar_grafico_comparativo(
        self,
        dados: Dict[str, float],
        moeda_base: str,
        arquivo: Optional[Path] = None
    ) -> Path:
        """
        Cria gráfico comparativo de moedas.
        
        Args:
            dados: Dicionário {moeda: valor}
            moeda_base: Moeda base da comparação
            arquivo: Caminho do arquivo (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        if not dados:
            raise ValueError("Nenhum dado fornecido")
        
        if arquivo is None:
            arquivo = Path(f"charts/comparativo_{moeda_base}.png")
        
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepara dados
        moedas = list(dados.keys())
        valores = [v if v is not None else 0 for v in dados.values()]
        
        # Cores
        cores = plt.cm.Set3(range(len(moedas)))
        
        # Cria figura
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(moedas, valores, color=cores, edgecolor='black', linewidth=1.2)
        
        # Adiciona valores nas barras
        for bar, valor in zip(bars, valores):
            height = bar.get_height()
            if valor > 0:
                ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height,
                    f'{valor:,.2f}',
                    ha='center',
                    va='bottom',
                    fontsize=10,
                    fontweight='bold'
                )
        
        # Configurações
        ax.set_xlabel('Moeda', fontsize=12)
        ax.set_ylabel(f'Valor equivalente em {moeda_base}', fontsize=12)
        ax.set_title(f'Comparação de Moedas (Base: {moeda_base})', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        plt.close()
        
        return arquivo
    
    def criar_grafico_pizza(
        self,
        dados: Dict[str, float],
        titulo: str = "Distribuição",
        arquivo: Optional[Path] = None
    ) -> Path:
        """Cria gráfico de pizza."""
        if not dados:
            raise ValueError("Nenhum dado fornecido")
        
        if arquivo is None:
            arquivo = Path("charts/distribuicao.png")
        
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepara dados
        labels = list(dados.keys())
        valores = [v if v is not None else 0 for v in dados.values()]
        
        # Cria figura
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Cores
        cores = plt.cm.Set3(range(len(labels)))
        
        # Gráfico de pizza
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            autopct='%1.1f%%',
            colors=cores,
            startangle=90,
            textprops={'fontsize': 11}
        )
        
        # Destaca os autotextos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(titulo, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        plt.close()
        
        return arquivo
    
    def criar_dashboard(
        self,
        estatisticas: Estatisticas,
        conversoes: List[Conversao],
        arquivo: Optional[Path] = None
    ) -> Path:
        """Cria dashboard completo."""
        if arquivo is None:
            arquivo = Path(f"charts/dashboard_{estatisticas.moeda_origem}_{estatisticas.moeda_destino}.png")
        
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        # Cria figura com múltiplos subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Título
        fig.suptitle(
            f'Dashboard: {estatisticas.moeda_origem} → {estatisticas.moeda_destino}',
            fontsize=16,
            fontweight='bold'
        )
        
        # 1. Gráfico de linha - Histórico
        ax1 = fig.add_subplot(gs[0, :2])
        if conversoes:
            datas = [c.timestamp for c in conversoes if c.timestamp]
            taxas = [float(c.taxa) for c in conversoes]
            ax1.plot(datas, taxas, marker='o', color='#366092')
            ax1.set_title('Histórico de Taxas')
            ax1.set_xlabel('Data')
            ax1.set_ylabel('Taxa')
            ax1.grid(True, alpha=0.3)
        
        # 2. Estatísticas em texto
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        stats_text = f"""
        ESTATÍSTICAS
        
        Total de conversões: {estatisticas.total_conversoes}
        
        Taxa média: {float(estatisticas.taxa_media):.4f}
        Taxa mínima: {float(estatisticas.taxa_minima):.4f}
        Taxa máxima: {float(estatisticas.taxa_maxima):.4f}
        
        Variação: {float(estatisticas.variacao_percentual or 0):.2f}%
        """
        ax2.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 3. Gráfico de barras - Volume
        ax3 = fig.add_subplot(gs[1, :])
        if conversoes:
            # Agrupa por data
            from collections import defaultdict
            volumes = defaultdict(float)
            for c in conversoes:
                if c.timestamp:
                    data_str = c.timestamp.strftime('%d/%m')
                    volumes[data_str] += float(c.valor_original)
            
            datas = list(volumes.keys())
            vals = list(volumes.values())
            ax3.bar(datas, vals, color='#5B9BD5')
            ax3.set_title('Volume de Conversões por Data')
            ax3.set_xlabel('Data')
            ax3.set_ylabel(f'Volume ({estatisticas.moeda_origem})')
            ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Evolução acumulada
        ax4 = fig.add_subplot(gs[2, :])
        if conversoes:
            datas = sorted([c.timestamp for c in conversoes if c.timestamp])
            acumulado = []
            total = 0
            for c in sorted(conversoes, key=lambda x: x.timestamp or datetime.min):
                total += float(c.valor_original)
                acumulado.append(total)
            
            ax4.fill_between(datas[:len(acumulado)], acumulado, alpha=0.5, color='#70AD47')
            ax4.plot(datas[:len(acumulado)], acumulado, color='#70AD47', linewidth=2)
            ax4.set_title('Volume Acumulado')
            ax4.set_xlabel('Data')
            ax4.set_ylabel(f'Volume Acumulado ({estatisticas.moeda_origem})')
            ax4.grid(True, alpha=0.3)
        
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        plt.close()
        
        return arquivo
