import { useState, useEffect } from "react";
import axios from "axios";
import { formatTimestampTH } from "./function/formatTimestampTH";

interface TempData {
  Location: string;
  Timestamps: number;
  Temperature: number;
}

interface MotionData {
  Timestamp: number;
  NumberOfMovements: number;
}

export default function Home() {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [tempData, setTempData] = useState<Record<string, TempData>>({});
  const [motionData, setMotionData] = useState<Record<string, MotionData>>({});
  const [motionDataGroup, setMotionDataGroup] = useState<Record<string, any>>({});
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tempResponse, motionGroupResponse, motionEachResponse] = await Promise.all([
          axios.get("http://localhost:8000/temp"),
          axios.get("http://localhost:8000/motion/group"),
          axios.get("http://localhost:8000/motion/each"),
        ]);

        setTempData(tempResponse.data);
        setMotionDataGroup(motionGroupResponse.data);
        setMotionData(motionEachResponse.data);
      } catch (err: any) {
        console.error(err);
        setError(`Error: ${err?.message || "Failed to fetch data."}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleOpenDoor = async () => {
    setIsOpen((prev) => !prev);

    try {
      const response = await axios.post("http://localhost:8000/api/open");

      console.log("Door Open Response:", response.data);
    } catch (error) {
      console.error("Error opening door:", error);
    }
  };


  if (loading) return <p className="text-center text-gray-500">Loading...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="flex flex-col h-full gap-4">
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <RoomStatus isOpen={isOpen} handleOpenDoor={handleOpenDoor} />
        <TemperatureDisplay tempData={tempData} />
      </section>
      <MotionDataTable motionData={motionData} motionDataGroup={motionDataGroup} />
    </div>
  );
}

const RoomStatus = ({ isOpen, handleOpenDoor }: { isOpen: boolean; handleOpenDoor: () => void }) => (
  <section className="w-full">
    <div className="h-d bg-white rounded-xl p-4 flex flex-col justify-between shadow-md">
      <div className="flex flex-col">
        <h2 className="text-xl font-bold">Room 39</h2>
        <div className="flex items-center">
          <p>
            Status:<span className={isOpen ? "text-green-500" : "text-red-500"}> {isOpen ? "open" : "closed"}</span>
          </p>
        </div>
      </div>
      <button
        onClick={handleOpenDoor}
        className="mt-4 py-2 px-4 rounded w-full text-white bg-blue-500 font-bold transition duration-200bg-blue-500 hover:bg-blue-700 cursor-pointer"
      >
        {isOpen ? "Close" : "Open"}
      </button>
    </div>
  </section>
);

const TemperatureDisplay = ({ tempData }: { tempData: Record<string, TempData> }) => {
  const locations = ["Inside", "Outside"];
  return (
    <section className="flex flex-col sm:flex-row gap-4 col-span-1 md:col-span-2">
      {locations.map((location) => (
        <div key={location} className="flex flex-col justify-between w-full h-d md:h-full p-4 bg-white rounded-xl text-center">
          <h2 className="text-xl font-medium">{location} Temperature</h2>
          <span className="text-4xl font-bold text-blue-600">
            {tempData?.[location]?.Temperature?.toFixed(1) ?? "--.-"}°C
          </span>
          <p className="text-sm text-gray-500">
            {formatTimestampTH(tempData?.[location]?.Timestamps).date}
            <br />
            {formatTimestampTH(tempData?.[location]?.Timestamps).time}
          </p>
        </div>
      ))}
    </section>
  );
};

const MotionDataTable = ({ motionData, motionDataGroup }: { motionData: Record<string, MotionData>; motionDataGroup: Record<string, any> }) => (
  <section className="w-full">
    <div className="bg-white h-full rounded-xl p-4 flex flex-col">
      <h2>Motion</h2>
      <p>Total time stamps: {formatTimestampTH(motionDataGroup?.maxTimestamp).time}</p>
      <p>Total number of movements: {motionDataGroup?.totalMovements ?? "--"}</p>

      <div className="relative overflow-x-auto">
        <table className="mt-4 w-full text-sm text-left text-gray-600">
          <thead className="text-gray-700 uppercase bg-gray-200 whitespace-nowrap">
            <tr>
              <th className="px-6 py-3">Location</th>
              <th className="px-6 py-3">Timestamps</th>
              <th className="px-6 py-3">Number of movements</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(motionData ?? {}).map(([location, data]) => (
              <tr key={location} className="odd:bg-white even:bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-4 font-medium text-gray-900">{location}</th>
                <td className="px-6 py-4">{formatTimestampTH(data.Timestamp).time}</td>
                <td className="px-6 py-4">{data.NumberOfMovements ?? "--"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </section>

);