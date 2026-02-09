--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2026-02-08 22:10:49

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 97862)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5284 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 260 (class 1255 OID 98413)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 98687)
-- Name: agent_decisions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_decisions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    agent_type character varying(50) NOT NULL,
    request_type character varying(100) NOT NULL,
    request_data jsonb NOT NULL,
    context_snapshot jsonb,
    plan_attempted jsonb,
    tool_results jsonb,
    feasible boolean,
    feasibility_reason text,
    policy_compliant boolean,
    policy_violations jsonb,
    confidence double precision,
    confidence_factors jsonb,
    decision character varying(20),
    reasoning text,
    escalation_reason text,
    response text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone,
    agent_version character varying(20),
    execution_time_ms integer,
    retry_count integer DEFAULT 0,
    CONSTRAINT agent_decisions_decision_check CHECK (((decision)::text = ANY ((ARRAY['approve'::character varying, 'deny'::character varying, 'escalate'::character varying])::text[])))
);


ALTER TABLE public.agent_decisions OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 98807)
-- Name: budget_adjustments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.budget_adjustments (
    adjustment_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    budget_id uuid,
    adjustment_amount numeric(18,2) NOT NULL,
    reason text,
    requested_by character varying(255),
    approved_by character varying(255),
    approved_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.budget_adjustments OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 99152)
-- Name: coordination_decisions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coordination_decisions (
    id integer NOT NULL,
    coordination_id character varying(100) NOT NULL,
    agent_type character varying(50),
    agent_id character varying(100),
    location character varying(255),
    resources_needed text[],
    estimated_cost numeric(15,2),
    plan_details jsonb,
    conflict_type character varying(50),
    agents_involved text[],
    resolution_method character varying(20),
    resolution_rationale text,
    llm_confidence numeric(3,2),
    human_approver character varying(100),
    outcome character varying(50),
    approval_notes text,
    created_at timestamp without time zone DEFAULT now(),
    resolved_at timestamp without time zone,
    status character varying(20) DEFAULT 'active'::character varying
);


ALTER TABLE public.coordination_decisions OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 99151)
-- Name: coordination_decisions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.coordination_decisions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coordination_decisions_id_seq OWNER TO postgres;

--
-- TOC entry 5285 (class 0 OID 0)
-- Dependencies: 248
-- Name: coordination_decisions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.coordination_decisions_id_seq OWNED BY public.coordination_decisions.id;


--
-- TOC entry 219 (class 1259 OID 98704)
-- Name: department_budgets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.department_budgets (
    budget_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    year integer NOT NULL,
    month integer NOT NULL,
    total_budget numeric(15,2) NOT NULL,
    allocated numeric(15,2) DEFAULT 0,
    spent numeric(15,2) DEFAULT 0,
    remaining numeric(15,2) GENERATED ALWAYS AS ((total_budget - spent)) STORED,
    utilization_percent numeric(5,2) GENERATED ALWAYS AS (
CASE
    WHEN (total_budget > (0)::numeric) THEN ((spent / total_budget) * (100)::numeric)
    ELSE (0)::numeric
END) STORED,
    status character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT department_budgets_month_check CHECK (((month >= 1) AND (month <= 12))),
    CONSTRAINT department_budgets_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'depleted'::character varying, 'frozen'::character varying, 'closed'::character varying])::text[])))
);


ALTER TABLE public.department_budgets OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 99059)
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    department_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department_key character varying(50) NOT NULL,
    display_name character varying(255) NOT NULL,
    contact_email character varying(255),
    contact_phone character varying(50),
    manager_name character varying(255),
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 98855)
-- Name: disease_incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.disease_incidents (
    incident_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    incident_type character varying(255) NOT NULL,
    location text NOT NULL,
    severity character varying(20),
    reported_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reported_by character varying(255),
    status character varying(50),
    description text,
    public_health_actions jsonb,
    related_decision_id uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT disease_incidents_severity_check CHECK (((severity)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying])::text[]))),
    CONSTRAINT disease_incidents_status_check CHECK (((status)::text = ANY ((ARRAY['reported'::character varying, 'investigating'::character varying, 'contained'::character varying, 'closed'::character varying])::text[])))
);


ALTER TABLE public.disease_incidents OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 98723)
-- Name: finance_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_accounts (
    account_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    account_name character varying(255) NOT NULL,
    account_type character varying(50),
    currency character varying(10) DEFAULT 'INR'::character varying,
    balance numeric(18,2) DEFAULT 0,
    reserved_amount numeric(18,2) DEFAULT 0,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.finance_accounts OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 98845)
