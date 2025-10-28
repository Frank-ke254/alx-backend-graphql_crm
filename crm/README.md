# CRM Celery Setup Guide

This guide explains how to set up and run the Celery-based background task system that generates weekly CRM reports.

---

## 1. Install Redis and Dependencies

Make sure Redis is installed and running locally.

### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
