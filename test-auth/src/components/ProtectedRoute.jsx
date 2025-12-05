import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

export default function ProtectedRoute({ children, requireProfile = false }) {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();
console.log('ProtectedRoute - isAuthenticated:', isAuthenticated, 'user:', user, 'loading:', loading);
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if profile completion is required
  if (requireProfile && user && !user.profile_complete) {
    return <Navigate to="/complete-profile" replace />;
  }

  return children;
}