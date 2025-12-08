import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import './AIAnalysis.css';

const MAX_IMAGES = 3;

// --- Local Question Data ---
const diagnosticQuestions = [
  {
    prompt: "What is the approximate duration of the issue? (e.g., when did you first notice it)",
    options: ["Less than 1 week", "1 to 4 weeks", "1 to 6 months", "More than 6 months"],
    key: "duration"
  },
  {
    prompt: "How would you describe the severity or discomfort level?",
    options: ["Mild (barely noticeable)", "Moderate (interferes sometimes)", "Severe (interferes significantly)", "Painful and debilitating"],
    key: "severity"
  },
  {
    prompt: "What is the main symptom besides the visual appearance?",
    options: ["Itching", "Burning/Stinging", "Pain", "Dryness/Flakiness", "No major symptom"],
    key: "symptom"
  },
  {
    prompt: "Have you tried any treatments (creams, medication) for this issue, and did they help?",
    options: ["No prior treatments", "Over-the-counter treatment (helped)", "Over-the-counter treatment (no help)", "Prescription treatment (helped)", "Prescription treatment (no help)"],
    key: "treatment"
  }
];

const conditionOptions = {
  skin: [
    'Rash', 'Acne / Pimples', 'Eczema', 'Psoriasis', 'Dermatitis',
    'Hives / Urticaria', 'Fungal Infection', 'Moles / Dark Spots',
    'Burns / Wounds', 'Swelling / Inflammation', 'Skin Discoloration',
    'Warts', 'Dry / Flaky Skin', 'Other Skin Issue'
  ],
  hair: [
    'Hair Loss / Alopecia', 'Dandruff', 'Scalp Irritation / Redness',
    'Thinning Hair', 'Bald Patches', 'Scalp Infection', 'Itchy Scalp',
    'Greasy Hair / Oily Scalp', 'Dry Hair / Dry Scalp', 'Hair Breakage',
    'Scalp Psoriasis', 'Other Hair Issue'
  ]
};

