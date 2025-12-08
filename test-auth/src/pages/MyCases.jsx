import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCases } from '../api/caseService';
import { FileText, Calendar, ChevronRight, Plus, Loader2 } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function MyCases() {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      const data = await getCases();
      setCases(data);
    } catch (err) {
      console.error('Failed to fetch cases:', err);
      setError('Failed to load cases. Please try again.');
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

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Cases</h1>
            <p className="text-gray-600 mt-1">Manage your medical cases and history</p>
          </div>
          <button
            onClick={() => navigate('/create-case')}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark flex items-center gap-2 transition"
          >
            <Plus className="w-4 h-4" />
            Create New Case
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Cases List */}
        {cases.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Cases Found</h3>
            <p className="text-gray-600 mb-6">You haven't created any medical cases yet.</p>
            <button
              onClick={() => navigate('/create-case')}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition inline-flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Create Your First Case
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="divide-y divide-gray-200">
              {cases.map((caseItem) => (
                <div key={caseItem.id} className="p-6 hover:bg-gray-50 transition flex items-center justify-between group cursor-pointer" onClick={() => navigate(`/cases/${caseItem.id}`)}>
                  <div className="flex items-center space-x-4">
                    <div className="bg-blue-100 p-3 rounded-lg group-hover:bg-blue-200 transition">
                      <FileText className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary transition">{caseItem.title}</h3>
                      <p className="text-gray-600 text-sm mt-1 line-clamp-1">{caseItem.symptoms}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                        <span className="flex items-center"><Calendar className="w-3 h-3 mr-1" /> {new Date(caseItem.created_at).toLocaleDateString()}</span>
                        {/* Add more metadata if available */}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                     {/* Status Badge can go here if status exists in caseItem */}
                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-primary transition" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
