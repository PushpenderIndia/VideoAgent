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

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your API keys
cp .env.example .env
# Edit .env with your API keys
```

### Required API Keys

Create a `.env` file with:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
ELEVEN_LABS_API=your_elevenlabs_api_key_here
```

### Basic Usage

```bash
# Generate a video about any topic
python main.py

# Or use the orchestrator directly
python video_generation_orchestrator.py "photosynthesis"
```

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