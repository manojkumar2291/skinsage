import axiosClient from './axiosClient';

/**
 * Upload visit summary (Provider)
 * @param {number} appointmentId - The appointment ID
 * @param {Object} data - Visit summary data
 * @param {string} data.diagnosis - Diagnosis text
 * @param {string} data.summary - Summary text
 * @param {string} data.next_steps - Next steps text
 * @returns {Promise} - Response data
 */
export const uploadVisitSummary = async (appointmentId, data) => {
  const response = await axiosClient.post(`/api/visits/visits/${appointmentId}/summary`, data);
  return response.data;
};

/**
 * Start follow-up chat (Provider)
 * @param {number} appointmentId - The appointment ID
 * @returns {Promise} - Chat session data
 */
export const startFollowUpChat = async (appointmentId) => {
  const response = await axiosClient.post(`/api/visits/visits/${appointmentId}/follow-up`);
  return response.data;
};

/**
 * Get visit summary (Patient)
 * @param {number} visitId - The visit ID
 * @returns {Promise} - Visit summary data
 */
export const getVisitSummary = async (visitId) => {
  const response = await axiosClient.get(`/api/visits/visits/${visitId}`);
  return response.data;
};

/**
 * Send follow-up message
 * @param {number} visitId
 * @param {string} message
 * @returns {Promise}
 */
export const sendFollowUpMessage = async (visitId, message) => {
  const response = await axiosClient.post(`/api/visits/visits/${visitId}/follow-up`, {
    message
  });
  return response.data;
};

/**
 * Get visit history
 * @returns {Promise<Array>}
 */
export const getVisitHistory = async () => {
 const response = await axiosClient.get('/api/appointment/appointments');  return response.data;
};