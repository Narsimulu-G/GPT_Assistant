from openai import OpenAI
from apikey import api_data 
import os
import speech_recognition as sr # Converts my voice commands to text 
import pyttsx3 # Read out text output to voice. 
import webbrowser
import json
from system_controller import SystemController

Model = "gpt-4o"
client = OpenAI(api_key=api_data)

# Initialize system controller
sys_controller = SystemController()

def parse_command_with_gpt(query):
    """Use GPT to parse natural language commands and determine the action"""
    try:
        system_prompt = """You are a command parser for a voice-controlled system assistant. 
Analyze the user's voice command and determine what action to take.

Available actions:
- open_app: Open an application (e.g., "open chrome", "launch calculator")
- open_website: Open a website (e.g., "open facebook.com", "go to youtube")
- search_google: Search Google (e.g., "search for python tutorials", "google how to code")
- create_folder: Create a folder (e.g., "create folder named Documents")
- create_file: Create a file (e.g., "create file test.txt")
- take_screenshot: Take a screenshot (e.g., "take a screenshot", "capture screen")
- close_app: Close an application (e.g., "close chrome", "exit notepad")
- system_info: Get system information (e.g., "system status", "check cpu usage")
- lock_screen: Lock the computer (e.g., "lock screen", "lock computer")
- shutdown: Shutdown computer (e.g., "shutdown", "turn off computer")
- restart: Restart computer (e.g., "restart", "reboot")
- general_query: General question or conversation

Respond ONLY with a JSON object in this format:
{
    "action": "action_name",
    "parameters": {
        "param1": "value1"
    },
    "confirmation_needed": true/false
}

Examples:
User: "open chrome"
Response: {"action": "open_app", "parameters": {"app_name": "chrome"}, "confirmation_needed": false}

User: "search for best restaurants"
Response: {"action": "search_google", "parameters": {"query": "best restaurants"}, "confirmation_needed": false}

User: "shutdown computer"
Response: {"action": "shutdown", "parameters": {}, "confirmation_needed": true}

User: "what is the weather today"
Response: {"action": "general_query", "parameters": {}, "confirmation_needed": false}
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
        # Parse JSON response
        command_data = json.loads(response)
        return command_data
    except Exception as e:
        print(f"GPT parsing error: {e}")
        return {"action": "general_query", "parameters": {}, "confirmation_needed": False}

def Reply(question):
    """Get general AI response for conversation"""
    try:
        completion = client.chat.completions.create(
            model=Model,
            messages=[
                {'role':"system","content":"You are a helpful assistant"},
                {'role':'user','content':question}
            ],
            max_tokens=200
        )
        answer = completion.choices[0].message.content
        return answer
    except Exception as e:
        if "insufficient_quota" in str(e) or "429" in str(e):
            return "I'm sorry, but I've reached my usage limit. Please check your OpenAI API billing or try again later."
        elif "authentication" in str(e).lower():
            return "I'm sorry, but there's an issue with the API authentication. Please check your API key."
        else:
            return f"I'm sorry, but I encountered an error: {str(e)}"

# Text to speech 
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        print(f"Response: {text}")
    
speak("Hello! I am your AI assistant with full system control. How can I help you?")

def takeCommand():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source: 
            print('Listening .......')
            r.pause_threshold = 1 # Wait for 1 sec before considering the end of a phrase
            audio = r.listen(source)
        try: 
            print('Recognizing ....')
            query = r.recognize_google(audio, language = 'en-in')
            print("User Said: {} \n".format(query))
        except sr.UnknownValueError:
            print("Could not understand audio")
            return "None"
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return "None"
    except Exception as e:
        print(f"Microphone error: {e}")
        return "None"
    return query

def execute_system_command(command_data):
    """Execute system commands based on parsed command data"""
    action = command_data.get('action')
    params = command_data.get('parameters', {})
    
    result = None
    
    if action == 'open_app':
        app_name = params.get('app_name', '')
        result = sys_controller.open_application(app_name)
    
    elif action == 'open_website':
        url = params.get('url', '')
        result = sys_controller.open_website(url)
    
    elif action == 'search_google':
        query = params.get('query', '')
        result = sys_controller.search_google(query)
    
    elif action == 'create_folder':
        path = params.get('path', '')
        result = sys_controller.create_folder(path)
    
    elif action == 'create_file':
        path = params.get('path', '')
        result = sys_controller.create_file(path)
    
    elif action == 'take_screenshot':
        result = sys_controller.take_screenshot()
    
    elif action == 'close_app':
        app_name = params.get('app_name', '')
        result = sys_controller.close_application(app_name)
    
    elif action == 'system_info':
        info = sys_controller.get_system_info()
        result = f"CPU usage: {info['cpu_usage']}, Memory usage: {info['memory_usage']}"
    
    elif action == 'lock_screen':
        result = sys_controller.lock_screen()
    
    elif action == 'shutdown':
        result = sys_controller.shutdown_system()
    
    elif action == 'restart':
        result = sys_controller.restart_system()
    
    return result

if __name__ == '__main__':
    while True: 
        query = takeCommand()
        if query.lower() == 'none':
            continue
        
        # Exit command
        if "bye" in query.lower() or "goodbye" in query.lower() or "exit" in query.lower():
            print("Goodbye!")
            speak("Goodbye! Have a great day!")
            break
        
        # Parse command with GPT
        print("Analyzing command...")
        command_data = parse_command_with_gpt(query)
        print(f"Parsed action: {command_data.get('action')}")
        
        # Check if confirmation needed
        if command_data.get('confirmation_needed'):
            speak(f"Are you sure you want to {command_data.get('action')}? Say yes to confirm.")
            confirmation = takeCommand().lower()
            if 'yes' not in confirmation:
                speak("Action cancelled")
                continue
        
        # Execute system command
        result = execute_system_command(command_data)
        
        # If no system command matched, treat as general query
        if result is None or command_data.get('action') == 'general_query':
            ans = Reply(query)
            print(ans)
            speak(ans)
        else:
            print(result)
            speak(result)