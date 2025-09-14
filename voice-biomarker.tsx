import React, { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Upload, Activity, Volume2, Zap, Clock } from 'lucide-react';

const VoiceBiomarkerApp = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError('Error accessing microphone: ' + err.message);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const analyzeAudio = async () => {
    if (!audioBlob) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await fetch('/api/analyze-voice', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();
      setAnalysis(result);
    } catch (err) {
      setError('Error analyzing audio: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      setAudioBlob(file);
      setError(null);
    } else {
      setError('Please select a valid audio file');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Activity className="w-8 h-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-900">Voice Biomarker Analysis</h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Record or upload audio to analyze voice characteristics including cadence, 
            respiratory events, tone, and pitch patterns for health insights.
          </p>
        </header>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Recording Section */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Mic className="w-5 h-5 text-indigo-600" />
              Audio Input
            </h2>
            
            <div className="space-y-6">
              {/* Recording Controls */}
              <div className="text-center">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isRecording 
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                      : 'bg-indigo-600 hover:bg-indigo-700'
                  } text-white shadow-lg hover:shadow-xl`}
                >
                  {isRecording ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
                </button>
                <p className="mt-3 text-sm text-gray-600">
                  {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
                </p>
              </div>

              {/* File Upload */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 transition-colors">
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                <label className="cursor-pointer">
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <span className="text-indigo-600 hover:text-indigo-700 font-medium">
                    Upload audio file
                  </span>
                </label>
                <p className="text-xs text-gray-500 mt-1">MP3, WAV, M4A supported</p>
              </div>

              {/* Audio Preview */}
              {audioBlob && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-700 mb-2">Audio ready for analysis:</p>
                  <audio 
                    controls 
                    src={URL.createObjectURL(audioBlob)}
                    className="w-full"
                  />
                </div>
              )}

              {/* Analyze Button */}
              <button
                onClick={analyzeAudio}
                disabled={!audioBlob || loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 
                         text-white font-medium py-3 px-4 rounded-lg transition-colors
                         disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    Analyze Voice
                  </>
                )}
              </button>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-600" />
              Analysis Results
            </h2>

            {analysis ? (
              <div className="space-y-6">
                {/* Voice Characteristics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-4 h-4 text-blue-600" />
                      <span className="font-medium text-blue-900">Cadence</span>
                    </div>
                    <p className="text-2xl font-bold text-blue-700">
                      {analysis.cadence?.toFixed(1) || 'N/A'} <span className="text-sm font-normal">WPM</span>
                    </p>
                  </div>

                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Volume2 className="w-4 h-4 text-green-600" />
                      <span className="font-medium text-green-900">Pitch</span>
                    </div>
                    <p className="text-2xl font-bold text-green-700">
                      {analysis.pitch_mean?.toFixed(0) || 'N/A'} <span className="text-sm font-normal">Hz</span>
                    </p>
                  </div>
                </div>

                {/* Respiratory Events */}
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h3 className="font-medium text-yellow-900 mb-3">Respiratory Events</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-yellow-700">Coughs detected:</span>
                      <span className="font-bold ml-2">{analysis.cough_count || 0}</span>
                    </div>
                    <div>
                      <span className="text-yellow-700">Sneezes detected:</span>
                      <span className="font-bold ml-2">{analysis.sneeze_count || 0}</span>
                    </div>
                  </div>
                </div>

                {/* Detailed Metrics */}
                <div className="bg-purple-50 rounded-lg p-4">
                  <h3 className="font-medium text-purple-900 mb-3">Voice Characteristics</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-purple-700">Pitch Variation:</span>
                      <span className="font-medium">{analysis.pitch_std?.toFixed(1) || 'N/A'} Hz</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-700">Tone Quality:</span>
                      <span className="font-medium">{analysis.tone_quality || 'Normal'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-700">Speech Rate:</span>
                      <span className="font-medium">{analysis.speech_rate || 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Health Insights */}
                {analysis.health_insights && (
                  <div className="bg-indigo-50 rounded-lg p-4">
                    <h3 className="font-medium text-indigo-900 mb-3">Health Insights</h3>
                    <p className="text-sm text-indigo-800">{analysis.health_insights}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Activity className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg font-medium mb-2">No analysis yet</p>
                <p className="text-sm">Record or upload audio to see biomarker analysis</p>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">About Voice Biomarker Analysis</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">What we analyze:</h4>
              <ul className="space-y-1">
                <li>• Speech cadence and rhythm patterns</li>
                <li>• Vocal pitch and frequency characteristics</li>
                <li>• Respiratory events (coughs, sneezes)</li>
                <li>• Voice tone and quality indicators</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Applications:</h4>
              <ul className="space-y-1">
                <li>• Early health screening</li>
                <li>• Respiratory health monitoring</li>
                <li>• Speech therapy assessment</li>
                <li>• Wellness tracking over time</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceBiomarkerApp;