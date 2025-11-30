# SmartAttend Deployment Guide

This guide provides instructions for deploying the SmartAttend application in a production environment.

## Architecture Overview

The SmartAttend application consists of two main components:
1. **Frontend**: Flutter mobile application
2. **Backend**: Django REST API with PostgreSQL database

## Prerequisites

### Backend Server Requirements
- Ubuntu 20.04 LTS or newer (recommended)
- Python 3.11+
- PostgreSQL 15+
- Nginx
- Gunicorn
- Redis (for caching and background tasks)
- Docker & Docker Compose (optional but recommended)

### Mobile App Requirements
- Flutter SDK 3.10+
- Android Studio / Xcode for mobile builds
- Signing certificates for app store distribution

## Backend Deployment

### 1. Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Start and enable services
sudo systemctl start postgresql redis
sudo systemctl enable postgresql redis
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE smartattend_db;
CREATE USER smartattend_user WITH PASSWORD 'your_secure_password';
ALTER ROLE smartattend_user SET client_encoding TO 'utf8';
ALTER ROLE smartattend_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE smartattend_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE smartattend_db TO smartattend_user;
\q
```

### 3. Application Deployment

```bash
# Clone the repository
git clone https://github.com/your-username/smartattend.git
cd smartattend/smartattend_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file for production
cat > .env << EOF
DEBUG=False
SECRET_KEY=your_production_secret_key
DB_NAME=smartattend_db
DB_USER=smartattend_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
EOF
```

### 4. Database Migration and Initial Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Gunicorn Configuration

Create a Gunicorn configuration file:

```bash
# gunicorn_config.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### 6. Systemd Service

Create a systemd service file for the Django application:

```bash
# /etc/systemd/system/smartattend.service
[Unit]
Description=SmartAttend Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/smartattend/smartattend_backend
ExecStart=/path/to/smartattend/smartattend_backend/venv/bin/gunicorn --config gunicorn_config.py smartattend.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start smartattend
sudo systemctl enable smartattend
```

### 7. Nginx Configuration

Create an Nginx configuration file:

```nginx
# /etc/nginx/sites-available/smartattend
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /path/to/smartattend/smartattend_backend/media/;
    }

    location /static/ {
        alias /path/to/smartattend/smartattend_backend/staticfiles/;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/smartattend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL Certificate (Recommended)

Install Certbot and obtain an SSL certificate:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Mobile App Deployment

### Android Deployment

1. **Build Release APK**:
   ```bash
   cd ../smart_attend
   flutter build apk --release
   ```

2. **Build App Bundle for Play Store**:
   ```bash
   flutter build appbundle --release
   ```

3. **Sign the APK/App Bundle**:
   - Create a keystore file
   - Configure signing in `android/app/build.gradle`

### iOS Deployment

1. **Build for iOS**:
   ```bash
   flutter build ios --release
   ```

2. **Open in Xcode**:
   - Open `ios/Runner.xcworkspace` in Xcode
   - Configure signing and capabilities
   - Archive and upload to App Store

## Docker Deployment (Alternative)

For easier deployment, you can use Docker:

1. **Build and run with Docker Compose**:
   ```bash
   cd smartattend_backend
   docker-compose up -d --build
   ```

2. **Run migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

## Environment Variables

Ensure the following environment variables are set in production:

| Variable | Description | Example |
|----------|-------------|---------|
| DEBUG | Debug mode | False |
| SECRET_KEY | Django secret key | your_secret_key |
| DB_NAME | Database name | smartattend_db |
| DB_USER | Database user | smartattend_user |
| DB_PASSWORD | Database password | your_secure_password |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 5432 |

## Security Considerations

1. **Use strong passwords** for database and admin accounts
2. **Enable HTTPS** with SSL certificates
3. **Regular backups** of database and media files
4. **Firewall configuration** to restrict access
5. **Regular updates** of system packages and dependencies
6. **Rate limiting** to prevent abuse
7. **Input validation** to prevent injection attacks

## Monitoring and Maintenance

1. **Log monitoring** with tools like ELK stack or Papertrail
2. **Uptime monitoring** with services like UptimeRobot
3. **Database backups** scheduled regularly
4. **Application performance monitoring** with tools like New Relic
5. **Error tracking** with Sentry or similar services

## Scaling Considerations

For high-traffic deployments:

1. **Load balancing** with multiple application servers
2. **Database replication** for read scaling
3. **Caching** with Redis or Memcached
4. **CDN** for static assets
5. **Horizontal scaling** with container orchestration (Kubernetes)

## Troubleshooting

Common issues and solutions:

1. **Database connection errors**: Check database credentials and network connectivity
2. **Permission errors**: Ensure proper file permissions for media and static directories
3. **Memory issues**: Monitor resource usage and scale accordingly
4. **Timeout errors**: Adjust Gunicorn timeout settings

## Backup and Recovery

Regular backup strategy:

1. **Database dumps**:
   ```bash
   pg_dump smartattend_db > backup_$(date +%F).sql
   ```

2. **Media files backup**:
   ```bash
   tar -czf media_backup_$(date +%F).tar.gz media/
   ```

3. **Automated backups** with cron jobs:
   ```bash
   # Daily database backup at 2 AM
   0 2 * * * pg_dump smartattend_db > /backups/db_backup_$(date +\%F).sql
   
   # Weekly media backup on Sundays at 3 AM
   0 3 * * 0 tar -czf /backups/media_backup_$(date +\%F).tar.gz /path/to/media/
   ```

## Support

For support and issues, please contact the development team or refer to the project documentation.