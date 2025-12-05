import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import API from "../api";
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { Phone, Calendar } from 'lucide-react';

export default function CompleteProfile() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [showConsent, setShowConsent] = useState(false);
  
  const [form, setForm] = useState({
    phone: "",
    dob: "",
    gender: "",
    language_pref: "",
    role: "",
    consent: false,
  });

  const handleSubmit = async () => {
    if (!form.consent) {
      setToast({
        message: "You must agree to the Terms & Conditions to continue",
        type: 'error'
      });
      return;
    }

    try {
      setLoading(true);
      const payload = {
        phone: form.phone,
        dob: form.dob,
        gender: form.gender,
        language_pref: form.language_pref,
        role: form.role,
        consent: form.consent,
      };

      const res = await API.post("/auth/complete-profile", payload);
      
      if (refreshUser) await refreshUser();
      
      setToast({
        message: res.data.message || 'Profile completed successfully!',
        type: 'success'
      });

      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 2000);
    } catch (err) {
      console.error(err);
      setToast({
        message: "Could not update profile",
        type: 'error'
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

      {/* Consent Modal */}
      {showConsent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Privacy Policy & Terms of Service</h2>
            </div>
            
            <div className="p-6 space-y-4 text-gray-700">
              <section>
                <h3 className="font-bold text-lg mb-2">Privacy Policy</h3>
                <p className="text-sm">
                  We are committed to protecting your privacy. Your personal health information will be:
                </p>
                <ul className="list-disc list-inside text-sm mt-2 space-y-1">
                  <li>Encrypted and stored securely</li>
                  <li>Only shared with your chosen healthcare providers</li>
                  <li>Never sold to third parties</li>
                  <li>Used solely for providing medical services</li>
                </ul>
              </section>

              <section>
                <h3 className="font-bold text-lg mb-2">Terms of Service</h3>
                <p className="text-sm">
                  By using SkinSage, you agree to:
                </p>
                <ul className="list-disc list-inside text-sm mt-2 space-y-1">
                  <li>Provide accurate health information</li>
                  <li>Use the platform responsibly</li>
                  <li>Follow medical advice from licensed professionals</li>
                  <li>Understand that AI analysis is supplementary, not diagnostic</li>
                </ul>
              </section>
            </div>

            <div className="p-6 border-t border-gray-200 flex gap-4">
              <button
                onClick={() => setShowConsent(false)}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">Complete Your Profile</h1>
          <p className="text-gray-600">Just a few more details to get started</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="space-y-6">
            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone <span className="text-error">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Phone className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  placeholder="Phone"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                />
              </div>
            </div>

            {/* Date of Birth */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date of Birth <span className="text-error">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Calendar className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="date"
                  value={form.dob}
                  onChange={(e) => setForm({ ...form, dob: e.target.value })}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                />
              </div>
            </div>

            {/* Gender */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Gender <span className="text-error">*</span>
              </label>
              <div className="grid grid-cols-3 gap-4">
                <label className="relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer hover:border-primary transition has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                  <input
                    type="radio"
                    value="male"
                    checked={form.gender === "male"}
                    onChange={(e) => setForm({ ...form, gender: e.target.value })}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-2xl mb-1">👨</div>
                    <div className="text-sm font-medium">Male</div>
                  </div>
                </label>
                <label className="relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer hover:border-primary transition has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                  <input
                    type="radio"
                    value="female"
                    checked={form.gender === "female"}
                    onChange={(e) => setForm({ ...form, gender: e.target.value })}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-2xl mb-1">👩</div>
                    <div className="text-sm font-medium">Female</div>
                  </div>
                </label>
                <label className="relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer hover:border-primary transition has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                  <input
                    type="radio"
                    value="other"
                    checked={form.gender === "other"}
                    onChange={(e) => setForm({ ...form, gender: e.target.value })}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-2xl mb-1">🧑</div>
                    <div className="text-sm font-medium">Other</div>
                  </div>
                </label>
              </div>
            </div>

            {/* Language Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Language Preference
              </label>
              <input
                placeholder="Language Preference (e.g., English)"
                value={form.language_pref}
                onChange={(e) => setForm({ ...form, language_pref: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
              />
            </div>

            {/* Role */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role <span className="text-error">*</span>
              </label>
              <select
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
              >
                <option value="">Select Role</option>
                <option value="user">User</option>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            {/* Consent Checkbox */}
            <div className="flex items-start">
              <input
                type="checkbox"
                checked={form.consent}
                onChange={(e) => setForm({ ...form, consent: e.target.checked })}
                className="h-4 w-4 mt-1 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700">
                I agree to the{' '}
                <button
                  type="button"
                  onClick={() => setShowConsent(true)}
                  className="text-primary hover:text-primary-dark underline"
                >
                  Terms & Conditions
                </button>
              </label>
            </div>

            {/* Submit */}
            <button
              onClick={handleSubmit}
              disabled={loading || !form.consent}
              className="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Saving...</span>
                </>
              ) : (
                'Save Profile'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}