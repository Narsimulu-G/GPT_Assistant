from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import queue
from openai import OpenAI
from apikey import api_data
import speech_recognition as sr
import pyttsx3
import json
import os
from system_controller import SystemController

app = Flask(__name__, static_folder='frontend/dist/assets', template_folder='frontend/dist')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Serve React App
@app.route('/')
def serve_index():
    return send_from_directory('frontend/dist', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('frontend/dist', path)):
        return send_from_directory('frontend/dist', path)
    return send_from_directory('frontend/dist', 'index.html')

# Initialize
Model = "gpt-4o"
client = OpenAI(api_key=api_data)
sys_controller = SystemController()

# Global state
assistant_state = {
    'is_running': False,
    'status': 'idle',
    'system_info': {}
}

message_queue = queue.Queue()

# Text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    """Text to speech"""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

def parse_command_locally(query):
    """Parse common commands locally without API"""
    query_lower = query.lower()
    
    # Open application commands
    if "open" in query_lower or "launch" in query_lower or "start" in query_lower:
        for app in ['chrome', 'calculator', 'notepad', 'paint', 'edge', 'explorer', 'vs code', 'word', 'excel']:
            if app in query_lower:
                return {"action": "open_app", "parameters": {"app_name": app}, "confirmation_needed": False}
        
        # Check for websites
        if any(site in query_lower for site in ['youtube', 'google', 'facebook', 'twitter', 'instagram', '.com', '.org']):
            words = query_lower.split()
            for word in words:
                if '.com' in word or '.org' in word or word in ['youtube', 'google', 'facebook']:
                    return {"action": "open_website", "parameters": {"url": word}, "confirmation_needed": False}
    
    # Search commands
    if "search" in query_lower or "google" in query_lower:
        search_query = query_lower.replace("search for", "").replace("search", "").replace("google", "").strip()
        return {"action": "search_google", "parameters": {"query": search_query}, "confirmation_needed": False}
    
    # Screenshot
    if "screenshot" in query_lower or "capture screen" in query_lower:
        return {"action": "take_screenshot", "parameters": {}, "confirmation_needed": False}
    
    # Close application
    if "close" in query_lower or "exit" in query_lower:
        for app in ['chrome', 'calculator', 'notepad', 'paint', 'edge']:
            if app in query_lower:
                return {"action": "close_app", "parameters": {"app_name": app}, "confirmation_needed": False}
    
    # System info
    if "system" in query_lower and ("info" in query_lower or "status" in query_lower or "usage" in query_lower):
        return {"action": "system_info", "parameters": {}, "confirmation_needed": False}
    
    # Lock screen
    if "lock" in query_lower:
        return {"action": "lock_screen", "parameters": {}, "confirmation_needed": False}
    
    # Shutdown/Restart
    if "shutdown" in query_lower or "shut down" in query_lower:
        return {"action": "shutdown", "parameters": {}, "confirmation_needed": True}
    if "restart" in query_lower or "reboot" in query_lower:
        return {"action": "restart", "parameters": {}, "confirmation_needed": True}
    
    return None

def parse_command_with_gpt(query):
    """Parse command using GPT"""
    try:
        system_prompt = """You are a command parser. Respond ONLY with JSON:
{"action": "action_name", "parameters": {"param1": "value1"}, "confirmation_needed": false}

Actions: open_app, open_website, search_google, create_folder, create_file, take_screenshot, close_app, system_info, lock_screen, shutdown, restart, general_query"""
        
        completion = client.chat.completions.create(
            model=Model,
            messages=[
                {'role': "system", 'content': system_prompt},
                {'role': 'user', 'content': query}
            ],
            max_tokens=150
        )
        
        response = completion.choices[0].message.content
        command_data = json.loads(response)
        return command_data
    except Exception as e:
        return {"action": "general_query", "parameters": {}, "confirmation_needed": False}

def execute_system_command(command_data):
    """Execute system commands"""
    action = command_data.get('action')
    params = command_data.get('parameters', {})
    
    result = None
    
    if action == 'open_app':
        result = sys_controller.open_application(params.get('app_name', ''))
    elif action == 'open_website':
        result = sys_controller.open_website(params.get('url', ''))
    elif action == 'search_google':
        result = sys_controller.search_google(params.get('query', ''))
    elif action == 'create_folder':
        result = sys_controller.create_folder(params.get('path', ''))
    elif action == 'create_file':
        result = sys_controller.create_file(params.get('path', ''))
    elif action == 'take_screenshot':
        result = sys_controller.take_screenshot()
    elif action == 'close_app':
        result = sys_controller.close_application(params.get('app_name', ''))
    elif action == 'system_info':
        info = sys_controller.get_system_info()
        result = f"CPU: {info['cpu_usage']}, Memory: {info['memory_usage']}"
    elif action == 'lock_screen':
        result = sys_controller.lock_screen()
    elif action == 'shutdown':
        result = sys_controller.shutdown_system()
    elif action == 'restart':
        result = sys_controller.restart_system()
    
    return result

