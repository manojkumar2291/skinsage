# Backend Test Scenarios (Manual & Automated)

This document outlines high-level test scenarios for the SkinSage Backend API. The backend is built using FastAPI and interacts with a MySQL database.

## 1. Authentication & Authorization (`/api/auth`)

### 1.1 User Registration
*   **Scenario:** Successful user registration with valid data.
    *   **Action:** POST `/api/auth/register` with valid `email`, `password`, `full_name`, etc.
    *   **Expected (Manual/Auto):** HTTP 200/201. User is created in the database. Password should be hashed.
*   **Scenario:** Duplicate email registration.
    *   **Action:** POST `/api/auth/register` with an email that already exists.
    *   **Expected (Manual/Auto):** HTTP 400 Bad Request. Error message indicating email is already registered.

### 1.2 User Login (Email/Password)
*   **Scenario:** Successful login.
    *   **Action:** POST `/api/auth/login` with valid credentials.
    *   **Expected (Manual/Auto):** HTTP 200. Response contains `access_token` and `refresh_token` (as HTTP-only cookie).
*   **Scenario:** Failed login with incorrect password.
    *   **Action:** POST `/api/auth/login` with valid email but wrong password.
    *   **Expected (Manual/Auto):** HTTP 401/400. Error message for invalid credentials.

### 1.3 OTP Flow (Passwordless / Verification)
*   **Scenario:** Generate OTP successfully.
    *   **Action:** POST `/api/auth/otp/generate` with valid identifier (email/phone).
    *   **Expected (Manual/Auto):** HTTP 200. Background task triggers email/SMS. DB stores OTP code with expiration.
*   **Scenario:** Verify valid OTP.
    *   **Action:** POST `/api/auth/otp/verify` with correct identifier and code.
    *   **Expected (Manual/Auto):** HTTP 200. Access token returned. User is verified in DB.
*   **Scenario:** Verify invalid/expired OTP.
    *   **Action:** POST `/api/auth/otp/verify` with wrong code or expired code.
    *   **Expected (Manual/Auto):** HTTP 400 Bad Request.

### 1.4 Password Reset
*   **Scenario:** Request password reset link.
    *   **Action:** POST `/api/auth/forgot-password` with valid email.
    *   **Expected (Manual/Auto):** HTTP 200. Background task sends email. Token stored in `password_resets` table.
*   **Scenario:** Complete password reset.
    *   **Action:** POST `/api/auth/reset-password` with valid token and new password.
    *   **Expected (Manual/Auto):** HTTP 200. Password updated in DB. Token marked as used.

## 2. AI Analysis (`/api/ai`)
*   **Scenario:** Submit image and symptoms for analysis.
    *   **Action:** POST `/api/ai/analyze` (or equivalent endpoint) with image file and symptom text.
    *   **Expected (Manual/Auto):** HTTP 200. Returns JSON with AI diagnostic probabilities, risk level, and recommendations. (Requires mocking the actual AI service in automated tests).
*   **Scenario:** Submit analysis without required image.
    *   **Action:** POST `/api/ai/analyze` without image payload.
    *   **Expected (Manual/Auto):** HTTP 422 Unprocessable Entity.

## 3. Appointments (`/api/appointment`)
*   **Scenario:** Book an appointment successfully.
    *   **Action:** POST `/api/appointment/book` with valid provider ID, date, time, and patient details.
    *   **Expected (Manual/Auto):** HTTP 200/201. Appointment created with 'pending' status.
*   **Scenario:** Provider accepts an appointment.
    *   **Action:** PUT/POST `/api/appointment/{id}/accept` (Provider Auth required).
    *   **Expected (Manual/Auto):** HTTP 200. Appointment status changes to 'confirmed'.
*   **Scenario:** Get user appointments.
    *   **Action:** GET `/api/appointment/me` (Patient Auth required).
    *   **Expected (Manual/Auto):** HTTP 200. Returns list of appointments belonging to the logged-in user.

## 4. Video Calls (`/api/videocall`)
*   **Scenario:** Generate video call token (Time-gated).
    *   **Action:** GET `/api/videocall/token?appointment_id={id}` 5 minutes before appointment.
    *   **Expected (Manual/Auto):** HTTP 200. Returns Agora token.
*   **Scenario:** Generate video call token too early.
    *   **Action:** GET `/api/videocall/token?appointment_id={id}` 2 hours before appointment.
    *   **Expected (Manual/Auto):** HTTP 403/400. Error indicating it is too early to join.

## 5. Payments (`/api/payment`)
*   **Scenario:** Create payment order.
    *   **Action:** POST `/api/payment/create-order` with amount and appointment/product details.
    *   **Expected (Manual/Auto):** HTTP 200. Returns Razorpay order ID.
*   **Scenario:** Verify successful payment.
    *   **Action:** POST `/api/payment/verify` with Razorpay payment signature.
    *   **Expected (Manual/Auto):** HTTP 200. Payment status updated to 'completed' in DB.

## 6. Rate Limiting and Security
*   **Scenario:** Trigger rate limit.
    *   **Action:** Send > N requests to an endpoint within 1 minute.
    *   **Expected (Auto):** HTTP 429 Too Many Requests.
*   **Scenario:** Access protected route without token.
    *   **Action:** GET `/api/auth/me` without Authorization header.
    *   **Expected (Auto):** HTTP 401 Unauthorized.