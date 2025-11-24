# AI Voice Assistant - React Frontend

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
cd "c:\Users\naras\Documents\GPT Assistant"
python backend_server.py
```
Backend runs on: `http://localhost:5000`

### 2. Start the React Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`

### 3. Open in Browser
Navigate to: `http://localhost:5173`

## 🎯 Features

- **Real-time Status Indicator** - Animated pulse showing listening/processing/ready states
- **Command History** - Live chat-style display of all voice commands and responses
- **System Monitoring** - Real-time CPU, memory, and disk usage
- **WebSocket Communication** - Instant updates without page refresh
- **Beautiful Dark Theme** - Modern gradient design with smooth animations
- **Responsive Design** - Works on desktop, tablet, and mobile

## 📡 API Endpoints

### REST API
- `GET /api/status` - Get assistant status
- `GET /api/system-info` - Get system information
- `POST /api/start` - Start voice assistant
- `POST /api/stop` - Stop voice assistant

### WebSocket Events
- `status_update` - Real-time status changes
- `message` - New messages (user/assistant/system)

## 🎨 Tech Stack

- **Frontend**: React 18 + Vite
- **Backend**: Flask + Flask-SocketIO
- **Communication**: Socket.IO, Axios
- **Styling**: Vanilla CSS with animations

## 📝 Usage

1. Click "Start Assistant" button
2. Wait for status to show "Listening..." (blue indicator)
3. Speak your command clearly
4. Watch the real-time updates in the command history
5. See system info update every 5 seconds

## 🎤 Voice Commands

All the same commands from the desktop app work here:
- "Open Chrome"
- "Search for Python tutorials"
- "Take a screenshot"
- "What's my CPU usage?"
- And many more!

## 🔧 Development

### Install Dependencies
```bash
npm install
```

### Run Dev Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

## 📦 Dependencies

- react
- socket.io-client
- axios
- vite

## 🌐 Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Any modern browser with WebSocket support
