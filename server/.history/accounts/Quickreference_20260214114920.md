# CareNova API - Quick Reference Guide

## Authentication Headers

```bash
# For authenticated requests
Authorization: Bearer <access_token>
```

## Quick Endpoint Reference

### Public Endpoints (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/verify-otp/` | Verify email with OTP |
| POST | `/api/auth/resend-otp/` | Resend OTP code |
| POST | `/api/auth/login/` | User login |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Protected Endpoints (Auth Required)

| Method | Endpoint | Description | User Type |
|--------|----------|-------------|-----------|
| POST | `/api/auth/logout/` | User logout | All |
| GET | `/api/auth/me/` | Get current user profile | All |
| PATCH/PUT | `/api/auth/update/` | Update basic user info | All |
| PATCH/PUT | `/api/auth/profile/update/` | Update general profile | All |
| PATCH/PUT | `/api/auth/profile/patient/update/` | Update patient profile | Patient only |
| PATCH/PUT | `/api/auth/profile/doctor/update/` | Update doctor profile | Doctor only |
| PATCH/PUT | `/api/auth/profile/lab-technician/update/` | Update lab tech profile | Staff only |
| PATCH/PUT | `/api/auth/profile/admin/update/` | Update admin profile | Admin only |
| POST | `/api/auth/change-password/` | Change password | All |

## Common Request Examples

### 1. Register
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "user_type": "patient"
  }'
```

### 2. Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Get Profile
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Update Profile
```bash
curl -X PATCH http://127.0.0.1:8000/api/auth/update/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 5. Logout
```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## User Types

- `patient` - Patients
- `doctor` - Doctors
- `nurse` - Nurses
- `staff` - Lab Technicians
- `admin` - Administrators

## Token Expiration

- **Access Token**: 60 minutes
- **Refresh Token**: 7 days

## Response Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Server Error