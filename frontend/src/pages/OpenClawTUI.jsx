import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Send, Settings, Zap, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';

const OpenClawTUI = () => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentAgent, setCurrentAgent] = useState('main');
  const [currentSession, setCurrentSession] = useState('main');
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [deliveryEnabled, setDeliveryEnabled] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // OpenClaw Gateway WebSocket URL
  const GATEWAY_URL = 'ws://127.0.0.1:18789';

  useEffect(() => {
    connectToGateway();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const connectToGateway = () => {
    try {
      setConnectionStatus('connecting');
      
      // Connect to OpenClaw Gateway
      const ws = new WebSocket(GATEWAY_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('Connected to OpenClaw Gateway');
        setConnected(true);
        setConnectionStatus('connected');
        
        addSystemMessage('✓ Connected to OpenClaw Gateway', 'success');
        
        // Register as TUI client
        sendToGateway({
          jsonrpc: '2.0',
          method: 'register',
          params: { mode: 'tui', agent: currentAgent },
          id: Date.now()
        });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleGatewayMessage(data);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        addSystemMessage('✗ Connection error', 'error');
      };

      ws.onclose = () => {
        console.log('Disconnected from Gateway');
        setConnected(false);
        setConnectionStatus('disconnected');
        addSystemMessage('Disconnected from Gateway', 'warning');
      };
    } catch (error) {
      console.error('Failed to connect:', error);
      setConnectionStatus('error');
      addSystemMessage('Failed to connect to Gateway', 'error');
    }
  };

  const sendToGateway = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  const handleGatewayMessage = (data) => {
    // Handle different message types from Gateway
    if (data.method === 'message') {
      const { role, content } = data.params || {};
      
      if (role === 'assistant') {
        addMessage(content, 'assistant');
      } else if (role === 'system') {
        addSystemMessage(content, 'info');
      }
    } else if (data.method === 'stream') {
      // Handle streaming responses
      setIsStreaming(true);
      updateLastMessage(data.params?.chunk || '');
    } else if (data.method === 'stream_end') {
      setIsStreaming(false);
    } else if (data.result) {
      // Handle JSON-RPC responses
      console.log('Gateway response:', data.result);
    }
  };

  const addMessage = (content, sender) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      content,
      sender,
      timestamp: new Date().toISOString()
    }]);
  };

  const addSystemMessage = (content, level = 'info') => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      content,
      sender: 'system',
      level,
      timestamp: new Date().toISOString()
    }]);
  };

  const updateLastMessage = (chunk) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMsg = newMessages[newMessages.length - 1];
      
      if (lastMsg && lastMsg.sender === 'assistant') {
        lastMsg.content += chunk;
      } else {
        newMessages.push({
          id: Date.now(),
          content: chunk,
          sender: 'assistant',
          timestamp: new Date().toISOString()
        });
      }
      
      return newMessages;
    });
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !connected) return;

    const message = inputMessage.trim();
    
    // Check for slash commands
    if (message.startsWith('/')) {
      handleSlashCommand(message);
    } else {
      // Send regular message
      addMessage(message, 'user');
      
      sendToGateway({
        jsonrpc: '2.0',
        method: 'chat.send',
        params: {
          agent: currentAgent,
          session: currentSession,
          message: message,
          deliver: deliveryEnabled
        },
        id: Date.now()
      });
    }

    setInputMessage('');
    inputRef.current?.focus();
  };

  const handleSlashCommand = (command) => {
    const parts = command.slice(1).split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    addSystemMessage(`> ${command}`, 'info');

    switch (cmd) {
      case 'help':
        addSystemMessage('Available commands: /help, /status, /agent, /session, /deliver, /clear, /reconnect', 'info');
        break;
      
      case 'status':
        addSystemMessage(`Status: ${connectionStatus} | Agent: ${currentAgent} | Session: ${currentSession} | Delivery: ${deliveryEnabled ? 'ON' : 'OFF'}`, 'info');
        break;
      
      case 'agent':
        if (args[0]) {
          setCurrentAgent(args[0]);
          addSystemMessage(`Switched to agent: ${args[0]}`, 'success');
        } else {
          addSystemMessage(`Current agent: ${currentAgent}`, 'info');
        }
        break;
      
      case 'session':
        if (args[0]) {
          setCurrentSession(args[0]);
          addSystemMessage(`Switched to session: ${args[0]}`, 'success');
        } else {
          addSystemMessage(`Current session: ${currentSession}`, 'info');
        }
        break;
      
      case 'deliver':
        if (args[0] === 'on') {
          setDeliveryEnabled(true);
          addSystemMessage('Delivery enabled', 'success');
        } else if (args[0] === 'off') {
          setDeliveryEnabled(false);
          addSystemMessage('Delivery disabled', 'success');
        } else {
          addSystemMessage(`Delivery: ${deliveryEnabled ? 'ON' : 'OFF'}`, 'info');
        }
        break;
      
      case 'clear':
        setMessages([]);
        addSystemMessage('Messages cleared', 'success');
        break;
      
      case 'reconnect':
        connectToGateway();
        break;
      
      default:
        // Forward to gateway
        sendToGateway({
          jsonrpc: '2.0',
          method: 'command',
          params: { command: command },
          id: Date.now()
        });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected': return <CheckCircle className="w-4 h-4" />;
      case 'connecting': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                OpenClaw TUI 🦞
              </h1>
              <p className="text-slate-300">Terminal User Interface - Interactive Gateway Chat</p>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Connection Status */}
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${getStatusColor()} bg-opacity-20`}>
                {getStatusIcon()}
                <span className="font-medium capitalize">{connectionStatus}</span>
              </div>
              
              {/* Delivery Toggle */}
              <button
                onClick={() => setDeliveryEnabled(!deliveryEnabled)}
                className={`px-4 py-2 rounded-lg transition-all ${
                  deliveryEnabled 
                    ? 'bg-green-600 text-white' 
                    : 'bg-slate-700 text-slate-300'
                }`}
              >
                <Zap className="w-4 h-4 inline mr-2" />
                Delivery: {deliveryEnabled ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>
        </div>

        {/* Session Info Bar */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-lg p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-sm text-slate-400">Agent:</span>
              <Badge variant="outline" className="ml-2">{currentAgent}</Badge>
            </div>
            <div>
              <span className="text-sm text-slate-400">Session:</span>
              <Badge variant="outline" className="ml-2">{currentSession}</Badge>
            </div>
            <div>
              <span className="text-sm text-slate-400">Gateway:</span>
              <Badge variant="outline" className="ml-2">127.0.0.1:18789</Badge>
            </div>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleSlashCommand('/help')}
          >
            <Terminal className="w-4 h-4 mr-2" />
            Commands
          </Button>
        </div>

        {/* Chat Window */}
        <Card className="bg-slate-800/50 backdrop-blur-lg border-purple-500/20">
          <CardContent className="p-0">
            {/* Messages */}
            <div className="h-[500px] overflow-y-auto p-6 space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {msg.sender === 'system' ? (
                    <div className={`px-4 py-2 rounded-lg text-sm ${
                      msg.level === 'success' ? 'bg-green-900/30 text-green-400' :
                      msg.level === 'error' ? 'bg-red-900/30 text-red-400' :
                      msg.level === 'warning' ? 'bg-yellow-900/30 text-yellow-400' :
                      'bg-slate-700/30 text-slate-300'
                    }`}>
                      {msg.content}
                    </div>
                  ) : (
                    <div
                      className={`max-w-[70%] px-4 py-3 rounded-lg ${
                        msg.sender === 'user'
                          ? 'bg-purple-600 text-white'
                          : 'bg-slate-700 text-slate-100'
                      }`}
                    >
                      <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                      <div className="text-xs opacity-60 mt-1">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {isStreaming && (
                <div className="flex items-center gap-2 text-blue-400 text-sm">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Streaming response...
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-slate-700 p-4">
              <div className="flex items-center gap-2">
                <Input
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={connected ? "Type a message or /help for commands..." : "Connecting to gateway..."}
                  disabled={!connected}
                  className="flex-1 bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!connected || !inputMessage.trim()}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="mt-2 text-xs text-slate-400">
                Press Enter to send • Shift+Enter for new line • Type /help for commands
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Help Section */}
        <div className="mt-6 grid md:grid-cols-2 gap-4">
          <Card className="bg-slate-800/30 border-slate-700">
            <CardHeader>
              <CardTitle className="text-sm">Quick Commands</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm text-slate-300">
                <div><code className="bg-slate-700 px-2 py-1 rounded">/help</code> - Show all commands</div>
                <div><code className="bg-slate-700 px-2 py-1 rounded">/status</code> - Connection status</div>
                <div><code className="bg-slate-700 px-2 py-1 rounded">/agent &lt;name&gt;</code> - Switch agent</div>
                <div><code className="bg-slate-700 px-2 py-1 rounded">/session &lt;name&gt;</code> - Switch session</div>
                <div><code className="bg-slate-700 px-2 py-1 rounded">/deliver on/off</code> - Toggle delivery</div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/30 border-slate-700">
            <CardHeader>
              <CardTitle className="text-sm">Features</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm text-slate-300">
                <div>✓ Real-time WebSocket connection</div>
                <div>✓ Streaming responses</div>
                <div>✓ Agent & session management</div>
                <div>✓ Slash commands support</div>
                <div>✓ Message history</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default OpenClawTUI;
