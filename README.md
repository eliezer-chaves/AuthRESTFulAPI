# 📘 BaseAPI — Backend em FastAPI com Autenticação JWT + Cookies HTTP-only

Este projeto é uma API moderna construída com FastAPI, utilizando:
- Autenticação JWT com cookies HTTP-only
- ORM SQLAlchemy
- Migrações com Alembic
- Validação de email
- Suporte a PostgreSQL e MySQL
- SSL local via mkcert

## 🚀 Tecnologias Principais
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- PyMySQL / psycopg2
- Passlib (bcrypt)
- Python-JOSE (JWT)
- python-multipart
- python-dotenv

### 📦 Instalação
1️⃣ Criar e ativar o ambiente virtual

Windows
````python -m venv venv````
````source venv/Scripts/activate````
 
Linux/Mac
````python -m venv venv````
````source venv/Scripts/activate````

2️⃣ Instalar dependências
```` pip install -r requirements.txt ````

⚙️ Configuração do Ambiente
Renomeie o arquivo:
.env.example → .env

Preencha suas variáveis:
DATABASE_URL=mysql+pymysql://root:senha@localhost/dbname
JWT_SECRET=coloque_um_segredo_forte
JWT_EXPIRES=3600

## 🔐 Configurar HTTPS Local com mkcert
Este projeto inclui suporte a SSL local usando mkcert.

📥 1️⃣ Baixar o mkcert

Baixe o executável para Windows:
[🔗](https://github.com/FiloSottile/mkcert/releases)

Arquivo recomendado:
mkcert-v1.4.4-windows-amd64.exe

Renomeie para:
mkcert.exe

E coloque em uma pasta no PATH, por exemplo:
C:\Windows\System32

Ou simplesmente mantenha na pasta do projeto.

## 🏦 2️⃣ Instalar o root CA (somente na primeira vez)
Abra o PowerShell como administrador e execute:
```` mkcert -install ````

📍 3️⃣ Ir até a pasta do projeto
````cd BaseAPI````

🔏 4️⃣ Gerar os certificados SSL
````mkcert localhost 127.0.0.1 ::1````

(apenas para desenvolvimento local, algumas hospedagens já fornecem o certificado ssl, que é necessário para usar Http Cookie Only)

Isso irá criar arquivos como:
- localhost+2.pem
- localhost+2-key.pem

## 🧪 Rodar migrações Alembic
Aplicar migration (irá gerar a tabela usr_user):
```` alembic upgrade head ````

## ▶ Rodar o servidor FastAPI com HTTPS
Após gerar os certificados, rode:
```` uvicorn main:app --reload --ssl-keyfile localhost+2-key.pem --ssl-certfile localhost+2.pem --host 0.0.0.0 --port 8000 ````

Agora seu backend está no HTTPS local:
````https://localhost:8000````

## 📝 Licença
Projeto de uso pessoal e educacional.