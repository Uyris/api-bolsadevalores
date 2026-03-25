from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import requests
import os
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from models import Transacao, get_db, init_db
from schemas import TransacaoCreate, TransacaoResponse, UsuarioExterno

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (no cleanup needed for this app)


app = FastAPI(
    title="API Bolsa de Valores",
    description="API para gerenciar transações de ações na bolsa de valores",
    lifespan=lifespan
)

# Configuration
USERS_API_URL = os.getenv("USERS_API_URL", "http://18.228.48.67")
USERS_API_TIMEOUT = int(os.getenv("USERS_API_TIMEOUT", "10"))


def validar_usuario(usuario_id: str) -> UsuarioExterno:
    """Valida se o usuário existe na API externa"""
    try:
        response = requests.get(
            f"{USERS_API_URL}/users/{usuario_id}",
            timeout=USERS_API_TIMEOUT
        )
        
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Usuário com ID {usuario_id} não encontrado"
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Erro ao validar usuário com a API externa"
            )
        
        usuario_data = response.json()
        return UsuarioExterno(
            id=usuario_data.get("id", usuario_id),
            email=usuario_data.get("email"),
            name=usuario_data.get("name")
        )
    
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Erro ao conectar com a API de usuários"
        )


@app.get("/transacao", response_model=List[TransacaoResponse])
def listar_transacoes(
    usuario_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista todas as transações cadastradas.
    Se usuario_id for fornecido, lista apenas as transações desse cliente.
    """
    query = db.query(Transacao)
    
    if usuario_id:
        query = query.filter(Transacao.usuario_id == usuario_id)
    
    transacoes = query.all()
    return transacoes


@app.delete("/transacao/{transacao_id}", status_code=204)
def deletar_transacao(
    transacao_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta uma transação pelo seu ID.
    Retorna erro 404 se a transação não existir.
    """
    transacao = db.query(Transacao).filter(
        Transacao.id == transacao_id
    ).first()
    
    if not transacao:
        raise HTTPException(
            status_code=404,
            detail=f"Transação com ID {transacao_id} não encontrada"
        )
    
    db.delete(transacao)
    db.commit()
    return None


@app.post("/transacao", response_model=TransacaoResponse, status_code=201)
def criar_transacao(
    transacao_data: TransacaoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova transação.
    Valida se o usuário existe na API externa.
    Calcula o valor total da transação no backend.
    """
    # Validar usuário
    usuario = validar_usuario(transacao_data.usuario_id)
    
    if not usuario.email:
        raise HTTPException(
            status_code=500,
            detail="Email do usuário não encontrado na API externa"
        )
    
    # Calcular valor total
    valor_total = transacao_data.quantidade * transacao_data.preco_unitario
    
    # Criar transação
    nova_transacao = Transacao(
        usuario_id=transacao_data.usuario_id,
        usuario_email=usuario.email,
        codigo_acao=transacao_data.codigo_acao,
        quantidade=transacao_data.quantidade,
        preco_unitario=transacao_data.preco_unitario,
        valor_total=valor_total,
        data_transacao=transacao_data.data_transacao
    )
    
    db.add(nova_transacao)
    db.commit()
    db.refresh(nova_transacao)
    
    return nova_transacao


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