-- Name: finance_policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_policies (
    policy_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    policy_name character varying(255) NOT NULL,
    description text,
    effective_date date,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.finance_policies OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 98790)
-- Name: financial_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_transactions (
    transaction_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50),
    account_id uuid,
    amount numeric(18,2) NOT NULL,
    transaction_type character varying(20),
    description text,
    reference_id uuid,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT financial_transactions_transaction_type_check CHECK (((transaction_type)::text = ANY ((ARRAY['credit'::character varying, 'debit'::character varying])::text[])))
);


ALTER TABLE public.financial_transactions OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 98770)
-- Name: fund_allocations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fund_allocations (
    allocation_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    budget_id uuid,
    account_id uuid,
    amount numeric(18,2) NOT NULL,
    purpose text,
    allocated_by character varying(255),
    allocated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.fund_allocations OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 98758)
-- Name: grants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grants (
    grant_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    grant_name character varying(255) NOT NULL,
    provider character varying(255),
    department character varying(50),
    amount_awarded numeric(18,2),
    amount_received numeric(18,2) DEFAULT 0,
    start_date date,
    end_date date,
    status character varying(50),
    match_requirements jsonb,
    terms jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT grants_status_check CHECK (((status)::text = ANY ((ARRAY['proposed'::character varying, 'awarded'::character varying, 'active'::character varying, 'closed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.grants OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 98907)
-- Name: health_facilities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_facilities (
    facility_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    location text,
    capacity integer,
    services jsonb,
    status character varying(50),
    contact jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT health_facilities_status_check CHECK (((status)::text = ANY ((ARRAY['open'::character varying, 'closed'::character varying, 'under_maintenance'::character varying])::text[])))
);


ALTER TABLE public.health_facilities OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 98940)
-- Name: health_policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_policies (
    policy_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    policy_name character varying(255) NOT NULL,
    description text,
    effective_date date,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.health_policies OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 98919)
-- Name: health_resources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_resources (
    resource_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    resource_type character varying(255),
    quantity integer DEFAULT 0,
    location text,
    status character varying(50),
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.health_resources OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 98930)
-- Name: health_surveillance_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_surveillance_reports (
    report_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    source character varying(255),
    report_date timestamp without time zone NOT NULL,
    summary jsonb,
    severity_assessment character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.health_surveillance_reports OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 99043)
-- Name: incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.incidents (
    incident_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    incident_type character varying(100) NOT NULL,
    location text NOT NULL,
    severity character varying(20),
    reported_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reported_by character varying(255),
    description text,
    status character varying(20),
    resolution_date timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text,
    CONSTRAINT incidents_severity_check CHECK (((severity)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying])::text[]))),
    CONSTRAINT incidents_status_check CHECK (((status)::text = ANY ((ARRAY['reported'::character varying, 'investigating'::character varying, 'resolved'::character varying, 'closed'::character varying])::text[])))
);


ALTER TABLE public.incidents OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 99072)
-- Name: pipeline_inspections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pipeline_inspections (
    inspection_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    pipeline_id uuid,
    inspector character varying(255),
    inspection_date date NOT NULL,
    outcome character varying(50),
    notes text,
    findings jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.pipeline_inspections OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 99012)
-- Name: pipelines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pipelines (
    pipeline_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    location text NOT NULL,
    zone character varying(50),
    pipeline_type character varying(20),
    diameter_mm integer,
    material character varying(50),
    length_meters numeric(10,2),
    pressure_psi numeric(6,2),
    flow_rate numeric(10,2),
    condition character varying(20),
    installation_date date,
    last_inspection_date date,
    next_inspection_due date,
    operational_status character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text,
    CONSTRAINT pipelines_condition_check CHECK (((condition)::text = ANY ((ARRAY['excellent'::character varying, 'good'::character varying, 'fair'::character varying, 'poor'::character varying, 'critical'::character varying])::text[]))),
    CONSTRAINT pipelines_operational_status_check CHECK (((operational_status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'under_repair'::character varying, 'retired'::character varying])::text[]))),
    CONSTRAINT pipelines_pipeline_type_check CHECK (((pipeline_type)::text = ANY ((ARRAY['supply'::character varying, 'drainage'::character varying, 'sewage'::character varying])::text[])))
);


