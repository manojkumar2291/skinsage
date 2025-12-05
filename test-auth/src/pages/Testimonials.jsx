import { Link } from 'react-router-dom';

export default function Testimonials() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Patient Testimonials
          </h1>
          <p className="text-lg text-gray-600">
            Coming soon - Read what our patients have to say
          </p>
        </div>
        <div className="text-center">
          <Link
            to="/"
            className="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}