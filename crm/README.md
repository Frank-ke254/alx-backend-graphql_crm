# CRM Celery Report Setup

## Requirements
- Redis installed and running on localhost:6379
- Dependencies installed:
  ```bash
  pip install -r requirements.txt
  ```
# CRM Celery Setup Guide

## Setup Steps

### 1. Install Redis and Dependencies
Install Redis and the necessary dependencies.

```bash
sudo apt install redis-server
sudo systemctl start redis-server
```
### 2. Run migrations
```bash
python manage.py migrate
```
### 3. Start celery worker
```bash
celery -A crm worker -l info
```
### 4. Start celery beat
```bash
celery -A crm beat -l info
```
### 5. Verify logs
```bash
cat /tmp/crm_report_log.txt
```