ALTER TABLE public.pipelines OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 98950)
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    project_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    project_name character varying(255) NOT NULL,
    project_type character varying(100),
    location text,
    estimated_cost numeric(15,2),
    actual_cost numeric(15,2) DEFAULT 0,
    start_date date,
    end_date date,
    completion_date date,
    status character varying(20),
    agent_decision_id uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text,
    CONSTRAINT projects_status_check CHECK (((status)::text = ANY ((ARRAY['planned'::character varying, 'approved'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 98822)
-- Name: reserve_funds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reserve_funds (
    reserve_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    reserve_name character varying(255),
    amount numeric(18,2) DEFAULT 0,
    min_required_percent numeric(5,2) DEFAULT 0,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.reserve_funds OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 99029)
-- Name: reservoirs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservoirs (
    reservoir_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    location text NOT NULL,
    capacity_liters bigint NOT NULL,
    current_level_liters bigint,
    level_percentage numeric(5,2) GENERATED ALWAYS AS (
CASE
    WHEN (capacity_liters > 0) THEN (((current_level_liters)::numeric / (capacity_liters)::numeric) * (100)::numeric)
    ELSE (0)::numeric
END) STORED,
    operational_status character varying(20),
    last_reading_time timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reservoirs_operational_status_check CHECK (((operational_status)::text = ANY ((ARRAY['active'::character varying, 'maintenance'::character varying, 'emergency'::character varying, 'inactive'::character varying])::text[])))
);


ALTER TABLE public.reservoirs OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 98748)
-- Name: revenue_forecasts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.revenue_forecasts (
    forecast_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50),
    period_start date NOT NULL,
    period_end date NOT NULL,
    forecast_amount numeric(18,2) NOT NULL,
    method character varying(100),
    confidence numeric(5,4),
    model_metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.revenue_forecasts OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 98737)
-- Name: revenue_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.revenue_history (
    revenue_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50),
    period_start date NOT NULL,
    period_end date NOT NULL,
    amount numeric(18,2) NOT NULL,
    source character varying(255),
    details jsonb,
    recorded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.revenue_history OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 98885)
-- Name: sanitation_inspections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sanitation_inspections (
    inspection_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    location text,
    facility character varying(255),
    inspection_date date NOT NULL,
    outcome character varying(50),
    inspector character varying(255),
    notes text,
    findings jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT sanitation_inspections_outcome_check CHECK (((outcome)::text = ANY ((ARRAY['pass'::character varying, 'conditional_pass'::character varying, 'fail'::character varying])::text[])))
);


ALTER TABLE public.sanitation_inspections OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 99103)
-- Name: service_outages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_outages (
    outage_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    location text,
    zone character varying(50),
    reported_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    started_at timestamp without time zone,
    resolved_at timestamp without time zone,
    severity character varying(20),
    cause text,
    affected_customers integer,
    status character varying(20),
    related_pipeline_id uuid,
    incident_id uuid,
    notes text,
    CONSTRAINT service_outages_severity_check CHECK (((severity)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying])::text[]))),
    CONSTRAINT service_outages_status_check CHECK (((status)::text = ANY ((ARRAY['reported'::character varying, 'investigating'::character varying, 'mitigating'::character varying, 'resolved'::character varying, 'closed'::character varying])::text[])))
);


ALTER TABLE public.service_outages OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 98835)
-- Name: tax_revenues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tax_revenues (
    tax_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    period_start date,
    period_end date,
    source character varying(255),
    department character varying(50),
    amount numeric(18,2),
    details jsonb,
    recorded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tax_revenues OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 98874)
-- Name: vaccination_campaigns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vaccination_campaigns (
    campaign_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    location text,
    start_date date,
    end_date date,
    target_groups jsonb,
    coverage_percent numeric(5,2),
    status character varying(50),
    resources jsonb,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT vaccination_campaigns_status_check CHECK (((status)::text = ANY ((ARRAY['planned'::character varying, 'active'::character varying, 'completed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.vaccination_campaigns OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 98897)
-- Name: vulnerable_populations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vulnerable_populations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    location text,
    population_group character varying(255),
    population_count integer,
    vulnerability_index numeric(5,2),
    notes text,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.vulnerable_populations OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 99088)
-- Name: water_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.water_readings (
    reading_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    pipeline_id uuid,
    location text,
    reading_time timestamp without time zone NOT NULL,
    pressure_psi numeric(10,2),
    flow_rate numeric(12,4),
    temperature numeric(8,2),
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.water_readings OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 98971)
-- Name: work_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_schedules (
    schedule_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    activity_type character varying(100) NOT NULL,
    location text NOT NULL,
    scheduled_date date NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    priority character varying(20),
    workers_assigned integer,
    equipment_assigned jsonb,
    status character varying(20),
    project_id uuid,
    agent_decision_id uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text,
    CONSTRAINT work_schedules_priority_check CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying])::text[]))),
    CONSTRAINT work_schedules_status_check CHECK (((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.work_schedules OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 98998)
-- Name: workers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workers (
    worker_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    department character varying(50) NOT NULL,
    worker_name character varying(255) NOT NULL,
    role character varying(100),
    skills jsonb,
    certifications jsonb,
    status character varying(20),
    phone character varying(20),
    email character varying(255),
    hire_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT workers_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'on_leave'::character varying, 'sick'::character varying, 'inactive'::character varying])::text[])))
);


