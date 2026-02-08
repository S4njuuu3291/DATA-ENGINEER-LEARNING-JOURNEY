CREATE TABLE metal_prices (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    metal TEXT,
    currency TEXT,
    exchange TEXT,
    symbol TEXT,
    price_usd NUMERIC,
    price_idr NUMERIC,
    prev_close_price NUMERIC,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    ch NUMERIC,
    chp NUMERIC,
    ingestion_times TIMESTAMP NOT NULL
);