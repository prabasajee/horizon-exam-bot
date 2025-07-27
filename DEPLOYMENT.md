# 🚀 Deployment Guide for Horizon Exam Bot

This guide covers multiple deployment options for the Horizon Exam Bot application.

## 📋 Prerequisites

- Python 3.11 or higher
- Git
- Docker (for containerized deployments)

## 🐳 Docker Deployment (Recommended)

### Local Development with Docker

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Visit `http://localhost:5000`

3. **For production with Nginx:**
   ```bash
   docker-compose --profile production up --build
   ```
   - Visit `http://localhost` (port 80)

### Manual Docker Build

1. **Build the image:**
   ```bash
   docker build -t horizon-exam-bot .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 \
     -e SECRET_KEY=your-secret-key \
     -e FLASK_ENV=production \
     -v $(pwd)/data:/app/data \
     horizon-exam-bot
   ```

## ☁️ Cloud Platform Deployments

### 🚂 Railway Deployment

1. **Connect your GitHub repository to Railway**
2. **Railway will automatically detect and use the `railway.toml` configuration**
3. **Set environment variables in Railway dashboard:**
   ```
   SECRET_KEY=your-super-secret-key
   FLASK_ENV=production
   ```
4. **Deploy with a single click!**

### 🟣 Heroku Deployment

1. **Install Heroku CLI and login:**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app:**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-super-secret-key
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

5. **Open your app:**
   ```bash
   heroku open
   ```

### 🎨 Render Deployment

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Use these settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app`
   - **Environment:** `production`
4. **Set environment variables:**
   ```
   SECRET_KEY=your-super-secret-key
   FLASK_ENV=production
   PYTHONUNBUFFERED=1
   ```

### 🌊 DigitalOcean App Platform

1. **Connect your GitHub repository**
2. **DigitalOcean will auto-detect the Python app**
3. **Set environment variables:**
   ```
   SECRET_KEY=your-super-secret-key
   FLASK_ENV=production
   ```
4. **Deploy!**

## 🏠 VPS/Server Deployment

### Manual Server Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/horizon-exam-bot.git
   cd horizon-exam-bot
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export SECRET_KEY=your-super-secret-key
   export FLASK_ENV=production
   export PORT=5000
   ```

5. **Run with Gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
   ```

### Using Systemd (Ubuntu/Debian)

1. **Create a systemd service file:**
   ```bash
   sudo nano /etc/systemd/system/horizon-exam-bot.service
   ```

2. **Add this configuration:**
   ```ini
   [Unit]
   Description=Horizon Exam Bot
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/horizon-exam-bot
   Environment=PATH=/path/to/horizon-exam-bot/venv/bin
   Environment=SECRET_KEY=your-super-secret-key
   Environment=FLASK_ENV=production
   ExecStart=/path/to/horizon-exam-bot/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable horizon-exam-bot
   sudo systemctl start horizon-exam-bot
   ```

## 🔒 Production Security Configuration

### Environment Variables

Set these environment variables in production:

```bash
SECRET_KEY=your-very-secure-random-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
MAX_CONTENT_LENGTH=16777216
```

### Generate a Secure Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

## 🌐 Domain and SSL Setup

### Using Nginx as Reverse Proxy

1. **Install Nginx:**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Create Nginx configuration:**
   ```bash
   sudo nano /etc/nginx/sites-available/horizon-exam-bot
   ```

3. **Add this configuration:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       client_max_body_size 20M;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Enable the site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/horizon-exam-bot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring and Maintenance

### Health Checks

The application includes health check endpoints:
- `GET /` - Basic application check

### Logs

- **Docker:** `docker logs container-name`
- **Systemd:** `sudo journalctl -u horizon-exam-bot -f`
- **Application logs:** Check your platform's logging system

### Backup

Important directories to backup:
- `data/` - Contains all quiz files
- Environment variables/configuration

## 🔧 Troubleshooting

### Common Issues

1. **File upload errors:**
   - Check `MAX_CONTENT_LENGTH` setting
   - Ensure `uploads/` directory is writable

2. **Memory issues:**
   - Reduce number of Gunicorn workers
   - Increase server memory

3. **Timeout errors:**
   - Increase Gunicorn timeout settings
   - Check large file processing

### Debug Mode

For debugging in production (not recommended):
```bash
FLASK_DEBUG=True FLASK_ENV=development python app.py
```

## 📈 Scaling Considerations

### Database Migration

For high traffic, consider migrating from JSON file storage to:
- PostgreSQL
- MongoDB
- Redis for sessions

### Load Balancing

Use multiple instances behind a load balancer:
- Nginx
- HAProxy
- Cloud load balancers

### CDN and Static Files

Serve static files through a CDN for better performance.

---

## 🎯 Quick Deploy Commands

**Railway:** Connect repo → Deploy
**Heroku:** `git push heroku main`
**Docker:** `docker-compose up --build`
**Local:** `python run.py`

Choose the deployment method that best fits your needs! 🚀