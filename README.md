# GPT Voice Assistant

A Python-based voice assistant that uses OpenAI's GPT model for natural language processing and speech recognition for voice commands.

## Features

- Voice recognition using Google Speech Recognition
- Text-to-speech output using pyttsx3
- OpenAI GPT integration for intelligent responses
- Built-in commands for opening websites (YouTube, Google)
- Error handling for API quota limits and authentication issues

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- OpenAI API key
- Microphone for voice input
- Speakers for voice output

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Narsimulu-G/GPT_Assistant.git
   cd GPT_Assistant
   ```

2. **Install required packages:**
   ```bash
   pip install openai SpeechRecognition pyttsx3 pyaudio
   ```

3. **Set up your API key:**
   - Copy `apikey_template.py` to `apikey.py`
   - Replace `"your_openai_api_key_here"` with your actual OpenAI API key
   - Get your API key from [OpenAI Platform](https://platform.openai.com/)

4. **Run the application:**
   ```bash
   python app.py
   ```

## Usage

- **Voice Commands:** Speak naturally to ask questions or give commands
- **Built-in Commands:**
  - "Open YouTube" - Opens YouTube in your default browser
  - "Open Google" - Opens Google in your default browser
  - "Bye" or "Goodbye" - Exits the application
- **AI Responses:** Ask any question and get intelligent responses from GPT

## Troubleshooting

### PyAudio Installation Issues (Windows)
If you encounter issues installing PyAudio on Windows, try:
```bash
pip install pipwin
pipwin install pyaudio
```

### API Quota Issues
If you get quota errors, check your OpenAI billing at https://platform.openai.com/account/billing

### Microphone Issues
- Ensure your microphone is properly connected and set as default
- Check microphone permissions in your system settings

## Security Note

- Never commit your actual API key to version control
- The `apikey.py` file is included in `.gitignore` to prevent accidental exposure
- Use environment variables for production deployments

## License

This project is open source and available under the MIT License.
