from system_controller import SystemController
import os

sc = SystemController()
# Save to artifacts directory
screenshot_path = r"C:\Users\naras\.gemini\antigravity\brain\bc61b91b-3fab-470a-9777-ae928b8be570\app_screenshot.png"
result = sc.take_screenshot(screenshot_path)
print(result)
