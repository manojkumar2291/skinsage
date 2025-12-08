import axiosClient from './axiosClient';

/**
 * Create Razorpay order
 * @param {Object} orderData
 * @param {number} orderData.appointment_id
 * @param {number} orderData.amount
 * @returns {Promise<{order_id: string, amount: number, currency: string}>}
 */
export const createOrder = async (orderData) => {
  console.log('Creating order with data:', orderData);
  const response = await axiosClient.post('/api/payment/payments/create-order', orderData);
  return response.data;
};

/**
 * Verify Razorpay payment
 * @param {Object} paymentData
 * @param {string} paymentData.razorpay_order_id
 * @param {string} paymentData.razorpay_payment_id
 * @param {string} paymentData.razorpay_signature
 * @returns {Promise}
 */
export const verifyPayment = async (paymentData) => {

  const response = await axiosClient.post('/api/payment/payments/verify', paymentData);
  return response.data;
};

/**
 * Get payment history
 * @returns {Promise<Array>}
 */
export const getPaymentHistory = async () => {
  const response = await axiosClient.get('/api/payment/payments/history');
  return response.data;
};