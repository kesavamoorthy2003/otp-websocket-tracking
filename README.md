# Backend OTP & Real-Time Driver Tracking Service

This project implements a secure OTP-based authentication system and a real-time driver location tracking service.

## 📌 Project Overview
- **Task 1**: OTP Login system using Django REST Framework, PostgreSQL, and JWT.
- **Task 2**: Live location tracking using Django Channels (WebSockets) and Redis.

## 🛠️ Tech Stack
- **Framework**: Django 6.0, Django REST Framework
- **Database**: PostgreSQL
- **Real-time**: Django Channels & Redis
- **Auth**: JWT (SimpleJWT)
- **Security**: OTP Hashing (Bcrypt)

---

## ⚙️ Setup Instructions

### 1. Install Dependencies
Make sure you have a virtual environment active, then run:
```bash
pip install django djangorestframework djangorestframework-simplejwt django-channels channels-redis psycopg2-binary django-cors-headers python-dotenv
