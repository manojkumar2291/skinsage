import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVisitSummary } from '../api/visitService';
import LoadingSpinner from '../components/LoadingSpinner';
import { FileText, Calendar, User, Clock, Activity, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';

export default function PatientVisitDetails() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [visit, setVisit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadVisitDetails();
  }, [visitId]);

  const loadVisitDetails = async () => {
    try {
      setLoading(true);
      const data = await getVisitSummary(visitId);
      setVisit(data);
    } catch (err) {
      console.error('Failed to load visit details:', err);
      setError('Failed to load visit details. Please try again.');
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

  if (error || !visit) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-white rounded-lg shadow-md p-12">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-error" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Details</h2>
            <p className="text-gray-600 mb-6">{error || 'Visit information not found.'}</p>
            <button
              onClick={() => navigate('/visit-history')}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
            >
              Back to History
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
            onClick={() => navigate('/visit-history')}
            className="text-primary hover:text-primary-dark mb-4 flex items-center gap-2"
          >
            ← Back to History
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Visit Summary</h1>
              <p className="text-gray-600">
                Consultation details and doctor's notes
              </p>
            </div>
            <div className="text-right">
              <span className="inline-block px-4 py-2 bg-success/10 text-success rounded-full font-medium border border-success/20">
                Completed
              </span>
            </div>
          </div>
        </div>

        <div className="grid gap-6">
          {/* Appointment Info */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary" />
              Appointment Information
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-500 mb-1">Date & Time</p>
                <p className="font-medium text-gray-900 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-400" />
                  {visit.appointment_date && format(new Date(visit.appointment_date), 'MMMM dd, yyyy - hh:mm a')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Provider</p>
                <p className="font-medium text-gray-900 flex items-center gap-2">
                  <User className="w-4 h-4 text-gray-400" />
                  Dr. {visit.provider_name}
                </p>
              </div>
            </div>
          </div>

          {/* Clinical Notes */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Clinical Notes
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Diagnosis</h3>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-gray-800">
                  {visit.diagnosis || 'No diagnosis recorded.'}
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Summary & Observations</h3>
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {visit.summary || 'No summary recorded.'}
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Treatment Plan & Next Steps</h3>
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {visit.next_steps || 'No next steps recorded.'}
                </p>
              </div>
            </div>
          </div>

          {/* Prescriptions (Placeholder if you have prescription data) */}
          {/*
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              Prescriptions
            </h2>
            ...
          </div>
          */}

          {/* Actions */}
          <div className="flex justify-end gap-4">
            <button
              onClick={() => window.print()}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Print Summary
            </button>
            <button
              onClick={() => navigate(`/chat/${visitId}`)}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium"
            >
              Message Doctor
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
