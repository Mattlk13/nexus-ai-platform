import { useEffect, useRef, useState, useCallback } from 'react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

/**
 * Custom hook for WebSocket connections
 * Provides real-time data streaming with auto-reconnect
 */
export const useWebSocket = (endpoint, options = {}) => {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const shouldReconnect = useRef(true);

  // Convert HTTP URL to WebSocket URL
  const getWebSocketUrl = useCallback(() => {
    const wsProtocol = API_BASE.startsWith('https') ? 'wss' : 'ws';
    const baseUrl = API_BASE.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${baseUrl}${endpoint}`;
  }, [endpoint]);

  const connect = useCallback(() => {
    try {
      const wsUrl = getWebSocketUrl();
      if (process.env.NODE_ENV === 'development') {
        console.log('Connecting to WebSocket:', wsUrl);
      }
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (process.env.NODE_ENV === 'development') {
          console.log('WebSocket connected:', endpoint);
        }
        setIsConnected(true);
        setError(null);
        setReconnectAttempts(0);
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        const errorMsg = 'WebSocket connection error';
        setError(errorMsg);
        onError?.(errorMsg);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected:', endpoint);
        setIsConnected(false);
        onDisconnect?.();
        
        // Auto-reconnect logic
        if (shouldReconnect.current && autoReconnect) {
          if (reconnectAttempts < maxReconnectAttempts) {
            console.log(`Reconnecting in ${reconnectInterval}ms... (attempt ${reconnectAttempts + 1})`);
            reconnectTimeoutRef.current = setTimeout(() => {
              setReconnectAttempts(prev => prev + 1);
              connect();
            }, reconnectInterval);
          } else {
            console.error('Max reconnect attempts reached');
            setError('Failed to reconnect after multiple attempts');
          }
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError(err.message);
    }
  }, [endpoint, getWebSocketUrl, onConnect, onMessage, onDisconnect, onError, autoReconnect, reconnectInterval, maxReconnectAttempts, reconnectAttempts]);

  const disconnect = useCallback(() => {
    shouldReconnect.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    shouldReconnect.current = true;
    connect();

    return () => {
      disconnect();
    };
  }, [endpoint]); // Only reconnect if endpoint changes

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    disconnect,
    reconnect: connect
  };
};

export default useWebSocket;
