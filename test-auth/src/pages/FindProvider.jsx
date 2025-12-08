import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProviders } from '../api/providerService';
import LoadingSpinner from '../components/LoadingSpinner';
import { Search, MapPin, Star, Calendar } from 'lucide-react';

export default function FindProvider() {
  const navigate = useNavigate();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [specialization, setSpecialization] = useState('');

  useEffect(() => {
    loadProviders();
  }, [specialization]);

  const loadProviders = async () => {
    try {
      setLoading(true);
      const params = specialization ? { specialization } : {};
      const data = await getProviders(params);
      setProviders(data);
    } catch (error) {
      console.error('Failed to load providers:', error);
    } finally {
      setLoading(false);
    }
  };
  console.log(providers)

  const filteredProviders = providers.filter(provider =>
    provider.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    provider.speciality?.toLowerCase().includes(searchQuery.toLowerCase())
  );
  console.log(filteredProviders)

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
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Find a Dermatologist</h1>
          <p className="text-gray-600">
            Browse certified dermatologists and book your consultation
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid md:grid-cols-2 gap-4">
            {/* Search */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="Search by name or specialization..."
              />
            </div>

            {/* Specialization Filter */}
            <select
              value={specialization}
              onChange={(e) => setSpecialization(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
            >
              <option value="">All Specializations</option>
              <option value="general">General Dermatology</option>
              <option value="cosmetic">Cosmetic Dermatology</option>
              <option value="pediatric">Pediatric Dermatology</option>
              <option value="surgical">Surgical Dermatology</option>
            </select>
          </div>
        </div>

        {/* Providers Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredProviders.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-gray-400 mb-4">
              <Search className="w-16 h-16 mx-auto" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No providers found</h3>
            <p className="text-gray-600">
              Try adjusting your search or filters
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProviders.map((provider) => (
              <div
                key={provider.id}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition overflow-hidden"
              >
                {/* Provider Image */}
                <div className="h-48 bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center text-3xl font-bold text-primary">
                    {provider.name?.charAt(0) || 'D'}
                  </div>
                </div>

                {/* Provider Info */}
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-1">
                    Dr. {provider.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {provider.speciality || 'General Dermatology'}
                  </p>

                  {/* Rating */}
                  <div className="flex items-center gap-2 mb-3">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-4 h-4 ${
                            i < (provider.rating || 4)
                              ? 'text-warning fill-warning'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm text-gray-600">
                      {provider.rating || 4.5} ({provider.reviews || 0} reviews)
                    </span>
                  </div>

                  {/* Location */}
                  {provider.location && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                      <MapPin className="w-4 h-4" />
                      <span>{provider.location}</span>
                    </div>
                  )}

                  {/* Experience */}
                  <p className="text-sm text-gray-600 mb-4">
                    {provider.experience_years || 10}+ years of experience
                  </p>

                  {/* Book Button */}
                  <button
                    onClick={() => navigate(`/book-appointment/${provider.id}`)}
                    className="w-full px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium flex items-center justify-center gap-2"
                  >
                    <Calendar className="w-5 h-5" />
                    Book Appointment
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}