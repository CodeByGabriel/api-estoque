from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ======== PRODUTOS ========
class ProdutoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    quantidadeEstoque: int

class ProdutoCreate(ProdutoBase):
    pass

class Produto(ProdutoBase):
    id: int

    class Config:
        orm_mode = True


# ======== ITENS DO PEDIDO ========
class ItemPedido(BaseModel):
    produtoId: int
    nomeProduto: str
    quantidade: int
    precoUnitario: float
    valorTotalItem: float

    class Config:
        orm_mode = True


# ======== PEDIDOS ========
class PedidoBase(BaseModel):
    cliente: str
    itens: List[dict]

class PedidoCreate(PedidoBase):
    pass

class Pedido(PedidoBase):
    id: int
    valorTotalPedido: float
    dataPedido: datetime
    status: str

    class Config:
        orm_mode = True
