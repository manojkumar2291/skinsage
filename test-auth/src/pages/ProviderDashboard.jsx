import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getAppointments } from '../api/appointmentService';
import LoadingSpinner from '../components/LoadingSpinner';
import { Calendar, Users, Activity, Clock, LogOut, CheckCircle, Video, FileText } from 'lucide-react';
import { format } from 'date-fns';

export default function ProviderDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // Fetch appointments for this provider
      const data = await getAppointments(); // Assuming API filters for provider if logged in as provider
      setAppointments(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/provider/login');
  };

  const todayAppointments = appointments.filter(
    (apt) => new Date(apt.preferred_slot).toDateString() === new Date().toDateString()
  );

  const pendingAppointments = appointments.filter(apt => apt.status === 'pending');

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Activity className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Provider Portal</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-700 font-medium">Dr. {user?.full_name}</span>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-500 hover:text-red-600 transition rounded-full hover:bg-gray-100"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Today's Appointments</p>
                <p className="text-3xl font-bold text-gray-900">{todayAppointments.length}</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-orange-500">
             <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending Requests</p>
                <p className="text-3xl font-bold text-gray-900">{pendingAppointments.length}</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-green-500">
             <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Patients</p>
                <p className="text-3xl font-bold text-gray-900">--</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <Users className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Today's Schedule */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-lg font-bold text-gray-900">Today's Schedule</h2>
                <span className="text-sm text-gray-500">{format(new Date(), 'MMMM dd, yyyy')}</span>
              </div>
              <div className="divide-y divide-gray-200">
                {todayAppointments.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    No appointments scheduled for today.
                  </div>
                ) : (
                  todayAppointments.map((apt) => (
                    <div key={apt.id} className="p-6 hover:bg-gray-50 transition">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="text-center min-w-[60px]">
                            <p className="text-sm font-bold text-gray-900">
                              {format(new Date(apt.preferred_slot), 'hh:mm')}
                            </p>
                            <p className="text-xs text-gray-500">
                              {format(new Date(apt.preferred_slot), 'a')}
                            </p>
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{apt.patient_name || 'Patient Name'}</h3>
                            <p className="text-sm text-gray-600">{apt.case_title || 'General Consultation'}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                           {apt.status === 'confirmed' && (
                             <button
                               onClick={() => navigate(`/video-call/${apt.id}`)}
                               className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition"
                               title="Start Video Call"
                             >
                               <Video className="w-5 h-5" />
                             </button>
                           )}
                           <button
                             onClick={() => navigate(`/provider/visit-summary/${apt.id}`)}
                             className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition"
                             title="View/Edit Summary"
                           >
                             <FileText className="w-5 h-5" />
                           </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div>
             <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  <button onClick={() => navigate('/provider/schedule')} className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-blue-600" />
                    <span>Manage Schedule</span>
                  </button>
                  <button onClick={() => navigate('/provider/patients')} className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition flex items-center gap-3">
                     <Users className="w-5 h-5 text-green-600" />
                    <span>Patient Directory</span>
                  </button>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
