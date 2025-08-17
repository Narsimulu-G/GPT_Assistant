from openai import OpenAI
from apikey import api_data 
import os
import speech_recognition as sr # Converts my voice commands to text 
import pyttsx3 # Read out text output to voice. 
import webbrowser 

Model = "gpt-4o"
client = OpenAI(api_key=api_data)

def Reply(question):
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
    
speak("Hello! How are you?")

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

if __name__ == '__main__':
    while True: 
        query = takeCommand().lower()
        if query == 'none':
            continue
        
        # Handle specific commands first
        if "open youtube" in query: 
            print("Opening YouTube...")
            speak("Opening YouTube")
            webbrowser.open('https://www.youtube.com')
            continue
        if "open google" in query: 
            print("Opening Google...")
            speak("Opening Google")
            webbrowser.open('https://www.google.com')
            continue
        if "bye" in query or "goodbye" in query or "exit" in query:
            print("Goodbye!")
            speak("Goodbye! Have a great day!")
            break
        
        # Get AI response for other queries
        ans = Reply(query)
        print(ans)
        speak(ans)
        