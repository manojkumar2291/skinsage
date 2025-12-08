import axiosClient from './axiosClient';

/**
 * Request a new appointment
 * @param {Object} appointmentData
 * @param {number} appointmentData.provider_id
 * @param {number} appointmentData.case_id
 * @param {string} appointmentData.preferred_slot - ISO datetime string
 * @returns {Promise}
 */
export const requestAppointment = async (appointmentData) => {
  const response = await axiosClient.post('/api/appointment/appointments/request', appointmentData);
  return response.data;
};

/**
 * Confirm appointment (Provider only)
 * @param {number} appointmentId
 * @returns {Promise}
 */
export const confirmAppointment = async (appointmentId, appointmentData) => {
 
  const response = await axiosClient.patch(
    `/api/appointment/appointments/${appointmentId}/confirm`,
    appointmentData
  );
  return response.data;
};

/**
 * Cancel appointment
 * @param {number} appointmentId
 * @returns {Promise}
 */
export const cancelAppointment = async (appointmentId) => {
  const response = await axiosClient.post(`/api/appointment/appointments/${appointmentId}/cancel`);
  return response.data;
};

/**
 * Get all appointments
 * @param {Object} params
 * @param {string} params.status - 'pending', 'confirmed', 'completed', 'cancelled'
 * @returns {Promise<Array>}
 */
export const getAppointments = async (params = {}) => {
  const response = await axiosClient.get('/api/appointment/appointments', { params });
  return response.data;
};

/**
 * Get appointment by ID
 * @param {number} appointmentId
 * @returns {Promise}
 */
export const getAppointmentById = async (appointmentId) => {
  const response = await axiosClient.get(`/api/appointment/appointments/${appointmentId}`);
  return response.data;
};