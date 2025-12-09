# BaseAPI

Backend em FastAPI com autenticação JWT + Cookies HTTP-only, ORM SQLAlchemy e migrações Alembic.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Configuração HTTPS Local](#configuração-https-local)
- [Migrações de Banco de Dados](#migrações-de-banco-de-dados)
- [Executando o Projeto](#executando-o-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Frontend](#frontend)

## 🎯 Sobre o Projeto

BaseAPI é uma API REST completa construída com FastAPI, oferecendo autenticação segura, gerenciamento de banco de dados e suporte para HTTPS local.

## ✨ Funcionalidades

- 🔐 **Autenticação JWT** - Tokens seguros com cookies HTTP-only
- 🗄️ **ORM SQLAlchemy** - Gerenciamento eficiente de banco de dados
- 🔄 **Migrações Alembic** - Controle de versão do banco de dados
- 📧 **Validação de email** - Verificação de emails válidos
- 🔒 **Suporte SSL** - HTTPS local com mkcert
- 📝 **Sistema de logs** - Registro de atividades
- 🔑 **Hash de senhas** - Bcrypt para segurança
- 🍪 **Cookie Manager** - Gestão de cookies seguros

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI
- **SQLAlchemy** - ORM para Python
- **Alembic** - Ferramenta de migração de banco de dados
- **PyMySQL** - Driver MySQL para Python
- **Psycopg2** - Adaptador PostgreSQL
- **Passlib[bcrypt]** - Biblioteca para hash de senhas
- **Python-JOSE** - Implementação de JWT
- **Python-Multipart** - Suporte para upload de arquivos
- **Email-Validator** - Validação de endereços de email
- **Python-Dotenv** - Gerenciamento de variáveis de ambiente

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python** 3.11+ 
- **pip** (gerenciador de pacotes Python)
- **MySQL** ou **PostgreSQL**
- **Git** (para clonar o repositório)
- **mkcert** (para certificados SSL locais - opcional)

## 🚀 Instalação

### 1️⃣ Criar e ativar o ambiente virtual

**Windows:**
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
```
```bash
source venv/bin/activate
```

### 2️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração do Ambiente

### Renomeie o arquivo de exemplo:

```bash
.env.example → .env
```

### Preencha suas variáveis:

**Para MySQL:**
```env
DB_USER=root	
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_NAME=db	
```

**Origens de Domínio Permitidas Para Acessar a API**
***Importante para CORS***
```env
CORS_ORIGINS=https://localhost:4200
```

**Chave JWT**
```env
JWT_SECRET=coloque_um_segredo_forte
```

> **Dica:** Gere uma chave JWT forte usando: [Gerador de Chaves JWT](https://jwtsecretkeygenerator.com/)

## 🔒 Configuração HTTPS Local

Este projeto inclui suporte a SSL local usando mkcert.

### 📥 1️⃣ Baixar o mkcert

Baixe o executável para Windows:

[https://github.com/FiloSottile/mkcert/releases](https://github.com/FiloSottile/mkcert/releases)

Arquivo recomendado: `mkcert-v1.4.4-windows-amd64.exe`

Renomeie para: `mkcert.exe`

E coloque em uma pasta no PATH, por exemplo: `C:\Windows\System32`

Ou simplesmente mantenha na pasta do projeto.

### 🏦 2️⃣ Instalar o root CA (somente na primeira vez)

Abra o PowerShell como administrador e execute:

```bash
mkcert -install
```

### 📍 3️⃣ Ir até a pasta do projeto

```bash
cd BaseAPI
```

### 🔏 4️⃣ Gerar os certificados SSL

```bash
mkcert localhost 127.0.0.1 ::1
```

> **Nota:** Apenas para desenvolvimento local. Algumas hospedagens já fornecem o certificado SSL, que é necessário para usar HTTP Cookie Only.

Isso irá criar arquivos como:
- `localhost+2.pem` (certificado)
- `localhost+2-key.pem` (chave privada)

## 🧪 Migrações de Banco de Dados

### Aplicar migration (irá gerar a tabela usr_user):

```bash
alembic upgrade head
```

### Criar uma nova migração:

```bash
alembic revision --autogenerate -m "descrição da migração"
```

### Reverter última migração:

```bash
alembic downgrade -1
```

### Ver histórico de migrações:

```bash
alembic history
```

## ▶️ Executando o Projeto

### Servidor de Desenvolvimento (HTTP)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000`

### Servidor de Desenvolvimento (HTTPS)

Após gerar os certificados, rode:

```bash
uvicorn main:app --reload --ssl-keyfile localhost+2-key.pem --ssl-certfile localhost+2.pem --host 0.0.0.0 --port 8000
```

Agora seu backend está no HTTPS local: [https://localhost:8000](https://localhost:8000)

## 📂 Estrutura do Projeto

```
BaseAPI/
├── alembic/              # Migrações de banco de dados
│   └── versions/         # Versões de migração
├── infra/                # Infraestrutura
│   ├── auth/            # Serviços de autenticação
│   │   ├── auth_service.py
│   │   └── cookie_manager.py
│   ├── dependencies/    # Dependências do FastAPI
│   └── providers/       # Provedores (hash, JWT)
│       ├── hash_provider.py
│       └── jwt_provider.py
├── models/              # Modelos SQLAlchemy
│   └── user.py
├── routers/             # Rotas da API
│   ├── auth.py
│   └── users.py
├── schemas/             # Schemas Pydantic
│   └── user.py
├── .env                 # Variáveis de ambiente (não versionado)
├── .env.example         # Exemplo de variáveis de ambiente
├── .gitignore           # Arquivos ignorados pelo Git
├── alembic.ini          # Configuração do Alembic
├── database.py          # Configuração do banco de dados
├── logging_config.py    # Configuração de logs
├── main.py              # Ponto de entrada da aplicação
└── requirements.txt     # Dependências do projeto
```

## 🔗 Frontend

Este projeto serve como backend para uma aplicação frontend. Para configurar e executar o frontend, acesse:

**BaseFrontAngular:** [https://github.com/eliezer-chaves/BaseFrontAngular.git](https://github.com/eliezer-chaves/BaseFrontAngular.git)

Certifique-se de que o backend esteja rodando antes de iniciar o frontend para garantir o funcionamento completo da aplicação.

## 📚 Documentação da API

Com o servidor rodando, acesse:

- **Swagger UI:** `https://localhost:8000/docs`
- **ReDoc:** `https://localhost:8000/redoc`

## 📝 Licença

Projeto de uso pessoal e educacional.

## 👨‍💻 Autor

Desenvolvido por Eliézer Chaves

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!

Desenvolvido com ❤️ usando FastAPI