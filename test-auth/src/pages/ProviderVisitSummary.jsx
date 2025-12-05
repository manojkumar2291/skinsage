import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { getVisitSummary, uploadVisitSummary } from '../api/visitService';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { FileText, Save, ArrowLeft, Calendar, User } from 'lucide-react';

const summarySchema = z.object({
  diagnosis: z.string().min(5, 'Diagnosis is required'),
  summary: z.string().min(10, 'Summary must be detailed'),
  next_steps: z.string().min(5, 'Next steps are required'),
  prescription: z.string().optional(), // Adding prescription field as optional for now
});

export default function ProviderVisitSummary() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [visitData, setVisitData] = useState(null);
  const [toast, setToast] = useState(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(summarySchema),
  });

  useEffect(() => {
    loadVisitData();
  }, [visitId]);

  const loadVisitData = async () => {
    try {
      setLoading(true);
      const data = await getVisitSummary(visitId);
      setVisitData(data);
      // Pre-fill form if data exists
      if (data.diagnosis) setValue('diagnosis', data.diagnosis);
      if (data.summary) setValue('summary', data.summary);
      if (data.next_steps) setValue('next_steps', data.next_steps);
      // Prescription might not be in the initial data structure from my previous read, but let's assume it could be
    } catch (error) {
      setToast({
        message: 'Failed to load visit data',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      setSaving(true);
      await uploadVisitSummary(visitId, data);

      setToast({
        message: 'Visit summary saved successfully',
        type: 'success',
      });

      setTimeout(() => {
        navigate('/provider/dashboard');
      }, 1500);
    } catch (error) {
      setToast({
        message: error.detail || 'Failed to save summary',
        type: 'error',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/provider/dashboard')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Visit Summary & Diagnosis</h1>
          <div className="flex items-center gap-6 text-gray-600 mt-2">
             <span className="flex items-center gap-2"><User className="w-4 h-4" /> {visitData?.patient_name || 'Patient'}</span>
             <span className="flex items-center gap-2"><Calendar className="w-4 h-4" /> {new Date().toLocaleDateString()}</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-md p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

            {/* Diagnosis */}
            <div>
              <label htmlFor="diagnosis" className="block text-sm font-medium text-gray-700 mb-2">
                Diagnosis <span className="text-red-500">*</span>
              </label>
              <input
                {...register('diagnosis')}
                type="text"
                id="diagnosis"
                className={`w-full px-4 py-3 border ${
                  errors.diagnosis ? 'border-red-500' : 'border-gray-300'
                } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition`}
                placeholder="e.g., Atopic Dermatitis"
              />
              {errors.diagnosis && (
                <p className="mt-1 text-sm text-red-500">{errors.diagnosis.message}</p>
              )}
            </div>

            {/* Clinical Summary */}
            <div>
              <label htmlFor="summary" className="block text-sm font-medium text-gray-700 mb-2">
                Clinical Summary & Observations <span className="text-red-500">*</span>
              </label>
              <textarea
                {...register('summary')}
                id="summary"
                rows={4}
                className={`w-full px-4 py-3 border ${
                  errors.summary ? 'border-red-500' : 'border-gray-300'
                } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition resize-none`}
                placeholder="Detailed observations about the patient's condition..."
              />
              {errors.summary && (
                <p className="mt-1 text-sm text-red-500">{errors.summary.message}</p>
              )}
            </div>

            {/* Treatment Plan */}
            <div>
              <label htmlFor="next_steps" className="block text-sm font-medium text-gray-700 mb-2">
                Treatment Plan & Next Steps <span className="text-red-500">*</span>
              </label>
              <textarea
                {...register('next_steps')}
                id="next_steps"
                rows={4}
                className={`w-full px-4 py-3 border ${
                  errors.next_steps ? 'border-red-500' : 'border-gray-300'
                } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition resize-none`}
                placeholder="Recommended treatment, follow-up instructions, etc."
              />
              {errors.next_steps && (
                <p className="mt-1 text-sm text-red-500">{errors.next_steps.message}</p>
              )}
            </div>

            {/* Prescription (Optional) */}
            <div>
              <label htmlFor="prescription" className="block text-sm font-medium text-gray-700 mb-2">
                Prescription (Optional)
              </label>
              <textarea
                {...register('prescription')}
                id="prescription"
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition resize-none"
                placeholder="Medications, dosage, frequency..."
              />
            </div>

            {/* Submit */}
            <div className="pt-4 border-t border-gray-100 flex justify-end gap-4">
              <button
                type="button"
                onClick={() => navigate('/provider/dashboard')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                disabled={saving}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    Save Summary
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
