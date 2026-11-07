import { useState, useEffect, useRef, useCallback } from 'react';

const AUTH_DENIED_CODES = [4401, 4403];

const formatTime = (iso) => {
  if (!iso) return '';
  const date = new Date(iso);
  return Number.isNaN(date.getTime())
    ? ''
    : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

/**
 * Live chat for one private room.
 *
 * The server only lets the two participants of a room join, and it identifies each sender from the
 * access token sent as the first message, so the sender shown for a message is the verified one.
 * Without a room id or a signed-in user the hook stays in local-only mode.
 *
 * options.selfId      the signed-in user's id, used to tell your messages from the other person's
 * options.otherSender label given to the other person's messages (the modals style by this)
 */
export const useWebSocketChat = (roomId, initialMessages = [], options = {}) => {
  const { selfId = null, otherSender = 'other' } = options;
  const [messages, setMessages] = useState(initialMessages);
  const [isConnected, setIsConnected] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('staymatch_token');
    if (!roomId || !token) return undefined;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // In dev mode, connect directly to search-service on port 8001 to bypass Vite proxy socket abort error
    const host = import.meta.env.DEV ? `${window.location.hostname}:8001` : window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/search/ws/chat/${roomId}`;

    let socket;
    try {
      socket = new WebSocket(wsUrl);
      socketRef.current = socket;
      setAccessDenied(false);

      socket.onopen = () => {
        // The token goes in the first message, not the URL, so it never ends up in server logs.
        socket.send(JSON.stringify({ type: 'auth', token }));
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'connection_established') {
            setIsConnected(true);
            return;
          }
          if (data.type === 'error') {
            console.warn('Chat server error:', data.code);
            return;
          }
          if (data.type === 'chat_message' && data.text) {
            const mine = Boolean(selfId) && data.sender_id === selfId;
            setMessages((prev) => {
              // Your own message is already on screen (added when you sent it); the server echoes it back.
              if (prev.some((m) => m.id === data.id)) return prev;
              if (mine && data.client_id != null && prev.some((m) => m.id === data.client_id)) return prev;
              return [
                ...prev,
                {
                  id: data.id,
                  sender: mine ? 'user' : otherSender,
                  sender_name: data.sender_name,
                  text: data.text,
                  timestamp: formatTime(data.timestamp)
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

      socket.onclose = (event) => {
        setIsConnected(false);
        if (AUTH_DENIED_CODES.includes(event.code)) setAccessDenied(true);
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
  }, [roomId, selfId, otherSender]);

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

    // Send via WebSocket if connected; the server decides who the sender is
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ id: msgId, text: newMsg.text, sender_name: senderName }));
    }
  }, []);

  return {
    messages,
    setMessages,
    isConnected,
    accessDenied,
    sendMessage
  };
};
