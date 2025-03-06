import { useState, useEffect } from "react";
import axios from "axios";

interface TempData {
  Location: string;
  Timestamps: number;
  Temperature: number;
}

export default function Home() {
  const [tempData, setTempData] = useState<Record<string, TempData> | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get<{ [key: string]: TempData }>(
          "http://localhost:8000/temp"
        );
        setTempData(response.data);
      } catch (err: any) {
        console.log(err);

        setError(`Error: ${err?.message || "Failed to fetch temperature data."}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => console.log("Connected to WebSocket Server");
    ws.onmessage = (event) => {
      console.log("Message from server:", event.data);
      setMessages((prev) => [...prev, event.data]); // Store received messages
    };
    ws.onclose = () => console.log("WebSocket disconnected");

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const handleButtonClick = () => {
    if (socket) {
      socket.send("Open Door"); // Send message to WebSocket server
      console.log("Sent: Open Door");
    }
  };

  if (loading) return <p className="text-center text-gray-500">Loading...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg flex flex-col items-center">
        <section className="my-6 w-full">
          <h1 className="text-2xl font-semibold mb-4 text-center">Temperature Data</h1>
          {tempData ? (
            <ul>
              {Object.entries(tempData).map(([key, data]) => (
                <li
                  key={key}
                  className="border-b py-2 flex justify-between items-center"
                >
                  <div>
                    <p className="text-lg font-medium">{data.Location}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(data.Timestamps * 1000).toLocaleString()}
                    </p>
                  </div>
                  <span className="text-lg font-bold text-blue-600">
                    {data.Temperature.toFixed(2)}°C
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-center text-gray-500">No data available</p>
          )}
        </section>

        <section className="mt-6">
          <h1 className="text-2xl font-semibold mb-4 text-center">Room</h1>
          <button onClick={handleButtonClick}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded cursor-pointer">Open Door</button>
        </section>

        <section className="mt-6 w-full">
          <h2 className="text-xl font-semibold mb-2 text-center">WebSocket Messages</h2>
          <div className="border p-4 rounded-md h-40 overflow-y-auto bg-gray-50">
            {messages.length > 0 ? (
              messages.map((msg, index) => (
                <p key={index} className="text-gray-700">{msg}</p>
              ))
            ) : (
              <p className="text-center text-gray-500">No messages received yet</p>
            )}
          </div>
        </section>

      </div>
    </div>
  );
}
