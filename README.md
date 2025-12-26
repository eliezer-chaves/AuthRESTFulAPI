# AuthAPI

RESTful API built with FastAPI featuring JWT authentication, HTTP-only cookies, email verification, password recovery, SQLAlchemy ORM, and Alembic migrations.

---

## 📌 About the Project

AuthAPI is a production-ready RESTful authentication API built with FastAPI.  
It provides secure session management using JWT stored in HTTP-only cookies, full email-based account validation, password reset flows, and database versioning with Alembic.

This project is designed to be used as a backend foundation for web applications that require secure authentication and session handling.

---

## ✨ Features

- 🔐 **JWT Authentication**
  - Access tokens with configurable expiration
  - Secure token generation and validation
- 🍪 **HTTP-only Cookie Sessions**
  - Secure against XSS attacks
  - SameSite protection
  - Configurable TTL
- 📧 **Email Account Confirmation**
  - Token-based email verification
  - HTML email templates
  - Resend confirmation capability
- 🔁 **Password Reset Flow**
  - One-time reset codes
  - Expiration and reuse protection
- 🧠 **Authentication Services Layer**
  - Clear separation between routers, services, and providers
  - Modular architecture for easy maintenance
- 🗄️ **SQLAlchemy ORM**
  - MySQL and PostgreSQL support
  - Relationship mapping
- 🔄 **Alembic Migrations**
  - Versioned database schema
  - Easy rollback capability
- 🔑 **Password Hashing**
  - Bcrypt via Passlib (cost factor 12)
- 📝 **Centralized Logging**
  - Daily log files with rotation
  - Comprehensive activity tracking
- 🔒 **Local HTTPS Support**
  - mkcert for secure cookie testing in development

---

## 🛠️ Technologies Used

- **FastAPI** 0.123.9 - Modern, fast web framework
- **Uvicorn** 0.38.0 - ASGI server
- **SQLAlchemy** 2.0.44 - SQL toolkit and ORM
- **Alembic** 1.17.2 - Database migration tool
- **PyMySQL** 1.1.2 - MySQL driver
- **Passlib[bcrypt]** 1.7.4 - Password hashing library
- **Python-JOSE** 3.5.0 - JWT implementation
- **FastAPI-Mail** 1.6.0 - Email sending service
- **Python-Dotenv** 1.2.1 - Environment variable management
- **Email-Validator** 2.3.0 - Email address validation

---

## 📦 Requirements

Before starting, ensure you have:

- **Python** 3.11+
- **pip** (Python package manager)
- **Git**
- **MySQL** database
- **SMTP Email Account** (Gmail, SendGrid, etc.)
- **mkcert** (optional, for local HTTPS)

---

## 📥 Clone the Repository

```bash
git clone https://github.com/eliezer-chaves/BaseAPI.git
cd BaseAPI
```

---

## 🧪 Virtual Environment Setup

### Create a virtual environment

**Windows:**
```bash
python -m venv venv
```

**Linux / macOS:**
```bash
python3 -m venv venv
```

### Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file based on `.env.example`.

### Database Configuration

**MySQL:**
```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
```

### JWT & Security

