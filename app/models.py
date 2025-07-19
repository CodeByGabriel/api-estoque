from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
from datetime import datetime

class ProdutoModel(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    descricao = Column(String, nullable=True)
    preco = Column(Float)
    quantidadeEstoque = Column(Integer)

class PedidoModel(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String)
    valorTotalPedido = Column(Float)
    dataPedido = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="em_andamento")
