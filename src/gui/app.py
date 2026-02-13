#!/usr/bin/env python3
"""
Interface gráfica moderna com Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from src.core import ConversorMoedas
from src.core.models import HistoricoFiltro, ExportacaoConfig
from src.services.export import ExportService
from src.services.charts import ChartService


class ModernStyle:
    """Estilos modernos para a GUI."""
    
    BG_COLOR = "#f0f0f0"
    PRIMARY_COLOR = "#366092"
    SECONDARY_COLOR = "#5B9BD5"
    SUCCESS_COLOR = "#70AD47"
    WARNING_COLOR = "#FFC000"
    ERROR_COLOR = "#C5504B"
    TEXT_COLOR = "#333333"
    
    FONT_TITLE = ("Segoe UI", 16, "bold")
    FONT_HEADER = ("Segoe UI", 12, "bold")
    FONT_NORMAL = ("Segoe UI", 10)
    FONT_SMALL = ("Segoe UI", 9)


class ConversorApp:
    """Aplicação GUI do conversor de moedas."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("💱 Conversor de Moedas Pro")
        self.root.geometry("900x700")
        self.root.configure(bg=ModernStyle.BG_COLOR)
        self.root.minsize(800, 600)
        
        # Inicializa conversor
        self.conversor = ConversorMoedas()
        self.export_service = ExportService()
        self.chart_service = ChartService()
        
        # Configura estilos
        self._setup_styles()
        
        # Cria interface
        self._create_widgets()
        
        # Carrega dados iniciais
        self._carregar_moedas()
    
    def _setup_styles(self):
        """Configura estilos do ttk."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurações gerais
        style.configure('.', font=ModernStyle.FONT_NORMAL)
        
        # Botões
        style.configure(
            'Primary.TButton',
            font=ModernStyle.FONT_HEADER,
            background=ModernStyle.PRIMARY_COLOR,
            foreground='white',
            padding=10
        )
        style.map('Primary.TButton',
            background=[('active', ModernStyle.SECONDARY_COLOR)]
        )
        
        # Frames
        style.configure(
            'Card.TFrame',
            background='white',
            relief='solid',
            borderwidth=1
        )
        
        # Labels
        style.configure(
            'Title.TLabel',
            font=ModernStyle.FONT_TITLE,
            background=ModernStyle.BG_COLOR,
            foreground=ModernStyle.PRIMARY_COLOR
        )
        
        style.configure(
            'Header.TLabel',
            font=ModernStyle.FONT_HEADER,
            background=ModernStyle.BG_COLOR
        )
    
    def _create_widgets(self):
        """Cria widgets da interface."""
        # Container principal
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_container,
            text="💱 Conversor de Moedas Pro",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Abas
        self.tab_converter = self._create_converter_tab()
        self.tab_history = self._create_history_tab()
        self.tab_stats = self._create_stats_tab()
        
        self.notebook.add(self.tab_converter, text="💰 Converter")
        self.notebook.add(self.tab_history, text="📜 Histórico")
        self.notebook.add(self.tab_stats, text="📊 Estatísticas")
        
        # Status bar
        self.status_bar = ttk.Label(
            main_container,
            text="Pronto",
            font=ModernStyle.FONT_SMALL,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def _create_converter_tab(self) -> ttk.Frame:
        """Cria aba de conversão."""
        tab = ttk.Frame(self.notebook, padding="20")
        
        # Frame de entrada
        input_frame = ttk.LabelFrame(tab, text="Conversão", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Valor
        ttk.Label(input_frame, text="Valor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_valor = ttk.Entry(input_frame, width=20, font=ModernStyle.FONT_NORMAL)
        self.entry_valor.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.entry_valor.insert(0, "100")
        
        # De moeda
        ttk.Label(input_frame, text="De:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_de = ttk.Combobox(input_frame, width=15, state="readonly")
        self.combo_de.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Para moeda
        ttk.Label(input_frame, text="Para:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.combo_para = ttk.Combobox(input_frame, width=15, state="readonly")
        self.combo_para.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Botão converter
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        btn_convert = tk.Button(
            btn_frame,
            text="🔄 Converter",
            font=ModernStyle.FONT_HEADER,
            bg=ModernStyle.PRIMARY_COLOR,
            fg='white',
            activebackground=ModernStyle.SECONDARY_COLOR,
            activeforeground='white',
            cursor='hand2',
            padx=20,
            pady=8,
            command=self._on_convert
        )
        btn_convert.pack()
        
        # Frame de resultado
        result_frame = ttk.LabelFrame(tab, text="Resultado", padding="15")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.lbl_resultado = tk.Label(
            result_frame,
            text="Aguardando conversão...",
            font=("Segoe UI", 24, "bold"),
            fg=ModernStyle.PRIMARY_COLOR,
            bg='white'
        )
        self.lbl_resultado.pack(expand=True)
        
        # Detalhes
        self.lbl_detalhes = tk.Label(
            result_frame,
            text="",
            font=ModernStyle.FONT_NORMAL,
            fg=ModernStyle.TEXT_COLOR,
            bg='white'
        )
        self.lbl_detalhes.pack(pady=10)
        
        # Botões de ação
        action_frame = ttk.Frame(result_frame)
        action_frame.pack(pady=10)
        
        tk.Button(
            action_frame,
            text="📊 Gráfico",
            command=self._on_chart
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="💾 Salvar",
            command=self._on_save_result
        ).pack(side=tk.LEFT, padx=5)
        
        return tab
    
    def _create_history_tab(self) -> ttk.Frame:
        """Cria aba de histórico."""
        tab = ttk.Frame(self.notebook, padding="20")
        
        # Filtros
        filter_frame = ttk.LabelFrame(tab, text="Filtros", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Moeda:").pack(side=tk.LEFT, padx=5)
        self.combo_filter_moeda = ttk.Combobox(filter_frame, width=10, state="readonly")
        self.combo_filter_moeda.pack(side=tk.LEFT, padx=5)
        self.combo_filter_moeda.set("Todas")
        
        ttk.Button(
            filter_frame,
            text="🔍 Filtrar",
            command=self._on_filter_history
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            filter_frame,
            text="📤 Exportar",
            command=self._on_export_history
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ('id', 'data', 'origem', 'valor_orig', 'destino', 'valor_dest', 'taxa')
        self.tree_history = ttk.Treeview(
            tab,
            columns=columns,
            show='headings',
            height=15
        )
        
        self.tree_history.heading('id', text='ID')
        self.tree_history.heading('data', text='Data')
        self.tree_history.heading('origem', text='Origem')
        self.tree_history.heading('valor_orig', text='Valor Orig.')
        self.tree_history.heading('destino', text='Destino')
        self.tree_history.heading('valor_dest', text='Valor Dest.')
        self.tree_history.heading('taxa', text='Taxa')
        
        self.tree_history.column('id', width=50)
        self.tree_history.column('data', width=120)
        self.tree_history.column('origem', width=80)
        self.tree_history.column('valor_orig', width=100)
        self.tree_history.column('destino', width=80)
        self.tree_history.column('valor_dest', width=100)
        self.tree_history.column('taxa', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=scrollbar.set)
        
        self.tree_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Carrega histórico
        self._carregar_historico()
        
        return tab
    
    def _create_stats_tab(self) -> ttk.Frame:
        """Cria aba de estatísticas."""
        tab = ttk.Frame(self.notebook, padding="20")
        
        # Seleção de moedas
        select_frame = ttk.Frame(tab)
        select_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(select_frame, text="De:").pack(side=tk.LEFT, padx=5)
        self.combo_stats_de = ttk.Combobox(select_frame, width=10, state="readonly")
        self.combo_stats_de.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(select_frame, text="Para:").pack(side=tk.LEFT, padx=5)
        self.combo_stats_para = ttk.Combobox(select_frame, width=10, state="readonly")
        self.combo_stats_para.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            select_frame,
            text="📊 Calcular",
            command=self._on_calc_stats
        ).pack(side=tk.LEFT, padx=10)
        
        # Frame de estatísticas
        self.stats_frame = ttk.LabelFrame(tab, text="Estatísticas", padding="20")
        self.stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.lbl_stats = tk.Label(
            self.stats_frame,
            text="Selecione as moedas e clique em Calcular",
            font=ModernStyle.FONT_NORMAL,
            wraplength=600
        )
        self.lbl_stats.pack(expand=True)
        
        return tab
    
    def _carregar_moedas(self):
        """Carrega lista de moedas nos comboboxes."""
        moedas = list(self.conversor.MOEDAS_POPULARES.keys())
        
        # Ordena
        moedas.sort()
        
        # Atualiza comboboxes
        self.combo_de['values'] = moedas
        self.combo_para['values'] = moedas
        self.combo_filter_moeda['values'] = ['Todas'] + moedas
        self.combo_stats_de['values'] = moedas
        self.combo_stats_para['values'] = moedas
        
        # Seleções padrão
        self.combo_de.set('USD')
        self.combo_para.set('BRL')
        self.combo_stats_de.set('USD')
        self.combo_stats_para.set('BRL')
    
    def _carregar_historico(self):
        """Carrega histórico na treeview."""
        # Limpa
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)
        
        # Busca dados
        filtro = HistoricoFiltro(limit=100)
        conversoes, _ = self.conversor.obter_historico(filtro)
        
        # Preenche
        for conv in conversoes:
            self.tree_history.insert('', tk.END, values=(
                conv.id,
                conv.timestamp.strftime("%d/%m/%Y %H:%M") if conv.timestamp else "",
                conv.moeda_origem,
                f"{float(conv.valor_original):,.2f}",
                conv.moeda_destino,
                f"{float(conv.valor_convertido):,.2f}",
                f"{float(conv.taxa):,.6f}"
            ))
    
    def _on_convert(self):
        """Handler do botão converter."""
        try:
            valor = float(self.entry_valor.get())
            de_moeda = self.combo_de.get()
            para_moeda = self.combo_para.get()
            
            if not de_moeda or not para_moeda:
                messagebox.showwarning("Aviso", "Selecione as moedas")
                return
            
            self.status_bar.config(text="Convertendo...")
            self.root.update()
            
            resultado = self.conversor.converter(valor, de_moeda, para_moeda)
            
            # Atualiza resultado
            self.lbl_resultado.config(
                text=f"{float(resultado.valor_convertido):,.2f} {resultado.moeda_destino}"
            )
            
            detalhes = (
                f"{float(resultado.valor_original):,.2f} {resultado.moeda_origem} = "
                f"{float(resultado.valor_convertido):,.2f} {resultado.moeda_destino}\n"
                f"Taxa: 1 {resultado.moeda_origem} = {float(resultado.taxa):,.6f} {resultado.moeda_destino}\n"
                f"Data: {resultado.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            self.lbl_detalhes.config(text=detalhes)
            
            self.status_bar.config(text="Conversão realizada com sucesso")
            
            # Atualiza histórico
            self._carregar_historico()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}")
            self.status_bar.config(text="Erro na conversão")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self.status_bar.config(text="Erro na conversão")
    
    def _on_chart(self):
        """Handler do botão gráfico."""
        try:
            de_moeda = self.combo_de.get()
            para_moeda = self.combo_para.get()
            
            filtro = HistoricoFiltro(
                moeda_origem=de_moeda,
                moeda_destino=para_moeda,
                limit=100
            )
            conversoes, _ = self.conversor.obter_historico(filtro)
            
            if len(conversoes) < 2:
                messagebox.showwarning("Aviso", "Dados insuficientes para gerar gráfico")
                return
            
            arquivo = self.chart_service.criar_grafico_historico(
                conversoes, de_moeda, para_moeda
            )
            
            messagebox.showinfo("Sucesso", f"Gráfico salvo em:\n{arquivo}")
            
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def _on_save_result(self):
        """Handler do botão salvar."""
        messagebox.showinfo("Info", "Resultado salvo no histórico automaticamente!")
    
    def _on_filter_history(self):
        """Handler do filtro de histórico."""
        self._carregar_historico()
    
    def _on_export_history(self):
        """Handler da exportação."""
        try:
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel", "*.xlsx"),
                    ("CSV", "*.csv"),
                    ("JSON", "*.json"),
                    ("PDF", "*.pdf")
                ]
            )
            
            if not arquivo:
                return
            
            # Determina formato
            ext = Path(arquivo).suffix.lower()
            formatos = {'.xlsx': 'excel', '.csv': 'csv', '.json': 'json', '.pdf': 'pdf'}
            formato = formatos.get(ext, 'excel')
            
            # Busca dados
            filtro = HistoricoFiltro(limit=1000)
            conversoes, _ = self.conversor.obter_historico(filtro)
            
            # Exporta
            config = ExportacaoConfig(formato=formato, arquivo=arquivo)
            self.export_service.exportar(conversoes, config)
            
            messagebox.showinfo("Sucesso", f"Exportado para:\n{arquivo}")
            
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def _on_calc_stats(self):
        """Handler do cálculo de estatísticas."""
        try:
            de_moeda = self.combo_stats_de.get()
            para_moeda = self.combo_stats_para.get()
            
            estatisticas = self.conversor.obter_estatisticas(de_moeda, para_moeda, dias=30)
            
            if not estatisticas:
                self.lbl_stats.config(text="Nenhuma estatística disponível para este par de moedas")
                return
            
            texto = f"""
📊 ESTATÍSTICAS: {de_moeda} → {para_moeda}

Total de Conversões: {estatisticas.total_conversoes}
Volume Total: {float(estatisticas.valor_total_origem):,.2f} {estatisticas.moeda_origem}

Taxa Média: {float(estatisticas.taxa_media):,.6f}
Taxa Mínima: {float(estatisticas.taxa_minima):,.6f}
Taxa Máxima: {float(estatisticas.taxa_maxima):,.6f}

Variação: {float(estatisticas.variacao_percentual or 0):,.2f}%
            """
            
            self.lbl_stats.config(text=texto)
            
        except Exception as e:
            messagebox.showerror("Erro", str(e))


def main():
    """Função principal da GUI."""
    root = tk.Tk()
    app = ConversorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
