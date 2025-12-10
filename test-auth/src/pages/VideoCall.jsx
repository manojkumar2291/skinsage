import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AgoraRTC from 'agora-rtc-sdk-ng';
import { Mic, MicOff, Video, VideoOff, PhoneOff, AlertCircle } from 'lucide-react';
import { getVideoToken } from '../api/videocallService';
import { useAuth } from '../contexts/AuthContext'; // Assuming you have this
import LoadingSpinner from '../components/LoadingSpinner';

// Create the client outside the component to prevent recreation on re-renders
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });

export default function VideoRoom() {
  const { appointmentId } = useParams();
  const { user } = useAuth(); // We need user.id
  const navigate = useNavigate();

  // State Management
  const [users, setUsers] = useState([]);
  const [localTracks, setLocalTracks] = useState([]);
  const [micOn, setMicOn] = useState(true);
  const [camOn, setCamOn] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isTooEarly, setIsTooEarly] = useState(false);

  // References for video DOM elements
  const localVideoRef = useRef(null);
  const remoteVideoRefs = useRef({});

  useEffect(() => {
    let isMounted = true;

    const initCall = async () => {
      try {
        if (!user) return;
        console.log("Initializing call for user:", user);

        // 1. Get Token from Backend
        const data = await getVideoToken(appointmentId, user.id);
        console.log("Received token data:", data);
        
        if (!isMounted) return;

        // 2. Setup Event Handlers
        client.on('user-published', handleUserPublished);
        client.on('user-unpublished', handleUserUnpublished);
        client.on('user-left', handleUserLeft);

        // 3. Join Channel
        await client.join(data.appId, data.channelName, data.token, data.uid);

        // 4. Create Local Tracks (Mic & Cam)
        const [audioTrack, videoTrack] = await AgoraRTC.createMicrophoneAndCameraTracks();
        
        if (!isMounted) {
            audioTrack.close();
            videoTrack.close();
            return;
        }

        setLocalTracks([audioTrack, videoTrack]);
        
        // Play local video immediately
        videoTrack.play(localVideoRef.current);

        // Publish tracks to channel
        await client.publish([audioTrack, videoTrack]);
        
        setLoading(false);

      } catch (err) {
        console.log("Video Call Error:", err);
        if (isMounted) {
          setLoading(false);
          // Check for specific "Too Early" error text from backend
          if (err.message.includes("Too early")) {
            setIsTooEarly(true);
            setError(err.message);
          } else {
            setError("Unable to join the call. Please check your connection.");
          }
        }
      }
    };

    initCall();

    // Cleanup on component unmount
    return () => {
      isMounted = false;
      localTracks.forEach(track => {
        track.stop();
        track.close();
      });
      client.removeAllListeners();
      client.leave();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appointmentId, user]);

  // --- Agora Event Handlers ---

  const handleUserPublished = async (user, mediaType) => {
    await client.subscribe(user, mediaType);

    if (mediaType === 'video') {
      setUsers(prev => {
        // Prevent duplicates
        if (prev.find(u => u.uid === user.uid)) return prev;
        return [...prev, user];
      });
    }

    if (mediaType === 'audio') {
      user.audioTrack.play();
    }
  };

  const handleUserUnpublished = (user, mediaType) => {
    if (mediaType === 'audio') {
      if (user.audioTrack) user.audioTrack.stop();
    }
    // We don't remove the user from state immediately on unpublish (they might just turn off cam)
  };

  const handleUserLeft = (user) => {
    setUsers(prev => prev.filter(u => u.uid !== user.uid));
  };

  // Play remote videos when `users` state updates
  useEffect(() => {
    users.forEach(user => {
      const ref = remoteVideoRefs.current[user.uid];
      if (ref && user.videoTrack) {
        user.videoTrack.play(ref);
      }
    });
  }, [users]);

  // --- Controls ---

  const toggleMic = async () => {
    if (localTracks[0]) {
      await localTracks[0].setEnabled(!micOn);
      setMicOn(!micOn);
    }
  };

  const toggleCam = async () => {
    if (localTracks[1]) {
      await localTracks[1].setEnabled(!camOn);
      setCamOn(!camOn);
    }
  };

  const leaveCall = async () => {
    localTracks.forEach(track => track.close());
    await client.leave();
    navigate('/dashboard'); // Return to dashboard
  };

  // --- Render Views ---

  if (loading) return (
    <div className="h-screen bg-gray-900 flex items-center justify-center text-white">
      <LoadingSpinner size="lg" />
      <span className="ml-4">Connecting to secure room...</span>
    </div>
  );

  // Error State / Too Early State
  if (error) return (
    <div className="h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
        <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${isTooEarly ? 'bg-yellow-100 text-yellow-600' : 'bg-red-100 text-red-600'}`}>
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {isTooEarly ? "Appointment Not Started" : "Connection Error"}
        </h2>
        <p className="text-gray-600 mb-6">{error}</p>
        <button 
          onClick={() => navigate('/dashboard')}
          className="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-gray-900 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="h-16 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6 z-10">
        <div className="flex items-center gap-2 text-white">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="font-semibold">Live Consultation #{appointmentId}</span>
        </div>
      </div>

      {/* Main Video Area */}
      <div className="flex-1 p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Local User (You) */}
        <div className="relative bg-black rounded-2xl overflow-hidden shadow-2xl border border-gray-700">
          <div ref={localVideoRef} className="w-full h-full object-cover transform -scale-x-100"></div>
          <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-sm px-3 py-1 rounded-lg text-white text-sm">
            You {micOn ? '' : '(Muted)'}
          </div>
        </div>

        {/* Remote Users (Doctor/Patient) */}
        {users.map(user => (
          <div key={user.uid} className="relative bg-black rounded-2xl overflow-hidden shadow-2xl border border-gray-700">
            <div 
              ref={el => remoteVideoRefs.current[user.uid] = el} 
              className="w-full h-full object-cover"
            ></div>
            <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-sm px-3 py-1 rounded-lg text-white text-sm">
              Remote User ({user.uid})
            </div>
          </div>
        ))}

        {users.length === 0 && (
          <div className="flex flex-col items-center justify-center bg-gray-800 rounded-2xl border border-gray-700 text-gray-400">
            <div className="animate-pulse flex flex-col items-center">
              <span className="text-lg">Waiting for the other participant to join...</span>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="h-20 bg-gray-800 border-t border-gray-700 flex items-center justify-center gap-6 z-10">
        <button 
          onClick={toggleMic}
          className={`p-4 rounded-full transition ${micOn ? 'bg-gray-700 text-white hover:bg-gray-600' : 'bg-red-500 text-white'}`}
        >
          {micOn ? <Mic /> : <MicOff />}
        </button>

        <button 
          onClick={leaveCall}
          className="p-4 rounded-full bg-red-600 text-white hover:bg-red-700 shadow-lg transform hover:scale-105 transition"
        >
          <PhoneOff />
        </button>

        <button 
          onClick={toggleCam}
          className={`p-4 rounded-full transition ${camOn ? 'bg-gray-700 text-white hover:bg-gray-600' : 'bg-red-500 text-white'}`}
        >
          {camOn ? <Video /> : <VideoOff />}
        </button>
      </div>
    </div>
  );
}