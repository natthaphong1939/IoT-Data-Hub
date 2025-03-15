import { useEffect, useState } from "react";
import { formatTimestampTH } from "../function/formatTimestampTH";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';

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
                    <div className="bg-white p-6 rounded-lg w-fit">
                        <div className="flex mb-4 gap-4">
                            <div>
                                <div className="flex items-center gap-2 mb-2">
                                    <FontAwesomeIcon icon={faTriangleExclamation} className="text-amber-500 text-2xl" />
                                    <h2 className="text-lg font-bold">Warning</h2>
                                </div>
                                <p className="">{alertMessage}</p>
                            </div>
                            <button
                                onClick={() => setAlertMessage(null)}
                                className="cursor-pointer h-fit"
                            >
                                ✖
                            </button>
                        </div>
                        <p className="text-right mt-4">
                            Timestamp: {formatTimestampTH()}
                        </p>
                    </div>
                </div>
            )}
        </>
    );
}