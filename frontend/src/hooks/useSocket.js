import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

export function useSocket(url = "http://localhost:5000") {
  const socketRef = useRef(null);
  const [connected,   setConnected]   = useState(false);
  const [moodUpdates, setMoodUpdates] = useState([]);

  useEffect(() => {
    socketRef.current = io(url, { transports: ["websocket"], autoConnect: true });

    socketRef.current.on("connect",    () => setConnected(true));
    socketRef.current.on("disconnect", () => setConnected(false));

    socketRef.current.on("mood_update", (data) => {
      setMoodUpdates((prev) => [data, ...prev].slice(0, 50));
    });

    return () => { socketRef.current?.disconnect(); };
  }, [url]);

  const emit = (event, data) => socketRef.current?.emit(event, data);

  return { connected, moodUpdates, emit };
}