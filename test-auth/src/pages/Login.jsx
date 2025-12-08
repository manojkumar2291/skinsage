import { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { login, googleLogin } from '../api/authService';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';

const loginSchema = z.object({
  username: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { refreshUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      await login(data);
      await refreshUser();
      
      setToast({
        message: 'Login successful!',
        type: 'success',
      });

      const from = location.state?.from?.pathname || '/dashboard';
      setTimeout(() => {
        navigate(from, { replace: true });
      }, 1000);
    } catch (error) {
      setToast({
        message: error.detail || 'Login failed. Please check your credentials.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleResponse = async (response) => {
    const token = response.credential;

    try {
      const res = await googleLogin(token);
      await refreshUser();

      if (!res.profile_complete) {
        navigate('/complete-profile');
      } else {
        navigate('/dashboard');
      }
    } catch (error) {
      setToast({
        message: 'Google login failed',
        type: 'error',
      });
    }
  };

  useEffect(() => {
    /* global google */
    if (window.google) {
      google.accounts.id.initialize({
        client_id: '142062834172-dmiub6u296ebchu3gm0bvd0ft8tdi8fo.apps.googleusercontent.com',
        callback: handleGoogleResponse,
      });

      google.accounts.id.renderButton(
        document.getElementById('googleBtn'),
        { theme: 'outline', size: 'large', width: '100%' }
      );
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-white to-secondary/5 flex items-center justify-center px-4 py-8 font-sans">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="max-w-md w-full animate-fadeIn">
        <div className="text-center mb-8">
          <div className="inline-block p-3 rounded-full bg-primary/10 mb-4">
            <Mail className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2 tracking-tight">Welcome Back</h1>
          <p className="text-gray-600">Sign in to your SkinSage account</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 backdrop-blur-sm">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-primary">
                  <Mail className="h-5 w-5 text-gray-400 group-focus-within:text-primary" />
                </div>
                <input
                  {...register('username')}
                  type="email"
                  id="username"
                  className={`w-full pl-10 pr-4 py-3 border ${
                    errors.username ? 'border-error' : 'border-gray-200'
                  } rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition bg-gray-50 focus:bg-white`}
                  placeholder="you@example.com"
                />
              </div>
              {errors.username && (
                <p className="mt-1 text-sm text-error animate-pulse">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-primary">
                  <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-primary" />
                </div>
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  className={`w-full pl-10 pr-12 py-3 border ${
                    errors.password ? 'border-error' : 'border-gray-200'
                  } rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition bg-gray-50 focus:bg-white`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-error animate-pulse">{errors.password.message}</p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center cursor-pointer">
                <input
                  id="remember"
                  type="checkbox"
                  className="w-4 h-4 text-primary focus:ring-primary border-gray-300 rounded cursor-pointer"
                />
                <span className="ml-2 text-sm text-gray-600">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-sm font-medium text-primary hover:text-primary-dark hover:underline">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-primary text-white rounded-xl hover:bg-primary-dark transition-all duration-200 font-semibold shadow-lg shadow-primary/30 hover:shadow-primary/50 disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 transform active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" color="white" />
                  <span>Signing in...</span>
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          <div id="googleBtn" className="mt-6"></div>

          <p className="mt-6 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:text-primary-dark font-semibold">
              Sign up
            </Link>
          </p>
        </div>

        <div className="text-center mt-6">
          <Link to="/" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}