import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { register as registerUser } from '../api/authService';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { Mail, Lock, User, Phone, Eye, EyeOff } from 'lucide-react';

const registerSchema = z.object({
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  role: z.enum(['patient', 'provider'], {
    errorMap: () => ({ message: 'Please select a role' }),
  }),
});

export default function Register() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: 'patient',
    },
  });

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      await registerUser(data);
      
      setToast({
        message: 'Registration successful! Please login.',
        type: 'success',
      });

      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      setToast({
        message: error.detail || 'Registration failed. Please try again.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-white to-secondary/10 flex items-center justify-center px-4 py-8">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">SkinSage</h1>
          <p className="text-gray-600">Create your account</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Full Name */}
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('full_name')}
                  type="text"
                  id="full_name"
                  className={`w-full pl-10 pr-4 py-3 border ${
                    errors.full_name ? 'border-error' : 'border-gray-300'
                  } rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition`}
                  placeholder="John Doe"
                />
              </div>
              {errors.full_name && (
                <p className="mt-1 text-sm text-error">{errors.full_name.message}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('email')}
                  type="email"
                  id="email"
                  className={`w-full pl-10 pr-4 py-3 border ${
                    errors.email ? 'border-error' : 'border-gray-300'
                  } rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition`}
                  placeholder="you@example.com"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-error">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  className={`w-full pl-10 pr-12 py-3 border ${
                    errors.password ? 'border-error' : 'border-gray-300'
                  } rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-error">{errors.password.message}</p>
              )}
            </div>

            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                I am a
              </label>
              <div className="grid grid-cols-2 gap-4">
                <label className="relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer hover:border-primary transition has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                  <input
                    {...register('role')}
                    type="radio"
                    value="patient"
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-2xl mb-2">🧑‍⚕️</div>
                    <div className="font-medium">Patient</div>
                  </div>
                </label>
                <label className="relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer hover:border-primary transition has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                  <input
                    {...register('role')}
                    type="radio"
                    value="provider"
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-2xl mb-2">👨‍⚕️</div>
                    <div className="font-medium">Provider</div>
                  </div>
                </label>
              </div>
              {errors.role && (
                <p className="mt-1 text-sm text-error">{errors.role.message}</p>
              )}
            </div>

            {/* Terms */}
            <div className="flex items-start">
              <input
                id="terms"
                type="checkbox"
                required
                className="h-4 w-4 mt-1 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <label htmlFor="terms" className="ml-2 block text-sm text-gray-700">
                I agree to the{' '}
                <Link to="/terms" className="text-primary hover:text-primary-dark">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-primary hover:text-primary-dark">
                  Privacy Policy
                </Link>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Creating account...</span>
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Sign In Link */}
          <p className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:text-primary-dark font-semibold">
              Sign in
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