def listen_and_process():
    """Voice processing loop"""
    r = sr.Recognizer()
    
    while assistant_state['is_running']:
        try:
            with sr.Microphone() as source:
                assistant_state['status'] = 'listening'
                socketio.emit('status_update', {'status': 'listening', 'color': '#00d9ff'})
                socketio.emit('message', {'type': 'system', 'content': 'Listening...'})
                
                r.pause_threshold = 1
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            
            assistant_state['status'] = 'recognizing'
            socketio.emit('status_update', {'status': 'recognizing', 'color': '#ffa500'})
            
            query = r.recognize_google(audio, language='en-in')
            socketio.emit('message', {'type': 'user', 'content': query})
            
            # Check for exit
            if any(word in query.lower() for word in ['bye', 'goodbye', 'exit', 'stop']):
                response = 'Goodbye! Have a great day!'
                socketio.emit('message', {'type': 'assistant', 'content': response})
                speak(response)
                assistant_state['is_running'] = False
                assistant_state['status'] = 'idle'
                socketio.emit('status_update', {'status': 'idle', 'color': '#555555'})
                break
            
            # Parse and execute
            assistant_state['status'] = 'processing'
            socketio.emit('status_update', {'status': 'processing', 'color': '#e94560'})
            
            command_data = parse_command_locally(query)
            
            if command_data is None:
                command_data = parse_command_with_gpt(query)
            else:
                socketio.emit('message', {'type': 'system', 'content': f'Action: {command_data.get("action")}'})
            
            result = execute_system_command(command_data)
            
            if result:
                socketio.emit('message', {'type': 'assistant', 'content': result})
                speak(result)
            else:
                # General query
                try:
                    completion = client.chat.completions.create(
                        model=Model,
                        messages=[
                            {'role': "system", 'content': "You are a helpful assistant"},
                            {'role': 'user', 'content': query}
                        ],
                        max_tokens=200
                    )
                    answer = completion.choices[0].message.content
                    socketio.emit('message', {'type': 'assistant', 'content': answer})
                    speak(answer)
                except Exception as e:
                    error_msg = "API quota exceeded. Please check your OpenAI billing."
                    socketio.emit('message', {'type': 'assistant', 'content': error_msg})
                    speak(error_msg)
            
            assistant_state['status'] = 'ready'
            socketio.emit('status_update', {'status': 'ready', 'color': '#00ff00'})
            
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            socketio.emit('message', {'type': 'system', 'content': 'Could not understand audio'})
        except Exception as e:
            socketio.emit('message', {'type': 'system', 'content': f'Error: {str(e)}'})

# REST API endpoints
@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current assistant status"""
    return jsonify({
        'is_running': assistant_state['is_running'],
        'status': assistant_state['status']
    })

@app.route('/api/system-info', methods=['GET'])
def get_system_info():
    """Get system information"""
    try:
        info = sys_controller.get_system_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start_assistant():
    """Start the voice assistant"""
    if not assistant_state['is_running']:
        assistant_state['is_running'] = True
        assistant_state['status'] = 'starting'
        
        # Start listening thread
        thread = threading.Thread(target=listen_and_process, daemon=True)
        thread.start()
        
        socketio.emit('message', {'type': 'system', 'content': 'Voice assistant started!'})
        speak('Hello! I am your AI assistant with full system control. How can I help you?')
        
        return jsonify({'success': True, 'message': 'Assistant started'})
    return jsonify({'success': False, 'message': 'Already running'}), 400

@app.route('/api/stop', methods=['POST'])
def stop_assistant():
    """Stop the voice assistant"""
    assistant_state['is_running'] = False
    assistant_state['status'] = 'idle'
    socketio.emit('message', {'type': 'system', 'content': 'Voice assistant stopped.'})
    return jsonify({'success': True, 'message': 'Assistant stopped'})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status_update', {'status': assistant_state['status'], 'color': '#555555'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("🚀 Starting Flask backend server...")
    port = int(os.environ.get('PORT', 5000))
    print(f"📡 Server running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