```env
SECRET_KEY=your_jwt_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

> **Tip:** Generate a strong JWT secret key at [JWT Secret Key Generator](https://jwtsecretkeygenerator.com/)

### Cookies

```env
AUTH_COOKIE_MAX_AGE=86400
COOKIE_SECRET=your_cookie_secret_key
SHORT_LIVED_TTL_MINUTES=5
```

> ⚠️ **Important:** HTTP-only cookies with `Secure=True` require HTTPS. This API is designed to run over HTTPS in development and production.

### CORS

```env
CORS_ORIGINS=https://localhost:4200
```

For multiple origins, use comma separation:
```env
CORS_ORIGINS=https://localhost:4200,https://yourdomain.com
```

### Email Configuration (Gmail SMTP)

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_FROM_NAME=AuthAPI
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

### App URLs

```env
APP_NAME=AuthAPI
FRONT_URL=https://localhost:4200
```

---

## 📧 Gmail App Password (Required)

Gmail does not allow normal account passwords for SMTP authentication.

### Steps to generate an App Password:

1. **Enable 2-Step Verification** on your Google account

2. **Go to App Passwords:**
   - Visit: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

3. **Create a new app password:**
   - Select app: Mail
   - Select device: Other (custom name)
   - Click "Generate"

4. **Use the generated password** in your `.env`:
   ```env
   MAIL_PASSWORD=xxxxxxxxxxxxxxxx
   ```

---

## 🔒 HTTPS Configuration (Required for HTTP-only Cookies)

### Install mkcert

**Windows:**
- Download from: [https://github.com/FiloSottile/mkcert/releases](https://github.com/FiloSottile/mkcert/releases)
- Recommended: `mkcert-v1.4.4-windows-amd64.exe`
- Rename to `mkcert.exe` and add to PATH

**Linux:**
```bash
sudo apt install mkcert  # Debian/Ubuntu
```

**macOS:**
```bash
brew install mkcert
```

### Install local CA (run once)

```bash
mkcert -install
```

### Generate SSL certificates

Navigate to your project folder and run:

```bash
mkcert localhost 127.0.0.1 ::1
```

This will generate:
- `localhost+2.pem` (certificate)
- `localhost+2-key.pem` (private key)

---

## ▶️ Running the Application

### HTTPS (Recommended)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --ssl-certfile localhost+2.pem --ssl-keyfile localhost+2-key.pem
```

**Access:**
- API: `https://localhost:8000`
- Docs: `https://localhost:8000/docs`
- ReDoc: `https://localhost:8000/redoc`

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --ssl-certfile /path/to/cert.pem --ssl-keyfile /path/to/key.pem
```

### ⚠️ Running Without HTTPS (Not Recommended)

If you must run over HTTP for testing, modify cookie settings in:
- `core/handler/cookie_manager.py`

Change:
- `secure=False`
- Adjust `samesite` parameter

**Note:** This is only for local testing. In production, always use HTTPS.

---

## 🧪 Database Migrations

### Apply all migrations

Run after configuring `.env`:

```bash
alembic upgrade head
```

This creates:
- `usr_users` table (user accounts)
- `email_confirmation_tokens` table (email verification)
- `password_reset_codes` table (password recovery)

### Create a new migration

```bash
alembic revision -m "migration description"
```

### Rollback last migration

```bash
alembic downgrade -1
```

### View migration history

```bash
alembic history
```

---

## 🌐 API Routes

### Authentication Routes

#### Sessions (Login/Logout)
- `POST /auth/sessions/login` - User login
- `POST /auth/sessions/logout` - User logout
- `GET /auth/sessions/validate` - Validate current session

#### Accounts (Registration/Verification)
- `POST /auth/accounts/register` - Create new account
- `POST /auth/accounts/confirm` - Confirm email with token
- `POST /auth/accounts/resend-confirmation` - Resend confirmation email

#### Password Resets
- `POST /auth/password-resets/request` - Request password reset code
- `POST /auth/password-resets/validate` - Validate reset code
- `POST /auth/password-resets/reset` - Reset password with code

---

## 📂 Project Structure

```
BaseAPI/
├── alembic/                          # Database migrations
│   ├── versions/                     # Migration version files
│   │   ├── f5dbc96d3811_create_usr_users_table.py
│   │   ├── 0c4f9a65af1b_email_confirmation_token_table.py
│   │   └── 2cf037885739_create_password_reset_codes_table.py
│   ├── env.py
│   └── script.py.mako
├── core/                                       # Core application logic
│   ├── config/                                 # Configuration files
│   │   └── email_config.py                     # Email service configuration
│   ├── handler/                                # Request/Response handlers
│   │   └── cookie_manager.py                   # HTTP-only cookie management
│   ├── providers/                              # Security providers
│   │   ├── hash_provider.py                    # Password hashing with bcrypt
│   │   └── jwt_provider.py                     # JWT token generation/validation
│   ├── services/                               # Business logic services
│   │   ├── auth/                               # Authentication services
│   │   │   ├── auth_service.py                 # Login/logout logic
│   │   │   └── password_reset_service.py       # Password reset flow
│   │   └── email_service.py                    # Email sending service
│   ├── templates/                              # HTML email templates
│   │   ├── confirm_account.html                # Account confirmation email
│   │   └── reset_password.html                 # Password reset email
│   └── utils/                                  # Utility functions
│       └── email_utils.py                      # Email helpers
├── logs/                                       # Application logs (daily rotation)
│   └── YYYY-MM-DD.log                          # Daily log files
├── models/                                     # SQLAlchemy models
│   └── auth_models/                            # Authentication models
│       ├── user_model.py                       # User account model
│       ├── email_tokens_model.py               # Email verification tokens
│       ├── password_reset_code_model.py        # Password reset codes
│       └── __init__.py
├── routers/                                    # API route handlers
│   └── auth/                                   # Authentication routes
│       ├── sessions_router.py                  # Login/logout endpoints
│       ├── accounts_router.py                  # Registration/verification
│       └── password_resets_router.py           # Password reset endpoints
├── schemas/                                    # Pydantic validation schemas
│   └── user_schema.py                          # User request/response schemas
├── .env                                        # Environment variables (not in git)
├── .env.example                                # Environment variables template
├── .gitignore                                  # Git ignore rules
├── alembic.ini                                 # Alembic configuration
├── database.py                                 # Database connection setup
├── logging_config.py                           # Logging configuration
├── main.py                                     # Application entry point
├── requirements.txt                            # Python dependencies
└── README.md                                   # This file
```

---

## 📚 API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI:** `https://localhost:8000/docs`
- **ReDoc:** `https://localhost:8000/redoc`

