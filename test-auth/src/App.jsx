import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { QueryProvider } from './contexts/QueryProvider';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AIAnalysis from './pages/AIAnalysis';
import CreateCase from './pages/CreateCase';
import MyCases from './pages/MyCases';
import CaseDetails from './pages/CaseDetails';
import FindProvider from './pages/FindProvider';
import BookAppointment from './pages/BookAppointment';
import VisitHistory from './pages/VisitHistory';
import CompleteProfile from './pages/CompleteProfile';
import VideoCall from './pages/VideoCall';
import ChatInterface from './pages/ChatInterface';
import PatientVisitDetails from './pages/PatientVisitDetails';
import ProviderVisitSummary from './pages/ProviderVisitSummary';
import ContentManagement from './pages/ContentManagement';
import DemoPage from './pages/DemoPage';
import Testimonials from './pages/Testimonials';

const App = () => {
  return (
    <QueryProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/demo" element={<DemoPage />} />
            <Route path="/testimonials" element={<Testimonials />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/complete-profile" element={<CompleteProfile />} />
              <Route path="/ai-analysis" element={<AIAnalysis />} />
              <Route path="/cases" element={<MyCases />} />
              <Route path="/cases/:caseId" element={<CaseDetails />} />
              <Route path="/create-case" element={<CreateCase />} />
              <Route path="/find-provider" element={<FindProvider />} />
              <Route path="/book-appointment/:providerId" element={<BookAppointment />} />
              <Route path="/visit-history" element={<VisitHistory />} />
              <Route path="/patient/visit/:visitId" element={<PatientVisitDetails />} />
              <Route path="/provider/visit-summary/:visitId" element={<ProviderVisitSummary />} />
              <Route path="/video-call/:appointmentId" element={<VideoCall />} />
              <Route path="/chat/:visitId" element={<ChatInterface />} />
              <Route path="/content-management" element={<ContentManagement />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryProvider>
  );
};

export default App;
