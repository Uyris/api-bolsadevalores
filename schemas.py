from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TransacaoCreate(BaseModel):
    usuario_id: str
    codigo_acao: str
    quantidade: int
    preco_unitario: float
    data_transacao: datetime


class TransacaoResponse(BaseModel):
    id: int
    usuario_id: str
    usuario_email: str
    codigo_acao: str
    quantidade: int
    preco_unitario: float
    valor_total: float
    data_transacao: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UsuarioExterno(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