ALTER TABLE public.workers OWNER TO postgres;

--
-- TOC entry 4960 (class 2604 OID 99155)
-- Name: coordination_decisions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coordination_decisions ALTER COLUMN id SET DEFAULT nextval('public.coordination_decisions_id_seq'::regclass);


--
-- TOC entry 4986 (class 2606 OID 98697)
-- Name: agent_decisions agent_decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_decisions
    ADD CONSTRAINT agent_decisions_pkey PRIMARY KEY (id);


--
-- TOC entry 5021 (class 2606 OID 98815)
-- Name: budget_adjustments budget_adjustments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budget_adjustments
    ADD CONSTRAINT budget_adjustments_pkey PRIMARY KEY (adjustment_id);


--
-- TOC entry 5109 (class 2606 OID 99163)
-- Name: coordination_decisions coordination_decisions_coordination_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coordination_decisions
    ADD CONSTRAINT coordination_decisions_coordination_id_key UNIQUE (coordination_id);


--
-- TOC entry 5111 (class 2606 OID 99161)
-- Name: coordination_decisions coordination_decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coordination_decisions
    ADD CONSTRAINT coordination_decisions_pkey PRIMARY KEY (id);


--
-- TOC entry 4994 (class 2606 OID 98719)
-- Name: department_budgets department_budgets_department_year_month_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department_budgets
    ADD CONSTRAINT department_budgets_department_year_month_key UNIQUE (department, year, month);


--
-- TOC entry 4996 (class 2606 OID 98717)
-- Name: department_budgets department_budgets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department_budgets
    ADD CONSTRAINT department_budgets_pkey PRIMARY KEY (budget_id);


--
-- TOC entry 5093 (class 2606 OID 99070)
-- Name: departments departments_department_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_department_key_key UNIQUE (department_key);


--
-- TOC entry 5095 (class 2606 OID 99068)
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (department_id);


--
-- TOC entry 5033 (class 2606 OID 98866)
-- Name: disease_incidents disease_incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disease_incidents
    ADD CONSTRAINT disease_incidents_pkey PRIMARY KEY (incident_id);


--
-- TOC entry 5001 (class 2606 OID 98735)
-- Name: finance_accounts finance_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_accounts
    ADD CONSTRAINT finance_accounts_pkey PRIMARY KEY (account_id);


--
-- TOC entry 5030 (class 2606 OID 98853)
-- Name: finance_policies finance_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_policies
    ADD CONSTRAINT finance_policies_pkey PRIMARY KEY (policy_id);


--
-- TOC entry 5017 (class 2606 OID 98799)
-- Name: financial_transactions financial_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_transactions
    ADD CONSTRAINT financial_transactions_pkey PRIMARY KEY (transaction_id);


--
-- TOC entry 5014 (class 2606 OID 98778)
-- Name: fund_allocations fund_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fund_allocations
    ADD CONSTRAINT fund_allocations_pkey PRIMARY KEY (allocation_id);


--
-- TOC entry 5011 (class 2606 OID 98768)
-- Name: grants grants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grants
    ADD CONSTRAINT grants_pkey PRIMARY KEY (grant_id);


--
-- TOC entry 5047 (class 2606 OID 98917)
-- Name: health_facilities health_facilities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_facilities
    ADD CONSTRAINT health_facilities_pkey PRIMARY KEY (facility_id);


--
-- TOC entry 5056 (class 2606 OID 98948)
-- Name: health_policies health_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_policies
    ADD CONSTRAINT health_policies_pkey PRIMARY KEY (policy_id);


--
-- TOC entry 5050 (class 2606 OID 98928)
-- Name: health_resources health_resources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_resources
    ADD CONSTRAINT health_resources_pkey PRIMARY KEY (resource_id);


--
-- TOC entry 5053 (class 2606 OID 98938)
-- Name: health_surveillance_reports health_surveillance_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_surveillance_reports
    ADD CONSTRAINT health_surveillance_reports_pkey PRIMARY KEY (report_id);


