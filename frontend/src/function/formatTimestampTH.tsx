export const formatTimestampTH = (timestamp?: number) => {
    const date = new Date(timestamp ? timestamp * 1000 : Date.now());
    return date.toLocaleString("th-TH", { 
        year: "numeric", 
        month: "numeric", 
        day: "numeric", 
        hour: "2-digit", 
        minute: "2-digit"
    });
};
