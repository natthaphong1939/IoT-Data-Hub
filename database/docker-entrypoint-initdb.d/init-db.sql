\c mydatabase;

CREATE TABLE iot_data (
    id SERIAL PRIMARY KEY,
    location VARCHAR(255),
    timestamps BIGINT,
    temperature DECIMAL
);
