# Video Generation Agent System

A multi-agent AI system that automatically generates educational videos using ADK (Agent Development Kit). The system uses 5 specialized agents to create videos from topic to final output.

## 🎬 Overview

This system creates 2-minute educational videos automatically through a pipeline of AI agents:

1. **Video Script Agent** - Generates engaging scripts using Google Gemini
2. **Audio Generation Agent** - Creates voiceovers using ElevenLabs/gTTS  
3. **Video Illustration Agent** - Finds relevant video clips from Getty Images
4. **Manim Illustration Agent** - Creates mathematical/graphical animations
5. **Video Compiler Agent** - Combines everything using MoviePy

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- FFmpeg (for video processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd VideoAgent
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the sample environment file
   cp env.sample .env
   
   # Edit .env with your actual API keys
   nano .env  # or use your preferred editor
   ```

### Required API Keys

You'll need to obtain the following API keys:

#### 1. Google Gemini API Key (REQUIRED)
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create a new API key
- Add to `.env` file: `GEMINI_API_KEY=your_key_here`

#### 2. ElevenLabs API Key (Optional but recommended)
- Go to [ElevenLabs](https://elevenlabs.io/)
- Sign up and get your API key
- Add to `.env` file: `ELEVEN_LABS_API=your_key_here`
- If not provided, system falls back to Google Text-to-Speech

### System Dependencies

Install FFmpeg for video processing:

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
- Download from [FFmpeg official site](https://ffmpeg.org/download.html)
- Add to system PATH

### Verify Installation

Run the test suite to ensure everything is working:
```bash
python3 test_system.py
```

### Basic Usage

1. **Using the main interface:**
   ```bash
   python3 main.py
   ```

2. **Using the orchestrator directly:**
   ```bash
   python3 video_generation_orchestrator.py "photosynthesis"
   ```

3. **Testing individual agents:**
   ```bash
   python3 demo.py
   ```

### Output Locations

Generated videos will be saved in:
- `static/compiled_videos/` - Final video outputs
- `static/manim_outputs/` - Mathematical animations

## 🤖 Agent Architecture

### 1. Video Script Agent
- Generates structured video scripts in JSON format
- Uses Google Gemini for content creation

### 2. Audio Generation Agent  
- Converts text to speech using ElevenLabs API
- Falls back to gTTS if ElevenLabs fails

### 3. Video Illustration Agent
- Finds relevant video clips from Getty Images
- Uses Gemini AI to generate search keywords

### 4. Manim Illustration Agent
- Creates mathematical/scientific animations
- Uses Gemini AI to detect mathematical content

### 5. Video Compiler Agent
- Combines all elements using MoviePy
- Adds intro/outro and handles final compilation

## 🛠️ Troubleshooting

### Common Issues

1. **ModuleNotFoundError: google.adk**
   ```bash
   pip install google-adk
   ```

2. **FFmpeg not found**
   - Install FFmpeg as described in setup instructions
   - Ensure it's added to your system PATH

3. **API Key errors**
   - Check that your `.env` file exists
   - Verify API keys are valid and properly formatted
   - Ensure no extra spaces around the `=` sign

4. **Manim rendering issues**
   ```bash
   # Install additional dependencies
   pip install manim[gui]
   ```

5. **MoviePy video compilation errors**
   - Check that all input files exist
   - Verify FFmpeg installation
   - Check file permissions in output directories

### Debug Mode

Enable debug mode in your `.env` file:
```bash
DEBUG_MODE=true
```

This will provide verbose logging to help identify issues.

### Getting Help

1. Run the test suite: `python3 test_system.py`
2. Check the logs for specific error messages
3. Ensure all API keys are valid and have sufficient credits/quota

## 📝 License

This project is open source and available under the MIT License.