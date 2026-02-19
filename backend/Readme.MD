# CareNova Health — Backend API

> A modular, production-ready backend for a hospital management and telemedicine platform — connecting patients with doctors, managing appointments, delivering health news, and enabling real-time secure chat.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Authentication Flow](#authentication-flow)
- [Appointment System](#appointment-system)
- [Chat System](#chat-system)
- [News Module](#news-module)
- [Running Tests](#running-tests)
- [Contributing](#contributing)

---

## Overview

CareNova is a healthcare API built for clinics and telemedicine services. It handles the full patient–doctor lifecycle: account registration and OTP verification, appointment booking (including emergency escalation), doctor availability management, clinical note submission, real-time private and group chat, and a health news feed with likes, comments, and social sharing.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5 + Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| API Docs | drf-spectacular (Swagger UI + ReDoc) |
| Real-time | Django Channels + WebSockets |
| Database | PostgreSQL (production) / SQLite (development) |
| Email | SMTP via Gmail |
| Push Notifications | Firebase Cloud Messaging (FCM) |
| Filtering | django-filter |
| CORS | django-cors-headers |

---

## Project Structure

```
backend/
├── core/               # Project settings, root URLs, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   └── pagination.py
├── users/              # Auth, profiles, doctor discovery
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   └── notifications.py
├── appointments/       # Appointments, availability, reviews, patient history
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── chat/               # Private messaging, group chat, presence, moderation
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── news/               # Health news articles, paragraphs, likes, comments
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── manage.py
├── requirements.txt
└── .env                # Never commit this file
```

---

## Core Features

### Authentication & Account Management
- Two-step registration: account created as `is_active=False`, activated via 6-digit OTP sent to email
- OTP resend with a **60-second rate limit** to prevent abuse
- JWT-based login returning access + refresh tokens
- Logout via refresh token blacklisting
- Account deactivation (reversible by admin) and permanent deletion

### Appointment System
- Patients book appointments against doctor availability slots
- Emergency appointments bypass slot availability checks and trigger immediate doctor alerts
- Recurring appointments: book a full series in one request, cancel the entire series atomically
- Doctors can reschedule, complete (with clinical notes), or change status
- Patients can cancel with reason; emergency cancellations flag the doctor account
- Admin traffic monitor endpoint surfaces unattended emergencies and rerouted cases

### Doctor Availability
- Doctors publish individual or bulk availability slots
- Slots are atomically locked on booking using `select_for_update`
- Cancelled recurring series releases all booked slots back to availability

### Reviews & Patient History
- Patients can review completed appointments
- Patient history endpoint returns paginated completed appointment records with clinical notes

### Real-time Chat
- **Private messaging**: inbox view, conversation history, message send with attachment support
- **Group chat**: admin-created support groups, join/leave, message history
- **Presence**: users set ONLINE / AWAY / OFFLINE status
- **Moderation**: doctors and admins can block patients; blocked users cannot send messages
- **Complaints**: doctors file formal complaints against patients; admins triage and resolve

### Health News
- Multi-paragraph articles with per-section subheadings and images
- Top news pinning, tag-based filtering
- Like toggle (one per user), threaded comments (one level of replies)
- Social share link generation for Facebook, Twitter/X, WhatsApp, Telegram, LinkedIn, Reddit

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- (Optional) PostgreSQL for production

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/carenova-backend.git
cd carenova-backend/backend
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

> **Important:** Always ensure `(venv)` is showing in your terminal prompt before running any `pip` commands.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the `backend/` directory (see [Environment Variables](#environment-variables) below).

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional, for admin panel access)

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## Environment Variables

Create a `.env` file in the `backend/` directory with the following keys. **Do not use quotes or spaces around the `=` sign.**

```env
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_gmail_address@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_gmail_app_password
DEFAULT_FROM_EMAIL=CareNova <your_gmail_address@gmail.com>
```

> **Gmail App Password:** Go to your Google account → Security → 2-Step Verification → App Passwords. Generate a 16-character password specifically for this app. Never use your main Gmail password here.

> **Secret Key:** Generate a strong key with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`.

---

## API Reference

Once the server is running, the full interactive API documentation is available at:

| Interface | URL |
|---|---|
| Swagger UI | `http://127.0.0.1:8000/api/schema/swagger-ui/` |
| ReDoc | `http://127.0.0.1:8000/api/schema/redoc/` |
| Raw OpenAPI Schema | `http://127.0.0.1:8000/api/schema/` |

### Base URL

All endpoints are prefixed with `/api/v1/`.

### Endpoint Groups

| Tag | Prefix | Description |
|---|---|---|
| Authentication | `/api/v1/users/` | Register, verify OTP, login, logout |
| Account Management | `/api/v1/users/me/` | Profile, deactivate, delete |
| Doctors | `/api/v1/users/doctors/` | Browse and search verified doctors |
| Admin | `/api/v1/users/members/` | Admin user management |
| Appointments | `/api/v1/appointments/appointment/` | Full appointment lifecycle |
| Availability | `/api/v1/appointments/availability/` | Slot management |
| Agenda | `/api/v1/appointments/agenda/` | Doctor's daily schedule |
| Reviews | `/api/v1/appointments/reviews/` | Patient reviews |
| Patient History | `/api/v1/appointments/history/` | Completed appointment records |
| Chat — Private | `/api/v1/chat/private/` | One-on-one messaging |
| Chat — Groups | `/api/v1/chat/groups/` | Support group chat |
| Chat — Presence | `/api/v1/chat/presence/` | Online status |
| Chat — Moderation | `/api/v1/chat/moderation/` | Blocking and complaints |
| News | `/api/v1/news/` | Articles, likes, comments, sharing |

### Authentication Header

All protected endpoints require a Bearer token:

```
Authorization: Bearer <access_token>
```

---

## Authentication Flow

```
POST /api/v1/users/register/
  → Account created (is_active=False)
  → OTP sent to email

POST /api/v1/users/verify-otp/
  → Account activated (is_active=True)

POST /api/v1/users/login/
  → Returns { access, refresh }

POST /api/v1/users/logout/      ← body: { "refresh": "<token>" }
  → Refresh token blacklisted

POST /api/v1/users/me/deactivate/   ← reversible
POST /api/v1/users/me/delete/       ← permanent
```

---

## Appointment System

### Booking Flow

```
GET  /api/v1/appointments/availability/?doctor=<id>
  → Patient finds an open slot

POST /api/v1/appointments/appointment/
  → Slot is atomically locked; confirmation email sent to patient
  → If is_emergency=True, high-priority alert sent to doctor

POST /api/v1/appointments/appointment/<id>/complete/
  → Doctor submits clinical_note + prescriptions
  → Status set to COMPLETED; patient can now leave a review

POST /api/v1/appointments/reviews/
  → Patient submits rating + comment
```

### Recurring Appointments

```
POST /api/v1/appointments/appointment/book-recurrent/
  → Creates full series; all slots marked booked
  → Returns recurrence_group_id

POST /api/v1/appointments/appointment/<id>/cancel-series/
  → All future PENDING/CONFIRMED appointments in the group cancelled
  → All corresponding availability slots released
```

---

## Chat System

### Private Messaging

```
GET  /api/v1/chat/private/                        → Inbox (recent messages)
GET  /api/v1/chat/private/history/<user_id>/      → Full conversation
POST /api/v1/chat/private/send/                   → Send message (+ optional attachment)
```

### Moderation

```
POST /api/v1/chat/moderation/blocked/block/       → Doctor/admin blocks a patient
POST /api/v1/chat/moderation/blocked/unblock/     → Remove block
POST /api/v1/chat/moderation/complaints/file/     → Doctor files complaint
PATCH /api/v1/chat/moderation/complaints/<id>/resolve/  → Admin resolves complaint
```

### Presence

```
POST /api/v1/chat/presence/set-status/   → Body: { "status": "ONLINE" | "AWAY" | "OFFLINE" }
GET  /api/v1/chat/presence/<user_id>/    → Check another user's status
```

---

## News Module

```
GET  /api/v1/news/                          → All articles (filter: ?tag=Cardiology)
GET  /api/v1/news/<id>/                     → Full article with paragraphs
POST /api/v1/news/                          → Create article (admin/doctor only)
POST /api/v1/news/<id>/paragraphs/          → Add a paragraph block
POST /api/v1/news/<id>/like/                → Toggle like
GET  /api/v1/news/<id>/comments/            → List comments + replies
POST /api/v1/news/<id>/comments/add/        → Post a comment or reply
GET  /api/v1/news/<id>/share/?base_url=...  → Get social share links
```

---

## Running Tests

```bash
python manage.py test
```

For coverage:

```bash
pip install coverage
coverage run manage.py test
coverage report
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: description of change"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request against `main`

Please ensure all endpoints include `@extend_schema` documentation and that migrations are included with any model changes.

---

> Built with Django REST Framework · Documented with drf-spectacular · Ready for production on PostgreSQL