import axiosClient from './axiosClient';

/**
 * Get Agora token for video call
 * @param {Object} params
 * @param {string} params.channel_name - Usually appointment ID
 * @param {number} params.uid - User ID
 * @returns {Promise<{token: string, channel: string, uid: number, app_id: string}>}
 */
export const getAgoraToken = async (params) => {
  const response = await axiosClient.get('/api/videocall/get-agora-token', { params });
  return response.data;
};