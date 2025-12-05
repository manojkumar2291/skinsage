import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AgoraRTC from 'agora-rtc-sdk-ng';
import { LocalUser, RemoteUser, useRTCClient, useLocalMicrophoneTrack, useLocalCameraTrack, usePublish, useRemoteUsers } from 'agora-rtc-react';
import { getAgoraToken } from '../api/videocallService';
import { getAppointmentById } from '../api/appointmentService';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { Mic, MicOff, Video, VideoOff, PhoneOff, MessageSquare } from 'lucide-react';

const APP_ID = import.meta.env.VITE_AGORA_APP_ID || 'your-agora-app-id';

export default function VideoCall() {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const [appointment, setAppointment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);
  const [inCall, setInCall] = useState(false);
  const [toast, setToast] = useState(null);
  const [token, setToken] = useState('');
  const [channelName, setChannelName] = useState('');
  const [uid, setUid] = useState(0);

  const agoraEngine = useRTCClient(AgoraRTC.createClient({ codec: 'vp8', mode: 'rtc' }));
  const { localMicrophoneTrack } = useLocalMicrophoneTrack();
  const { localCameraTrack } = useLocalCameraTrack();
  const remoteUsers = useRemoteUsers();

  usePublish([localMicrophoneTrack, localCameraTrack]);

  const [micOn, setMicOn] = useState(true);
  const [cameraOn, setCameraOn] = useState(true);

  useEffect(() => {
    loadAppointment();
  }, [appointmentId]);

  const loadAppointment = async () => {
    try {
      setLoading(true);
      const data = await getAppointmentById(appointmentId);
      setAppointment(data);
    } catch (error) {
      setToast({
        message: 'Failed to load appointment',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const joinCall = async () => {
    try {
      setJoining(true);
      
      // Get Agora token
      const tokenData = await getAgoraToken({
        channel_name: `appointment-${appointmentId}`,
        uid: Math.floor(Math.random() * 100000),
      });

      setToken(tokenData.token);
      setChannelName(tokenData.channel);
      setUid(tokenData.uid);

      // Join channel
      await agoraEngine.join(APP_ID, tokenData.channel, tokenData.token, tokenData.uid);
      setInCall(true);

      setToast({
        message: 'Joined video call successfully',
        type: 'success',
      });
    } catch (error) {
      setToast({
        message: error.message || 'Failed to join call',
        type: 'error',
      });
    } finally {
      setJoining(false);
    }
  };

  const leaveCall = async () => {
    try {
      await agoraEngine.leave();
      setInCall(false);
      navigate('/visit-history');
    } catch (error) {
      console.error('Error leaving call:', error);
    }
  };

  const toggleMic = async () => {
    if (localMicrophoneTrack) {
      await localMicrophoneTrack.setEnabled(!micOn);
      setMicOn(!micOn);
    }
  };

  const toggleCamera = async () => {
    if (localCameraTrack) {
      await localCameraTrack.setEnabled(!cameraOn);
      setCameraOn(!cameraOn);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {!inCall ? (
        // Pre-call screen
        <div className="min-h-screen flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Video Consultation</h1>
            
            <div className="mb-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-bold">
                  {appointment?.provider_name?.charAt(0) || 'D'}
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Dr. {appointment?.provider_name}</h3>
                  <p className="text-sm text-gray-600">Dermatologist</p>
                </div>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg mb-6">
                <p className="text-sm text-gray-700">
                  <strong>Note:</strong> Make sure your camera and microphone are working properly before joining the call.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <button
                onClick={joinCall}
                disabled={joining}
                className="w-full px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {joining ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Joining...</span>
                  </>
                ) : (
                  <>
                    <Video className="w-5 h-5" />
                    <span>Join Video Call</span>
                  </>
                )}
              </button>

              <button
                onClick={() => navigate('/visit-history')}
                className="w-full px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      ) : (
        // In-call screen
        <div className="h-screen flex flex-col">
          {/* Video Grid */}
          <div className="flex-1 relative">
            {/* Remote Users */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full p-4">
              {remoteUsers.length === 0 ? (
                <div className="flex items-center justify-center bg-gray-800 rounded-lg">
                  <div className="text-center text-white">
                    <div className="w-24 h-24 bg-gray-700 rounded-full flex items-center justify-center text-3xl font-bold mx-auto mb-4">
                      {appointment?.provider_name?.charAt(0) || 'D'}
                    </div>
                    <p className="text-lg">Waiting for Dr. {appointment?.provider_name} to join...</p>
                  </div>
                </div>
              ) : (
                remoteUsers.map((user) => (
                  <div key={user.uid} className="relative bg-gray-800 rounded-lg overflow-hidden">
                    <RemoteUser user={user} />
                  </div>
                ))
              )}

              {/* Local User (Picture-in-Picture) */}
              <div className="absolute bottom-24 right-8 w-64 h-48 bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                <LocalUser
                  audioTrack={localMicrophoneTrack}
                  videoTrack={localCameraTrack}
                  cameraOn={cameraOn}
                  micOn={micOn}
                  playAudio={false}
                  playVideo={cameraOn}
                />
                <div className="absolute bottom-2 left-2 text-white text-sm bg-black/50 px-2 py-1 rounded">
                  You
                </div>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="bg-gray-800 p-6">
            <div className="max-w-4xl mx-auto flex items-center justify-center gap-4">
              {/* Microphone */}
              <button
                onClick={toggleMic}
                className={`w-14 h-14 rounded-full flex items-center justify-center transition ${
                  micOn
                    ? 'bg-gray-700 hover:bg-gray-600 text-white'
                    : 'bg-error hover:bg-error/90 text-white'
                }`}
              >
                {micOn ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
              </button>

              {/* Camera */}
              <button
                onClick={toggleCamera}
                className={`w-14 h-14 rounded-full flex items-center justify-center transition ${
                  cameraOn
                    ? 'bg-gray-700 hover:bg-gray-600 text-white'
                    : 'bg-error hover:bg-error/90 text-white'
                }`}
              >
                {cameraOn ? <Video className="w-6 h-6" /> : <VideoOff className="w-6 h-6" />}
              </button>

              {/* End Call */}
              <button
                onClick={leaveCall}
                className="w-14 h-14 bg-error hover:bg-error/90 rounded-full flex items-center justify-center text-white transition"
              >
                <PhoneOff className="w-6 h-6" />
              </button>

              {/* Chat */}
              <button
                className="w-14 h-14 bg-gray-700 hover:bg-gray-600 rounded-full flex items-center justify-center text-white transition"
              >
                <MessageSquare className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}