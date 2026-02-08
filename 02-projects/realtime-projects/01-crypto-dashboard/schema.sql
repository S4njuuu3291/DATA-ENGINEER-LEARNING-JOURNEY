--
-- PostgreSQL database dump
--

\restrict 2GENQ6R1qHGfYiMozpHhKEXVZKikBjdOCUsFfMDjNAeZpGP6eOYziDIytxaTcm3

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

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

--
-- Name: window_1m; Type: TABLE; Schema: public; Owner: crypto-stream-user
--

CREATE TABLE public.window_1m (
    window_start timestamp with time zone NOT NULL,
    window_end timestamp with time zone,
    symbol character varying(255) NOT NULL,
    open numeric(38,18),
    high numeric(38,18),
    low numeric(38,18),
    close numeric(38,18)
);


ALTER TABLE public.window_1m OWNER TO "crypto-stream-user";

--
-- Name: candle_15m; Type: VIEW; Schema: public; Owner: crypto-stream-user
--

CREATE VIEW public.candle_15m AS
 SELECT (date_trunc('hour'::text, window_1m.window_start) + (((((date_part('minute'::text, window_1m.window_start))::integer / 15) * 15) || ' minutes'::text))::interval) AS "time",
    window_1m.symbol,
    (array_agg(window_1m.open ORDER BY window_1m.window_start))[1] AS open,
    max(window_1m.high) AS high,
    min(window_1m.low) AS low,
    (array_agg(window_1m.close ORDER BY window_1m.window_start DESC))[1] AS close
   FROM public.window_1m
  GROUP BY (date_trunc('hour'::text, window_1m.window_start) + (((((date_part('minute'::text, window_1m.window_start))::integer / 15) * 15) || ' minutes'::text))::interval), window_1m.symbol;


ALTER VIEW public.candle_15m OWNER TO "crypto-stream-user";

--
-- Name: candle_1h; Type: VIEW; Schema: public; Owner: crypto-stream-user
--

CREATE VIEW public.candle_1h AS
 SELECT date_trunc('hour'::text, window_1m.window_start) AS "time",
    window_1m.symbol,
    (array_agg(window_1m.open ORDER BY window_1m.window_start))[1] AS open,
    max(window_1m.high) AS high,
    min(window_1m.low) AS low,
    (array_agg(window_1m.close ORDER BY window_1m.window_start DESC))[1] AS close
   FROM public.window_1m
  GROUP BY (date_trunc('hour'::text, window_1m.window_start)), window_1m.symbol;


ALTER VIEW public.candle_1h OWNER TO "crypto-stream-user";

--
-- Name: candle_1m; Type: VIEW; Schema: public; Owner: crypto-stream-user
--

CREATE VIEW public.candle_1m AS
 SELECT window_1m.window_start AS "time",
    window_1m.symbol,
    window_1m.open,
    window_1m.high,
    window_1m.low,
    window_1m.close
   FROM public.window_1m;


ALTER VIEW public.candle_1m OWNER TO "crypto-stream-user";

--
-- Name: candle_45m; Type: VIEW; Schema: public; Owner: crypto-stream-user
--

CREATE VIEW public.candle_45m AS
 SELECT (date_trunc('hour'::text, window_1m.window_start) + (((((date_part('minute'::text, window_1m.window_start))::integer / 45) * 45) || ' minutes'::text))::interval) AS "time",
    window_1m.symbol,
    (array_agg(window_1m.open ORDER BY window_1m.window_start))[1] AS open,
    max(window_1m.high) AS high,
    min(window_1m.low) AS low,
    (array_agg(window_1m.close ORDER BY window_1m.window_start DESC))[1] AS close
   FROM public.window_1m
  GROUP BY (date_trunc('hour'::text, window_1m.window_start) + (((((date_part('minute'::text, window_1m.window_start))::integer / 45) * 45) || ' minutes'::text))::interval), window_1m.symbol;


ALTER VIEW public.candle_45m OWNER TO "crypto-stream-user";

--
-- Name: candle_5m; Type: VIEW; Schema: public; Owner: crypto-stream-user
--

CREATE VIEW public.candle_5m AS
 SELECT (date_trunc('hour'::text, window_1m.window_start) + (((((date_part('minute'::text, window_1m.window_start))::integer / 5) * 5) || ' minutes'::text))::interval) AS "time",
    window_1m.symbol,
    (array_agg(window_1m.open ORDER BY window_1m.window_start))[1] AS open,
    max(window_1m.high) AS high,
    min(window_1m.low) AS low,
    (array_agg(window_1m.close ORDER BY window_1m.window_start DESC))[1] AS close
   FROM public.window_1m
  GROUP BY (date_trunc('hour'::text, window_1m.window_start) + (((((date_part('minute'::text, window_1m.window_start))::integer / 5) * 5) || ' minutes'::text))::interval), window_1m.symbol;


ALTER VIEW public.candle_5m OWNER TO "crypto-stream-user";

--
-- Name: crypto_prices; Type: TABLE; Schema: public; Owner: crypto-stream-user
--

CREATE TABLE public.crypto_prices (
    symbol character varying(20),
    price numeric(38,18),
    event_time timestamp with time zone,
    processed_time timestamp with time zone
);


ALTER TABLE public.crypto_prices OWNER TO "crypto-stream-user";

--
-- Name: temp_window_1m; Type: TABLE; Schema: public; Owner: crypto-stream-user
--

CREATE TABLE public.temp_window_1m (
    window_start timestamp without time zone,
    window_end timestamp without time zone,
    symbol text,
    open numeric(38,18),
    high numeric(38,18),
    low numeric(38,18),
    close numeric(38,18)
);


ALTER TABLE public.temp_window_1m OWNER TO "crypto-stream-user";

--
-- Name: window_1m window_1m_pkey; Type: CONSTRAINT; Schema: public; Owner: crypto-stream-user
--

ALTER TABLE ONLY public.window_1m
    ADD CONSTRAINT window_1m_pkey PRIMARY KEY (window_start, symbol);


--
-- PostgreSQL database dump complete
--

\unrestrict 2GENQ6R1qHGfYiMozpHhKEXVZKikBjdOCUsFfMDjNAeZpGP6eOYziDIytxaTcm3

