# Branch Loans API

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/branch-loans-api.git
cd branch-loans-api
```

### 2. First-time setup

#### Windows (Powershell, Run as Administrator)

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup_ssl_and_hosts.ps1
```
This will generate .key, .crt, .pem files in nginx/ssl/branchloans

#### Linux/macOS

```bash
# Make the setup script executable
chmod +x ./scripts/setup.sh

# Run the setup script
./scripts/setup.sh
```

### 3. Running (Development)

```bash
docker compose up -d --build
docker compose  exec api alembic upgrade head 

Access
- Health: `https://branchloans.com:8443/health`
- API Docs: `https://branchloans.com:8443/docs`
- Prometheus: `https://localhost:9090` (this will run only when docker-compose.monitoring.yml is implemented)
- Grafana: `https://localhost:3000`  (default: username and password, both are admin, admin)


To stop: 

```bash
docker compose down -v
```

## Project Structure

```
.
├── .github/                          # GitHub workflows and templates
│   └── workflows/ci-cd.yaml          # CI/CD pipelines
├── app/                              # Application code
├── nginx/                            # Nginx configuration
├── scripts/                          # Utility scripts
├── tests/                            # Test suite
├── docker-compose.staging.yml        # Stagging overrides
├── docker-compose.monitoring.yml     # Prometheus + Grafana add-on
├── docker-compose.override.yml       # Development overrides
├── docker-compose.prod.yml           # Production overrides
└── docker-compose.yml                # Base Docker Compose Config 
```

# Running the Application
```bash
docker-compose up --build
docker compose -f docker-compose.yml -f docker-compose.override.yml up --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
docker compose -f docker-compose.yml -f docker-compose.staging.yml up --build
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up --build
```


# Run in detached mode
```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

# View logs
```bash
docker compose logs -f
```

# Stop all services
```bash
docker compose down
```

## API Documentation

Once the application is running, access the interactive API documentation:

- Swagger UI: https://localhost:8443/docs
- ReDoc: https://localhost:8443/redoc

### Health Checks

```bash
# Basic health check
curl -k https://localhost:8443/health

# Detailed health check
curl -k https://localhost:8443/health/detailed
```

###  Port Conflicts

If you get port conflicts, update the ports in `.env`:

```env
API_PORT=8000
NGINX_HTTP_PORT=8080
NGINX_HTTPS_PORT=8443
POSTGRES_PORT=5432
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
Configure Local Domain
Add the following line to your hosts file (`C:\Windows\System32\drivers\etc\hosts`):
```
127.0.0.1   branchloans.com www.branchloans.com
```

## Generate SSL Certificates
Run the following command to generate self-signed SSL certificates:
```bash
# On Windows (PowerShell as Administrator):
.\generate_ssl.ps1

# On Linux/macOS:
chmod +x nginx/ssl/generate_ssl.sh
./nginx/ssl/generate_ssl.sh
```

###  Run Database Migrations
```bash
docker compose exec api alembic upgrade head
```

###  Seed Dummy Data (Optional)
```bash
docker compose exec api python scripts/seed.py
```






