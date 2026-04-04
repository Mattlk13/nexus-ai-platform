import React, { useState, useEffect, useRef } from 'react';
import { Send, StopCircle, Loader, Terminal, Trash2, Download, User, Bot } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const OpenClawChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentRunId, setCurrentRunId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws) ws.close();
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const connectWebSocket = () => {
    const wsUrl = `${API.replace('https://', 'wss://').replace('http://', 'ws://')}/api/openclaw/ui/ws`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      
      // Request chat history
      socket.send(JSON.stringify({
        jsonrpc: '2.0',
        method: 'chat.history',
        params: { sessionKey: 'default' },
        id: Date.now()
      }));
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle chat history response
        if (data.result && data.result.messages) {
          const historyMessages = data.result.messages.map(msg => ({
            role: msg.role,
            content: msg.content || msg.text || '',
            timestamp: msg.timestamp || new Date().toISOString()
          }));
          setMessages(historyMessages);
        }
        
        // Handle streaming chat events
        if (data.method === 'chat') {
          const event = data.params;
          
          if (event.type === 'start') {
            setCurrentRunId(event.runId);
            setIsLoading(true);
          } else if (event.type === 'text') {
            // Append assistant text
            setMessages(prev => {
              const last = prev[prev.length - 1];
              if (last && last.role === 'assistant' && last.runId === event.runId) {
                return [
                  ...prev.slice(0, -1),
                  { ...last, content: last.content + (event.text || '') }
                ];
              } else {
                return [
                  ...prev,
                  {
                    role: 'assistant',
                    content: event.text || '',
                    runId: event.runId,
                    timestamp: new Date().toISOString()
                  }
                ];
              }
            });
          } else if (event.type === 'end') {
            setIsLoading(false);
            setCurrentRunId(null);
          } else if (event.type === 'error') {
            setIsLoading(false);
            setMessages(prev => [
              ...prev,
              {
                role: 'system',
                content: `Error: ${event.error || 'Unknown error'}`,
                timestamp: new Date().toISOString()
              }
            ]);
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Attempt reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    setWs(socket);
  };

  const sendMessage = () => {
    if (!input.trim() || !ws || !isConnected) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Send via WebSocket using chat.send RPC
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      method: 'chat.send',
      params: {
        sessionKey: 'default',
        message: input,
        idempotencyKey: `${Date.now()}-${Math.random()}`
      },
      id: Date.now()
    }));
  };

  const stopGeneration = () => {
    if (!ws || !currentRunId) return;

    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      method: 'chat.abort',
      params: {
        sessionKey: 'default',
        runId: currentRunId
      },
      id: Date.now()
    }));

    setIsLoading(false);
    setCurrentRunId(null);
  };

  const clearChat = () => {
    setMessages([]);
  };

  const exportChat = () => {
    const chatText = messages
      .map(m => `[${m.role.toUpperCase()}]: ${m.content}`)
      .join('\n\n');
    
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `openclaw-chat-${Date.now()}.txt`;
    a.click();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-lg border-b border-purple-500/20 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Terminal className="w-6 h-6 text-purple-400" />
            <h1 className="text-2xl font-bold text-white">OpenClaw Chat</h1>
            <div className={`px-3 py-1 rounded-full text-sm ${
              isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
              {isConnected ? '● Connected' : '● Disconnected'}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={exportChat}
              className="p-2 hover:bg-slate-700/50 rounded-lg transition-all"
              title="Export chat"
            >
              <Download className="w-5 h-5 text-slate-400" />
            </button>
            <button
              onClick={clearChat}
              className="p-2 hover:bg-slate-700/50 rounded-lg transition-all"
              title="Clear chat"
            >
              <Trash2 className="w-5 h-5 text-slate-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <Bot className="w-16 h-16 text-purple-400 mx-auto mb-4 opacity-50" />
              <p className="text-slate-400 text-lg">Start a conversation with OpenClaw</p>
              <p className="text-slate-500 text-sm mt-2">Using Emergent provider (GPT-5.2, Claude 4)</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-4 ${
                msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                msg.role === 'user' 
                  ? 'bg-blue-500/20' 
                  : msg.role === 'assistant'
                  ? 'bg-purple-500/20'
                  : 'bg-red-500/20'
              }`}>
                {msg.role === 'user' ? (
                  <User className="w-5 h-5 text-blue-400" />
                ) : msg.role === 'assistant' ? (
                  <Bot className="w-5 h-5 text-purple-400" />
                ) : (
                  <Terminal className="w-5 h-5 text-red-400" />
                )}
              </div>
              
              <div
                className={`flex-1 max-w-3xl rounded-2xl p-4 ${
                  msg.role === 'user'
                    ? 'bg-blue-500/10 border border-blue-500/20'
                    : msg.role === 'assistant'
                    ? 'bg-slate-800/50 border border-purple-500/20'
                    : 'bg-red-500/10 border border-red-500/20'
                }`}
              >
                <div className="text-white whitespace-pre-wrap break-words">
                  {msg.content}
                </div>
                <div className="text-xs text-slate-500 mt-2">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                <Bot className="w-5 h-5 text-purple-400" />
              </div>
              <div className="flex-1 max-w-3xl rounded-2xl p-4 bg-slate-800/50 border border-purple-500/20">
                <Loader className="w-5 h-5 text-purple-400 animate-spin" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-slate-800/50 backdrop-blur-lg border-t border-purple-500/20 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              className="flex-1 bg-slate-900/50 border border-purple-500/20 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50 resize-none"
              rows={3}
              disabled={!isConnected}
            />
            <div className="flex flex-col gap-2">
              {isLoading ? (
                <button
                  onClick={stopGeneration}
                  className="p-3 bg-red-600 hover:bg-red-700 rounded-xl transition-all"
                  title="Stop generation"
                >
                  <StopCircle className="w-6 h-6 text-white" />
                </button>
              ) : (
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || !isConnected}
                  className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Send message"
                >
                  <Send className="w-6 h-6 text-white" />
                </button>
              )}
            </div>
          </div>

          {!isConnected && (
            <div className="text-center text-red-400 text-sm mt-2">
              WebSocket disconnected. Reconnecting...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OpenClawChat;
