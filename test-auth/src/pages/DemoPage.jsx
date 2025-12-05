import { Link } from 'react-router-dom';

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            SkinSage Frontend Demo
          </h1>
          <p className="text-gray-600 mb-6">
            This page demonstrates all the available pages and components in the application.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-primary mb-4">Public Pages</h2>
            <div className="space-y-2">
              <Link
                to="/"
                className="block px-4 py-2 bg-primary bg-opacity-10 text-primary rounded hover:bg-opacity-20 transition"
              >
                Landing Page
              </Link>
              <Link
                to="/login"
                className="block px-4 py-2 bg-primary bg-opacity-10 text-primary rounded hover:bg-opacity-20 transition"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="block px-4 py-2 bg-primary bg-opacity-10 text-primary rounded hover:bg-opacity-20 transition"
              >
                Register
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-secondary mb-4">Protected Pages</h2>
            <div className="space-y-2">
              <Link
                to="/dashboard"
                className="block px-4 py-2 bg-secondary bg-opacity-10 text-secondary rounded hover:bg-opacity-20 transition"
              >
                Dashboard
              </Link>
              <Link
                to="/complete-profile"
                className="block px-4 py-2 bg-secondary bg-opacity-10 text-secondary rounded hover:bg-opacity-20 transition"
              >
                Complete Profile
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}