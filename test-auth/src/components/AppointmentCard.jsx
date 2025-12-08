import { useNavigate } from 'react-router-dom';
import { format, differenceInMinutes } from 'date-fns';
import { Calendar, Clock, Video, FileText, CheckCircle, XCircle, User } from 'lucide-react';
import { confirmAppointment, cancelAppointment } from '../api/appointmentService';
import Toast from './Toast';
import { useState } from 'react';
import LoadingSpinner from './LoadingSpinner';

export default function AppointmentCard({ appointment, role = 'patient', onStatusChange }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const appointmentDate = new Date(appointment.preferred_slot);
  const now = new Date();
  const minutesUntilAppointment = differenceInMinutes(appointmentDate, now);
  // Video call available 5 minutes before and up to 30 minutes after (assuming 30 min duration)
  const isVideoCallAvailable = minutesUntilAppointment <= 5 && minutesUntilAppointment > -30;

  const handleAccept = async () => {
    try {
      setLoading(true);
      const data= { status: 'confirmed' ,confirmed_slot:appointment.preferred_slot}
      await confirmAppointment(appointment.id,data );
      setToast({ message: 'Appointment confirmed', type: 'success' });
      if (onStatusChange) onStatusChange();
    } catch (error) {
      setToast({ message: 'Failed to confirm appointment', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;
    try {
      setLoading(true);
      await cancelAppointment(appointment.id);
      setToast({ message: 'Appointment cancelled', type: 'success' });
      if (onStatusChange) onStatusChange();
    } catch (error) {
      setToast({ message: 'Failed to cancel appointment', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      confirmed: 'bg-green-100 text-green-800 border-green-200',
      completed: 'bg-blue-100 text-blue-800 border-blue-200',
      cancelled: 'bg-red-100 text-red-800 border-red-200',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.pending}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition relative">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${
            role === 'provider' ? 'bg-green-600' : 'bg-gradient-to-br from-blue-500 to-teal-500'
          }`}>
            {role === 'provider' ? (
               <User className="w-6 h-6" /> // Icon for patient
            ) : (
               appointment.provider_name?.charAt(0) || 'D' // Initial for provider
            )}
          </div>
          <div>
            <h3 className="font-bold text-gray-900">
              {role === 'provider'
                ? appointment.patient_name || 'Patient Name'
                : `Dr. ${appointment.provider_name}`}
            </h3>
            <p className="text-sm text-gray-600">
              {role === 'provider'
                ? appointment.case_title || 'General Consultation'
                : appointment.specialization || 'Dermatologist'}
            </p>
          </div>
        </div>
        {getStatusBadge(appointment.status)}
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex items-center gap-3 text-gray-700">
          <Calendar className="w-5 h-5 text-gray-400" />
          <span>{format(appointmentDate, 'MMMM dd, yyyy')}</span>
        </div>
        <div className="flex items-center gap-3 text-gray-700">
          <Clock className="w-5 h-5 text-gray-400" />
          <span>{format(appointmentDate, 'hh:mm a')}</span>
        </div>
        {/* For provider, show more case details if available */}
        {role === 'provider' && appointment.symptoms && (
          <div className="mt-2 p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
            <p className="font-medium mb-1">Symptoms:</p>
            <p className="line-clamp-2">{appointment.symptoms}</p>
          </div>
        )}
      </div>

      <div className="flex gap-3 flex-wrap">
        {/* Actions for Provider */}
        {role === 'provider' && (
          <>
            {appointment.status === 'pending' && (
              <button
                onClick={handleAccept}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center justify-center gap-2"
              >
                {loading ? <LoadingSpinner size="sm" /> : <><CheckCircle className="w-4 h-4" /> Accept</>}
              </button>
            )}

            {appointment.status === 'confirmed' && isVideoCallAvailable && (
              <button
                onClick={() => navigate(`/video-call/${appointment.id}`)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
              >
                <Video className="w-4 h-4" /> Join Call
              </button>
            )}

            <button
               onClick={() => navigate(`/provider/visit-summary/${appointment.id}`)}
               className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition flex items-center justify-center gap-2"
            >
              <FileText className="w-4 h-4" /> Summary
            </button>
          </>
        )}

        {/* Actions for Patient */}
        {role === 'patient' && (
          <>
            {appointment.status === 'confirmed' && isVideoCallAvailable && (
              <button
                onClick={() => navigate(`/video-call/${appointment.id}`)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
              >
                <Video className="w-4 h-4" /> Join Call
              </button>
            )}

            {(appointment.status === 'pending' || appointment.status === 'confirmed') && (
              <button
                onClick={handleCancel}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100 transition flex items-center justify-center gap-2"
              >
                 {loading ? <LoadingSpinner size="sm" /> : <><XCircle className="w-4 h-4" /> Cancel</>}
              </button>
            )}

            {(appointment.status === 'completed') && (
               <button
                onClick={() => navigate(`/patient/visit/${appointment.id}`)}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition flex items-center justify-center gap-2"
              >
                <FileText className="w-4 h-4" /> Summary
              </button>
            )}
          </>
        )}

        {/* Actions for Admin */}
        {role === 'admin' && (
           <>
             {/* Admin can view or maybe cancel? For now just view summary if completed */}
             {appointment.status === 'completed' && (
               <button
                 className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition flex items-center justify-center gap-2"
               >
                 View Records
               </button>
             )}
             <div className="w-full text-center text-xs text-gray-500 mt-2">
               Admin View
             </div>
           </>
        )}
      </div>
    </div>
  );
}
