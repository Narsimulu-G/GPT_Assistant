import { useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import axios from 'axios'
import './App.css'

const API_URL = 'http://localhost:5000'
const socket = io(API_URL)

function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [status, setStatus] = useState('idle')
  const [statusColor, setStatusColor] = useState('#555555')
  const [messages, setMessages] = useState([])
  const [systemInfo, setSystemInfo] = useState({})
  const messagesEndRef = useRef(null)

  useEffect(() => {
    // Socket event listeners
    socket.on('connect', () => {
      console.log('Connected to server')
    })

    socket.on('status_update', (data) => {
      setStatus(data.status)
      setStatusColor(data.color)
    })

    socket.on('message', (data) => {
      const timestamp = new Date().toLocaleTimeString()
      setMessages(prev => [...prev, { ...data, timestamp }])
    })

    // Fetch system info periodically
    const interval = setInterval(fetchSystemInfo, 5000)
    fetchSystemInfo()

    return () => {
      clearInterval(interval)
      socket.off('connect')
      socket.off('status_update')
      socket.off('message')
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchSystemInfo = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/system-info`)
      setSystemInfo(response.data)
    } catch (error) {
      console.error('Error fetching system info:', error)
    }
  }

  const handleStart = async () => {
    try {
      await axios.post(`${API_URL}/api/start`)
      setIsRunning(true)
    } catch (error) {
      console.error('Error starting assistant:', error)
    }
  }

  const handleStop = async () => {
    try {
      await axios.post(`${API_URL}/api/stop`)
      setIsRunning(false)
      setStatus('idle')
      setStatusColor('#555555')
    } catch (error) {
      console.error('Error stopping assistant:', error)
    }
  }

  const getMessageClass = (type) => {
    switch(type) {
      case 'user': return 'message-user'
      case 'assistant': return 'message-assistant'
      case 'system': return 'message-system'
      default: return ''
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>🎤 AI Voice Assistant</h1>
        <p>Full System Control with Voice Commands</p>
      </header>

      {/* Main Container */}
      <div className="main-container">
        {/* Left Panel */}
        <div className="left-panel">
          {/* Status Indicator */}
          <div className="status-section">
            <h3>Status</h3>
            <div className="status-indicator-container">
              <div 
                className="status-indicator"
                style={{ backgroundColor: statusColor }}
              >
                <div className="pulse-ring" style={{ borderColor: statusColor }}></div>
              </div>
              <p className="status-text">{status}</p>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="controls">
            <button 
              className="btn btn-start"
              onClick={handleStart}
              disabled={isRunning}
            >
              ▶ Start Assistant
            </button>
            <button 
              className="btn btn-stop"
              onClick={handleStop}
              disabled={!isRunning}
            >
              ⏹ Stop Assistant
            </button>
          </div>

          {/* System Info */}
          <div className="system-info">
            <h3>System Info</h3>
            <div className="info-content">
              <div className="info-item">
                <span className="info-label">CPU Usage:</span>
                <span className="info-value">{systemInfo.cpu_usage || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Memory:</span>
                <span className="info-value">{systemInfo.memory_usage || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Disk:</span>
                <span className="info-value">{systemInfo.disk_usage || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Available RAM:</span>
                <span className="info-value">{systemInfo.available_memory || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="right-panel">
          <h3>Command History</h3>
          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <p>👋 Welcome! Click "Start Assistant" to begin.</p>
                <p className="hint">Try saying: "Open Chrome", "Search for Python tutorials", "Take a screenshot"</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className={`message ${getMessageClass(msg.type)}`}>
                  <span className="timestamp">[{msg.timestamp}]</span>
                  <span className="message-type">{msg.type}:</span>
                  <span className="message-content">{msg.content}</span>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>🔊 Speak naturally - the AI will understand your commands</p>
      </footer>
    </div>
  )
}

export default App
