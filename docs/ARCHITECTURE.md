# SkinSage System Architecture

The following diagram illustrates the high-level architecture of the SkinSage platform. It is a modern web application utilizing a React frontend, a FastAPI backend, a MySQL database, and several external service integrations for payments and video conferencing.

```mermaid
architecture-beta
    group frontend(internet)[Frontend]
    group backend(cloud)[Backend Services]
    group data(database)[Data Layer]
    group external(cloud)[External Integrations]

    service react(internet)[React Client (Vite)] in frontend

    service api(server)[FastAPI Server] in backend
    service ai(server)[AI Analysis Service (HuggingFace/OpenRouter)] in backend
    service auth(server)[Authentication Service (JWT)] in backend

    service db(database)[MySQL Database] in data

    service razorpay(cloud)[Razorpay (Payments)] in external
    service agora(cloud)[Agora (Video Calls)] in external

    react:R --> L:api
    api:B --> T:db

    api:R --> L:ai
    api:R --> L:auth

    api:T --> B:razorpay
    api:T --> B:agora

    react:T --> B:razorpay
    react:T --> B:agora
```

## Architecture Components

1.  **Frontend Layer (React Client)**
    *   Built with React and Vite.
    *   Handles the user interface for Patients, Providers, and Admins.
    *   Communicates directly with the Agora SDK for WebRTC video calls and Razorpay for client-side payment tokenization.

2.  **Backend API (FastAPI)**
    *   Provides RESTful endpoints for the frontend.
    *   Manages business logic for appointments, users, cases, and payments.
    *   Generates necessary tokens for external services (e.g., Agora RTC tokens).

3.  **Data Layer (MySQL)**
    *   Relational database storing user profiles, appointment schedules, payment records, and AI chat histories.

4.  **External Integrations**
    *   **Agora:** Facilitates real-time video consultations between Providers and Patients.
    *   **Razorpay:** Handles secure payment processing for appointments and platform services.
    *   **AI Services (HuggingFace / OpenRouter):** Processes images and text for the initial AI dermatological analysis.
