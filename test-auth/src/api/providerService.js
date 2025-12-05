import axiosClient from './axiosClient';

/**
 * Get list of providers with optional filters
 * @param {Object} params
 * @param {string} params.specialization
 * @param {number} params.skip
 * @param {number} params.limit
 * @returns {Promise<Array>}
 */
export const getProviders = async (params = {}) => {
  const response = await axiosClient.get('/api/provider/providers', { params });
  return response.data;
};

/**
 * Get provider details by ID
 * @param {number} providerId
 * @returns {Promise}
 */
export const getProviderById = async (providerId) => {
  const response = await axiosClient.get(`/api/provider/providers/${providerId}`);
  return response.data;
};

/**
 * Search providers
 * @param {string} query
 * @returns {Promise<Array>}
 */
export const searchProviders = async (query) => {
  const response = await axiosClient.get('/api/provider/providers/search', {
    params: { q: query }
  });
  return response.data;
};