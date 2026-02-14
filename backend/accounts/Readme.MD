# CareNova Accounts API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [API Endpoints](#api-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [User Profile Endpoints](#user-profile-endpoints)
  - [Password Management](#password-management)
- [Error Handling](#error-handling)
- [User Types](#user-types)

---

## Overview

The CareNova Accounts API provides user authentication, registration, and profile management functionality for a healthcare management system. It supports multiple user types including patients, doctors, lab technicians, and administrators.

## Authentication

This API uses JWT (JSON Web Token) authentication. After logging in, you'll receive:
- **Access Token**: Used for authenticating API requests (expires in 60 minutes)
- **Refresh Token**: Used to obtain new access tokens (expires in 7 days)

### Using Authentication

Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Base URL

```
http://127.0.0.1:8000/api/auth/
```

For production, replace with your actual domain.

---

## API Endpoints

### Authentication Endpoints

#### 1. User Registration

**Endpoint:** `POST /register/`

**Description:** Register a new user account. An OTP will be sent to the provided email for verification.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "user_type": "patient",
  "date_of_birth": "1990-05-15",
  "address": "123 Main Street, City, State"
}
```

**Required Fields:**
- `email` (string): Valid email address
- `password` (string): Minimum 8 characters
- `password_confirm` (string): Must match password
- `user_type` (string): One of: `patient`, `doctor`, `nurse`, `admin`, `staff`

**Optional Fields:**
- `first_name` (string)
- `last_name` (string)
- `phone_number` (string): Format: +1234567890
- `date_of_birth` (date): Format: YYYY-MM-DD
- `address` (string)

**Success Response (201 Created):**
```json
{
  "message": "Registration successful. Please check your email for OTP verification.",
  "user": {
    "email": "john.doe@example.com",
    "user_type": "patient"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "email": ["A user with this email already exists."],
  "password_confirm": ["Password fields didn't match."]
}
```

---

#### 2. Verify OTP

**Endpoint:** `POST /verify-otp/`

**Description:** Verify email address using the OTP code sent during registration.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "otp_code": "123456"
}
```

**Required Fields:**
- `email` (string): Email address
- `otp_code` (string): 6-digit numeric code

**Success Response (200 OK):**
```json
{
  "message": "Email verified successfully.",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "email": "john.doe@example.com",
    "user_type": "patient",
    "is_verified": true
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid or expired OTP."
}
```

---

#### 3. Resend OTP

**Endpoint:** `POST /resend-otp/`

**Description:** Request a new OTP code if the previous one expired or was not received.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "john.doe@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "message": "OTP sent successfully. Please check your email."
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "User not found."
}
```

---

#### 4. Login

**Endpoint:** `POST /login/`

**Description:** Authenticate user and receive JWT tokens.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Login successful",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "patient",
    "is_verified": true
  }
}
```

**Error Responses:**

*Email not verified (400 Bad Request):*
```json
{
  "non_field_errors": ["Email not verified. Please verify your email before logging in."]
}
```

*Invalid credentials (400 Bad Request):*
```json
{
  "non_field_errors": ["Invalid email or password."]
}
```

*Account disabled (400 Bad Request):*
```json
{
  "non_field_errors": ["User account is disabled."]
}
```

---

#### 5. Logout

**Endpoint:** `POST /logout/`

**Description:** Logout user by blacklisting the refresh token.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid token or token already blacklisted"
}
```

---

#### 6. Refresh Token

**Endpoint:** `POST /token/refresh/`

**Description:** Get a new access token using the refresh token.

**Authentication:** Not required

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### User Profile Endpoints

#### 7. Get Current User Profile

**Endpoint:** `GET /me/`

**Description:** Retrieve complete profile information for the authenticated user, including role-specific data.

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-05-15",
  "age": 35,
  "address": "123 Main Street",
  "profile_picture": null,
  "user_type": "patient",
  "is_verified": true,
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z",
  "last_login": "2024-02-14T08:15:00Z",
  "user_profile": {
    "blood_group": "",
    "emergency_contact_name": "",
    "emergency_contact_phone": "",
    "emergency_contact_relationship": "",
    "bio": "",
    "notifications_enabled": true,
    "sms_notifications_enabled": false
  },
  "patient_profile": {
    "blood_group": "A+",
    "allergies": "Peanuts",
    "chronic_conditions": "",
    "current_medications": "None",
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_phone": "+1234567891",
    "emergency_contact_relationship": "Spouse",
    "insurance_provider": "Blue Cross",
    "insurance_policy_number": "BC123456"
  },
  "doctor_profile": null,
  "lab_technician_profile": null,
  "admin_profile": null
}
```

---

#### 8. Update Basic User Information

**Endpoint:** `PATCH /update/` or `PUT /update/`

**Description:** Update basic user information (name, phone, address, etc.).

**Authentication:** Required (Bearer Token)

**Request Body (all fields optional):**
```json
{
  "first_name": "Jonathan",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-05-15",
  "address": "456 New Street, City, State",
  "profile_picture": null
}
```

**Success Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "first_name": "Jonathan",
    "last_name": "Doe",
    "full_name": "Jonathan Doe",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-05-15",
    "age": 35,
    "address": "456 New Street, City, State",
    "profile_picture": null,
    "user_type": "patient",
    "is_active": true,
    "is_verified": true,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-02-14T08:15:00Z"
  }
}
```

---

#### 9. Update General User Profile

**Endpoint:** `PATCH /profile/update/` or `PUT /profile/update/`

**Description:** Update general profile settings (bio, notifications, etc.).

**Authentication:** Required (Bearer Token)

**Request Body (all fields optional):**
```json
{
  "bio": "Experienced healthcare professional",
  "notifications_enabled": true,
  "sms_notifications_enabled": false
}
```

**Success Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "profile": {
    "blood_group": "",
    "emergency_contact_name": "",
    "emergency_contact_phone": "",
    "emergency_contact_relationship": "",
    "license_number": null,
    "specialization": "",
    "department": "",
    "years_of_experience": null,
    "bio": "Experienced healthcare professional",
    "notifications_enabled": true,
    "sms_notifications_enabled": false
  }
}
```

