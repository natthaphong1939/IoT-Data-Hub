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
        <>
            {alertMessage && (
                <div className="fixed inset-0 z-1 flex items-center justify-center bg-opacity-50">
                    <div className="bg-white p-6 rounded-lg w-96">
                        <div className="flex mb-4">
                            <div>
                                <h2 className="text-lg font-bold text-orange-700">Be Warned</h2>
                                <p className="text-gray-700">{alertMessage}</p>
                            </div>
                            <button
                                onClick={() => setAlertMessage(null)}
                                className="cursor-pointer h-fit"
                            >
                                ✖
                            </button>
                        </div>
                        <p className="text-gray-500 text-right mt-4">
                            Time: {new Date().toLocaleTimeString()}
                        </p>
                    </div>
                </div>
            )}
        </>
    );
}