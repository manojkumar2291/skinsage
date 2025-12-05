import axiosClient from './axiosClient';

/**
 * Upload image for AI skin analysis
 * @param {File} imageFile - The image file to analyze
 * @returns {Promise<{analysis_id: string, result: Object, confidence: number}>}
 */
export const analyzeImage = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await axiosClient.post('/api/v1/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Get analysis history
 * @returns {Promise<Array>}
 */
export const getAnalysisHistory = async () => {
  const response = await axiosClient.get('/api/v1/analysis/history');
  return response.data;
};

/**
 * Get specific analysis by ID
 * @param {string} analysisId
 * @returns {Promise}
 */
export const getAnalysisById = async (analysisId) => {
  const response = await axiosClient.get(`/api/v1/analysis/${analysisId}`);
  return response.data;
};