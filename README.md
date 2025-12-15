# BaseAPI

FastAPI backend with JWT authentication + HTTP-only Cookies, SQLAlchemy ORM, and Alembic migrations.

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Local HTTPS Configuration](#local-https-configuration)
- [Database Migrations](#database-migrations)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [Frontend](#frontend)

## 🎯 About the Project

BaseAPI is a complete REST API built with FastAPI, offering secure authentication, database management, and local HTTPS support.

## ✨ Features

- 🔐 **JWT Authentication** - Secure tokens with HTTP-only cookies
- 🗄️ **SQLAlchemy ORM** - Efficient database management
- 🔄 **Alembic Migrations** - Database version control
- 📧 **Email Validation** - Valid email verification
- 🔒 **SSL Support** - Local HTTPS with mkcert
- 📝 **Logging System** - Activity recording
- 🔑 **Password Hashing** - Bcrypt for security
- 🍪 **Cookie Manager** - Secure cookie management

## 🛠️ Technologies Used

- **FastAPI** - Modern and fast web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for Python
- **Alembic** - Database migration tool
- **PyMySQL** - MySQL driver for Python
- **Psycopg2** - PostgreSQL adapter
- **Passlib[bcrypt]** - Password hashing library
- **Python-JOSE** - JWT implementation
- **Python-Multipart** - File upload support
- **Email-Validator** - Email address validation
- **Python-Dotenv** - Environment variable management

## 📦 Prerequisites

Before starting, make sure you have installed:

- **Python** 3.11+ 
- **pip** (Python package manager)
- **MySQL** or **PostgreSQL**
- **Git** (to clone the repository)
- **mkcert** (for local SSL certificates - optional)

## 🚀 Installation

### 1️⃣ Create and activate virtual environment

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

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Environment Configuration

### Rename the example file:

```bash
.env.example → .env
```

### Fill in your variables:

**For MySQL:**
```env
DB_USER=root	
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_NAME=db	
```

**Allowed Domain Origins to Access the API**
***Important for CORS***
```env
CORS_ORIGINS=https://localhost:4200
```

**JWT Key**
```env
JWT_SECRET=put_a_strong_secret_here
```

> **Tip:** Generate a strong JWT key using: [JWT Secret Key Generator](https://jwtsecretkeygenerator.com/)

## 🔒 Local HTTPS Configuration

This project includes local SSL support using mkcert.

### 📥 1️⃣ Download mkcert

Download the executable for Windows:

[https://github.com/FiloSottile/mkcert/releases](https://github.com/FiloSottile/mkcert/releases)

Recommended file: `mkcert-v1.4.4-windows-amd64.exe`

Rename to: `mkcert.exe`

And place it in a folder in PATH, for example: `C:\Windows\System32`

Or simply keep it in the project folder.

### 🏦 2️⃣ Install the root CA (only the first time)

Open PowerShell as administrator and run:

```bash
mkcert -install
```

### 📍 3️⃣ Navigate to the project folder

```bash
cd BaseAPI
```

### 🔏 4️⃣ Generate SSL certificates

```bash
mkcert localhost 127.0.0.1 ::1
```

> **Note:** Only for local development. Some hosting providers already provide SSL certificates, which are necessary to use HTTP-only cookies.

This will create files like:
- `localhost+2.pem` (certificate)
- `localhost+2-key.pem` (private key)

## 🧪 Database Migrations

### Apply migration (will generate the usr_user table):

```bash
alembic upgrade head
```

### Create a new migration:

```bash
alembic revision -m "migration description"
```

### Rollback last migration:

```bash
alembic downgrade -1
```

### View migration history:

```bash
alembic history
```

## ▶️ Running the Project

### Development Server (HTTP)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access: `http://localhost:8000`

### Development Server (HTTPS)

After generating the certificates, run:

```bash
uvicorn main:app --reload --ssl-keyfile localhost+2-key.pem --ssl-certfile localhost+2.pem --host 0.0.0.0 --port 8000
```

Now your backend is on local HTTPS: [https://localhost:8000](https://localhost:8000)

## 📂 Project Structure

```
BaseAPI/
├── alembic/              # Database migrations
│   └── versions/         # Migration versions
├── infra/                # Infrastructure
│   ├── auth/            # Authentication services
│   │   ├── auth_service.py
│   │   └── cookie_manager.py
│   ├── dependencies/    # FastAPI dependencies
│   └── providers/       # Providers (hash, JWT)
│       ├── hash_provider.py
│       └── jwt_provider.py
├── models/              # SQLAlchemy models
│   └── user.py
├── routers/             # API routes
│   ├── auth.py
│   └── users.py
├── schemas/             # Pydantic schemas
│   └── user.py
├── .env                 # Environment variables (not versioned)
├── .env.example         # Environment variables example
├── .gitignore           # Files ignored by Git
├── alembic.ini          # Alembic configuration
├── database.py          # Database configuration
├── logging_config.py    # Logging configuration
├── main.py              # Application entry point
└── requirements.txt     # Project dependencies
```

## 🔗 Frontend

This project serves as the backend for a frontend application. To configure and run the frontend, visit:

**BaseFrontAngular:** [https://github.com/eliezer-chaves/BaseFrontAngular.git](https://github.com/eliezer-chaves/BaseFrontAngular.git)

Make sure the backend is running before starting the frontend to ensure the full functionality of the application.

## 📚 API Documentation

With the server running, access:

- **Swagger UI:** `https://localhost:8000/docs`
- **ReDoc:** `https://localhost:8000/redoc`

## 📝 License

Personal and educational use project.

## 👨‍💻 Author

Developed by Eliézer Chaves

---

⭐ If this project was useful to you, consider giving the repository a star!

Developed with ❤️ using FastAPI
