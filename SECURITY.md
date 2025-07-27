# Security Configuration Guide

## Overview
This document provides comprehensive security guidelines for deploying and maintaining the Horizon Exam Bot application safely.

## Critical Security Configurations

### 1. Secret Key Management
**CRITICAL**: Never use the default secret key in production!

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set as environment variable
export SECRET_KEY="your-generated-secret-key-here"
```

### 2. Environment Variables
Create a `.env` file (never commit this to version control):

```env
# Production Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SECRET_KEY=your-secure-generated-secret-key

# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
```

### 3. Production Deployment

#### Using Gunicorn (Recommended)
```bash
# Install gunicorn
pip install gunicorn

# Run with security settings
gunicorn --bind 127.0.0.1:5000 --workers 4 --access-logfile - --error-logfile - app:app
```

#### Environment Setup
```bash
# Disable debug mode
export FLASK_DEBUG=False
export FLASK_ENV=production

# Set secure host binding
export FLASK_HOST=127.0.0.1

# Set secure secret key
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Enable secure cookies (for HTTPS)
export SESSION_COOKIE_SECURE=True
```

### 4. Web Server Configuration

#### Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers (additional to app headers)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Robots-Tag "noindex, nofollow" always;
    
    # File Upload Limits
    client_max_body_size 20M;
    
    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. File System Security

#### Directory Permissions
```bash
# Secure application directory
chmod 755 /path/to/horizon-exam-bot
chmod 644 /path/to/horizon-exam-bot/*.py

# Secure data directories
chmod 700 data/
chmod 700 uploads/

# Secure environment file
chmod 600 .env
```

#### File Upload Security
- Maximum file size: 16MB (configurable)
- Allowed file types: PDF, DOCX only
- Files are deleted after processing
- Secure filename handling with `werkzeug.utils.secure_filename`

### 6. Database Security (Future Implementation)
When implementing database storage:

```python
# Use environment variables for database credentials
DATABASE_URL = os.environ.get('DATABASE_URL')

# Use connection pooling and prepared statements
# Implement proper user authentication and authorization
# Use database-level encryption for sensitive data
```

### 7. Monitoring and Logging

#### Enable Security Logging
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure security logging
security_logger = logging.getLogger('security')
handler = RotatingFileHandler('logs/security.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s'
))
security_logger.addHandler(handler)
security_logger.setLevel(logging.INFO)
```

#### Monitor for Security Events
- Failed file uploads
- Invalid quiz submissions
- Unusual access patterns
- Error rates and exceptions

### 8. Dependency Security

#### Regular Security Updates
```bash
# Install safety for vulnerability scanning
pip install safety

# Check for known vulnerabilities
safety check

# Update dependencies regularly
pip list --outdated
pip install --upgrade package-name
```

#### Pin Dependency Versions
```txt
# requirements.txt with pinned versions
Flask==2.3.3
PyPDF2==3.0.1
python-docx==0.8.11
Werkzeug==2.3.7
```

### 9. Input Validation and Sanitization

The application includes:
- JSON input validation
- HTML escaping for user content
- File type and size validation
- Quiz content length limits
- UUID validation for IDs

### 10. Security Headers

The application automatically adds these security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'; ...`

## Security Checklist

### Before Production Deployment
- [ ] Generate and set a secure SECRET_KEY
- [ ] Set FLASK_DEBUG=False
- [ ] Set FLASK_ENV=production
- [ ] Configure secure host binding (127.0.0.1)
- [ ] Enable HTTPS and set SESSION_COOKIE_SECURE=True
- [ ] Set up proper file permissions
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up SSL/TLS certificates
- [ ] Configure security logging
- [ ] Run security scan: `python security_check.py`
- [ ] Test file upload functionality
- [ ] Test quiz creation and submission
- [ ] Verify security headers in browser

### Regular Maintenance
- [ ] Update dependencies monthly
- [ ] Run security scans weekly
- [ ] Monitor security logs daily
- [ ] Review file upload directory size
- [ ] Check for unusual access patterns
- [ ] Backup quiz data regularly

## Emergency Response

### If Security Breach Suspected
1. Immediately disable the application
2. Check security logs for intrusion attempts
3. Review uploaded files for malicious content
4. Change all secrets and keys
5. Update all dependencies
6. Audit code changes
7. Re-deploy with enhanced security

### Incident Reporting
- Document the incident details
- Identify the attack vector
- Implement additional security measures
- Update security procedures

## Security Tools Integration

### Automated Security Scanning
```bash
# Run comprehensive security check
python security_check.py

# Check dependencies
safety check

# Static code analysis (optional)
pip install bandit
bandit -r . -f json -o security_report.json
```

### Continuous Security Monitoring
Consider integrating:
- SIEM tools for log analysis
- Automated vulnerability scanning
- Real-time security monitoring
- Backup and disaster recovery plans

## Contact Information

For security issues or questions:
- Create a security issue on GitHub (private repository)
- Email: security@your-domain.com
- Follow responsible disclosure practices

---

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures.