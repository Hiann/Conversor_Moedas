"""Repositório de dados para conversões."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from .models import ConversaoDB, ConversaoMultiplaDB
from src.core.models import Conversao, ConversaoMultipla, HistoricoFiltro, Estatisticas


class ConversaoRepository:
    """Repositório para operações de conversão."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def salvar(self, conversao: Conversao) -> Conversao:
        """Salva uma conversão."""
        db_conversao = ConversaoDB(
            valor_original=conversao.valor_original,
            valor_convertido=conversao.valor_convertido,
            moeda_origem=conversao.moeda_origem,
            moeda_destino=conversao.moeda_destino,
            taxa=conversao.taxa,
            taxa_inversa=conversao.taxa_inversa,
            timestamp=conversao.timestamp,
            notas=conversao.notas
        )
        
        self.session.add(db_conversao)
        self.session.flush()
        
        conversao.id = db_conversao.id
        return conversao
    
    def salvar_multipla(self, multipla: ConversaoMultipla) -> ConversaoMultipla:
        """Salva uma conversão múltipla."""
        db_multipla = ConversaoMultiplaDB(
            valor_original=multipla.valor_original,
            moeda_origem=multipla.moeda_origem,
            timestamp=multipla.timestamp
        )
        
        self.session.add(db_multipla)
        self.session.flush()
        
        multipla.id = db_multipla.id
        return multipla
    
    def listar(self, filtro: HistoricoFiltro) -> Tuple[List[Conversao], int]:
        """Lista conversões com filtro."""
        query = self.session.query(ConversaoDB)
        
        # Aplica filtros
        if filtro.data_inicio:
            query = query.filter(ConversaoDB.timestamp >= datetime.combine(filtro.data_inicio, datetime.min.time()))
        
        if filtro.data_fim:
            query = query.filter(ConversaoDB.timestamp <= datetime.combine(filtro.data_fim, datetime.max.time()))
        
        if filtro.moeda_origem:
            query = query.filter(ConversaoDB.moeda_origem == filtro.moeda_origem.upper())
        
        if filtro.moeda_destino:
            query = query.filter(ConversaoDB.moeda_destino == filtro.moeda_destino.upper())
        
        if filtro.valor_minimo is not None:
            query = query.filter(ConversaoDB.valor_original >= filtro.valor_minimo)
        
        if filtro.valor_maximo is not None:
            query = query.filter(ConversaoDB.valor_original <= filtro.valor_maximo)
        
        # Conta total
        total = query.count()
        
        # Ordena e pagina
        query = query.order_by(ConversaoDB.timestamp.desc())
        
        if filtro.offset:
            query = query.offset(filtro.offset)
        
        if filtro.limit:
            query = query.limit(filtro.limit)
        
        # Converte para modelo
        conversoes = []
        for db_conv in query.all():
            conv = Conversao(
                id=db_conv.id,
                valor_original=Decimal(str(db_conv.valor_original)),
                valor_convertido=Decimal(str(db_conv.valor_convertido)),
                moeda_origem=db_conv.moeda_origem,
                moeda_destino=db_conv.moeda_destino,
                taxa=Decimal(str(db_conv.taxa)),
                taxa_inversa=Decimal(str(db_conv.taxa_inversa)),
                timestamp=db_conv.timestamp,
                notas=db_conv.notas
            )
            conversoes.append(conv)
        
        return conversoes, total
    
    def obter_por_id(self, id: int) -> Optional[Conversao]:
        """Obtém conversão por ID."""
        db_conv = self.session.query(ConversaoDB).filter(ConversaoDB.id == id).first()
        
        if not db_conv:
            return None
        
        return Conversao(
            id=db_conv.id,
            valor_original=Decimal(str(db_conv.valor_original)),
            valor_convertido=Decimal(str(db_conv.valor_convertido)),
            moeda_origem=db_conv.moeda_origem,
            moeda_destino=db_conv.moeda_destino,
            taxa=Decimal(str(db_conv.taxa)),
            taxa_inversa=Decimal(str(db_conv.taxa_inversa)),
            timestamp=db_conv.timestamp,
            notas=db_conv.notas
        )
    
    def obter_estatisticas(
        self, 
        moeda_origem: str, 
        moeda_destino: str,
        dias: int = 30
    ) -> Optional[Estatisticas]:
        """Obtém estatísticas de conversões."""
        from sqlalchemy import func
        from datetime import timedelta
        
        data_corte = datetime.now() - timedelta(days=dias)
        
        query = self.session.query(
            func.count(ConversaoDB.id).label('total'),
            func.sum(ConversaoDB.valor_original).label('total_origem'),
            func.sum(ConversaoDB.valor_convertido).label('total_destino'),
            func.avg(ConversaoDB.taxa).label('taxa_media'),
            func.min(ConversaoDB.taxa).label('taxa_min'),
            func.max(ConversaoDB.taxa).label('taxa_max'),
            func.min(ConversaoDB.timestamp).label('primeira'),
            func.max(ConversaoDB.timestamp).label('ultima')
        ).filter(
            and_(
                ConversaoDB.moeda_origem == moeda_origem.upper(),
                ConversaoDB.moeda_destino == moeda_destino.upper(),
                ConversaoDB.timestamp >= data_corte
            )
        )
        
        resultado = query.first()
        
        if not resultado or resultado.total == 0:
            return None
        
        # Calcula variação percentual
        variacao = None
        if resultado.taxa_min and resultado.taxa_max and resultado.taxa_min > 0:
            variacao = Decimal(str((resultado.taxa_max - resultado.taxa_min) / resultado.taxa_min * 100))
        
        return Estatisticas(
            moeda_origem=moeda_origem.upper(),
            moeda_destino=moeda_destino.upper(),
            total_conversoes=resultado.total,
            valor_total_origem=Decimal(str(resultado.total_origem or 0)),
            valor_total_destino=Decimal(str(resultado.total_destino or 0)),
            taxa_media=Decimal(str(resultado.taxa_media or 0)),
            taxa_minima=Decimal(str(resultado.taxa_min or 0)),
            taxa_maxima=Decimal(str(resultado.taxa_max or 0)),
            primeira_conversao=resultado.primeira,
            ultima_conversao=resultado.ultima,
            variacao_percentual=variacao
        )
    
    def excluir(self, id: int) -> bool:
        """Exclui uma conversão."""
        db_conv = self.session.query(ConversaoDB).filter(ConversaoDB.id == id).first()
        
        if db_conv:
            self.session.delete(db_conv)
            return True
        return False
    
    def limpar_historico(self, confirmar: bool = False) -> int:
        """Limpa todo o histórico."""
        if not confirmar:
            return 0
        
        count = self.session.query(ConversaoDB).delete()
        return count
