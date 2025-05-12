# API FastAPI para Geração de Relatório de Disparos

Este projeto é uma API FastAPI que gera um relatório em PDF com gráficos sobre disparos. A API usa um banco de dados PostgreSQL para armazenar os dados dos disparos.

## Pré-requisitos

- Python 3.7+
- PostgreSQL
- Pip

## Configuração do Ambiente

1. Clone o repositório:

```bash
git clone <repositorio>
```

2. Crie um ambiente virtual:

```bash
python -m venv venv
```

3. Ative o ambiente virtual:

```bash
# No Windows
venv\Scripts\activate
# No Linux/macOS
source venv/bin/activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:

Crie um arquivo `.env` com as seguintes variáveis:

```
DB_HOST=<host do banco de dados>
DB_PORT=<porta do banco de dados>
DB_NAME=<nome do banco de dados>
DB_USER=<usuário do banco de dados>
DB_PASS=<senha do banco de dados>
```

## Execução do Projeto

1. Execute o projeto:

```bash
uvicorn main:app --reload
```

2. Acesse a API:

A API estará disponível em `http://127.0.0.1:8000`.

## Uso da API

### Rota /disparador

Esta rota gera o relatório em PDF e retorna o arquivo para download.

- Método: GET
- Parâmetros:
    - page: número da página (opcional, padrão: 1)
    - limit: número de itens por página (opcional, padrão: 10)

Exemplo de requisição:

```
http://127.0.0.1:8000/disparador?page=1&limit=10
```

## Rotas

### /disparador

Gera um relatório em PDF com gráficos sobre disparos e retorna o arquivo para download.

## Dependências

- fastapi==0.110.0
- uvicorn[standard]==0.29.0
- sqlalchemy==2.0.29
- psycopg2-binary==2.9.9
- python-dotenv==1.0.1
- matplotlib==3.8.4
- reportlab==4.1.0
- pandas==2.2.2

## Licença

Este projeto está sob a licença MIT.

## Contato

- GitHub: [ViniciusNCorrea98](https://github.com/ViniciusNCorrea98)
- LinkedIn: [Vinicius Correa](https://www.linkedin.com/in/vinicius-correa-82a603230/)
