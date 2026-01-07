# Build and Run Script for Render

# 1. Build Frontend
cd frontend
npm install
npm run build
cd ..

# 2. Start Backend
# Use gunicorn with eventlet for SocketIO support
python backend_server.py
