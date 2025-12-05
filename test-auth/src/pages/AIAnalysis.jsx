import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { analyzeImage } from '../api/analysisService';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle } from 'lucide-react';

export default function AIAnalysis() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [toast, setToast] = useState(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        setPreview(URL.createObjectURL(file));
        setResult(null);
      }
    }
  });

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setToast({
        message: 'Please select an image first',
        type: 'error'
      });
      return;
    }

    try {
      setAnalyzing(true);
      const data = await analyzeImage(selectedFile);
      setResult(data);
      setToast({
        message: 'Analysis complete!',
        type: 'success'
      });
    } catch (error) {
      setToast({
        message: error.detail || 'Analysis failed. Please try again.',
        type: 'error'
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-primary hover:text-primary-dark mb-4 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Skin Analysis</h1>
          <p className="text-gray-600">
            Upload a clear photo of your skin concern for instant AI-powered analysis
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Image</h2>

            {!preview ? (
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
                  isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-300 hover:border-primary'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                {isDragActive ? (
                  <p className="text-lg text-primary">Drop the image here...</p>
                ) : (
                  <>
                    <p className="text-lg text-gray-700 mb-2">
                      Drag & drop an image here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports: PNG, JPG, JPEG, WEBP
                    </p>
                  </>
                )}
              </div>
            ) : (
              <div>
                <div className="relative rounded-lg overflow-hidden mb-4">
                  <img
                    src={preview}
                    alt="Preview"
                    className="w-full h-auto max-h-96 object-contain bg-gray-100"
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    onClick={handleReset}
                    className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                    disabled={analyzing}
                  >
                    Choose Different Image
                  </button>
                  <button
                    onClick={handleAnalyze}
                    disabled={analyzing}
                    className="flex-1 px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {analyzing ? (
                      <>
                        <LoadingSpinner size="sm" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      'Analyze Image'
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Guidelines */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-primary" />
                Photo Guidelines
              </h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• Take photo in good lighting</li>
                <li>• Focus clearly on the affected area</li>
                <li>• Avoid blurry or dark images</li>
                <li>• Keep the area clean and dry</li>
              </ul>
            </div>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Results</h2>

            {!result ? (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <AlertCircle className="w-16 h-16 mb-4" />
                <p className="text-center">
                  Upload and analyze an image to see results here
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Confidence Score */}
                <div className="p-4 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-gray-900">Confidence Score</span>
                    <span className="text-2xl font-bold text-primary">
                      {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-primary to-secondary h-2 rounded-full transition-all"
                      style={{ width: `${result.confidence * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Detected Condition */}
                <div className="border-l-4 border-primary pl-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Detected Condition</h3>
                  <p className="text-lg text-gray-700">
                    {result.result?.condition || 'Analysis in progress...'}
                  </p>
                </div>

                {/* Description */}
                {result.result?.description && (
                  <div className="border-l-4 border-secondary pl-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                    <p className="text-gray-700">{result.result.description}</p>
                  </div>
                )}

                {/* Recommendations */}
                {result.result?.recommendations && (
                  <div className="border-l-4 border-success pl-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Recommendations</h3>
                    <p className="text-gray-700">{result.result.recommendations}</p>
                  </div>
                )}

                {/* Disclaimer */}
                <div className="p-4 bg-warning/10 border border-warning/30 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <strong>Important:</strong> This AI analysis is for informational purposes only
                    and should not replace professional medical advice. Please consult with a
                    certified dermatologist for accurate diagnosis and treatment.
                  </p>
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                  <button
                    onClick={() => navigate('/create-case')}
                    className="flex-1 px-4 py-3 bg-secondary text-white rounded-lg hover:bg-secondary/90 transition"
                  >
                    Create Case
                  </button>
                  <button
                    onClick={() => navigate('/find-provider')}
                    className="flex-1 px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
                  >
                    Find Dermatologist
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}