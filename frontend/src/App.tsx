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
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("Connected to WebSocket Server");
    };

    ws.onmessage = (event) => {
      console.log("Message from server:", event.data);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);


  const handleButtonClick = () => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send("open");
      console.log("Sent: open");
    } else {
      console.error("WebSocket is not open");
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

        <section>

          <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
              <button
                onClick={handleButtonClick}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full">Send "open" to WebSocket
              </button>
            </div>
        </section>

      </div>
    </div>
  );
}
