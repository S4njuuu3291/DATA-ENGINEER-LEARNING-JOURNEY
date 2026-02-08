CREATE TABLE crypto_trades (
    symbol TEXT NOT NULL,
    price NUMERIC NOT NULL,
    event_time BIGINT NOT NULL,
    processed_at BIGINT NOT NULL,
    PRIMARY KEY (symbol, event_time)
);
