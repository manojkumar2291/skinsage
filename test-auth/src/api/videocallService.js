import axiosClient from './axiosClient';

/**
 * Get Agora token for video call
 * @param {Object} params
 * @param {string} params.channel_name - Usually appointment ID
 * @param {number} params.uid - User ID
 * @returns {Promise<{token: string, channel: string, uid: number, app_id: string}>}
 */
export const getVideoToken = async ({ appointmentId=2, uid=2 }) => {
  console.log("Fetching token for appointmentId:", appointmentId, "and uid:", uid);
  const response = await axiosClient.post('/api/videocall/get-agora-token', { 
    channel_name:String(appointmentId),
    uid:uid,
    role:'publisher'

   });
  return response.data;
};