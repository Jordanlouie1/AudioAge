# Voice Biomarker Analysis App

A full-stack web application that analyzes voice recordings to extract biomarkers for health monitoring. The app detects speech cadence, respiratory events (coughs/sneezes), pitch characteristics, and voice quality indicators.

## Features

- **Real-time Audio Recording**: Record voice samples directly in the browser
- **File Upload Support**: Upload existing audio files (MP3, WAV, M4A)
- **Comprehensive Voice Analysis**:
  - Speech cadence and rhythm patterns
  - Pitch analysis (mean, variation, range)
  - Respiratory event detection (coughs, sneezes)
  - Voice quality and tone assessment
  - Health insights generation

## Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: Python serverless functions
- **Audio Processing**: librosa, scipy, numpy
- **Deployment**: Vercel (full-stack)

## Project Structure

```
voice-biomarker-app/
├── api/
│   └── analyze-voice.py          # Python backend API
├── public/
│   └── index.html               # HTML template
├── src/
│   ├── index.js                 # React entry point
│   ├── index.css                # Global styles with Tailwind
│   └── App.js                   # Main React component
├── package.json                 # Node.js dependencies
├── requirements.txt             # Python dependencies
├── vercel.json                  # Vercel configuration
├── tailwind.config.js           # Tailwind configuration
├── postcss.config.js            # PostCSS configuration
└── README.md                    # This file
```

## Local Development Setup

### Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Git

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd voice-biomarker-app

# Install Node.js dependencies
npm install

# Install Python dependencies (for local testing)
pip install -r requirements.txt
```

### 2. Development Scripts

```bash
# Start React development server
npm start

# Build for production
npm run build

# Test the build locally
npx serve -s build
```

### 3. Local Backend Testing (Optional)

For local Python backend testing, you can use Vercel CLI:

```bash
# Install Vercel CLI
npm install -g vercel

# Start local development server
vercel dev
```

## Deployment to Vercel

### Method 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy from your project directory**:
```bash
# First deployment
vercel

# Follow the prompts:
# ? Set up and deploy "~/voice-biomarker-app"? [Y/n] Y
# ? Which scope should contain your project? [Your Account]
# ? Link to existing project? [y/N] N
# ? What's your project's name? voice-biomarker-app
# ? In which directory is your code located? ./

# Subsequent deployments
vercel --prod
```

### Method 2: Deploy via GitHub Integration

1. **Push code to GitHub**:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Configure project settings:
     - **Build Command**: `npm run build`
     - **Output Directory**: `build`
     - **Install Command**: `npm install`

3. **Deploy**: Vercel will automatically deploy on every push to main branch

### Method 3: Manual Deployment

1. **Build the project locally**:
```bash
npm run build
```

2. **Deploy using Vercel CLI**:
```bash
vercel --prod
```

## Configuration Files Explained

### `vercel.json`
Configures Vercel deployment settings:
- Sets up Python runtime for API functions
- Defines build configuration for React app
- Sets up routing for API and static files

### `package.json`
Defines Node.js dependencies and scripts:
- React and related packages
- Tailwind CSS for styling
- Build and development scripts

### `requirements.txt`
Python dependencies for audio processing:
- `librosa`: Audio analysis library
- `numpy`, `scipy`: Numerical computing
- `soundfile`: Audio file I/O

## 🔧 Environment Variables

No environment variables are required for basic functionality. All processing happens client-side (React) and in serverless functions (Python).

For production customization, you can add:

```bash
# Optional: Custom API endpoints
REACT_APP_API_BASE_URL=https://your-custom-domain.com

# Optional: Analytics tracking
REACT_APP_ANALYTICS_ID=your-analytics-id
```

Add these in Vercel dashboard under Project Settings → Environment Variables.

## 📱 Usage

1. **Access the deployed app** at your Vercel URL
2. **Record audio**:
   - Click the microphone button to start recording
   - Speak for 10-30 seconds for best results
   - Click stop to end recording
3. **Or upload an audio file**:
   - Click "Upload audio file"
   - Select MP3, WAV, or M4A file
4. **Analyze**:
   - Click "Analyze Voice"
   - View comprehensive biomarker results

## 🔬 Analysis Features

### Speech Cadence
- Words per minute calculation
- Speaking time ratio
- Speech rate classification (Slow/Normal/Fast)

### Pitch Analysis
- Mean fundamental frequency
- Pitch variation and range
- Voice stability metrics

### Respiratory Events
- Cough detection and counting
- Sneeze detection and counting
- Spectral analysis for event classification

### Voice Quality
- Tone quality assessment
- Harmonic-to-noise ratio
- Voice stability indicators

## 🛠️ Customization

### Adding New Analysis Features

1. **Extend the Python backend** (`api/analyze-voice.py`):
```python
def analyze_new_feature(self, y, sr):
    # Add your analysis logic
    return {'new_metric': calculated_value}
```

2. **Update the frontend** to display new metrics in the results section.

### Styling Changes

Modify `src/index.css` or component classes using Tailwind utilities.

### API Modifications

The backend API accepts multipart form data with audio files and returns JSON with analysis results.

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Ensure all dependencies in `package.json` are compatible
   - Check Node.js version (16+ required)

2. **Python Function Errors**:
   - Verify `requirements.txt` has correct library versions
   - Check Vercel function logs in dashboard

3. **Audio Recording Issues**:
   - Ensure HTTPS deployment (required for microphone access)
   - Check browser permissions for microphone

4. **Large Audio Files**:
   - Vercel has 50MB limit for serverless functions
   - Consider implementing file size limits in frontend

### Debug Steps

1. **Check Vercel function logs**:
   - Go to Vercel dashboard → Project → Functions tab
   - View real-time logs for errors

2. **Test locally**:
```bash
vercel dev
```

3. **Browser console**:
   - Open developer tools to check for JavaScript errors

## 📈 Performance Optimization

- Audio files are processed in memory (no persistent storage)
- Python libraries are cached between function calls
- Frontend uses React optimizations (memo, useCallback)
- Tailwind CSS is purged for smaller bundle size

## 🔐 Security Considerations

- Audio data is processed transiently (not stored permanently)
- CORS headers configured for cross-origin requests
- Input validation on both frontend and backend
- No authentication required (stateless design)

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For deployment issues:
- Check Vercel documentation: https://vercel.com/docs
- Review function logs in Vercel dashboard
- Ensure all configuration files are properly set up

For technical questions:
- Review the source code comments
- Check browser console for errors
- Verify audio file formats are supported

---

**Deployed on Vercel** 
