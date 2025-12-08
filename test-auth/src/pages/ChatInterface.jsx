import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { sendFollowUpMessage, getVisitSummary } from '../api/visitService';
import LoadingSpinner from '../components/LoadingSpinner';
import { Send, User, ArrowLeft, MoreVertical, AlertTriangle } from 'lucide-react';
import { differenceInDays } from 'date-fns';

export default function ChatInterface() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [visit, setVisit] = useState(null);
  const [isExpired, setIsExpired] = useState(false);
  const messagesEndRef = useRef(null);

  // Mock messages for demonstration (replace with actual API if available)
  // Since visitService.js only has sendFollowUpMessage and getVisitSummary (which might return chat history?)
  // I will assume getVisitSummary might return history or I'll just use local state for now + API send.

  useEffect(() => {
    loadChatData();
  }, [visitId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatData = async () => {
    try {
      setLoading(true);
      const data = await getVisitSummary(visitId);
      setVisit(data);

      // Check expiration (7 days from appointment)
      if (data.appointment_date) {
        const daysDiff = differenceInDays(new Date(), new Date(data.appointment_date));
        if (daysDiff > 7) {
          setIsExpired(true);
        }
      }

      // If the API returns chat history, set it here.
      // For now, I'll initialize with a system message or empty.
      setMessages([
        {
          id: 1,
          text: `This is the start of your follow-up chat with Dr. ${data.provider_name}.`,
          sender: 'system',
          timestamp: new Date().toISOString(),
        }
      ]);
    } catch (error) {
      console.error('Failed to load chat:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      setSending(true);

      // Optimistic update
      const tempMessage = {
        id: Date.now(),
        text: newMessage,
        sender: 'user',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempMessage]);
      setNewMessage('');

      // API call
      await sendFollowUpMessage(visitId, newMessage);

      // In a real app, you might re-fetch messages or get the confirmed message back
    } catch (error) {
      console.error('Failed to send message:', error);
      // Handle error (maybe remove optimistic message or show error toast)
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-100 rounded-full transition"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
            <User className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="font-bold text-gray-900">Dr. {visit?.provider_name}</h1>
            <p className="text-xs text-green-600 flex items-center gap-1">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              Online
            </p>
          </div>
        </div>
        <button className="p-2 hover:bg-gray-100 rounded-full transition">
          <MoreVertical className="w-5 h-5 text-gray-600" />
        </button>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'system' ? (
              <div className="w-full text-center my-4">
                <span className="text-xs text-gray-500 bg-gray-200 px-3 py-1 rounded-full">
                  {msg.text}
                </span>
              </div>
            ) : (
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2 shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-primary text-white rounded-br-none'
                    : 'bg-white text-gray-900 rounded-bl-none'
                }`}
              >
                <p>{msg.text}</p>
                <p
                  className={`text-[10px] mt-1 text-right ${
                    msg.sender === 'user' ? 'text-primary-100' : 'text-gray-400'
                  }`}
                >
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4 sticky bottom-0">
        {isExpired ? (
          <div className="max-w-4xl mx-auto p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center justify-center gap-2 text-yellow-800">
            <AlertTriangle className="w-5 h-5" />
            <p className="font-medium">This chat session has expired (limit: 7 days after appointment).</p>
          </div>
        ) : (
          <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-gray-100 border-0 rounded-full px-6 py-3 focus:ring-2 focus:ring-primary focus:bg-white transition outline-none"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!newMessage.trim() || sending}
              className="bg-primary hover:bg-primary-dark text-white p-3 rounded-full transition disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
