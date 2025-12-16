# 💬 ChatApp - Real-Time Messaging Platform

A full-stack Django chat application with real-time WebSocket messaging, blog system, and notifications.

## Features

- **Real-time Chat**: WebSocket messaging with typing indicators, read receipts, and reactions
- **Direct & Group Chats**: One-on-one and group conversations
- **Blog System**: Create posts with comments and likes
- **Notifications**: Real-time alerts for messages, comments, likes, and profile views
- **User Profiles**: Customizable profiles with avatars and status messages
- **REST API**: Complete API for mobile app integration
- **Responsive Design**: Mobile-friendly UI

## Tech Stack

- Django 5.0 + Django Channels (WebSocket)
- PostgreSQL (or SQLite for dev)
- In-memory channels (no Redis required)
- JWT authentication

## Quick Installation

### Requirements
- Python 3.11+
- PostgreSQL (optional - can use SQLite)

### Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd chatapp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your settings

# Initialize database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Access at: http://localhost:8000

## Configuration Options

### SQLite (Development)
In `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### PostgreSQL (Production)
In `.env`:
```
DB_NAME=chatapp
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Deployment

### Local Server

```bash
# Install production server
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Raspberry Pi Deployment

#### 1. Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx
```

#### 2. Setup PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE chatapp;
CREATE USER chatapp_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE chatapp TO chatapp_user;
\q
```

#### 3. Deploy Application
```bash
# Clone and setup
cd /home/pi
git clone <your-repo>
cd chatapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Edit settings

# Setup database
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 4. Create Systemd Service
Create `/etc/systemd/system/chatapp.service`:
```ini
[Unit]
Description=ChatApp
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/chatapp
Environment="PATH=/home/pi/chatapp/venv/bin"
ExecStart=/home/pi/chatapp/venv/bin/gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

#### 5. Configure Nginx
Create `/etc/nginx/sites-available/chatapp`:
```nginx
server {
    listen 80;
    server_name your_pi_ip;
    
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static/ {
        alias /home/pi/chatapp/staticfiles/;
    }

    location /media/ {
        alias /home/pi/chatapp/media/;
    }
}
```

#### 6. Start Services
```bash
# Enable and start
sudo systemctl enable chatapp
sudo systemctl start chatapp

# Enable Nginx
sudo ln -s /etc/nginx/sites-available/chatapp /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Check status
sudo systemctl status chatapp
```

Access via: `http://your_raspberry_pi_ip`

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Initialize
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## API Usage

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"pass123","password2":"pass123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
```

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/<room_id>/');

// Send message
ws.send(JSON.stringify({
  action: 'send_message',
  message_type: 'text',
  content: 'Hello!'
}));
```

## Admin Panel

Access at: http://localhost:8000/admin

## Notification Settings

Users can enable/disable notifications at: `/accounts/notifications/settings/`

## Troubleshooting

**Port already in use:**
```bash
sudo lsof -ti:8000 | xargs kill -9
```

**Permission denied (Pi):**
```bash
sudo chown -R pi:pi /home/pi/chatapp
```

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
```

## License

MIT License

## Support

For issues, check logs:
```bash
# Development
python manage.py runserver --verbosity 3

# Production (Pi)
sudo journalctl -u chatapp -f
```
