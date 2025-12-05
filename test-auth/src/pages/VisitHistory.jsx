import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAppointments } from '../api/appointmentService';
import { getVisitHistory } from '../api/visitService';
import LoadingSpinner from '../components/LoadingSpinner';
import { Calendar, Clock, User, FileText, Video, MessageSquare } from 'lucide-react';
import { format } from 'date-fns';

export default function VisitHistory() {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('upcoming');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [appointmentsData, visitsData] = await Promise.all([
        getAppointments(),
        getVisitHistory(),
      ]);
      setAppointments(appointmentsData);
      setVisits(visitsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };
  console.log(appointments)
  const upcomingAppointments = appointments.filter(
    (apt) => apt.status === 'pending' && new Date(apt.preferred_slot) > new Date()
  );

  const pastAppointments = appointments.filter(
    (apt) => apt.status === 'completed' || new Date(apt.preferred_slot) < new Date()
  );

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-warning/10 text-warning border-warning/30',
      confirmed: 'bg-success/10 text-success border-success/30',
      completed: 'bg-primary/10 text-primary border-primary/30',
      cancelled: 'bg-error/10 text-error border-error/30',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.pending}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const AppointmentCard = ({ appointment, isPast = false }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-bold">
            {appointment.provider_name?.charAt(0) || 'D'}
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Dr. {appointment.provider_name}</h3>
            <p className="text-sm text-gray-600">{appointment.specialization || 'Dermatologist'}</p>
          </div>
        </div>
        {getStatusBadge(appointment.status)}
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex items-center gap-3 text-gray-700">
          <Calendar className="w-5 h-5 text-primary" />
          <span>{format(new Date(appointment.preferred_slot), 'MMMM dd, yyyy')}</span>
        </div>
        <div className="flex items-center gap-3 text-gray-700">
          <Clock className="w-5 h-5 text-primary" />
          <span>{format(new Date(appointment.preferred_slot), 'hh:mm a')}</span>
        </div>
        {appointment.case_title && (
          <div className="flex items-center gap-3 text-gray-700">
            <FileText className="w-5 h-5 text-primary" />
            <span className="truncate">{appointment.case_title}</span>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        {!isPast && appointment.status === 'confirmed' && (
          <button
            onClick={() => navigate(`/video-call/${appointment.id}`)}
            className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition flex items-center justify-center gap-2"
          >
            <Video className="w-4 h-4" />
            Join Call
          </button>
        )}
        {isPast && (
          <button
            onClick={() => navigate(`/patient/visit/${appointment.id}`)}
            className="flex-1 px-4 py-2 bg-secondary text-white rounded-lg hover:bg-secondary/90 transition flex items-center justify-center gap-2"
          >
            <FileText className="w-4 h-4" />
            View Summary
          </button>
        )}
        {appointment.status === 'pending' && (
          <button
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Awaiting Confirmation
          </button>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-primary hover:text-primary-dark mb-4 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Visit History</h1>
          <p className="text-gray-600">View your appointments and consultations</p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-8">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('upcoming')}
                className={`flex-1 px-6 py-4 font-medium transition ${
                  activeTab === 'upcoming'
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Upcoming ({upcomingAppointments.length})
              </button>
              <button
                onClick={() => setActiveTab('past')}
                className={`flex-1 px-6 py-4 font-medium transition ${
                  activeTab === 'past'
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Past ({pastAppointments.length})
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'upcoming' ? (
          upcomingAppointments.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No upcoming appointments</h3>
              <p className="text-gray-600 mb-6">Book a consultation with a dermatologist</p>
              <button
                onClick={() => navigate('/find-provider')}
                className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
              >
                Find a Dermatologist
              </button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {upcomingAppointments.map((appointment) => (
                <AppointmentCard key={appointment.id} appointment={appointment} />
              ))}
            </div>
          )
        ) : pastAppointments.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No past appointments</h3>
            <p className="text-gray-600">Your completed consultations will appear here</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pastAppointments.map((appointment) => (
              <AppointmentCard key={appointment.id} appointment={appointment} isPast />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}