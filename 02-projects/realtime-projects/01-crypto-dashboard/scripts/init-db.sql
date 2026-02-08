--
-- PostgreSQL database dump (FIXED VERSION)
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';
SET default_table_access_method = heap;

--------------------------------------------------------------------------------
-- 1. DROP EXISTING TO AVOID CONFLICTS
--------------------------------------------------------------------------------
DROP VIEW IF EXISTS public.candle_1h;
DROP VIEW IF EXISTS public.candle_45m;
DROP VIEW IF EXISTS public.candle_15m;
DROP VIEW IF EXISTS public.candle_5m;
DROP VIEW IF EXISTS public.candle_1m;
DROP TABLE IF EXISTS public.temp_window_1m;
DROP TABLE IF EXISTS public.crypto_prices;
DROP TABLE IF EXISTS public.window_1m;

--------------------------------------------------------------------------------
-- 2. CREATE TABLES WITH TIMESTAMPTZ (WITH TIME ZONE)
--------------------------------------------------------------------------------

-- Tabel Utama untuk Data OHLC 1 Menit
CREATE TABLE public.window_1m (
    window_start timestamp with time zone NOT NULL,
    window_end timestamp with time zone,
    symbol character varying(255) NOT NULL,
    open numeric(38,18),
    high numeric(38,18),
    low numeric(38,18),
    close numeric(38,18),
    CONSTRAINT window_1m_pkey PRIMARY KEY (window_start, symbol)
);
ALTER TABLE public.window_1m OWNER TO "crypto-stream-user";

-- Tabel untuk Data Raw Prices (Tick Data)
CREATE TABLE public.crypto_prices (
    symbol character varying(20),
    price numeric(38,18),
    event_time timestamp with time zone,
    processed_time timestamp with time zone
);
ALTER TABLE public.crypto_prices OWNER TO "crypto-stream-user";

-- Tabel Temporary untuk Staging Upsert Spark
CREATE TABLE public.temp_window_1m (
    window_start timestamp with time zone,
    window_end timestamp with time zone,
    symbol text,
    open numeric(38,18),
    high numeric(38,18),
    low numeric(38,18),
    close numeric(38,18)
);
ALTER TABLE public.temp_window_1m OWNER TO "crypto-stream-user";

--------------------------------------------------------------------------------
-- 3. CREATE VIEWS FOR CANDLESTICK AGGREGATION
--------------------------------------------------------------------------------

-- View 1 Minute (Direct from Table)
CREATE VIEW public.candle_1m AS
 SELECT 
    window_start AS "time",
    symbol,
    open,
    high,
    low,
    close
 FROM public.window_1m;
ALTER VIEW public.candle_1m OWNER TO "crypto-stream-user";

-- View 5 Minutes
CREATE VIEW public.candle_5m AS
 SELECT 
    (date_trunc('hour', window_start) + (((date_part('minute', window_start)::integer / 5) * 5) || ' minutes')::interval) AS "time",
    symbol,
    (array_agg(open ORDER BY window_start ASC))[1] AS open,
    max(high) AS high,
    min(low) AS low,
    (array_agg(close ORDER BY window_start DESC))[1] AS close
 FROM public.window_1m
 GROUP BY 1, 2;
ALTER VIEW public.candle_5m OWNER TO "crypto-stream-user";

-- View 15 Minutes
CREATE VIEW public.candle_15m AS
 SELECT 
    (date_trunc('hour', window_start) + (((date_part('minute', window_start)::integer / 15) * 15) || ' minutes')::interval) AS "time",
    symbol,
    (array_agg(open ORDER BY window_start ASC))[1] AS open,
    max(high) AS high,
    min(low) AS low,
    (array_agg(close ORDER BY window_start DESC))[1] AS close
 FROM public.window_1m
 GROUP BY 1, 2;
ALTER VIEW public.candle_15m OWNER TO "crypto-stream-user";

-- View 45 Minutes
CREATE VIEW public.candle_45m AS
 SELECT 
    (date_trunc('hour', window_start) + (((date_part('minute', window_start)::integer / 45) * 45) || ' minutes')::interval) AS "time",
    symbol,
    (array_agg(open ORDER BY window_start ASC))[1] AS open,
    max(high) AS high,
    min(low) AS low,
    (array_agg(close ORDER BY window_start DESC))[1] AS close
 FROM public.window_1m
 GROUP BY 1, 2;
ALTER VIEW public.candle_45m OWNER TO "crypto-stream-user";

-- View 1 Hour
CREATE VIEW public.candle_1h AS
 SELECT 
    date_trunc('hour', window_start) AS "time",
    symbol,
    (array_agg(open ORDER BY window_start ASC))[1] AS open,
    max(high) AS high,
    min(low) AS low,
    (array_agg(close ORDER BY window_start DESC))[1] AS close
 FROM public.window_1m
 GROUP BY 1, 2;
ALTER VIEW public.candle_1h OWNER TO "crypto-stream-user";

-- Selesai