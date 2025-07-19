# main.py atualizado para usar schemas.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from app import schemas
import json
import os

app = FastAPI(title="API de Estoque e Pedidos", version="1.0")

# ======= Arquivos de persistência =======
PRODUTOS_FILE = "produtos.json"
PEDIDOS_FILE = "pedidos.json"

def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            return json.load(f)
    return []

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w') as f:
        json.dump(dados, f, indent=2, default=str)

produtos_db = carregar_dados(PRODUTOS_FILE)
pedidos_db = carregar_dados(PEDIDOS_FILE)

produto_id_counter = max([p['id'] for p in produtos_db], default=0)
pedido_id_counter = max([p['id'] for p in pedidos_db], default=0)

# ======= Middleware de log =======
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"\n[LOG] {request.method} {request.url}")
    response = await call_next(request)
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

# ======= PRODUTOS CRUD =======
@app.post("/produtos", response_model=schemas.Produto)
def criar_produto(produto: schemas.ProdutoCreate):
    global produto_id_counter
    if any(p['nome'].lower() == produto.nome.lower() for p in produtos_db):
        raise HTTPException(status_code=400, detail="Produto já existe")
    produto_id_counter += 1
    novo = schemas.Produto(id=produto_id_counter, **produto.dict())
    produtos_db.append(novo.dict())
    salvar_dados(PRODUTOS_FILE, produtos_db)
    return novo

@app.get("/produtos", response_model=List[schemas.Produto])
def listar_produtos(estoque_baixo: Optional[bool] = False):
    if estoque_baixo:
        return [schemas.Produto(**p) for p in produtos_db if p['quantidadeEstoque'] < 10]
    return [schemas.Produto(**p) for p in produtos_db]

@app.get("/produtos/{produto_id}", response_model=schemas.Produto)
def obter_produto(produto_id: int):
    for p in produtos_db:
        if p['id'] == produto_id:
            return schemas.Produto(**p)
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.put("/produtos/{produto_id}", response_model=schemas.Produto)
def atualizar_produto(produto_id: int, produto: schemas.ProdutoCreate):
    for i, p in enumerate(produtos_db):
        if p['id'] == produto_id:
            atualizado = schemas.Produto(id=produto_id, **produto.dict())
            produtos_db[i] = atualizado.dict()
            salvar_dados(PRODUTOS_FILE, produtos_db)
            return atualizado
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int):
    for i, p in enumerate(produtos_db):
        if p['id'] == produto_id:
            produtos_db.pop(i)
            salvar_dados(PRODUTOS_FILE, produtos_db)
            return {"mensagem": "Produto removido"}
    raise HTTPException(status_code=404, detail="Produto não encontrado")

# ======= PEDIDOS CRUD =======
@app.post("/pedidos", response_model=schemas.Pedido)
def criar_pedido(pedido: schemas.PedidoCreate):
    global pedido_id_counter
    itens_detalhados = []
    valor_total = 0
    for item in pedido.itens:
        prod = next((p for p in produtos_db if p['id'] == item['produtoId']), None)
        if not prod:
            raise HTTPException(status_code=404, detail=f"Produto ID {item['produtoId']} não encontrado")
        if prod['quantidadeEstoque'] < item['quantidade']:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para o produto ID {prod['id']}")

        total_item = prod['preco'] * item['quantidade']
        valor_total += total_item
        prod['quantidadeEstoque'] -= item['quantidade']

        itens_detalhados.append(schemas.ItemPedido(
            produtoId=prod['id'],
            nomeProduto=prod['nome'],
            quantidade=item['quantidade'],
            precoUnitario=prod['preco'],
            valorTotalItem=total_item
        ))

    pedido_id_counter += 1
    novo_pedido = schemas.Pedido(
        id=pedido_id_counter,
        cliente=pedido.cliente,
        itens=itens_detalhados,
        valorTotalPedido=valor_total,
        dataPedido=datetime.utcnow(),
        status="em_andamento"
    )
    pedidos_db.append(novo_pedido.dict())
    salvar_dados(PEDIDOS_FILE, pedidos_db)
    salvar_dados(PRODUTOS_FILE, produtos_db)
    return novo_pedido

@app.get("/pedidos", response_model=List[schemas.Pedido])
def listar_pedidos():
    return [schemas.Pedido(**p) for p in pedidos_db]

@app.get("/pedidos/{pedido_id}", response_model=schemas.Pedido)
def obter_pedido(pedido_id: int):
    for p in pedidos_db:
        if p['id'] == pedido_id:
            return schemas.Pedido(**p)
    raise HTTPException(status_code=404, detail="Pedido não encontrado")

@app.delete("/pedidos/{pedido_id}")
def deletar_pedido(pedido_id: int):
    for i, p in enumerate(pedidos_db):
        if p['id'] == pedido_id:
            pedidos_db.pop(i)
            salvar_dados(PEDIDOS_FILE, pedidos_db)
            return {"mensagem": "Pedido removido"}
    raise HTTPException(status_code=404, detail="Pedido não encontrado")
