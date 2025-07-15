# Configuration Guide

## Environment Variables

All configuration is now managed through environment variables. Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

## Available Configuration Options

### Database Configuration
- `MYSQL_ROOT_PASSWORD`: Root password for MySQL
- `MYSQL_DATABASE`: Database name
- `MYSQL_USER`: Database user
- `MYSQL_PASSWORD`: Database password  
- `DB_PORT`: MySQL port (default: 3307)
- `DATABASE_URL`: Full database connection URL

### Application Configuration
- `SECRET_KEY`: JWT signing key (change in production!)
- `BACKEND_PORT`: Port for direct backend access (default: 8000)

### Nginx Configuration
- `NGINX_PORT`: Port for nginx proxy (default: 8811)
- `NGINX_SSL_PORT`: SSL port (default: 443)

### MinIO Configuration
- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key
- `MINIO_BUCKET_NAME`: Bucket name for file storage
- `MINIO_SECURE`: Use HTTPS for MinIO (true/false)

## Quick Start

1. **Setup configuration:**
   ```bash
   ./setup.sh
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Access your application:**
   - Production API: `http://localhost:${NGINX_PORT}`
   - Development API: `http://localhost:${BACKEND_PORT}/docs`
   - Health Check: `http://localhost:${NGINX_PORT}/health`

## Cloudflare Tunnel Setup

Point your Cloudflare tunnel to:
```
http://localhost:${NGINX_PORT}
```

## File Structure

- `nginx.conf.template`: Template for nginx configuration
- `nginx-entrypoint.sh`: Script to process nginx template with environment variables
- `docker-compose.yml`: Main orchestration file (now uses environment variables)
- `.env.example`: Template for environment variables
- `.env`: Your actual configuration (not tracked in git)
- `setup.sh`: Helper script for initial setup
