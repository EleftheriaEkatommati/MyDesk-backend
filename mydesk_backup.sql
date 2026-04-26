--
-- PostgreSQL database dump
--

\restrict pA8Omolg3hKNd7xQNhWfej9H7qEWVU7FecRrxa7SXWaYPN36ivtecIUniOXQVgQ

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Name: bookingstatus; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.bookingstatus AS ENUM (
    'ACTIVE',
    'CANCELLED',
    'CHECKED_IN'
);


ALTER TYPE public.bookingstatus OWNER TO admin;

--
-- Name: roleenum; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.roleenum AS ENUM (
    'admin',
    'user'
);


ALTER TYPE public.roleenum OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO admin;

--
-- Name: bookings; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.bookings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    desk_id integer NOT NULL,
    booking_date date NOT NULL,
    status public.bookingstatus NOT NULL
);


ALTER TABLE public.bookings OWNER TO admin;

--
-- Name: bookings_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.bookings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bookings_id_seq OWNER TO admin;

--
-- Name: bookings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.bookings_id_seq OWNED BY public.bookings.id;


--
-- Name: desks; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.desks (
    id integer NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    rotation integer NOT NULL,
    floor_id integer NOT NULL
);


ALTER TABLE public.desks OWNER TO admin;

--
-- Name: desks_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.desks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.desks_id_seq OWNER TO admin;

--
-- Name: desks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.desks_id_seq OWNED BY public.desks.id;


--
-- Name: floors; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.floors (
    id integer NOT NULL,
    floor_number integer NOT NULL,
    floor_name character varying(255)
);


ALTER TABLE public.floors OWNER TO admin;

--
-- Name: floors_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.floors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.floors_id_seq OWNER TO admin;

--
-- Name: floors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.floors_id_seq OWNED BY public.floors.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name public.roleenum NOT NULL
);


ALTER TABLE public.roles OWNER TO admin;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO admin;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    name character varying,
    hashed_password character varying NOT NULL,
    role_id integer,
    surname character varying
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: bookings id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bookings ALTER COLUMN id SET DEFAULT nextval('public.bookings_id_seq'::regclass);


--
-- Name: desks id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.desks ALTER COLUMN id SET DEFAULT nextval('public.desks_id_seq'::regclass);


--
-- Name: floors id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.floors ALTER COLUMN id SET DEFAULT nextval('public.floors_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.alembic_version (version_num) FROM stdin;
a1b2c3d4e5f6
\.


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.bookings (id, user_id, desk_id, booking_date, status) FROM stdin;
61	2	12	2026-04-26	ACTIVE
62	11	89	2026-04-26	ACTIVE
\.


--
-- Data for Name: desks; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.desks (id, x, y, rotation, floor_id) FROM stdin;
89	180	320	0	10
6	120	150	0	2
8	60	220	90	3
5	120	220	0	2
38	220	220	0	2
71	120	340	0	2
72	220	340	0	2
37	640	80	90	2
73	640	180	90	2
15	120	220	0	1
16	200	220	0	1
75	520	80	90	2
74	520	180	90	2
12	500	60	270	1
3	640	300	0	1
76	540	300	90	2
77	640	300	90	2
9	60	300	90	3
78	200	380	0	3
11	800	320	270	1
79	300	380	0	3
80	140	440	0	3
81	80	500	0	3
82	380	440	0	3
83	460	500	0	3
10	560	300	0	1
39	120	460	0	1
40	220	460	0	1
41	140	60	0	1
42	220	60	0	1
84	140	120	180	3
85	240	120	180	3
86	360	120	180	3
43	500	160	270	1
45	500	480	90	1
44	500	400	90	1
7	220	140	0	2
88	480	300	270	3
87	480	200	270	3
\.


--
-- Data for Name: floors; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.floors (id, floor_number, floor_name) FROM stdin;
1	1	1st Floor
2	2	2nd Floor
3	3	3rd Floor
10	4	4rth Floor
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.roles (id, name) FROM stdin;
1	admin
2	user
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (id, email, name, hashed_password, role_id, surname) FROM stdin;
1	admin@mydesk.com	Admin User	$2b$12$zPGIyEqhN5F09PKRUEgoA.A2APZAGUajuuvbenqueuMv/Vr/UoGvi	1	\N
2	user@mydesk.com	Regular User	$2b$12$KNRRCp4vzqqyALmTaCpj/OpsoVdAYi83vF7vrSG4HQ24cHdOKkNhy	2	\N
11	user_2@mydesk.com	user_2	$2b$12$MkNB65pK1mzEGUgjgtMyEugMFWxibGgyMUmsSxgFR6.qlsQpQ2kLm	2	\N
\.


--
-- Name: bookings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.bookings_id_seq', 62, true);


--
-- Name: desks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.desks_id_seq', 89, true);


--
-- Name: floors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.floors_id_seq', 10, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.roles_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 11, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- Name: desks desks_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.desks
    ADD CONSTRAINT desks_pkey PRIMARY KEY (id);


--
-- Name: floors floors_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.floors
    ADD CONSTRAINT floors_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_bookings_booking_date; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_bookings_booking_date ON public.bookings USING btree (booking_date);


--
-- Name: ix_bookings_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_bookings_id ON public.bookings USING btree (id);


--
-- Name: ix_bookings_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_bookings_status ON public.bookings USING btree (status);


--
-- Name: ix_desks_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_desks_id ON public.desks USING btree (id);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: bookings bookings_desk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_desk_id_fkey FOREIGN KEY (desk_id) REFERENCES public.desks(id);


--
-- Name: bookings bookings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: desks desks_floor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.desks
    ADD CONSTRAINT desks_floor_id_fkey FOREIGN KEY (floor_id) REFERENCES public.floors(id) ON DELETE CASCADE;


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict pA8Omolg3hKNd7xQNhWfej9H7qEWVU7FecRrxa7SXWaYPN36ivtecIUniOXQVgQ