--
-- TOC entry 5091 (class 2606 OID 99054)
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (incident_id);


--
-- TOC entry 5100 (class 2606 OID 99080)
-- Name: pipeline_inspections pipeline_inspections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_inspections
    ADD CONSTRAINT pipeline_inspections_pkey PRIMARY KEY (inspection_id);


--
-- TOC entry 5081 (class 2606 OID 99024)
-- Name: pipelines pipelines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipelines
    ADD CONSTRAINT pipelines_pkey PRIMARY KEY (pipeline_id);


--
-- TOC entry 5063 (class 2606 OID 98961)
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (project_id);


--
-- TOC entry 5025 (class 2606 OID 98833)
-- Name: reserve_funds reserve_funds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserve_funds
    ADD CONSTRAINT reserve_funds_pkey PRIMARY KEY (reserve_id);


--
-- TOC entry 5085 (class 2606 OID 99040)
-- Name: reservoirs reservoirs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservoirs
    ADD CONSTRAINT reservoirs_pkey PRIMARY KEY (reservoir_id);


--
-- TOC entry 5009 (class 2606 OID 98756)
-- Name: revenue_forecasts revenue_forecasts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revenue_forecasts
    ADD CONSTRAINT revenue_forecasts_pkey PRIMARY KEY (forecast_id);


--
-- TOC entry 5006 (class 2606 OID 98745)
-- Name: revenue_history revenue_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revenue_history
    ADD CONSTRAINT revenue_history_pkey PRIMARY KEY (revenue_id);


--
-- TOC entry 5042 (class 2606 OID 98894)
-- Name: sanitation_inspections sanitation_inspections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sanitation_inspections
    ADD CONSTRAINT sanitation_inspections_pkey PRIMARY KEY (inspection_id);


--
-- TOC entry 5107 (class 2606 OID 99113)
-- Name: service_outages service_outages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_outages
    ADD CONSTRAINT service_outages_pkey PRIMARY KEY (outage_id);


--
-- TOC entry 5028 (class 2606 OID 98843)
-- Name: tax_revenues tax_revenues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_revenues
    ADD CONSTRAINT tax_revenues_pkey PRIMARY KEY (tax_id);


--
-- TOC entry 5038 (class 2606 OID 98883)
-- Name: vaccination_campaigns vaccination_campaigns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vaccination_campaigns
    ADD CONSTRAINT vaccination_campaigns_pkey PRIMARY KEY (campaign_id);


--
-- TOC entry 5045 (class 2606 OID 98905)
-- Name: vulnerable_populations vulnerable_populations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vulnerable_populations
    ADD CONSTRAINT vulnerable_populations_pkey PRIMARY KEY (id);


--
-- TOC entry 5103 (class 2606 OID 99096)
-- Name: water_readings water_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.water_readings
    ADD CONSTRAINT water_readings_pkey PRIMARY KEY (reading_id);


--
-- TOC entry 5070 (class 2606 OID 98982)
-- Name: work_schedules work_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_schedules
    ADD CONSTRAINT work_schedules_pkey PRIMARY KEY (schedule_id);


--
-- TOC entry 5075 (class 2606 OID 99008)
-- Name: workers workers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workers
    ADD CONSTRAINT workers_pkey PRIMARY KEY (worker_id);


--
-- TOC entry 4987 (class 1259 OID 98703)
-- Name: idx_agent_decisions_confidence; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_decisions_confidence ON public.agent_decisions USING btree (confidence);


--
-- TOC entry 4988 (class 1259 OID 98701)
-- Name: idx_agent_decisions_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_decisions_created ON public.agent_decisions USING btree (created_at DESC);


--
-- TOC entry 4989 (class 1259 OID 98700)
-- Name: idx_agent_decisions_decision; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_decisions_decision ON public.agent_decisions USING btree (decision);


--
-- TOC entry 4990 (class 1259 OID 98702)
-- Name: idx_agent_decisions_feasible; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_decisions_feasible ON public.agent_decisions USING btree (feasible);


--
-- TOC entry 4991 (class 1259 OID 98699)
-- Name: idx_agent_decisions_request_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_decisions_request_type ON public.agent_decisions USING btree (request_type);


--
-- TOC entry 4992 (class 1259 OID 98698)
-- Name: idx_agent_decisions_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_decisions_type ON public.agent_decisions USING btree (agent_type);


--
-- TOC entry 5015 (class 1259 OID 98789)
-- Name: idx_allocations_budget; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_allocations_budget ON public.fund_allocations USING btree (budget_id);


