import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCaseById } from '../api/caseService';
import LoadingSpinner from '../components/LoadingSpinner';
import { FileText, Calendar, Image as ImageIcon, ArrowLeft } from 'lucide-react';
import { format } from 'date-fns';

export default function CaseDetails() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCaseDetails();
  }, [caseId]);

  const loadCaseDetails = async () => {
    try {
      setLoading(true);
      const data = await getCaseById(caseId);
      setCaseData(data);
    } catch (err) {
      console.error('Failed to load case details:', err);
      setError('Failed to load case details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-white rounded-lg shadow-md p-12">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-red-500" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Case</h2>
            <p className="text-gray-600 mb-6">{error || 'Case information not found.'}</p>
            <button
              onClick={() => navigate('/cases')}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
            >
              Back to Cases
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/cases')}
            className="text-primary hover:text-primary-dark mb-4 flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Cases
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{caseData.title}</h1>
              <p className="text-gray-600 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Created on {format(new Date(caseData.created_at), 'MMMM dd, yyyy')}
              </p>
            </div>
            <div className="text-right">
              <span className={`inline-block px-4 py-2 rounded-full font-medium text-sm ${
                caseData.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {caseData.status?.charAt(0).toUpperCase() + caseData.status?.slice(1) || 'Active'}
              </span>
            </div>
          </div>
        </div>

        <div className="grid gap-6">
          {/* Symptoms */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              Symptoms & Description
            </h2>
            <div className="prose max-w-none text-gray-700">
              <p className="whitespace-pre-wrap">{caseData.symptoms}</p>
            </div>
          </div>

          {/* Photos */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ImageIcon className="w-5 h-5 text-primary" />
              Attached Photos
            </h2>
            {caseData.photos && caseData.photos.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {caseData.photos.map((photo, index) => (
                  <div key={index} className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 border border-gray-200">
                    <img
                      src={photo.url || photo}
                      alt={`Case photo ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No photos attached to this case.</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-4">
             <button
              onClick={() => navigate('/find-provider')}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium"
            >
              Book Appointment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
