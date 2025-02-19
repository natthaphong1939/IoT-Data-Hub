\c mydatabase;

CREATE TABLE temperature_logs  (
    id SERIAL PRIMARY KEY,
    location VARCHAR(255),
    timestamps BIGINT,
    temperature DECIMAL
);

CREATE TABLE motion_logs  (
    id SERIAL PRIMARY KEY,
    location VARCHAR(255),
    timestamps BIGINT,
    Number_of_movements DECIMAL
);