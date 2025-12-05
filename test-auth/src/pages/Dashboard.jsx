import { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import API from "../api";
import { Brain, Calendar, FileText, Users, LogOut, User } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user: authUser, logout } = useAuth();
  const [user, setUser] = useState(null);

  useEffect(() => {
    API.get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => alert("Token expired or invalid"));
  }, []);

  const features = [
    {
      icon: Brain,
      title: 'AI Skin Analysis',
      description: 'Upload photos for instant AI-powered skin analysis',
      color: 'from-primary to-primary-dark',
      path: '/ai-analysis',
    },
    {
      icon: FileText,
      title: 'My Cases',
      description: 'Manage your skin health cases',
      color: 'from-secondary to-purple-600',
      path: '/cases',
    },
    {
      icon: Users,
      title: 'Find Dermatologist',
      description: 'Browse and book appointments with certified dermatologists',
      color: 'from-success to-green-600',
      path: '/find-provider',
    },
    {
      icon: Calendar,
      title: 'Visit History',
      description: 'View your appointments and consultation history',
      color: 'from-warning to-orange-600',
      path: '/visit-history',
    },
  ];

  const handleLogout = () => {
    localStorage.clear();
    if (logout) logout();
    window.location.href = "/";
  };

  const displayUser = user || authUser;

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-white to-secondary/5">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-bold">
                {displayUser?.full_name?.charAt(0) || 'U'}
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">
                  Welcome, {displayUser?.full_name || 'User'}!
                </h2>
                <p className="text-sm text-gray-600">{displayUser?.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/complete-profile')}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
              >
                <User className="w-4 h-4" />
                Profile
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-error hover:bg-error/10 rounded-lg transition flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Your Skin Health Dashboard
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Access AI-powered analysis, connect with dermatologists, and manage your skin health journey
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <button
                key={index}
                onClick={() => navigate(feature.path)}
                className="group bg-white rounded-xl shadow-md hover:shadow-xl transition-all p-6 text-left"
              >
                <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary transition">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm">
                  {feature.description}
                </p>
              </button>
            );
          })}
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-xl shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Stats</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-primary/5 rounded-lg">
              <div className="text-4xl font-bold text-primary mb-2">0</div>
              <div className="text-gray-600">AI Analyses</div>
            </div>
            <div className="text-center p-6 bg-secondary/5 rounded-lg">
              <div className="text-4xl font-bold text-secondary mb-2">0</div>
              <div className="text-gray-600">Cases Created</div>
            </div>
            <div className="text-center p-6 bg-success/5 rounded-lg">
              <div className="text-4xl font-bold text-success mb-2">0</div>
              <div className="text-gray-600">Consultations</div>
            </div>
          </div>
        </div>

        {/* User Data Debug (from original) */}
        {user && (
          <div className="bg-white rounded-xl shadow-md p-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">User Data (Debug)</h2>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-auto text-sm">
              {JSON.stringify(user, null, 2)}
            </pre>
          </div>
        )}

        {/* CTA Section */}
        <div className="mt-12 bg-gradient-to-r from-primary to-secondary text-white rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Need Immediate Assistance?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Connect with a dermatologist today for expert care
          </p>
          <button
            onClick={() => navigate('/find-provider')}
            className="px-8 py-4 bg-white text-primary rounded-lg hover:bg-gray-100 transition font-semibold text-lg"
          >
            Find a Dermatologist
          </button>
        </div>
      </div>
    </div>
  );
}