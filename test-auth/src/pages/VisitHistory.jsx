import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAppointments } from '../api/appointmentService';
import { getVisitHistory } from '../api/visitService';
import LoadingSpinner from '../components/LoadingSpinner';
import AppointmentCard from '../components/AppointmentCard';
import { Calendar, FileText } from 'lucide-react';

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
      const [appointmentsData, visitsData] = await Promise.allSettled([
        getAppointments(),
        getVisitHistory(),
      ]);
      setAppointments(appointmentsData.value);
      setVisits(visitsData.value);
      console.log(appointmentsData, visitsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  console.log(appointments)

  const upcomingAppointments = appointments.filter(
    (apt) => apt.status !== 'completed' && apt.status !== 'cancelled'
    // Simplified logic: anything not finished is "upcoming" or "active"
  );

  const pastAppointments = appointments.filter(
    (apt) => apt.status === 'completed' || apt.status === 'cancelled'
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
                <AppointmentCard
                  key={appointment.id}
                  appointment={appointment}
                  role="patient"
                  onStatusChange={loadData}
                />
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
              <AppointmentCard
                key={appointment.id}
                appointment={appointment}
                role="patient"
                onStatusChange={loadData}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}