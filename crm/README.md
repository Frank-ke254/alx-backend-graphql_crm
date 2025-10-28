# CRM Celery Setup Guide

## Setup Steps

### 1. Install Redis and Dependencies
Install Redis and the necessary dependencies.

```bash
sudo apt install redis-server
sudo systemctl start redis-server
python manage.py migrate
celery -A crm worker -l info
celery -A crm beat -l info
cat /tmp/crm_report_log.txt