Both provide complete API documentation with request/response examples and the ability to test endpoints directly from your browser.

---

## 🔐 Security Features

- ✅ HTTP-only cookies prevent XSS attacks
- ✅ CORS configuration limits allowed origins
- ✅ JWT tokens with configurable expiration
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ Email verification prevents fake accounts
- ✅ Rate limiting on email sending
- ✅ Secure password reset flow with time-limited codes
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ SameSite cookie protection

---

## 🐛 Troubleshooting

### Database connection issues
- Verify database credentials in `.env`
- Ensure database server is running
- Check that database exists (`DB_NAME`)
- Test connection manually

### Email not sending
- Verify SMTP credentials
- For Gmail, use App Password, not regular password
- Check firewall/antivirus blocking port 587
- Test SMTP connection separately

### SSL certificate errors
- Re-run `mkcert -install`
- Regenerate certificates: `mkcert localhost 127.0.0.1 ::1`
- Clear browser cache and restart browser

### Import errors
- Ensure virtual environment is activated
- Re-install dependencies: `pip install -r requirements.txt`
- Check Python version (3.11+ required)

### Cookie not being set
- Ensure HTTPS is enabled (cookies with `Secure=True` require HTTPS)
- Check CORS_ORIGINS matches your frontend URL
- Verify browser allows third-party cookies

---

## 🔗 Frontend Integration

This backend is designed to work with a frontend application.

**BaseFrontAngular:** [https://github.com/eliezer-chaves/BaseFrontAngular](https://github.com/eliezer-chaves/BaseFrontAngular)

The frontend includes:
- Login/Registration forms
- Email verification flow
- Password reset functionality
- Protected routes with JWT authentication
- HTTP-only cookie handling

Make sure the backend is running before starting the frontend application.

---

## 📝 License

This project is for personal and educational use.

---

## 👨‍💻 Author

**Developed by Eliézer Chaves**

- GitHub: [@eliezer-chaves](https://github.com/eliezer-chaves)

---

⭐ If this project helped you, consider starring the repository!

💻 Built with security, caffeine, and FastAPI ❤️