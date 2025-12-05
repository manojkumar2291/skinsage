import React, { useState, useEffect, createContext, useContext } from 'react';
import { 
  Camera, FileText, Calendar, Video, History, User, 
  LogOut, Menu, X, ChevronRight, Upload, Check, 
  Clock, MapPin, Star, AlertCircle, Loader2, 
  Phone, Mail, Shield, Heart, Award, Users, 
  Eye, EyeOff, Search, Filter, DollarSign
} from 'lucide-react';

// --- Auth Context ---
const AuthContext = createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setUser({
        id: '1',
        name: 'John Doe',
        email: 'john@example.com',
        role: 'patient',
        profileComplete: true
      });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const mockToken = 'mock-jwt-token';
    localStorage.setItem('token', mockToken);
    setUser({
      id: '1',
      name: 'John Doe',
      email,
      role: 'patient',
      profileComplete: true
    });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// --- Navigation Component ---
const Navigation = ({ navigate }) => {
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (!user) return null;

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: User },
    { path: '/ai-analysis', label: 'AI Analysis', icon: Camera },
    { path: '/cases', label: 'My Cases', icon: FileText },
    { path: '/providers', label: 'Find Doctor', icon: Users },
    { path: '/appointments', label: 'Appointments', icon: Calendar },
    { path: '/history', label: 'History', icon: History }
  ];

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <button onClick={() => navigate('/dashboard')} className="flex items-center space-x-2">
              <Heart className="w-8 h-8 text-teal-600" />
              <span className="text-xl font-bold text-gray-900">SkinSage</span>
            </button>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {navItems.map(item => {
              const IconComponent = item.icon;
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className="flex items-center space-x-1 px-3 py-2 rounded-lg text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition"
                >
                  <IconComponent className="w-4 h-4" />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              );
            })}
            <button
              onClick={logout}
              className="flex items-center space-x-1 px-3 py-2 rounded-lg text-red-600 hover:bg-red-50 transition"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm font-medium">Logout</span>
            </button>
          </div>

          <div className="md:hidden flex items-center">
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navItems.map(item => {
              const IconComponent = item.icon;
              return (
                <button
                  key={item.path}
                  onClick={() => {
                    navigate(item.path);
                    setMobileMenuOpen(false);
                  }}
                  className="flex items-center space-x-2 w-full px-3 py-2 rounded-lg text-gray-700 hover:bg-teal-50 hover:text-teal-600"
                >
                  <IconComponent className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
            <button
              onClick={logout}
              className="flex items-center space-x-2 w-full px-3 py-2 rounded-lg text-red-600 hover:bg-red-50"
            >
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

// --- Landing Page ---
const LandingPage = ({ navigate }) => {
  const features = [
    { icon: Camera, title: 'AI Skin Analysis', description: 'Get instant AI-powered analysis of your skin condition' },
    { icon: Video, title: 'Video Consultations', description: 'Connect with dermatologists from anywhere' },
    { icon: FileText, title: 'Case Management', description: 'Track your skin health journey' },
    { icon: Shield, title: 'Secure & Private', description: 'Your health data is encrypted and protected' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-blue-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Heart className="w-8 h-8 text-teal-600" />
              <span className="text-2xl font-bold text-gray-900">SkinSage</span>
            </div>
            <div className="space-x-4">
              <button onClick={() => navigate('/login')} className="px-4 py-2 text-teal-600 hover:text-teal-700 font-medium">Login</button>
              <button onClick={() => navigate('/register')} className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium">Sign Up</button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">Your Skin Health, <span className="text-teal-600">Simplified</span></h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">AI-powered skin analysis and virtual dermatology consultations. Get expert care from the comfort of your home.</p>
          <button onClick={() => navigate('/register')} className="px-8 py-4 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium text-lg inline-flex items-center space-x-2">
            <span>Get Started Free</span>
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-20 grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, idx) => {
            const IconComponent = feature.icon;
            return (
              <div key={idx} className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition">
                <IconComponent className="w-12 h-12 text-teal-600 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// --- Login Page ---
const LoginPage = ({ navigate }) => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email || !password) return;
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (error) {
      alert('Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <Heart className="w-12 h-12 text-teal-600 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900">Welcome Back</h2>
          <p className="text-gray-600 mt-2">Login to your SkinSage account</p>
        </div>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-4 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="••••••••"
              />
              <button onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600">
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>
          <button
            onClick={handleSubmit}
            disabled={loading || !email || !password}
            className="w-full py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium disabled:opacity-50 flex items-center justify-center"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Login'}
          </button>
        </div>
        <p className="text-center text-gray-600 mt-6">
          Don't have an account?{' '}
          <button onClick={() => navigate('/register')} className="text-teal-600 hover:text-teal-700 font-medium">Sign up</button>
        </p>
      </div>
    </div>
  );
};

// --- Register Page ---
const RegisterPage = ({ navigate }) => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '', confirmPassword: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      navigate('/login');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-blue-50 flex items-center justify-center px-4 py-8">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <Heart className="w-12 h-12 text-teal-600 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900">Create Account</h2>
          <p className="text-gray-600 mt-2">Join SkinSage today</p>
        </div>
        {/* Simplified form for brevity - logic remains the same */}
        <div className="space-y-4">
          <input type="text" value={formData.name} onChange={(e) => handleChange('name', e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500" placeholder="Full Name" />
          <input type="email" value={formData.email} onChange={(e) => handleChange('email', e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500" placeholder="Email" />
          <input type="password" value={formData.password} onChange={(e) => handleChange('password', e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500" placeholder="Password" />
          <input type="password" value={formData.confirmPassword} onChange={(e) => handleChange('confirmPassword', e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500" placeholder="Confirm Password" />
          <button onClick={handleSubmit} disabled={loading} className="w-full py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium disabled:opacity-50">
            {loading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Sign Up'}
          </button>
        </div>
        <p className="text-center text-gray-600 mt-6">
          Already have an account? <button onClick={() => navigate('/login')} className="text-teal-600 hover:text-teal-700 font-medium">Login</button>
        </p>
      </div>
    </div>
  );
};

// --- Dashboard ---
const Dashboard = ({ navigate }) => {
  const { user } = useAuth();
  const quickActions = [
    { icon: Camera, label: 'AI Analysis', path: '/ai-analysis', color: 'bg-teal-500' },
    { icon: FileText, label: 'New Case', path: '/cases', color: 'bg-blue-500' },
    { icon: Users, label: 'Find Doctor', path: '/providers', color: 'bg-purple-500' },
    { icon: Calendar, label: 'Appointments', path: '/appointments', color: 'bg-pink-500' }
  ];

  const stats = [
    { label: 'Total Analyses', value: '12', icon: Camera, color: 'text-teal-500' },
    { label: 'Active Cases', value: '3', icon: FileText, color: 'text-blue-500' },
    { label: 'Appointments', value: '5', icon: Calendar, color: 'text-purple-500' },
    { label: 'Video Calls', value: '8', icon: Video, color: 'text-pink-500' }
  ];

  const recentActivity = [
    { type: 'analysis', title: 'AI Skin Analysis Completed', time: '2 days ago', icon: Camera },
    { type: 'appointment', title: 'Appointment with Dr. Smith', time: '3 days ago', icon: Calendar },
    { type: 'case', title: 'New Case Created: Acne Treatment', time: '5 days ago', icon: FileText }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation navigate={navigate} />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-gradient-to-r from-teal-600 to-blue-600 rounded-2xl p-8 text-white mb-8">
          <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.name}!</h1>
          <p className="text-teal-100">Here is your skin health overview</p>
        </div>
        
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => {
            const IconComponent = stat.icon;
            return (
              <div key={idx} className="bg-white rounded-xl p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">{stat.label}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  </div>
                  <IconComponent className={`w-12 h-12 ${stat.color} opacity-20`} />
                </div>
              </div>
            );
          })}
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-4 gap-4">
            {quickActions.map((action, idx) => {
              const IconComponent = action.icon;
              return (
                <button key={idx} onClick={() => navigate(action.path)} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition text-left group">
                  <div className={`${action.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <p className="font-semibold text-gray-900">{action.label}</p>
                </button>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((item, idx) => {
              const IconComponent = item.icon;
              return (
                <div key={idx} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                  <div className="flex items-center space-x-4">
                    <div className="bg-teal-100 p-2 rounded-lg">
                      <IconComponent className="w-5 h-5 text-teal-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-sm text-gray-500">{item.time}</p>
                    </div>
                  </div>
                  <button className="text-teal-600 hover:text-teal-700 font-medium text-sm">View</button>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- AI Analysis Page ---
const AIAnalysisPage = ({ navigate }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => setSelectedImage(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setTimeout(() => {
      setResults({
        condition: 'Acne Vulgaris',
        confidence: 87,
        severity: 'Moderate',
        recommendations: [
          'Consult a dermatologist for personalized treatment',
          'Consider topical retinoids or benzoyl peroxide',
          'Maintain a gentle skincare routine',
          'Avoid touching or picking at affected areas'
        ]
      });
      setAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation navigate={navigate} />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">AI Skin Analysis</h1>
        <div className="bg-white rounded-xl shadow-sm p-8">
          {!selectedImage ? (
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-teal-400 transition">
              <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Skin Image</h3>
              <p className="text-gray-600 mb-6">Take a clear photo of the affected area for AI analysis</p>
              <label className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 cursor-pointer transition">
                <Upload className="w-5 h-5 mr-2" />
                Choose Image
                <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
              </label>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="relative">
                <img src={selectedImage} alt="Uploaded" className="w-full rounded-lg shadow-md" />
                <button onClick={() => { setSelectedImage(null); setResults(null); }} className="absolute top-4 right-4 bg-white p-2 rounded-full shadow-lg hover:bg-gray-100 transition">
                  <X className="w-5 h-5" />
                </button>
              </div>
              {!results && (
                <button onClick={handleAnalyze} disabled={analyzing} className="w-full py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium disabled:opacity-50 flex items-center justify-center transition">
                  {analyzing ? <><Loader2 className="w-5 h-5 mr-2 animate-spin" />Analyzing...</> : <><Camera className="w-5 h-5 mr-2" />Analyze Image</>}
                </button>
              )}
              {results && (
                <div className="space-y-6">
                  <div className="bg-teal-50 border-2 border-teal-200 rounded-lg p-6">
                    <div className="flex items-start space-x-4">
                      <div className="bg-teal-600 p-2 rounded-full"><Check className="w-6 h-6 text-white" /></div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">Analysis Complete</h3>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center"><span className="font-medium text-gray-700">Detected Condition:</span><span className="text-gray-900 font-semibold">{results.condition}</span></div>
                          <div className="flex justify-between items-center"><span className="font-medium text-gray-700">Confidence:</span><span className="text-gray-900 font-semibold">{results.confidence}%</span></div>
                          <div className="flex justify-between items-center"><span className="font-medium text-gray-700">Severity:</span><span className="text-gray-900 font-semibold">{results.severity}</span></div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center"><AlertCircle className="w-5 h-5 mr-2 text-blue-600" />AI Recommendations</h4>
                    <ul className="space-y-2">
                      {results.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start space-x-2"><ChevronRight className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">{rec}</span></li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// --- Cases Page (Fixed) ---
const CasesPage = ({ navigate }) => {
  const cases = [
    { id: 1, title: 'Acne Treatment', status: 'Active', date: '2024-01-15', provider: 'Dr. Smith' },
    { id: 2, title: 'Eczema Follow-up', status: 'Under Review', date: '2024-01-10', provider: 'Dr. Johnson' },
    { id: 3, title: 'Skin Rash', status: 'Closed', date: '2023-12-20', provider: 'Dr. Williams' }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'Under Review': return 'bg-yellow-100 text-yellow-800';
      case 'Closed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation navigate={navigate} />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Cases</h1>
          <button className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center">
            <FileText className="w-4 h-4 mr-2" /> New Case
          </button>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="divide-y divide-gray-200">
            {cases.map((caseItem) => (
              <div key={caseItem.id} className="p-6 hover:bg-gray-50 transition flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{caseItem.title}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                      <span className="flex items-center"><Calendar className="w-4 h-4 mr-1" /> {caseItem.date}</span>
                      <span className="flex items-center"><User className="w-4 h-4 mr-1" /> {caseItem.provider}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(caseItem.status)}`}>
                    {caseItem.status}
                  </span>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Placeholder Pages (To prevent crashes) ---
const ProvidersPage = ({ navigate }) => (
  <div className="min-h-screen bg-gray-50"><Navigation navigate={navigate} /><div className="p-8 text-center"><h1 className="text-2xl font-bold">Find Doctors</h1><p>Coming Soon</p></div></div>
);

const AppointmentsPage = ({ navigate }) => (
  <div className="min-h-screen bg-gray-50"><Navigation navigate={navigate} /><div className="p-8 text-center"><h1 className="text-2xl font-bold">Appointments</h1><p>Coming Soon</p></div></div>
);

const HistoryPage = ({ navigate }) => (
  <div className="min-h-screen bg-gray-50"><Navigation navigate={navigate} /><div className="p-8 text-center"><h1 className="text-2xl font-bold">History</h1><p>Coming Soon</p></div></div>
);

// --- Main App Component (Handles Routing) ---
const App = () => {
  const [currentPath, setCurrentPath] = useState('/');

  // Custom router function passed to all components
  const navigate = (path) => {
    setCurrentPath(path);
    window.scrollTo(0, 0);
  };

  const renderPage = () => {
    switch (currentPath) {
      case '/': return <LandingPage navigate={navigate} />;
      case '/login': return <LoginPage navigate={navigate} />;
      case '/register': return <RegisterPage navigate={navigate} />;
      case '/dashboard': return <Dashboard navigate={navigate} />;
      case '/ai-analysis': return <AIAnalysisPage navigate={navigate} />;
      case '/cases': return <CasesPage navigate={navigate} />;
      case '/providers': return <ProvidersPage navigate={navigate} />;
      case '/appointments': return <AppointmentsPage navigate={navigate} />;
      case '/history': return <HistoryPage navigate={navigate} />;
      default: return <LandingPage navigate={navigate} />;
    }
  };

  return (
    <AuthProvider>
      {renderPage()}
    </AuthProvider>
  );
};

export default App;