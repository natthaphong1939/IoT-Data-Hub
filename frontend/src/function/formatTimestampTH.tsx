export const formatTimestampTH = (timestamp?: number) => {
    const date = new Date(timestamp ? timestamp * 1000 : Date.now());
    return {
        date: date.toLocaleDateString("th-TH"),
        time: date.toLocaleTimeString("th-TH", { hour: "2-digit", minute: "2-digit" })
    };
};
