import React, { useEffect, useRef, useState } from "react";
import { useLogin } from "../hooks/useLogin";

const Realtime = () => {
  useLogin();
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const socketRef = useRef(null);

  const userData = localStorage.getItem("userData") ?? null;

  useEffect(() => {
    const ws = new WebSocket("ws://web07.cs.ait.ac.th:7777");
    socketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      try {
        // Try to parse JSON first
        const data = JSON.parse(event.data);

        if (data.echo) {
          setMessages((prev) => [...prev, data.echo]);
        } else if (data.time) {
          setMessages((prev) => [...prev, data.time]);
        } else {
          setMessages((prev) => [...prev, event.data]);
        }
      } catch {
        setMessages((prev) => [...prev, event.data]);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const user = userData ? JSON.parse(userData) : null;
      const email = user ? user.email : null;
      const eMessage = email ? `${email}: ${message}` : message;
      socketRef.current.send(eMessage);
      setMessage("");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>WebSocket Demo (React)</h2>

      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message"
      />

      <button onClick={sendMessage}>Send</button>

      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
    </div>
  );
};

export default Realtime;
