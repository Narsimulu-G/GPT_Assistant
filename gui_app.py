import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
from datetime import datetime
from openai import OpenAI
from apikey import api_data 
import speech_recognition as sr
import pyttsx3
import json
from system_controller import SystemController

# Initialize
Model = "gpt-4o"
client = OpenAI(api_key=api_data)
sys_controller = SystemController()

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Voice Assistant - System Control")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        # Queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # State variables
        self.is_listening = False
        self.is_running = False
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        
        self.create_widgets()
        self.check_message_queue()
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#0f3460', height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🎤 AI Voice Assistant",
            font=('Segoe UI', 24, 'bold'),
            bg='#0f3460',
            fg='#e94560'
        )
        title_label.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Status and Controls
        left_panel = tk.Frame(main_container, bg='#16213e', width=300)
        left_panel.pack(side='left', fill='both', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Status indicator
        status_frame = tk.Frame(left_panel, bg='#16213e')
        status_frame.pack(pady=20, padx=15)
        
        tk.Label(
            status_frame,
            text="Status",
            font=('Segoe UI', 14, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        ).pack()
        
        self.status_canvas = tk.Canvas(
            status_frame,
            width=100,
            height=100,
            bg='#16213e',
            highlightthickness=0
        )
        self.status_canvas.pack(pady=10)
        
        self.status_indicator = self.status_canvas.create_oval(
            20, 20, 80, 80,
            fill='#555555',
            outline='#888888',
            width=3
        )
        
        self.status_label = tk.Label(
            status_frame,
            text="Idle",
            font=('Segoe UI', 12),
            bg='#16213e',
            fg='#aaaaaa'
        )
        self.status_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(left_panel, bg='#16213e')
        button_frame.pack(pady=20, padx=15, fill='x')
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ Start Assistant",
            font=('Segoe UI', 12, 'bold'),
            bg='#e94560',
            fg='white',
            activebackground='#c93550',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            command=self.start_assistant,
            height=2
        )
        self.start_button.pack(fill='x', pady=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop Assistant",
            font=('Segoe UI', 12, 'bold'),
            bg='#555555',
            fg='white',
            activebackground='#444444',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            command=self.stop_assistant,
            height=2,
            state='disabled'
        )
        self.stop_button.pack(fill='x', pady=5)
        
        # System info
        info_frame = tk.Frame(left_panel, bg='#16213e')
        info_frame.pack(pady=20, padx=15, fill='both', expand=True)
        
        tk.Label(
            info_frame,
            text="System Info",
            font=('Segoe UI', 12, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        ).pack(anchor='w')
        
        self.info_text = tk.Text(
            info_frame,
            font=('Consolas', 9),
            bg='#0f3460',
            fg='#00d9ff',
            height=8,
            relief='flat',
            padx=10,
            pady=10
        )
        self.info_text.pack(fill='both', expand=True, pady=(10, 0))
        self.update_system_info()
        
        # Right panel - Chat/History
        right_panel = tk.Frame(main_container, bg='#16213e')
        right_panel.pack(side='right', fill='both', expand=True)
        
        tk.Label(
            right_panel,
            text="Command History",
            font=('Segoe UI', 14, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        ).pack(pady=15, padx=15, anchor='w')
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            right_panel,
            font=('Segoe UI', 10),
            bg='#0f3460',
            fg='#ffffff',
            relief='flat',
            padx=15,
            pady=15,
            wrap='word'
        )
        self.chat_display.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Configure text tags for styling
        self.chat_display.tag_config('user', foreground='#00d9ff', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_config('assistant', foreground='#e94560', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_config('system', foreground='#aaaaaa', font=('Segoe UI', 9, 'italic'))
        self.chat_display.tag_config('timestamp', foreground='#666666', font=('Segoe UI', 8))
        
        self.add_message("System", "Welcome! Click 'Start Assistant' to begin.", 'system')
        
    def update_status(self, status, color):
        """Update status indicator"""
        self.status_canvas.itemconfig(self.status_indicator, fill=color)
        self.status_label.config(text=status)
        
    def update_system_info(self):
        """Update system information display"""
        try:
            info = sys_controller.get_system_info()
            info_text = f"CPU Usage: {info['cpu_usage']}\n"
            info_text += f"Memory: {info['memory_usage']}\n"
            info_text += f"Disk: {info['disk_usage']}\n"
            info_text += f"Available RAM: {info['available_memory']}"
            
            self.info_text.delete('1.0', 'end')
            self.info_text.insert('1.0', info_text)
        except Exception as e:
            self.info_text.delete('1.0', 'end')
            self.info_text.insert('1.0', f"Error: {str(e)}")
        
        # Update every 5 seconds
        if self.is_running:
            self.root.after(5000, self.update_system_info)
    
    def add_message(self, sender, message, tag='user'):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert('end', f"[{timestamp}] ", 'timestamp')
        self.chat_display.insert('end', f"{sender}: ", tag)
        self.chat_display.insert('end', f"{message}\n\n")
        self.chat_display.see('end')
    
    def speak(self, text):
        """Text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def parse_command_locally(self, query):
        """Parse common commands locally without API"""
        query_lower = query.lower()
        
        # Open application commands
        if "open" in query_lower or "launch" in query_lower or "start" in query_lower:
            for app in ['chrome', 'calculator', 'notepad', 'paint', 'edge', 'explorer', 'vs code', 'word', 'excel']:
                if app in query_lower:
                    return {"action": "open_app", "parameters": {"app_name": app}, "confirmation_needed": False}
            
            # Check for websites
            if any(site in query_lower for site in ['youtube', 'google', 'facebook', 'twitter', 'instagram', '.com', '.org']):
                # Extract URL
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
        
        # If no local match, return general query
        return None
    
    def parse_command_with_gpt(self, query):
        """Parse command using GPT (fallback if local parsing fails)"""
        try:
            system_prompt = """You are a command parser for a voice-controlled system assistant. 
Analyze the user's voice command and determine what action to take.

Available actions:
- open_app: Open an application
- open_website: Open a website
- search_google: Search Google
- create_folder: Create a folder
- create_file: Create a file
- take_screenshot: Take a screenshot
- close_app: Close an application
- system_info: Get system information
- lock_screen: Lock the computer
- shutdown: Shutdown computer
- restart: Restart computer
- general_query: General question or conversation

Respond ONLY with a JSON object:
{"action": "action_name", "parameters": {"param1": "value1"}, "confirmation_needed": true/false}
"""
            
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
            self.message_queue.put(('system', f"GPT Error: {str(e)}", 'system'))
            return {"action": "general_query", "parameters": {}, "confirmation_needed": False}
    
    def execute_system_command(self, command_data):
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
    
    def listen_and_process(self):
        """Main voice processing loop"""
        r = sr.Recognizer()
        
        while self.is_running:
            try:
                with sr.Microphone() as source:
                    self.message_queue.put(('status', 'Listening...', '#00d9ff'))
                    self.message_queue.put(('system', 'Listening...', 'system'))
                    
                    r.pause_threshold = 1
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)
                
                self.message_queue.put(('status', 'Recognizing...', '#ffa500'))
                
                query = r.recognize_google(audio, language='en-in')
                self.message_queue.put(('user', query, 'user'))
                
                # Check for exit
                if any(word in query.lower() for word in ['bye', 'goodbye', 'exit', 'stop']):
                    self.message_queue.put(('assistant', 'Goodbye! Have a great day!', 'assistant'))
                    self.speak('Goodbye! Have a great day!')
                    self.message_queue.put(('stop', None, None))
                    break
                
                # Parse and execute - try local parsing first
                self.message_queue.put(('status', 'Processing...', '#e94560'))
                command_data = self.parse_command_locally(query)
                
                # If local parsing didn't match, try GPT
                if command_data is None:
                    command_data = self.parse_command_with_gpt(query)
                else:
                    self.message_queue.put(('system', f'Action: {command_data.get("action")}', 'system'))
                
                result = self.execute_system_command(command_data)
                
                if result:
                    self.message_queue.put(('assistant', result, 'assistant'))
                    self.speak(result)
                else:
                    # General query - get AI response
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
                        self.message_queue.put(('assistant', answer, 'assistant'))
                        self.speak(answer)
                    except Exception as e:
                        error_msg = "API quota exceeded. Please check your OpenAI billing."
                        self.message_queue.put(('assistant', error_msg, 'assistant'))
                        self.speak(error_msg)
                
                self.message_queue.put(('status', 'Ready', '#00ff00'))
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                self.message_queue.put(('system', 'Could not understand audio', 'system'))
            except Exception as e:
                self.message_queue.put(('system', f'Error: {str(e)}', 'system'))
    
    def check_message_queue(self):
        """Check for messages from worker thread"""
        try:
            while True:
                msg_type, content, tag = self.message_queue.get_nowait()
                
                if msg_type == 'status':
                    self.update_status(content, tag)
                elif msg_type == 'stop':
                    self.stop_assistant()
                else:
                    self.add_message(msg_type.capitalize(), content, tag)
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_message_queue)
    
    def start_assistant(self):
        """Start the voice assistant"""
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.update_status('Starting...', '#ffa500')
        self.add_message('System', 'Voice assistant started!', 'system')
        self.speak('Hello! I am your AI assistant with full system control. How can I help you?')
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_and_process, daemon=True)
        self.listen_thread.start()
        
        # Start system info updates
        self.update_system_info()
    
    def stop_assistant(self):
        """Stop the voice assistant"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.update_status('Idle', '#555555')
        self.add_message('System', 'Voice assistant stopped.', 'system')

def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
