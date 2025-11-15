# Branch Loans API

A production-ready REST API for microloans, built with FastAPI, SQLAlchemy, PostgreSQL, and Docker.

## Features

- 🐳 Containerized application with Docker
- 🔒 HTTPS support with self-signed certificates
- 🌐 Nginx reverse proxy with SSL termination
- 🏗️ Multi-environment ready (development, staging, production)
- ⚡ FastAPI for high-performance API endpoints
- 🗄️ PostgreSQL database with persistent storage
- 🔄 Health checks and monitoring endpoints

## Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)
- [OpenSSL](https://www.openssl.org/) (included with Git for Windows)
- Windows PowerShell (for Windows users)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/branch-loans-api.git
cd branch-loans-api
```

### 2. Set up SSL certificates and hosts file (Windows)

Run the setup script as administrator:

```powershell
# In PowerShell (Run as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup_ssl_and_hosts.ps1
```

For Linux/macOS, you'll need to manually:
1. Generate SSL certificates using the script in `nginx/ssl/generate_ssl.sh`
2. Add the following to your `/etc/hosts` file:
   ```
   127.0.0.1    branchloans.com www.branchloans.com
   ```

### 3. Start the application

```bash
docker-compose up --build -d
```

### 4. Access the application

- API: https://branchloans.com
- Health Check: https://branchloans.com/health
- API Documentation: https://branchloans.com/docs

> **Note**: You might see a security warning because of the self-signed certificate. You can safely proceed by accepting the certificate in your browser.

## Project Structure

```
.
├── app/                    # Application source code
│   ├── __init__.py         # Application factory
│   ├── main.py             # Main application module
│   ├── config.py           # Configuration settings
│   ├── db.py               # Database configuration
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   └── schemas.py          # Pydantic schemas
├── nginx/                  # Nginx configuration
│   ├── nginx.conf          # Nginx configuration
│   └── ssl/                # SSL certificates
├── tests/                  # Test files
├── .env.example           # Example environment variables
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Application Dockerfile
└── requirements.txt       # Python dependencies
```

## Available Endpoints

- `GET /health` - Health check endpoint
- `GET /api/loans` - List all loans
- `GET /api/loans/{id}` - Get specific loan details
- `POST /api/loans` - Create new loan application
- `GET /api/stats` - Get loan statistics

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+psycopg2://postgres:postgres@db:5432/microloans` |
| `PORT` | Application port | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins | `["https://branchloans.com"]` |

## Development

### Running the development server

```bash
docker-compose up --build
```

### Running tests

```bash
docker-compose run --rm api pytest
```

### Accessing the database

```bash
# Connect to the database container
docker-compose exec db psql -U postgres -d microloans
```

## Production Deployment

1. Set up environment variables in `.env` file
2. Update SSL certificates with valid ones from Let's Encrypt
3. Run in production mode:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## Troubleshooting

### Certificate Errors

If you see certificate errors in your browser:
1. Make sure you've run the setup script as administrator
2. Manually install the certificate by double-clicking `nginx/ssl/branchloans.crt`
3. Select "Local Machine" and place the certificate in the "Trusted Root Certification Authorities" store

### Port Conflicts

If you get port conflicts (especially on Windows):
- Stop any applications using ports 80, 443, or 5432
- Or update the ports in `docker-compose.yml`

## License

MIT

### 1. Configure Local Domain
Add the following line to your hosts file (`C:\Windows\System32\drivers\etc\hosts`):
```
127.0.0.1   branchloans.com www.branchloans.com
```

### 2. Generate SSL Certificates
Run the following command to generate self-signed SSL certificates:
```bash
# On Windows (PowerShell as Administrator):
.\generate_ssl.ps1

# On Linux/macOS:
chmod +x nginx/ssl/generate_ssl.sh
./nginx/ssl/generate_ssl.sh
```

### 3. Build and Start Services
```bash
docker compose up -d --build
```

### 4. Run Database Migrations
```bash
docker compose exec api alembic upgrade head
```

### 5. Seed Dummy Data (Optional)
```bash
docker compose exec api python scripts/seed.py
```

### 6. Access the API
- API: https://branchloans.com
- Health Check: https://branchloans.com/health
- API Docs: https://branchloans.com/api/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /health | Health check |
| GET    | /api/loans | List all loans |
| GET    | /api/loans/:id | Get loan details |
| POST   | /api/loans | Create new loan |
| GET    | /api/stats | Get loan statistics |

## Development

### Environment Variables
Create a `.env` file with the following variables:
```
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=microloans
DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# Application
FLASK_ENV=development
PORT=8000
PYTHONPATH=/app

# Nginx
NGINX_HOST=branchloans.com
NGINX_PORT=443
```

### Running Tests
```bash
docker compose exec api pytest
```

## Deployment

The application is configured with GitHub Actions for CI/CD. The workflow includes:
1. Running tests
2. Building Docker images
3. Scanning for vulnerabilities
4. Pushing to container registry
5. Deploying to production (manual trigger)

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │ ──> │    Nginx    │ ──> │    API      │
└─────────────┘     │  (SSL/TLS)  │     │  (Flask)    │
                    └─────────────┘     └──────┬──────┘
                                            │
                                            ▼
                                    ┌─────────────┐
                                    │  PostgreSQL │
                                    └─────────────┘
```

## Security

- All traffic is encrypted with TLS 1.2/1.3
- Secure headers are configured in Nginx
- Database credentials are stored in environment variables
- Container security best practices are followed

## Troubleshooting

### Certificate Warnings
If you see certificate warnings in your browser:
1. Open `https://branchloans.com`
2. Click "Advanced" > "Proceed to branchloans.com (unsafe)"
3. Install the certificate in your trusted root store

### Port Conflicts
If you encounter port conflicts (80/443), check for other services using these ports:
```bash
# On Windows
netstat -ano | findstr :80
netstat -ano | findstr :443
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.