/**
 * GPS CDM WebSocket Hook
 *
 * Provides real-time updates for:
 * - Processing error counts
 * - Pipeline throughput
 * - Batch progress
 */
import { useState, useEffect, useCallback, useRef } from 'react';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';

export interface WebSocketStats {
  errors: {
    by_status: Record<string, number>;
    pending_by_zone: Record<string, number>;
    total_pending: number;
    recent_5min: number;
  };
  throughput: {
    bronze_last_hour: number;
    silver_last_hour: number;
    gold_last_hour: number;
  };
  error?: string;
}

export interface WebSocketMessage {
  type: 'stats_update';
  timestamp: string;
  data: WebSocketStats;
}

export interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (data: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export interface UseWebSocketReturn {
  stats: WebSocketStats | null;
  isConnected: boolean;
  lastUpdate: Date | null;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: string) => void;
  error: string | null;
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [stats, setStats] = useState<WebSocketStats | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    clearTimers();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, [clearTimers]);

  const connect = useCallback(() => {
    // Don't connect if already connected or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN ||
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    clearTimers();
    setError(null);

    try {
      const ws = new WebSocket(`${WS_BASE_URL}/stream`);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onConnect?.();

        // Set up ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (message.type === 'stats_update') {
            setStats(message.data);
            setLastUpdate(new Date(message.timestamp));
            onMessage?.(message);
          }
        } catch {
          // Handle non-JSON messages (like pong)
          if (event.data !== 'pong') {
            console.warn('Received non-JSON WebSocket message:', event.data);
          }
        }
      };

      ws.onerror = (event) => {
        setError('WebSocket connection error');
        onError?.(event);
      };

      ws.onclose = () => {
        setIsConnected(false);
        clearTimers();
        onDisconnect?.();

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = Math.min(
            reconnectInterval * Math.pow(1.5, reconnectAttemptsRef.current - 1),
            30000
          );
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        } else {
          setError(`Failed to connect after ${maxReconnectAttempts} attempts`);
        }
      };
    } catch (err) {
      setError(`Failed to create WebSocket connection: ${err}`);
    }
  }, [
    clearTimers,
    maxReconnectAttempts,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
    reconnectInterval,
  ]);

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    stats,
    isConnected,
    lastUpdate,
    connect,
    disconnect,
    sendMessage,
    error,
  };
}

export default useWebSocket;