--
-- TOC entry 5022 (class 1259 OID 98821)
-- Name: idx_budget_adjustments_budget; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_budget_adjustments_budget ON public.budget_adjustments USING btree (budget_id);


--
-- TOC entry 4997 (class 1259 OID 98720)
-- Name: idx_budget_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_budget_department ON public.department_budgets USING btree (department);


--
-- TOC entry 4998 (class 1259 OID 98721)
-- Name: idx_budget_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_budget_period ON public.department_budgets USING btree (year, month);


--
-- TOC entry 4999 (class 1259 OID 98722)
-- Name: idx_budget_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_budget_status ON public.department_budgets USING btree (status);


--
-- TOC entry 5112 (class 1259 OID 99165)
-- Name: idx_coordination_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_coordination_created ON public.coordination_decisions USING btree (created_at DESC);


--
-- TOC entry 5113 (class 1259 OID 99166)
-- Name: idx_coordination_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_coordination_location ON public.coordination_decisions USING btree (location);


--
-- TOC entry 5114 (class 1259 OID 99164)
-- Name: idx_coordination_outcome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_coordination_outcome ON public.coordination_decisions USING btree (outcome);


--
-- TOC entry 5115 (class 1259 OID 99167)
-- Name: idx_coordination_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_coordination_status ON public.coordination_decisions USING btree (status);


--
-- TOC entry 5096 (class 1259 OID 99071)
-- Name: idx_departments_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_departments_key ON public.departments USING btree (department_key);


--
-- TOC entry 5034 (class 1259 OID 98872)
-- Name: idx_disease_incidents_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_disease_incidents_location ON public.disease_incidents USING btree (location);


--
-- TOC entry 5035 (class 1259 OID 98873)
-- Name: idx_disease_incidents_reported; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_disease_incidents_reported ON public.disease_incidents USING btree (reported_date DESC);


--
-- TOC entry 5002 (class 1259 OID 98736)
-- Name: idx_finance_accounts_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_accounts_department ON public.finance_accounts USING btree (department);


--
-- TOC entry 5031 (class 1259 OID 98854)
-- Name: idx_finance_policies_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_policies_name ON public.finance_policies USING btree (policy_name);


--
-- TOC entry 5007 (class 1259 OID 98757)
-- Name: idx_forecast_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_forecast_period ON public.revenue_forecasts USING btree (period_start, period_end);


--
-- TOC entry 5012 (class 1259 OID 98769)
-- Name: idx_grants_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_grants_department ON public.grants USING btree (department);


--
-- TOC entry 5048 (class 1259 OID 98918)
-- Name: idx_health_facilities_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_health_facilities_location ON public.health_facilities USING btree (location);


--
-- TOC entry 5057 (class 1259 OID 98949)
-- Name: idx_health_policies_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_health_policies_name ON public.health_policies USING btree (policy_name);


--
-- TOC entry 5051 (class 1259 OID 98929)
-- Name: idx_health_resources_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_health_resources_type ON public.health_resources USING btree (resource_type);


--
-- TOC entry 5054 (class 1259 OID 98939)
-- Name: idx_health_surveillance_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_health_surveillance_date ON public.health_surveillance_reports USING btree (report_date DESC);


--
-- TOC entry 5086 (class 1259 OID 99055)
-- Name: idx_incidents_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_incidents_department ON public.incidents USING btree (department);


--
-- TOC entry 5087 (class 1259 OID 99056)
-- Name: idx_incidents_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_incidents_location ON public.incidents USING btree (location);


--
-- TOC entry 5088 (class 1259 OID 99057)
-- Name: idx_incidents_reported_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_incidents_reported_date ON public.incidents USING btree (reported_date DESC);


--
-- TOC entry 5089 (class 1259 OID 99058)
-- Name: idx_incidents_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_incidents_severity ON public.incidents USING btree (severity);


--
-- TOC entry 5097 (class 1259 OID 99087)
-- Name: idx_pipeline_inspections_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipeline_inspections_date ON public.pipeline_inspections USING btree (inspection_date DESC);


--
-- TOC entry 5098 (class 1259 OID 99086)
-- Name: idx_pipeline_inspections_pipeline; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipeline_inspections_pipeline ON public.pipeline_inspections USING btree (pipeline_id);


--
-- TOC entry 5076 (class 1259 OID 99025)
-- Name: idx_pipelines_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipelines_location ON public.pipelines USING btree (location);


