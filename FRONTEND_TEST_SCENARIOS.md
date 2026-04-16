# Frontend Test Scenarios (Manual & Automated)

This document outlines high-level test scenarios for the SkinSage React/Vite Frontend Application.

## 1. Authentication & Onboarding

### 1.1 Login Flow
*   **Scenario:** Successful Email/Password Login.
    *   **Action (Manual):** Navigate to `/login`. Enter valid credentials. Click "Login".
    *   **Expected:** User is redirected to their respective dashboard (Patient, Provider, or Admin) based on their role. JWT is stored in localStorage.
*   **Scenario:** Login Validation Errors.
    *   **Action (Manual):** Leave fields blank or enter invalid email format and click "Login".
    *   **Expected:** UI displays appropriate validation error messages. Form is not submitted.
*   **Scenario:** OTP Login Flow.
    *   **Action (Manual):** Enter phone number/email, request OTP. Enter received OTP.
    *   **Expected:** Successful verification logs the user in and redirects.

### 1.2 Role-Based Access Control (RBAC)
*   **Scenario:** Patient attempting to access Provider Dashboard.
    *   **Action (Manual):** Log in as a Patient. Manually change URL to `/provider/dashboard`.
    *   **Expected:** Application redirects user to an "Unauthorized" page or back to the Patient dashboard.

## 2. AI Analysis Flow (`/ai-analysis`)

### 2.1 Image Upload & Diagnostic Chat
*   **Scenario:** Successful Image Upload.
    *   **Action (Manual):** Navigate to AI Analysis page. Drag and drop a valid skin image (.jpg, .png).
    *   **Expected:** Image preview appears. Upload progress bar shows.
*   **Scenario:** Invalid File Upload.
    *   **Action (Manual):** Attempt to upload a .pdf or a file exceeding the size limit.
    *   **Expected:** Error toast/message appears rejecting the file.
*   **Scenario:** AI Diagnostic Questionnaire.
    *   **Action (Manual):** Upload image, then answer the interactive AI questions (symptoms, duration). Submit.
    *   **Expected:** Loading skeleton appears. Results page renders with predicted conditions, risk level, and "Consult Provider" button.

## 3. Appointments & Provider Dashboard

### 3.1 Booking an Appointment
*   **Scenario:** Complete Booking Flow.
    *   **Action (Manual):** Select a provider -> Pick available date/time -> Confirm details -> Proceed to Payment -> Complete Razorpay mock payment.
    *   **Expected:** Success confirmation page shown. Appointment appears in "Upcoming Appointments" tab.

### 3.2 Provider Appointment Management
*   **Scenario:** Accept Pending Appointment.
    *   **Action (Manual):** Log in as Provider. Go to "Pending" tab. Click "Accept" on an appointment card.
    *   **Expected:** Appointment moves to "Accepted" tab. Status updates in the UI instantly (Optimistic UI update).

## 4. Video Consultation

### 4.1 Joining a Call
*   **Scenario:** Join Call (Time Valid).
    *   **Action (Manual):** View an appointment scheduled to start within 5 minutes.
    *   **Expected:** "Join Call" button is enabled. Clicking it requests camera/mic permissions and connects to the Agora video room.
*   **Scenario:** Join Call (Too Early).
    *   **Action (Manual):** View an appointment scheduled for tomorrow.
    *   **Expected:** "Join Call" button is disabled or shows a countdown timer.

### 4.2 In-Call Controls
*   **Scenario:** Toggle Media.
    *   **Action (Manual):** While in a call, click the Mute Microphone and Turn Off Camera buttons.
    *   **Expected:** Local media streams stop. UI indicators show media is disabled.

## 5. E-commerce / Shop Flow

### 5.1 Cart Management
*   **Scenario:** Add to Cart.
    *   **Action (Manual):** Browse shop, click "Add to Cart" on a product.
    *   **Expected:** Cart icon badge increments. Cart drawer/sidebar opens showing the added item.
*   **Scenario:** Checkout Flow.
    *   **Action (Manual):** Go to Cart -> Checkout -> Enter Shipping Details -> Pay via Razorpay.
    *   **Expected:** Order confirmation page displayed.

## 6. General UI / UX

*   **Scenario:** Responsive Design.
    *   **Action (Manual):** Resize browser window to mobile width (e.g., 375px).
    *   **Expected:** Sidebar collapses into a hamburger menu. Grids (like shop products) stack vertically.
*   **Scenario:** Global Error Handling.
    *   **Action (Manual):** Trigger a 500 error from the backend (e.g., mock a failure).
    *   **Expected:** A user-friendly error toast or boundary appears, not a blank white screen.