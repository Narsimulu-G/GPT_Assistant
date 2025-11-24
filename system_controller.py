import subprocess
import os
import shutil
import psutil
import pyautogui
from datetime import datetime
import json

class SystemController:
    """Handles all system-level operations for the voice assistant"""
    
    def __init__(self):
        # Common application paths for Windows
        self.app_paths = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'google chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'microsoft edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'file explorer': 'explorer.exe',
            'explorer': 'explorer.exe',
            'task manager': 'taskmgr.exe',
            'control panel': 'control.exe',
            'settings': 'ms-settings:',
            'cmd': 'cmd.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'vs code': r'C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe'.format(os.getenv('USERNAME')),
            'visual studio code': r'C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe'.format(os.getenv('USERNAME')),
            'word': r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
            'excel': r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
            'powerpoint': r'C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE',
            'outlook': r'C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE',
        }
        
        # Operations that require confirmation
        self.critical_operations = ['delete', 'shutdown', 'restart', 'format', 'remove']
        
    def open_application(self, app_name):
        """Open an application by name"""
        try:
            app_name = app_name.lower().strip()
            
            # Check if app is in predefined paths
            if app_name in self.app_paths:
                path = self.app_paths[app_name]
                if os.path.exists(path):
                    subprocess.Popen(path)
                    return f"Opening {app_name}"
                else:
                    # Try using start command for system apps
                    subprocess.Popen(['start', path], shell=True)
                    return f"Opening {app_name}"
            else:
                # Try to open using Windows start command
                subprocess.Popen(['start', app_name], shell=True)
                return f"Attempting to open {app_name}"
        except Exception as e:
            return f"Could not open {app_name}: {str(e)}"
    
    def create_folder(self, path):
        """Create a new folder"""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Created folder: {path}"
        except Exception as e:
            return f"Could not create folder: {str(e)}"
    
    def create_file(self, path, content=""):
        """Create a new file"""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Created file: {path}"
        except Exception as e:
            return f"Could not create file: {str(e)}"
    
    def delete_file(self, path):
        """Delete a file (with safety check)"""
        try:
            if os.path.exists(path):
                os.remove(path)
                return f"Deleted file: {path}"
            else:
                return f"File not found: {path}"
        except Exception as e:
            return f"Could not delete file: {str(e)}"
    
    def delete_folder(self, path):
        """Delete a folder (with safety check)"""
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                return f"Deleted folder: {path}"
            else:
                return f"Folder not found: {path}"
        except Exception as e:
            return f"Could not delete folder: {str(e)}"
    
    def rename_file(self, old_path, new_path):
        """Rename a file or folder"""
        try:
            os.rename(old_path, new_path)
            return f"Renamed {old_path} to {new_path}"
        except Exception as e:
            return f"Could not rename: {str(e)}"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            shutil.copy2(source, destination)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Could not copy file: {str(e)}"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            shutil.move(source, destination)
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Could not move file: {str(e)}"
    
    def take_screenshot(self, filename=None):
        """Take a screenshot"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Could not take screenshot: {str(e)}"
    
    def set_volume(self, level):
        """Set system volume (0-100)"""
        try:
            # Using nircmd for volume control (requires nircmd.exe)
            # Alternative: use pycaw library
            level = max(0, min(100, int(level)))
            volume_value = int((level / 100) * 65535)
            subprocess.run(['nircmd.exe', 'setsysvolume', str(volume_value)], check=False)
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Could not set volume: {str(e)}"
    
    def mute_volume(self):
        """Mute system volume"""
        try:
            subprocess.run(['nircmd.exe', 'mutesysvolume', '1'], check=False)
            return "Volume muted"
        except Exception as e:
            return f"Could not mute volume: {str(e)}"
    
    def unmute_volume(self):
        """Unmute system volume"""
        try:
            subprocess.run(['nircmd.exe', 'mutesysvolume', '0'], check=False)
            return "Volume unmuted"
        except Exception as e:
            return f"Could not unmute volume: {str(e)}"
    
    def get_running_processes(self):
        """Get list of running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes[:10]  # Return top 10 processes
        except Exception as e:
            return f"Could not get processes: {str(e)}"
    
    def close_application(self, app_name):
        """Close an application by name"""
        try:
            app_name = app_name.lower()
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name in proc.info['name'].lower():
                        proc.terminate()
                        closed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if closed:
                return f"Closed {app_name}"
            else:
                return f"Could not find running process: {app_name}"
        except Exception as e:
            return f"Could not close application: {str(e)}"
    
    def get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = {
                'cpu_usage': f"{cpu_percent}%",
                'memory_usage': f"{memory.percent}%",
                'disk_usage': f"{disk.percent}%",
                'available_memory': f"{memory.available / (1024**3):.2f} GB"
            }
            return info
        except Exception as e:
            return f"Could not get system info: {str(e)}"
    
    def shutdown_system(self):
        """Shutdown the system"""
        try:
            subprocess.run(['shutdown', '/s', '/t', '10'], check=True)
            return "System will shutdown in 10 seconds"
        except Exception as e:
            return f"Could not shutdown system: {str(e)}"
    
    def restart_system(self):
        """Restart the system"""
        try:
            subprocess.run(['shutdown', '/r', '/t', '10'], check=True)
            return "System will restart in 10 seconds"
        except Exception as e:
            return f"Could not restart system: {str(e)}"
    
    def lock_screen(self):
        """Lock the screen"""
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            return "Screen locked"
        except Exception as e:
            return f"Could not lock screen: {str(e)}"
    
    def open_website(self, url):
        """Open a website in default browser"""
        try:
            import webbrowser
            if not url.startswith('http'):
                url = 'https://' + url
            webbrowser.open(url)
            return f"Opening {url}"
        except Exception as e:
            return f"Could not open website: {str(e)}"
    
    def search_google(self, query):
        """Search Google for a query"""
        try:
            import webbrowser
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching Google for: {query}"
        except Exception as e:
            return f"Could not search Google: {str(e)}"
    
    def execute_command(self, command):
        """Execute a system command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"Could not execute command: {str(e)}"
