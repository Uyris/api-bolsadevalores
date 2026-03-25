# Bolsa de Valores API

API para gerenciar transações de ações na bolsa de valores.

## Funcionalidades

- **GET /transacao** - Lista todas as transações ou filtra por cliente
- **POST /transacao** - Cria uma nova transação com validação de cliente
- **DELETE /transacao/{id}** - Deleta uma transação
- **GET /health** - Verifica a saúde da aplicação

## Instalação Local

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd api-bolsadevalores
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.local.example .env.local
```

Edite `.env.local` com suas configurações locais.

### 3. Instale as dependências

```bash
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` no Windows
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

## Usando Docker Compose Localmente

```bash
cp .env.local.example .env.local
docker compose up -d
```

Acesse em `http://localhost:8000`

## Endpoints

### GET /transacao

Lista todas as transações ou filtra por cliente.

**Parâmetros Query:**
- `usuario_id` (opcional): ID do cliente para filtrar

**Exemplo:**
```bash
curl http://localhost:8000/transacao
curl http://localhost:8000/transacao?usuario_id=123
```

### POST /transacao

Cria uma nova transação. Valida o usuário contra a API externa.

**Body:**
```json
{
  "usuario_id": "123",
  "codigo_acao": "PETR4",
  "quantidade": 100,
  "preco_unitario": 28.50,
  "data_transacao": "2026-03-25T10:30:00"
}
```

**Retorno:**
```json
{
  "id": 1,
  "usuario_id": "123",
  "usuario_email": "user@example.com",
  "codigo_acao": "PETR4",
  "quantidade": 100,
  "preco_unitario": 28.50,
  "valor_total": 2850.00,
  "data_transacao": "2026-03-25T10:30:00",
  "created_at": "2026-03-25T10:35:00"
}
```

### DELETE /transacao/{id}

Deleta uma transação pelo ID.

**Exemplo:**
```bash
curl -X DELETE http://localhost:8000/transacao/1
```

**Retorna:** 204 No Content

## Variáveis de Ambiente

- `DATABASE_URL` - String de conexão PostgreSQL (obrigatório em produção)
- `USERS_API_URL` - URL base da API de usuários (padrão: http://18.228.48.67)
- `USERS_API_TIMEOUT` - Timeout para requisições HTTP em segundos (padrão: 10)
- `HOST` - Host onde a API será executada (padrão: 0.0.0.0)
- `PORT` - Porta da API (padrão: 8000)

## Estrutura do Banco de Dados

### Tabela: transacoes

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | Chave primária |
| usuario_id | STRING | ID do usuário (validado) |
| usuario_email | STRING | Email do usuário |
| codigo_acao | STRING | Código da ação (ex: PETR4) |
| quantidade | INTEGER | Quantidade de ações |
| preco_unitario | FLOAT | Preço por ação |
| valor_total | FLOAT | Valor total (calculado) |
| data_transacao | DATETIME | Data da transação |
| created_at | DATETIME | Data de criação do registro |

## Tratamento de Erros

- **400 Bad Request** - Dados inválidos na requisição
- **404 Not Found** - Usuário ou transação não encontrada
- **500 Internal Server Error** - Erro ao conectar com a API de usuários

## Testes

Para testar a API localmente:

```bash
# Listar transações
curl http://localhost:8000/transacao

# Criar transação (ajuste usuario_id conforme necessário)
curl -X POST http://localhost:8000/transacao \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "1",
    "codigo_acao": "VALE5",
    "quantidade": 50,
    "preco_unitario": 65.00,
    "data_transacao": "2026-03-25T10:00:00"
  }'

# Deletar transação
curl -X DELETE http://localhost:8000/transacao/1

# Health check
curl http://localhost:8000/health
```
