import { useEffect, useState } from "react";

export default function AlertComponent() {
    const [alertMessage, setAlertMessage] = useState<string | null>(null);

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8000/ws");

        ws.onopen = () => {
            console.log("Connected to WebSocket Server");
        };

        ws.onmessage = (event) => {
            console.log("Message from server:", event.data);
            setAlertMessage(event.data);
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <div className="flex justify-center">
            {alertMessage && (
                <div className="w-fit rounded fixed bg-orange-100 border-l-4 border-orange-500 text-orange-700 p-4">
                    <div className="flex justify-between items-center">
                        <p className="font-bold">Be Warned</p>
                        <button
                            onClick={() => setAlertMessage(null)}
                            className="text-orange-700 hover:text-orange-900 cursor-pointer"
                        >
                            ✖
                        </button>
                    </div>
                    <p>{alertMessage}</p>
                    <p className="text-xs text-right">Time: {new Date().toLocaleTimeString()}</p>
                </div>
            )}
        </div>
    );
}