---

#### 10. Update Patient Profile

**Endpoint:** `PATCH /profile/patient/update/` or `PUT /profile/patient/update/`

**Description:** Update patient-specific profile information.

**Authentication:** Required (Bearer Token)

**User Type:** Only `patient` users can access this endpoint

**Request Body (all fields optional):**
```json
{
  "blood_group": "A+",
  "allergies": "Peanuts, Penicillin",
  "chronic_conditions": "Diabetes Type 2",
  "current_medications": "Metformin 500mg",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1234567891",
  "emergency_contact_relationship": "Spouse",
  "insurance_provider": "Blue Cross Blue Shield",
  "insurance_policy_number": "BC123456789"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Patient profile updated successfully",
  "profile": {
    "blood_group": "A+",
    "allergies": "Peanuts, Penicillin",
    "chronic_conditions": "Diabetes Type 2",
    "current_medications": "Metformin 500mg",
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_phone": "+1234567891",
    "emergency_contact_relationship": "Spouse",
    "insurance_provider": "Blue Cross Blue Shield",
    "insurance_policy_number": "BC123456789"
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "Only patients can update patient profile"
}
```

---

#### 11. Update Doctor Profile

**Endpoint:** `PATCH /profile/doctor/update/` or `PUT /profile/doctor/update/`

**Description:** Update doctor-specific profile information.

**Authentication:** Required (Bearer Token)

**User Type:** Only `doctor` users can access this endpoint

**Request Body (all fields optional):**
```json
{
  "license_number": "MD123456",
  "specialization": "Cardiology",
  "sub_specialization": "Interventional Cardiology",
  "years_of_experience": 10,
  "medical_school": "Harvard Medical School",
  "graduation_year": 2014,
  "certifications": "Board Certified in Cardiology, ACLS, BLS",
  "department": "Cardiology Department",
  "consultation_fee": "200.00",
  "available_for_consultation": true,
  "bio": "Experienced cardiologist specializing in interventional procedures",
  "languages_spoken": "English, Spanish, French"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Doctor profile updated successfully",
  "profile": {
    "license_number": "MD123456",
    "specialization": "Cardiology",
    "sub_specialization": "Interventional Cardiology",
    "years_of_experience": 10,
    "medical_school": "Harvard Medical School",
    "graduation_year": 2014,
    "certifications": "Board Certified in Cardiology, ACLS, BLS",
    "department": "Cardiology Department",
    "consultation_fee": "200.00",
    "available_for_consultation": true,
    "bio": "Experienced cardiologist specializing in interventional procedures",
    "languages_spoken": "English, Spanish, French"
  }
}
```

---

#### 12. Update Lab Technician Profile

**Endpoint:** `PATCH /profile/lab-technician/update/` or `PUT /profile/lab-technician/update/`

**Description:** Update lab technician-specific profile information.

**Authentication:** Required (Bearer Token)

