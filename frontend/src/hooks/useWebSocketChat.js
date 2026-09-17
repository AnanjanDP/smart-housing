import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocketChat = (roomId, initialMessages = []) => {
  const [messages, setMessages] = useState(initialMessages);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!roomId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // In dev mode, connect directly to search-service on port 8001 to bypass Vite proxy socket abort error
    const host = import.meta.env.DEV ? `${window.location.hostname}:8001` : window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/search/ws/chat/${roomId}`;

    let socket;
    try {
      socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'chat_message' && data.text) {
            setMessages((prev) => {
              // Avoid duplicate messages if received back from broadcast
              if (prev.some((m) => m.id === data.id)) return prev;
              return [
                ...prev,
                {
                  id: data.id || Date.now(),
                  sender: data.sender || 'user',
                  sender_name: data.sender_name,
                  text: data.text,
                  timestamp: data.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }
              ];
            });
          }
        } catch (e) {
          console.warn('Error parsing incoming WS message:', e);
        }
      };

      socket.onerror = (err) => {
        console.warn('WebSocket error, using local fallback:', err);
        setIsConnected(false);
      };

      socket.onclose = () => {
        setIsConnected(false);
      };
    } catch (e) {
      console.warn('Could not establish WebSocket, fallback active:', e);
    }

    return () => {
      if (socket) {
        socket.onclose = null;
        socket.onerror = null;
        if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
          socket.close(1000, 'Closing connection');
        }
      }
    };
  }, [roomId]);

  const sendMessage = useCallback((text, sender = 'user', senderName = '') => {
    if (!text || !text.trim()) return;

    const msgId = Date.now();
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const newMsg = {
      id: msgId,
      sender: sender,
      sender_name: senderName,
      text: text.trim(),
      timestamp: timestamp
    };

    // Optimistically update UI
    setMessages((prev) => [...prev, newMsg]);

    // Send via WebSocket if connected
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(newMsg));
    }
  }, []);

  return {
    messages,
    setMessages,
    isConnected,
    sendMessage
  };
};
