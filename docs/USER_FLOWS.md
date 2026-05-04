# User Flow Diagrams

Below are the primary user flows for the SkinSage application, depicted using Mermaid.js diagrams.

## 1. Patient User Flow

The Patient flow encompasses registration, logging in, booking appointments, conducting the visit (including AI analysis and video calls), and making payments.

```mermaid
flowchart TD
    Start([Patient visits website]) --> LoginCheck{Has Account?}
    LoginCheck -- No --> Register[Register Patient Account]
    Register --> Login
    LoginCheck -- Yes --> Login[Login as Patient]
    Login --> Dashboard[Patient Dashboard]

    Dashboard --> BrowseProviders[Browse Providers]
    Dashboard --> ViewAppointments[View Appointments]
    Dashboard --> AIAnalysis[Start AI Analysis]

    BrowseProviders --> SelectProvider[Select Provider]
    SelectProvider --> BookAppointment[Book Appointment]
    BookAppointment --> Payment[Process Payment]
    Payment -- Success --> AppointmentConfirmed[Appointment Confirmed]

    ViewAppointments --> JoinCall[Join Video Call (If 5 mins before)]
    JoinCall --> ConductVisit[Conduct Virtual Visit]
    ConductVisit --> VisitCompleted[Visit Completed]

    AIAnalysis --> UploadImage[Upload Image & Describe Symptoms]
    UploadImage --> ReceiveResults[Receive AI Diagnostics]
    ReceiveResults --> Dashboard
```

## 2. Provider User Flow

The Provider flow involves logging in, managing the schedule (accepting/rejecting appointments), conducting visits, and reviewing patient data.

```mermaid
flowchart TD
    Start([Provider visits website]) --> Login[Login as Provider]
    Login --> Dashboard[Provider Dashboard]

    Dashboard --> ViewPending[View Pending Appointments]
    Dashboard --> ViewAccepted[View Accepted Appointments]
    Dashboard --> ViewCompleted[View Completed Appointments]

    ViewPending --> ActionAppointment{Accept or Reject?}
    ActionAppointment -- Accept --> ConfirmAppointment[Appointment Confirmed]
    ActionAppointment -- Reject --> CancelAppointment[Appointment Cancelled]
    ConfirmAppointment --> Dashboard

    ViewAccepted --> CheckTime{Time to Visit?}
    CheckTime -- No --> Dashboard
    CheckTime -- Yes --> JoinCall[Join Video Call]
    JoinCall --> ConductVisit[Conduct Virtual Visit with Patient]
    ConductVisit --> AddNotes[Add Consultation Notes/Prescription]
    AddNotes --> MarkComplete[Mark Visit as Completed]
    MarkComplete --> Dashboard
```

## 3. Admin User Flow

The Admin flow is focused on system management, overseeing users, providers, and overall platform activity.

```mermaid
flowchart TD
    Start([Admin visits website]) --> Login[Login as Admin]
    Login --> Dashboard[Admin Dashboard]

    Dashboard --> ManageUsers[Manage Patients]
    Dashboard --> ManageProviders[Manage Providers]
    Dashboard --> ManageAppointments[View All Appointments]
    Dashboard --> ManagePayments[View Payments]

    ManageUsers --> ViewUserDetails[View User Details]
    ManageUsers --> BanUser[Suspend/Ban User]

    ManageProviders --> VerifyProvider[Verify/Approve New Provider]
    ManageProviders --> ViewProviderStats[View Provider Statistics]

    ManageAppointments --> ViewDisputes[Handle Appointment Issues]
```
