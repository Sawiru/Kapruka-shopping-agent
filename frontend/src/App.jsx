import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      text: "Ayu-bowan! 🙏 I'm **Kapruka Podi Aiyya**, your personal retail concierge. What are we shopping for today, macho? Tell me what you need, and I'll search our live catalog instantly!"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  // Automatically anchors the chat view to the newest responses
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userPrompt = input.trim();
    setInput('');
    
    // Append the user's message bubble to the state layout
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), sender: 'user', text: userPrompt }
    ]);
    
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userPrompt }),
      });

      const data = await response.json();
      
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, sender: 'agent', text: data.reply }
      ]);
    } catch (error) {
      console.error("Frontend Gateway Error:", error);
      setMessages((prev) => [
        ...prev,
        { 
          id: Date.now() + 1, 
          sender: 'agent', 
          text: "Ayiyoo, I couldn't reach the backend server node. Check if your Flask application is running on port 5000!" 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Structural Header Section */}
      <header className="app-header">
        <div className="agent-profile">
          <div className="status-indicator"></div>
          <div>
            <h1>Kapruka Podi Aiyya 🇱🇰</h1>
            <p>Innovative MCP Shopping Agent v1.0</p>
          </div>
        </div>
      </header>

      {/* Persistent Dynamic Chat Feed Layer */}
      <main className="chat-window">
        <div className="messages-container">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-row ${msg.sender}`}>
              <div className="message-bubble">
                {/* Fallback layout representation of markdown segments */}
                <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-row agent">
              <div className="message-bubble typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Tray Segment */}
      <footer className="input-tray">
        <form onSubmit={handleSendMessage} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type in English, සිංහල, or Tanglish (e.g., 'Cakes under 6000 LKR')..."
            disabled={isLoading}
          />
          <button type="submit" disabled={!input.trim() || isLoading}>
            Send
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;