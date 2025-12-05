import axiosClient from './axiosClient';

/**
 * Create a new case
 * @param {Object} caseData
 * @param {string} caseData.title
 * @param {string} caseData.symptoms
 * @param {Array<string>} caseData.photo_ids - Array of analysis IDs
 * @returns {Promise}
 */
export const createCase = async (caseData) => {
  const response = await axiosClient.post('/api/case/cases', caseData);
  return response.data;
};

/**
 * Get all cases for current user
 * @returns {Promise<Array>}
 */
export const getCases = async () => {
  const response = await axiosClient.get('/api/case/cases');
  return response.data;
};

/**
 * Get case by ID
 * @param {number} caseId
 * @returns {Promise}
 */
export const getCaseById = async (caseId) => {
  const response = await axiosClient.get(`/api/case/cases/${caseId}`);
  return response.data;
};

/**
 * Update case
 * @param {number} caseId
 * @param {Object} caseData
 * @returns {Promise}
 */
export const updateCase = async (caseId, caseData) => {
  const response = await axiosClient.put(`/api/case/cases/${caseId}`, caseData);
  return response.data;
};

/**
 * Delete case
 * @param {number} caseId
 * @returns {Promise}
 */
export const deleteCase = async (caseId) => {
  const response = await axiosClient.delete(`/api/case/cases/${caseId}`);
  return response.data;
};