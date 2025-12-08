import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { getProviderById } from '../api/providerService';
import { getCases } from '../api/caseService';
import { requestAppointment } from '../api/appointmentService';
import { createOrder, verifyPayment } from '../api/paymentService';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { Calendar, Clock, FileText, CreditCard } from 'lucide-react';

const appointmentSchema = z.object({
  // Change z.number() to z.coerce.number()
  case_id: z.coerce.number().min(1, 'Please select a case'),
  preferred_slot: z.string().min(1, 'Please select a date and time'),
});

export default function BookAppointment() {
  const { providerId } = useParams();
  const navigate = useNavigate();
  const [provider, setProvider] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [toast, setToast] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(appointmentSchema),
  });

  useEffect(() => {
    loadData();
  }, [providerId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [providerData, casesData] = await Promise.all([
        getProviderById(providerId),
        getCases(),
      ]);
      setProvider(providerData);
      setCases(casesData);
    } catch (error) {
      setToast({
        message: 'Failed to load data',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (appointmentId, amount) => {
    console.log('Initiating payment for appointment ID:', appointmentId, 'Amount:', amount);
    try {
      // Create Razorpay order
      const orderData = await createOrder({
        appointment_id: String(appointmentId),
        amount: amount,
        currency: "INR"
      });
      console.log('Order created:', orderData);

      // Load Razorpay script
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.async = true;
      document.body.appendChild(script);

      script.onload = () => {
        const options = {
          key: import.meta.env.VITE_RAZORPAY_KEY_ID || "rzp_test_RkhfxJvitmevKb",
          amount: orderData.amount,
          currency: orderData.currency,
          order_id: orderData.order.id,
          name: 'SkinSage',
          description: 'Dermatology Consultation',
          handler: async (response) => {
            console.log(response)
            try {
              await verifyPayment({
                razorpay_order_id: String(response.razorpay_order_id),
                razorpay_payment_id:String(response.razorpay_payment_id),
                razorpay_signature:String(response.razorpay_signature),
              });

              setToast({
                message: 'Appointment booked successfully!',
                type: 'success',
              });

              setTimeout(() => {
                navigate('/visit-history');
              }, 2000);
            } catch (error) {
              setToast({
                message: 'Payment verification failed',
                type: 'error',
              });
            }
          },
          prefill: {
            name: 'Patient Name',
            email: 'patient@example.com',
          },
          theme: {
            color: '#0ea5e9',
          },
        };

        const razorpay = new window.Razorpay(options);
        razorpay.open();
      };
    } catch (error) {
      console.log('Payment initialization error:', error);
      setToast({
        message: 'Payment initialization failed',
        type: 'error',
      });
    }
  };

  const onSubmit = async (data) => {
    console.log('Booking appointment with data:', data);
    try {
      setBooking(true);
      const appointment = await requestAppointment({
        provider_id: parseInt(providerId),
        case_id: data.case_id,
        preferred_slot: data.preferred_slot,
      });
      console.log('Appointment requested:', appointment);
      // Initiate payment
      await handlePayment(appointment.id, 500); // ₹500 consultation fee
    } catch (error) {
      setToast({
        message: error.detail || 'Failed to book appointment',
        type: 'error',
      });
    } finally {
      setBooking(false);
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
    <div className="bg-white shadow-lg rounded-md px-4 py-3 border z-50 fixed top-5 right-5">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/find-provider')}
            className="text-primary hover:text-primary-dark mb-4 flex items-center gap-2"
          >
            ← Back to Providers
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Book Appointment</h1>
          <p className="text-gray-600">Schedule your consultation with Dr. {provider?.full_name}</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Provider Info */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
              <div className="w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-2xl font-bold text-white mx-auto mb-4">
                {provider?.full_name?.charAt(0) || 'D'}
              </div>
              <h3 className="text-xl font-bold text-gray-900 text-center mb-2">
                Dr. {provider?.full_name}
              </h3>
              <p className="text-sm text-gray-600 text-center mb-4">
                {provider?.specialization || 'General Dermatology'}
              </p>
              <div className="border-t border-gray-200 pt-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm text-gray-600">Consultation Fee</span>
                  <span className="text-lg font-bold text-primary">₹500</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Duration</span>
                  <span className="text-sm font-medium">30 minutes</span>
                </div>
              </div>
            </div>
          </div>

          {/* Booking Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-8">
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Select Case */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <FileText className="w-5 h-5 inline mr-2" />
                    Select Case <span className="text-error">*</span>
                  </label>
                  {cases.length === 0 ? (
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <p className="text-gray-600 mb-4">
                        No cases available. Please create a case first.
                      </p>
                      <button
                        type="button"
                        onClick={() => navigate('/create-case')}
                        className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
                      >
                        Create Case
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {cases.map((caseItem) => (
                        <label
                          key={caseItem.id}
                          className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:border-primary transition has-[:checked]:border-primary has-[:checked]:bg-primary/5"
                        >
                          <input
                            {...register('case_id', { valueAsNumber: true })}
                            type="radio"
                            value={caseItem.id}
                            className="mt-1 mr-3"
                          />
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">{caseItem.title}</div>
                            <div className="text-sm text-gray-600 mt-1">
                              {caseItem.symptoms?.substring(0, 100)}...
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                  )}
                  {errors.case_id && (
                    <p className="mt-2 text-sm text-error">{errors.case_id.message}</p>
                  )}
                </div>

                {/* Select Date & Time */}
                <div>
                  <label htmlFor="preferred_slot" className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="w-5 h-5 inline mr-2" />
                    Preferred Date & Time <span className="text-error">*</span>
                  </label>
                  <input
                    {...register('preferred_slot')}
                    type="datetime-local"
                    id="preferred_slot"
                    min={new Date().toISOString().slice(0, 16)}
                    className={`w-full px-4 py-3 border ${
                      errors.preferred_slot ? 'border-error' : 'border-gray-300'
                    } rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition`}
                  />
                  {errors.preferred_slot && (
                    <p className="mt-1 text-sm text-error">{errors.preferred_slot.message}</p>
                  )}
                  <p className="mt-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4 inline mr-1" />
                    The provider will confirm your preferred time slot
                  </p>
                </div>

                {/* Payment Info */}
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex gap-3">
                    <CreditCard className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-gray-700">
                      <p className="font-semibold mb-1">Payment Information</p>
                      <p>
                        You'll be redirected to a secure payment gateway to complete your booking.
                        Your appointment will be confirmed after successful payment.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Submit */}
                <div className="flex gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => navigate('/find-provider')}
                    className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                    disabled={booking}
                  >
                    Cancel
                  </button>
                  <button
  type="submit"
  // REMOVED: cases.length === 0 check
  disabled={booking} 
  className={`flex-1 px-6 py-3 rounded-lg transition font-medium flex items-center justify-center gap-2 ${
    booking 
      ? "bg-primary/70 cursor-not-allowed" 
      : "bg-primary hover:bg-primary-dark text-white"
  }`}
>
  {booking ? (
    <>
      <LoadingSpinner size="sm" />
      <span>Processing...</span>
    </>
  ) : (
    'Proceed to Payment'
  )}
</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}