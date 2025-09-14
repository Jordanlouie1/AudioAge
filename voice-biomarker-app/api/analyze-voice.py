from http.server import BaseHTTPRequestHandler
import json
import io
import numpy as np
import librosa
import scipy.signal
from scipy.stats import kurtosis, skew
import tempfile
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            # Parse multipart form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Extract audio file from form data
            audio_data = self.extract_audio_from_form_data(post_data)
            
            if not audio_data:
                self.wfile.write(json.dumps({'error': 'No audio data found'}).encode())
                return

            # Analyze the audio
            analysis_result = self.analyze_voice_biomarkers(audio_data)
            
            # Send response
            self.wfile.write(json.dumps(analysis_result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def extract_audio_from_form_data(self, data):
        """Extract audio data from multipart form data"""
        try:
            # Find the file boundary
            boundary_start = data.find(b'Content-Type: audio/')
            if boundary_start == -1:
                return None
            
            # Find the start of actual audio data (after double CRLF)
            audio_start = data.find(b'\r\n\r\n', boundary_start) + 4
            
            # Find the end boundary
            end_boundary = data.find(b'\r\n--', audio_start)
            if end_boundary == -1:
                audio_data = data[audio_start:]
            else:
                audio_data = data[audio_start:end_boundary]
                
            return audio_data
        except:
            return None

    def analyze_voice_biomarkers(self, audio_data):
        """Main function to analyze voice biomarkers"""
        try:
            # Save audio to temporary file and load with librosa
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name

            # Load audio file
            y, sr = librosa.load(tmp_file_path, sr=None)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            # Initialize results dictionary
            results = {}
            
            # 1. Cadence Analysis (Speech Rate)
            results.update(self.analyze_cadence(y, sr))
            
            # 2. Pitch Analysis
            results.update(self.analyze_pitch(y, sr))
            
            # 3. Respiratory Event Detection
            results.update(self.detect_respiratory_events(y, sr))
            
            # 4. Tone and Voice Quality
            results.update(self.analyze_voice_quality(y, sr))
            
            # 5. Generate Health Insights
            results['health_insights'] = self.generate_health_insights(results)
            
            return results
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}

    def analyze_cadence(self, y, sr):
        """Analyze speech cadence and rhythm"""
        # Voice Activity Detection using energy-based method
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)    # 10ms hop
        
        # Calculate energy
        frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
        energy = np.sum(frames ** 2, axis=0)
        
        # Threshold for voice activity (adaptive)
        energy_threshold = np.percentile(energy, 30)
        voiced_frames = energy > energy_threshold
        
        # Calculate speaking time
        total_time = len(y) / sr
        speaking_time = np.sum(voiced_frames) * hop_length / sr
        
        # Estimate words per minute (rough approximation)
        # Average syllable duration is ~0.2-0.3 seconds
        estimated_syllables = speaking_time / 0.25
        estimated_words = estimated_syllables / 2  # ~2 syllables per word average
        cadence_wpm = (estimated_words / total_time) * 60 if total_time > 0 else 0
        
        return {
            'cadence': cadence_wpm,
            'speaking_time_ratio': speaking_time / total_time if total_time > 0 else 0,
            'speech_rate': 'Normal' if 120 <= cadence_wpm <= 160 else ('Slow' if cadence_wpm < 120 else 'Fast')
        }

    def analyze_pitch(self, y, sr):
        """Analyze pitch characteristics"""
        # Extract fundamental frequency (F0)
        f0, voiced_flag, voiced_probs = librosa.pyin(y, 
                                                    fmin=librosa.note_to_hz('C2'),
                                                    fmax=librosa.note_to_hz('C7'))
        
        # Remove unvoiced frames
        voiced_f0 = f0[voiced_flag]
        
        if len(voiced_f0) == 0:
            return {
                'pitch_mean': 0,
                'pitch_std': 0,
                'pitch_range': 0,
                'pitch_variation': 'No voiced speech detected'
            }
        
        pitch_mean = np.mean(voiced_f0)
        pitch_std = np.std(voiced_f0)
        pitch_range = np.max(voiced_f0) - np.min(voiced_f0)
        
        # Classify pitch variation
        if pitch_std < 20:
            variation = 'Low'
        elif pitch_std < 40:
            variation = 'Normal'
        else:
            variation = 'High'
        
        return {
            'pitch_mean': float(pitch_mean),
            'pitch_std': float(pitch_std),
            'pitch_range': float(pitch_range),
            'pitch_variation': variation
        }

    def detect_respiratory_events(self, y, sr):
        """Detect coughs and sneezes"""
        # Preprocess audio
        y_filtered = scipy.signal.medfilt(y, kernel_size=3)
        
        # Calculate spectral features for event detection
        hop_length = 512
        stft = librosa.stft(y_filtered, hop_length=hop_length)
        magnitude = np.abs(stft)
        
        # Spectral centroid and bandwidth
        spectral_centroids = librosa.feature.spectral_centroid(S=magnitude, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(S=magnitude, sr=sr)[0]
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y_filtered, hop_length=hop_length)[0]
        
        # Energy envelope
        energy = np.sum(magnitude ** 2, axis=0)
        
        # Detect sudden energy spikes (potential coughs/sneezes)
        energy_threshold = np.percentile(energy, 85)
        energy_spikes = energy > energy_threshold
        
        # Detect high-frequency content (characteristic of coughs)
        high_freq_threshold = np.percentile(spectral_centroids, 80)
        high_freq_events = spectral_centroids > high_freq_threshold
        
        # Combine features to detect events
        potential_events = energy_spikes & high_freq_events
        
        # Count events (group consecutive frames)
        events = []
        in_event = False
        event_start = 0
        
        for i, is_event in enumerate(potential_events):
            if is_event and not in_event:
                in_event = True
                event_start = i
            elif not is_event and in_event:
                in_event = False
                event_duration = (i - event_start) * hop_length / sr
                if 0.1 < event_duration < 1.0:  # Reasonable duration for cough/sneeze
                    events.append((event_start, i, event_duration))
        
        # Classify events (simple heuristic)
        cough_count = 0
        sneeze_count = 0
        
        for start, end, duration in events:
            avg_zcr = np.mean(zcr[start:end])
            avg_bandwidth = np.mean(spectral_bandwidth[start:end])
            
            # Sneezes tend to have higher ZCR and bandwidth
            if avg_zcr > np.percentile(zcr, 70) and avg_bandwidth > np.percentile(spectral_bandwidth, 70):
                sneeze_count += 1
            else:
                cough_count += 1
        
        return {
            'cough_count': cough_count,
            'sneeze_count': sneeze_count,
            'total_respiratory_events': len(events)
        }

    def analyze_voice_quality(self, y, sr):
        """Analyze voice tone and quality indicators"""
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Extract other spectral features
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_flux = np.diff(librosa.stft(y))
        spectral_flux = np.mean(np.abs(spectral_flux))
        
        # Harmonic-to-noise ratio estimation
        harmonic, percussive = librosa.effects.hpss(y)
        hnr = np.mean(harmonic ** 2) / (np.mean(percussive ** 2) + 1e-10)
        hnr_db = 10 * np.log10(hnr + 1e-10)
        
        # Voice quality assessment
        mfcc_variance = np.var(mfccs, axis=1)
        voice_stability = np.mean(mfcc_variance)
        
        # Determine tone quality
        if hnr_db > 10 and voice_stability < 0.5:
            tone_quality = 'Clear'
        elif hnr_db > 5 and voice_stability < 1.0:
            tone_quality = 'Normal'
        elif hnr_db > 0:
            tone_quality = 'Slightly Rough'
        else:
            tone_quality = 'Rough'
        
        return {
            'tone_quality': tone_quality,
            'voice_stability': float(voice_stability),
            'harmonic_noise_ratio': float(hnr_db),
            'spectral_flux': float(spectral_flux)
        }

    def generate_health_insights(self, results):
        """Generate health insights based on analysis"""
        insights = []
        
        # Cadence insights
        if 'cadence' in results:
            cadence = results['cadence']
            if cadence < 100:
                insights.append("Slow speech rate may indicate fatigue or respiratory issues.")
            elif cadence > 180:
                insights.append("Rapid speech rate detected, possibly indicating anxiety or excitement.")
        
        # Respiratory event insights
        cough_count = results.get('cough_count', 0)
        sneeze_count = results.get('sneeze_count', 0)
        
        if cough_count > 3:
            insights.append("Frequent coughing detected, consider monitoring respiratory health.")
        if sneeze_count > 2:
            insights.append("Multiple sneezes detected, may indicate allergic response.")
        
        # Voice quality insights
        tone_quality = results.get('tone_quality', 'Normal')
        if tone_quality in ['Rough', 'Slightly Rough']:
            insights.append("Voice quality indicates possible vocal cord irritation or fatigue.")
        
        # Pitch insights
        pitch_variation = results.get('pitch_variation', 'Normal')
        if pitch_variation == 'Low':
            insights.append("Limited pitch variation may indicate monotone speech or vocal fatigue.")
        elif pitch_variation == 'High':
            insights.append("High pitch variation detected, indicating expressive speech patterns.")
        
        if not insights:
            insights.append("Voice analysis indicates normal speech patterns and vocal health.")
        
        return " ".join(insights)