import { Link } from 'react-router-dom';
import { Brain, Shield, Video, Clock } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/5 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Your Skin Health,{' '}
            <span className="text-primary">AI-Powered</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Get instant AI analysis of your skin concerns and connect with certified dermatologists for personalized care.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/register"
              className="px-8 py-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-semibold text-lg"
            >
              Get Started Free
            </Link>
            <Link
              to="/login"
              className="px-8 py-4 border-2 border-primary text-primary rounded-lg hover:bg-primary/5 transition font-semibold text-lg"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mt-20">
          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <Brain className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">AI Analysis</h3>
            <p className="text-gray-600">
              Advanced AI technology analyzes your skin condition instantly with high accuracy.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
              <Video className="w-6 h-6 text-secondary" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Video Consultations</h3>
            <p className="text-gray-600">
              Connect with certified dermatologists through secure video calls from home.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-success" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Secure & Private</h3>
            <p className="text-gray-600">
              Your health data is encrypted and protected with industry-leading security.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="w-12 h-12 bg-warning/10 rounded-lg flex items-center justify-center mb-4">
              <Clock className="w-6 h-6 text-warning" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">24/7 Access</h3>
            <p className="text-gray-600">
              Get care whenever you need it with our round-the-clock platform availability.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-20">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Upload Photo</h3>
              <p className="text-gray-600">
                Take a clear photo of your skin concern and upload it to our platform.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">AI Analysis</h3>
              <p className="text-gray-600">
                Our AI analyzes your photo and provides instant preliminary insights.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Expert Care</h3>
              <p className="text-gray-600">
                Book a video consultation with a dermatologist for personalized treatment.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-20 bg-gradient-to-r from-primary to-secondary text-white rounded-2xl p-12 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Take Control of Your Skin Health?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of users who trust SkinSage for their dermatological care.
          </p>
          <Link
            to="/register"
            className="inline-block px-8 py-4 bg-white text-primary rounded-lg hover:bg-gray-100 transition font-semibold text-lg"
          >
            Start Your Journey Today
          </Link>
        </div>
      </div>
    </div>
  );
}