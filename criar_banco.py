from app.database import Base, engine
from app.models import ProdutoModel, PedidoModel

Base.metadata.create_all(bind=engine)
