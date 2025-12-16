# 💬 ChatApp - Real-Time Messaging Platform (tested)

A Django-based chat application with WebSocket support for instant messaging, blogging, and user notifications.

## How It Works

**Architecture:**
- Django handles HTTP requests (web pages, API, authentication)
- Django Channels manages WebSocket connections for real-time chat
- PostgreSQL/SQLite stores all data (users, messages, posts)
- In-memory channel layer handles WebSocket message broadcasting

**Flow:**
1. Users register/login → Django creates session
2. Access chat room → WebSocket connection established
3. Send message → Saved to database + broadcast to room members via WebSocket
4. Notifications triggered via Django signals when events occur

## Features

✅ **Real-time Chat** - WebSocket messaging with typing indicators, read receipts  
✅ **Direct & Group Chats** - One-on-one and multi-user conversations  
✅ **Blog System** - Posts with comments, likes, and view tracking  
✅ **Notifications** - Alerts for messages, comments, likes, profile views  
✅ **User Profiles** - Avatars, status messages, privacy settings  
✅ **REST API** - JWT authentication for mobile apps  
✅ **Responsive UI** - Mobile-friendly design

## Quick Setup

```bash
# Clone and install
git clone <repo-url>
cd chatapp
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure (use SQLite for simplicity)
cp .env.example .env

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver 0.0.0.0:8000
```

Access at: `http://your-ip:8000`

## Local Server Deployment (Home/Office)

### Option 1: Simple runserver (Quick)

```bash
# Run on boot - Linux/Mac
crontab -e
# Add: @reboot cd /path/to/chatapp && /path/to/venv/bin/python manage.py runserver 0.0.0.0:8000

# Run on boot - Windows
# Create startup.bat:
cd C:\path\to\chatapp
venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
# Place shortcut in: shell:startup
```

**Pros:** Simple, no configuration  
**Cons:** Single-threaded, not production-grade

### Option 2: Production-ready (Recommended)

```bash
# Install
pip install gunicorn

# Run
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 2
```

**Create systemd service** `/etc/systemd/system/chatapp.service`:
```ini
[Unit]
Description=ChatApp
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/chatapp
Environment="PATH=/path/to/chatapp/venv/bin"
ExecStart=/path/to/chatapp/venv/bin/gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable chatapp
sudo systemctl start chatapp
```

## Raspberry Pi Deployment

### 1. Prepare Pi
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql nginx -y
```

### 2. Setup Database
```bash
sudo -u postgres psql
CREATE DATABASE chatapp;
CREATE USER chatapp WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatapp TO chatapp;
\q
```

### 3. Deploy App
```bash
cd /home/pi
git clone <repo-url> chatapp
cd chatapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
nano .env
# Set:
# DB_NAME=chatapp
# DB_USER=chatapp
# DB_PASSWORD=your_password
# DB_HOST=localhost

# Initialize
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. Create Service
`sudo nano /etc/systemd/system/chatapp.service`:
```ini
[Unit]
Description=ChatApp
After=network.target postgresql.service

[Service]
User=pi
WorkingDirectory=/home/pi/chatapp
Environment="PATH=/home/pi/chatapp/venv/bin"
ExecStart=/home/pi/chatapp/venv/bin/gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --workers 2

[Install]
WantedBy=multi-user.target
```

### 5. Configure Nginx
`sudo nano /etc/nginx/sites-available/chatapp`:
```nginx
server {
    listen 80;
    server_name _;
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/pi/chatapp/staticfiles/;
    }

    location /media/ {
        alias /home/pi/chatapp/media/;
    }
}
```

### 6. Start Everything
```bash
# Enable services
sudo systemctl enable chatapp
sudo systemctl start chatapp

# Configure Nginx
sudo ln -s /etc/nginx/sites-available/chatapp /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default
sudo systemctl restart nginx

# Check status
sudo systemctl status chatapp
sudo systemctl status nginx
```

**Access:** `http://raspberry-pi-ip`

### 7. Maintenance Commands
```bash
# View logs
sudo journalctl -u chatapp -f

# Restart after changes
cd /home/pi/chatapp
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart chatapp

# Check errors
sudo systemctl status chatapp
```

## Performance Tips (Raspberry Pi)

```python
# In config/settings.py - reduce workers memory
# Gunicorn: --workers 1 (for Pi Zero/1)
# Gunicorn: --workers 2 (for Pi 3/4)

# Enable connection pooling
DATABASES = {
    'default': {
        # ... other settings ...
        'CONN_MAX_AGE': 600,
    }
}
```

## Access Points

- **Web UI:** `http://your-ip`
- **Admin:** `http://your-ip/admin`
- **API:** `http://your-ip/api/v1/`
- **Notifications:** `http://your-ip/accounts/notifications/`

## Troubleshooting

**Can't access from other devices:**
```bash
# Check firewall
sudo ufw allow 80
sudo ufw allow 8000

# Check ALLOWED_HOSTS in settings.py
ALLOWED_HOSTS = ['*']  # For testing
```

**WebSocket not working:**
- Ensure using `gunicorn` with uvicorn workers, not Django's runserver
- Check browser console for connection errors

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

**Pi running slow:**
```bash
# Reduce workers to 1
# Use SQLite instead of PostgreSQL
# Disable debug mode: DEBUG=False
```

## Updates

```bash
cd /home/pi/chatapp
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart chatapp
```
