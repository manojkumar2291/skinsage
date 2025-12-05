import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { createCase } from '../api/caseService';
import { getAnalysisHistory } from '../api/analysisService';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { FileText, Image as ImageIcon } from 'lucide-react';

const caseSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  symptoms: z.string().min(10, 'Please describe your symptoms in detail (at least 10 characters)'),
  photo_ids: z.array(z.string()).min(1, 'Please select at least one analysis photo'),
});

export default function CreateCase() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState(true);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [selectedPhotos, setSelectedPhotos] = useState([]);
  const [toast, setToast] = useState(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(caseSchema),
  });

  useEffect(() => {
    loadAnalysisHistory();
  }, []);

  const loadAnalysisHistory = async () => {
    try {
      setLoadingAnalysis(true);
      const data = await getAnalysisHistory();
      setAnalysisHistory(data);
    } catch (error) {
      console.error('Failed to load analysis history:', error);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const togglePhotoSelection = (photoId) => {
    const newSelection = selectedPhotos.includes(photoId)
      ? selectedPhotos.filter(id => id !== photoId)
      : [...selectedPhotos, photoId];
    
    setSelectedPhotos(newSelection);
    setValue('photo_ids', newSelection);
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      await createCase(data);
      
      setToast({
        message: 'Case created successfully!',
        type: 'success',
      });

      setTimeout(() => {
        navigate('/find-provider');
      }, 2000);
    } catch (error) {
      setToast({
        message: error.detail || 'Failed to create case. Please try again.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

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
            onClick={() => navigate('/dashboard')}
            className="text-primary hover:text-primary-dark mb-4 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Create Medical Case</h1>
          <p className="text-gray-600">
            Document your skin concern to share with dermatologists
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Case Title <span className="text-error">*</span>
              </label>
              <input
                {...register('title')}
                type="text"
                id="title"
                className={`w-full px-4 py-3 border ${
                  errors.title ? 'border-error' : 'border-gray-300'
                } rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition`}
                placeholder="e.g., Persistent rash on left arm"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-error">{errors.title.message}</p>
              )}
            </div>

            {/* Symptoms */}
            <div>
              <label htmlFor="symptoms" className="block text-sm font-medium text-gray-700 mb-2">
                Symptoms Description <span className="text-error">*</span>
              </label>
              <textarea
                {...register('symptoms')}
                id="symptoms"
                rows={6}
                className={`w-full px-4 py-3 border ${
                  errors.symptoms ? 'border-error' : 'border-gray-300'
                } rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition resize-none`}
                placeholder="Describe your symptoms in detail: When did it start? How does it feel? Any triggers? etc."
              />
              {errors.symptoms && (
                <p className="mt-1 text-sm text-error">{errors.symptoms.message}</p>
              )}
            </div>

            {/* Photo Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select Analysis Photos <span className="text-error">*</span>
              </label>

              {loadingAnalysis ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner size="lg" />
                </div>
              ) : analysisHistory.length === 0 ? (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <ImageIcon className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-600 mb-4">
                    No analysis photos available. Please analyze an image first.
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate('/ai-analysis')}
                    className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
                  >
                    Go to AI Analysis
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {analysisHistory.map((analysis) => (
                    <div
                      key={analysis.analysis_id}
                      onClick={() => togglePhotoSelection(analysis.analysis_id)}
                      className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition ${
                        selectedPhotos.includes(analysis.analysis_id)
                          ? 'border-primary shadow-lg'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="aspect-square bg-gray-100 flex items-center justify-center">
                        <ImageIcon className="w-12 h-12 text-gray-400" />
                      </div>
                      {selectedPhotos.includes(analysis.analysis_id) && (
                        <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                      <div className="p-2 bg-white">
                        <p className="text-xs text-gray-600 truncate">
                          {new Date(analysis.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {errors.photo_ids && (
                <p className="mt-2 text-sm text-error">{errors.photo_ids.message}</p>
              )}
            </div>

            {/* Info Box */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex gap-3">
                <FileText className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <div className="text-sm text-gray-700">
                  <p className="font-semibold mb-1">Case Information</p>
                  <p>
                    This case will be shared with dermatologists when you book an appointment. Include
                    all relevant details to help them provide the best care.
                  </p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Creating...</span>
                  </>
                ) : (
                  'Create Case'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}