--
-- TOC entry 5077 (class 1259 OID 99028)
-- Name: idx_pipelines_pressure; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipelines_pressure ON public.pipelines USING btree (pressure_psi);


--
-- TOC entry 5078 (class 1259 OID 99027)
-- Name: idx_pipelines_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipelines_status ON public.pipelines USING btree (operational_status);


--
-- TOC entry 5079 (class 1259 OID 99026)
-- Name: idx_pipelines_zone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipelines_zone ON public.pipelines USING btree (zone);


--
-- TOC entry 5058 (class 1259 OID 98967)
-- Name: idx_projects_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_projects_department ON public.projects USING btree (department);


--
-- TOC entry 5059 (class 1259 OID 98970)
-- Name: idx_projects_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_projects_location ON public.projects USING btree (location);


--
-- TOC entry 5060 (class 1259 OID 98969)
-- Name: idx_projects_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_projects_start_date ON public.projects USING btree (start_date);


--
-- TOC entry 5061 (class 1259 OID 98968)
-- Name: idx_projects_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_projects_status ON public.projects USING btree (status);


--
-- TOC entry 5023 (class 1259 OID 98834)
-- Name: idx_reserve_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reserve_department ON public.reserve_funds USING btree (department);


--
-- TOC entry 5082 (class 1259 OID 99041)
-- Name: idx_reservoirs_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservoirs_location ON public.reservoirs USING btree (location);


--
-- TOC entry 5083 (class 1259 OID 99042)
-- Name: idx_reservoirs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservoirs_status ON public.reservoirs USING btree (operational_status);


--
-- TOC entry 5003 (class 1259 OID 98747)
-- Name: idx_revenue_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_revenue_department ON public.revenue_history USING btree (department);


--
-- TOC entry 5004 (class 1259 OID 98746)
-- Name: idx_revenue_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_revenue_period ON public.revenue_history USING btree (period_start, period_end);


--
-- TOC entry 5039 (class 1259 OID 98896)
-- Name: idx_sanitation_inspections_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sanitation_inspections_date ON public.sanitation_inspections USING btree (inspection_date DESC);


--
-- TOC entry 5040 (class 1259 OID 98895)
-- Name: idx_sanitation_inspections_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sanitation_inspections_location ON public.sanitation_inspections USING btree (location);


--
-- TOC entry 5064 (class 1259 OID 98994)
-- Name: idx_schedules_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedules_date ON public.work_schedules USING btree (scheduled_date);


--
-- TOC entry 5065 (class 1259 OID 98993)
-- Name: idx_schedules_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedules_department ON public.work_schedules USING btree (department);


--
-- TOC entry 5066 (class 1259 OID 98995)
-- Name: idx_schedules_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedules_location ON public.work_schedules USING btree (location);


--
-- TOC entry 5067 (class 1259 OID 98997)
-- Name: idx_schedules_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedules_priority ON public.work_schedules USING btree (priority);


--
-- TOC entry 5068 (class 1259 OID 98996)
-- Name: idx_schedules_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedules_status ON public.work_schedules USING btree (status);


--
-- TOC entry 5104 (class 1259 OID 99124)
-- Name: idx_service_outages_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_outages_location ON public.service_outages USING btree (location);


--
-- TOC entry 5105 (class 1259 OID 99125)
-- Name: idx_service_outages_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_outages_status ON public.service_outages USING btree (status);


--
-- TOC entry 5026 (class 1259 OID 98844)
-- Name: idx_tax_revenues_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tax_revenues_period ON public.tax_revenues USING btree (period_start, period_end);


--
-- TOC entry 5018 (class 1259 OID 98805)
-- Name: idx_transactions_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_account ON public.financial_transactions USING btree (account_id);


--
-- TOC entry 5019 (class 1259 OID 98806)
-- Name: idx_transactions_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_department ON public.financial_transactions USING btree (department);


--
-- TOC entry 5036 (class 1259 OID 98884)
-- Name: idx_vaccination_campaigns_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vaccination_campaigns_location ON public.vaccination_campaigns USING btree (location);


--
-- TOC entry 5043 (class 1259 OID 98906)
-- Name: idx_vulnerable_populations_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vulnerable_populations_location ON public.vulnerable_populations USING btree (location);


--
-- TOC entry 5101 (class 1259 OID 99102)
-- Name: idx_water_readings_pipeline_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_water_readings_pipeline_time ON public.water_readings USING btree (pipeline_id, reading_time DESC);


--
-- TOC entry 5071 (class 1259 OID 99009)
-- Name: idx_workers_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workers_department ON public.workers USING btree (department);