export default function AIAnalysis() {
  const navigate = useNavigate();
  const chatBoxRef = useRef(null);

  // State
  const [messages, setMessages] = useState([]);
  const [stage, setStage] = useState('selection'); // selection, chat, image_upload, analysis_complete
  const [currentQuestionStep, setCurrentQuestionStep] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [qnaSummary, setQnaSummary] = useState({});
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  // Initial Selection State
  const [category, setCategory] = useState('');
  const [condition, setCondition] = useState('');

  // Initial greeting
  useEffect(() => {
    startNewConversation();
  }, []);

  useEffect(() => {
    // Auto scroll to bottom
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const startNewConversation = () => {
    setMessages([{ role: 'bot', content: 'Hello! I am your Skin & Hair Issue Analyzer. Let us start by selecting the category and specific condition you are experiencing.' }]);
    setStage('selection');
    setCurrentQuestionStep(0);
    setSelectedFiles([]);
    setPreviews([]);
    setQnaSummary({});
    setCategory('');
    setCondition('');
    setLoading(false);
    setAnalysisResult(null);
  };

  const handleStartDiagnosis = () => {
    const userSelection = `Category: ${category}, Condition: ${condition}`;
    setQnaSummary(prev => ({ ...prev, category, condition }));
    setMessages(prev => [...prev, { role: 'user', content: userSelection }]);

    setStage('chat');
    setCurrentQuestionStep(0);
    askNextQuestion(0);
  };

  const askNextQuestion = (stepIndex) => {
    if (stepIndex < diagnosticQuestions.length) {
      const currentQ = diagnosticQuestions[stepIndex];
      // We add the question to messages, but the UI handles buttons separately based on currentQuestionStep
      // Actually, standard chat UI: bot asks, user answers.
      // So we add bot message.
      setMessages(prev => [...prev, { role: 'bot', content: currentQ.prompt }]);
    } else {
      // Q&A Complete
      setMessages(prev => [...prev, { role: 'bot', content: 'Thank you. Your symptom history is complete. Please upload 1 to 3 clear, well-lit images of the affected area(s) for visual analysis.' }]);
      setStage('image_upload');
    }
  };

  const handleAnswer = (answerText, key) => {
    // Add user answer to chat
    setMessages(prev => [...prev, { role: 'user', content: answerText }]);

    // Update summary
    setQnaSummary(prev => ({ ...prev, [key]: answerText }));

    // Move to next
    const nextStep = currentQuestionStep + 1;
    setCurrentQuestionStep(nextStep);

    // Slight delay for bot response
    setTimeout(() => {
      askNextQuestion(nextStep);
    }, 300);
  };

  const handleFileSelect = (e) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).slice(0, MAX_IMAGES);
      setSelectedFiles(files);

      // Create previews
      const newPreviews = files.map(file => URL.createObjectURL(file));
      setPreviews(newPreviews);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (selectedFiles.length === 0) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Please select at least one image to upload.' }]);
      return;
    }

    setMessages(prev => [...prev, { role: 'user', content: `Uploaded ${selectedFiles.length} image(s) for analysis.` }]);
    setLoading(true);

    const formData = new FormData();
    // Send entire Q&A history + selection as context
    // Constructing message history for the backend
    const contextMessages = [
        ...messages.map(m => ({ role: m.role, content: m.content })),
        // Ensure Q&A summary is explicitly part of the context if needed,
        // though the chat history contains it.
    ];
    formData.append('messages', JSON.stringify(contextMessages));

    selectedFiles.forEach(file => {
      formData.append('image_files', file);
    });

    try {
      // Using axiosClient which has base URL configured
      // Note: The HTML used /api/v1/analyze. Assuming this matches backend routes.
      // If backend is on port 8000 and vite proxies or axios has baseURL.
      const response = await axiosClient.post('/api/v1/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;
      setAnalysisResult(data);

      let responseText = data.reply;
      if (data.recommendation_needed) {
        responseText = 'URGENT ALERT: ' + responseText;
      }

      setMessages(prev => [...prev, { role: 'bot', content: responseText }]);
      setStage('analysis_complete');

    } catch (error) {
      console.error("Analysis error:", error);
      let errorMsg = 'Could not complete analysis. Please try again.';
      if (error.response?.data?.detail) {
        errorMsg += ' Detail: ' + error.response.data.detail;
      }
      setMessages(prev => [...prev, { role: 'bot', content: 'ERROR: ' + errorMsg }]);
    } finally {
      setLoading(false);
    }
  };

  const handleBookAppointment = () => {
    setMessages(prev => [...prev, { role: 'bot', content: 'Redirecting you to find a dermatologist...' }]);
    setTimeout(() => {
        navigate('/find-provider');
    }, 1000);
  };

  return (
    <div className="ai-chat-wrapper">
      <div className="chat-container">
        <div className="chat-header">Skin & Hair Issue Analyzer</div>

        <div className="chat-box" ref={chatBoxRef}>
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-content" dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br>') }} />
            </div>
          ))}
          {loading && (
            <div className="status-message">Assistant is analyzing data...</div>
          )}
        </div>

        <div className="input-area">

          {/* STEP 1: Initial Selection */}
          {stage === 'selection' && (
            <div className="initial-selection-container">
              <div className="select-group">
                <label htmlFor="issue-category">Select Issue Category:</label>
                <select
                  id="issue-category"
                  value={category}
                  onChange={(e) => {
                    setCategory(e.target.value);
                    setCondition(''); // Reset condition when category changes
                  }}
                >
                  <option value="">-- Choose Category --</option>
                  <option value="skin">Skin Issue</option>
                  <option value="hair">Hair Issue</option>
                </select>
              </div>

              {category && (
                <div className="select-group">
                  <label htmlFor="condition-type">Select Specific Condition:</label>
                  <select
                    id="condition-type"
                    value={condition}
                    onChange={(e) => setCondition(e.target.value)}
                  >
                    <option value="">-- Choose Condition --</option>
                    {conditionOptions[category].map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
              )}

              <button
                className="action-button start-button"
                onClick={handleStartDiagnosis}
                disabled={!category || !condition}
              >
                Start Diagnosis
              </button>
            </div>
          )}

          {/* STEP 2: Option-Based Chat */}
          {stage === 'chat' && !loading && (
            <div className="selection-input-container">
              {currentQuestionStep < diagnosticQuestions.length && (
                diagnosticQuestions[currentQuestionStep].options.map(optionText => (
                  <button
                    key={optionText}
                    className="selection-button"
                    onClick={() => handleAnswer(optionText, diagnosticQuestions[currentQuestionStep].key)}
                  >
                    {optionText}
                  </button>
                ))
              )}
            </div>
          )}

          {/* STEP 3: Image Upload */}
          {stage === 'image_upload' && (
            <div className="image-upload-row">
              <div className="image-preview-container">
                {previews.map((src, idx) => (
                  <img key={idx} src={src} className="image-preview-thumb" alt="preview" />
                ))}
              </div>
              <div className="upload-controls">
                <input
                  type="file"
                  id="image-file"
                  accept="image/*"
                  multiple
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                  disabled={loading}
                />
                <label htmlFor="image-file" className="upload-label">
                  Select Images (Max 3)
                </label>
                <button
                  className="action-button upload-button"
                  onClick={handleUploadAndAnalyze}
                  disabled={selectedFiles.length === 0 || loading}
                >
                  {loading ? 'Analyzing...' : 'Analyze Images'}
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: Final Actions */}
          {stage === 'analysis_complete' && (
            <div className="final-actions-row">
              {analysisResult?.recommendation_needed && (
                <button
                  className="action-button book-btn"
                  onClick={handleBookAppointment}
                >
                  Book Appointment Now
                </button>
              )}
              <button
                className="action-button restart-btn"
                onClick={startNewConversation}
                style={{ flexGrow: analysisResult?.recommendation_needed ? 1 : 2 }}
              >
                Start New Conversation
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