**User Type:** Only `staff` users can access this endpoint

**Request Body (all fields optional):**
```json
{
  "license_number": "LT789012",
  "certifications": "Clinical Laboratory Scientist (CLS)",
  "specialization": "Hematology",
  "years_of_experience": 5,
  "department": "Laboratory",
  "shift_timing": "Morning Shift (7AM - 3PM)"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Lab technician profile updated successfully",
  "profile": {
    "license_number": "LT789012",
    "certifications": "Clinical Laboratory Scientist (CLS)",
    "specialization": "Hematology",
    "years_of_experience": 5,
    "department": "Laboratory",
    "shift_timing": "Morning Shift (7AM - 3PM)"
  }
}
```

---

#### 13. Update Admin Profile

**Endpoint:** `PATCH /profile/admin/update/` or `PUT /profile/admin/update/`

**Description:** Update admin-specific profile information.

**Authentication:** Required (Bearer Token)

**User Type:** Only `admin` users can access this endpoint

**Request Body (all fields optional):**
```json
{
  "employee_id": "EMP001",
  "department": "Administration",
  "designation": "Senior Administrator",
  "can_manage_users": true,
  "can_manage_appointments": true,
  "can_manage_billing": true,
  "can_view_reports": true
}
```

**Success Response (200 OK):**
```json
{
  "message": "Admin profile updated successfully",
  "profile": {
    "employee_id": "EMP001",
    "department": "Administration",
    "designation": "Senior Administrator",
    "can_manage_users": true,
    "can_manage_appointments": true,
    "can_manage_billing": true,
    "can_view_reports": true
  }
}
```

---

### Password Management

#### 14. Change Password

**Endpoint:** `POST /change-password/`

**Description:** Change password for authenticated user (requires old password).

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "old_password": "OldSecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "old_password": ["Old password is incorrect."],
  "new_password_confirm": ["Password fields didn't match."]
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

### Error Response Format

All error responses follow this format:

```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"],
  "non_field_errors": ["General error message"]
}
```

### Common Errors

**Invalid Token (401):**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

**Permission Denied (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Validation Error (400):**
```json
{
  "email": ["This field is required."],
  "password": ["This field is required."]
}
```

---

## User Types

The system supports the following user types:

| User Type | Value | Description |
|-----------|-------|-------------|
| Patient | `patient` | Regular patients seeking healthcare services |
| Doctor | `doctor` | Medical practitioners providing consultations |
| Nurse | `nurse` | Nursing staff |
| Lab Technician | `staff` | Laboratory technicians |
| Administrator | `admin` | System administrators |

Each user type has access to specific profile endpoints and features.

---

## Example Workflow

### Complete Registration Flow

1. **Register a new user:**
```bash
POST /api/auth/register/
{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "user_type": "patient"
}
```

2. **Check email and get OTP code (e.g., 123456)**

3. **Verify OTP:**
```bash
POST /api/auth/verify-otp/
{
  "email": "john@example.com",
  "otp_code": "123456"
}
```

4. **Receive JWT tokens and use them for authenticated requests**

### Complete Login Flow

1. **Login:**
```bash
POST /api/auth/login/
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

2. **Use access token for authenticated requests:**
```bash
GET /api/auth/me/
Authorization: Bearer <access_token>
```

3. **When access token expires, refresh it:**
```bash
POST /api/auth/token/refresh/
{
  "refresh": "<refresh_token>"
}
```

4. **Logout when done:**
```bash
POST /api/auth/logout/
Authorization: Bearer <access_token>
{
  "refresh": "<refresh_token>"
}
```

---

## Postman Collection

You can import the following collection into Postman for easy testing:

### Environment Variables
```
base_url: http://127.0.0.1:8000
access_token: (will be set automatically after login)
refresh_token: (will be set automatically after login)
```

### Pre-request Script for Authenticated Endpoints
```javascript
pm.request.headers.add({
    key: 'Authorization',
    value: 'Bearer ' + pm.environment.get('access_token')
});
```

---

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider implementing rate limiting to prevent abuse.

---

## Security Considerations

1. **HTTPS Only**: Always use HTTPS in production
2. **Token Storage**: Store tokens securely (never in localStorage for sensitive apps)
3. **Token Expiration**: Access tokens expire in 60 minutes
4. **Password Requirements**: Minimum 8 characters with validation
5. **Email Verification**: Required before login

---

## Support

For issues or questions, please contact the CareNova development team or create an issue in the project repository.

---

**Last Updated:** February 14, 2026  
**API Version:** 1.0.0