--
-- TOC entry 5072 (class 1259 OID 99011)
-- Name: idx_workers_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workers_role ON public.workers USING btree (role);


--
-- TOC entry 5073 (class 1259 OID 99010)
-- Name: idx_workers_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workers_status ON public.workers USING btree (status);


--
-- TOC entry 5128 (class 2620 OID 99126)
-- Name: department_budgets update_department_budgets_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_department_budgets_updated_at BEFORE UPDATE ON public.department_budgets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5132 (class 2620 OID 99130)
-- Name: pipelines update_pipelines_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_pipelines_updated_at BEFORE UPDATE ON public.pipelines FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5129 (class 2620 OID 99127)
-- Name: projects update_projects_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5133 (class 2620 OID 99131)
-- Name: reservoirs update_reservoirs_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_reservoirs_updated_at BEFORE UPDATE ON public.reservoirs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5130 (class 2620 OID 99128)
-- Name: work_schedules update_work_schedules_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_work_schedules_updated_at BEFORE UPDATE ON public.work_schedules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5131 (class 2620 OID 99129)
-- Name: workers update_workers_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_workers_updated_at BEFORE UPDATE ON public.workers FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5119 (class 2606 OID 98816)
-- Name: budget_adjustments budget_adjustments_budget_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budget_adjustments
    ADD CONSTRAINT budget_adjustments_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.department_budgets(budget_id) ON DELETE CASCADE;


--
-- TOC entry 5120 (class 2606 OID 98867)
-- Name: disease_incidents disease_incidents_related_decision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disease_incidents
    ADD CONSTRAINT disease_incidents_related_decision_id_fkey FOREIGN KEY (related_decision_id) REFERENCES public.agent_decisions(id) ON DELETE SET NULL;


--
-- TOC entry 5118 (class 2606 OID 98800)
-- Name: financial_transactions financial_transactions_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_transactions
    ADD CONSTRAINT financial_transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.finance_accounts(account_id) ON DELETE SET NULL;


--
-- TOC entry 5116 (class 2606 OID 98784)
-- Name: fund_allocations fund_allocations_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fund_allocations
    ADD CONSTRAINT fund_allocations_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.finance_accounts(account_id) ON DELETE SET NULL;


--
-- TOC entry 5117 (class 2606 OID 98779)
-- Name: fund_allocations fund_allocations_budget_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fund_allocations
    ADD CONSTRAINT fund_allocations_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.department_budgets(budget_id) ON DELETE SET NULL;


--
-- TOC entry 5124 (class 2606 OID 99081)
-- Name: pipeline_inspections pipeline_inspections_pipeline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_inspections
    ADD CONSTRAINT pipeline_inspections_pipeline_id_fkey FOREIGN KEY (pipeline_id) REFERENCES public.pipelines(pipeline_id) ON DELETE CASCADE;


--
-- TOC entry 5121 (class 2606 OID 98962)
-- Name: projects projects_agent_decision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_agent_decision_id_fkey FOREIGN KEY (agent_decision_id) REFERENCES public.agent_decisions(id) ON DELETE SET NULL;


--
-- TOC entry 5126 (class 2606 OID 99119)
-- Name: service_outages service_outages_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_outages
    ADD CONSTRAINT service_outages_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(incident_id) ON DELETE SET NULL;


--
-- TOC entry 5127 (class 2606 OID 99114)
-- Name: service_outages service_outages_related_pipeline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_outages
    ADD CONSTRAINT service_outages_related_pipeline_id_fkey FOREIGN KEY (related_pipeline_id) REFERENCES public.pipelines(pipeline_id) ON DELETE SET NULL;


--
-- TOC entry 5125 (class 2606 OID 99097)
-- Name: water_readings water_readings_pipeline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.water_readings
    ADD CONSTRAINT water_readings_pipeline_id_fkey FOREIGN KEY (pipeline_id) REFERENCES public.pipelines(pipeline_id) ON DELETE SET NULL;


--
-- TOC entry 5122 (class 2606 OID 98988)
-- Name: work_schedules work_schedules_agent_decision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_schedules
    ADD CONSTRAINT work_schedules_agent_decision_id_fkey FOREIGN KEY (agent_decision_id) REFERENCES public.agent_decisions(id) ON DELETE SET NULL;


--
-- TOC entry 5123 (class 2606 OID 98983)
-- Name: work_schedules work_schedules_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_schedules
    ADD CONSTRAINT work_schedules_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE SET NULL;


-- Completed on 2026-02-08 22:10:49

--
-- PostgreSQL database dump complete
--

