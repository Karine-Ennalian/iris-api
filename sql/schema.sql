-- ÍRIS MOCK DATABASE
-- Execute este arquivo no SQL Editor do Supabase.
-- Todos os dados usados no TCC devem ser fictícios.

create extension if not exists pgcrypto;

create table if not exists health_units (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    type text not null,
    address text,
    neighborhood text,
    phone text,
    latitude double precision,
    longitude double precision,
    created_at timestamptz not null default now()
);

create table if not exists patients (
    id uuid primary key default gen_random_uuid(),
    cns varchar(15) unique not null,
    cpf varchar(11) unique,
    name text not null,
    birth_date date,
    phone text,
    email text,
    address text,
    health_unit_id uuid references health_units(id),
    created_at timestamptz not null default now()
);

create table if not exists auth_challenges (
    id text primary key,
    patient_id uuid not null references patients(id) on delete cascade,
    code_hash text not null,
    expires_at timestamptz not null,
    used boolean not null default false,
    created_at timestamptz not null default now()
);

create table if not exists appointment_slots (
    id uuid primary key default gen_random_uuid(),
    specialty text not null,
    professional_name text,
    health_unit_id uuid not null references health_units(id),
    appointment_date date not null,
    appointment_time time not null,
    available boolean not null default true,
    created_at timestamptz not null default now()
);

create table if not exists appointments (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null references patients(id) on delete cascade,
    specialty text not null,
    professional_name text,
    health_unit_id uuid not null references health_units(id),
    appointment_date date not null,
    appointment_time time not null,
    status text not null default 'scheduled',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists exams (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null references patients(id) on delete cascade,
    exam_type text not null,
    request_date date not null,
    scheduled_date date,
    status text not null,
    health_unit_name text,
    preparation text,
    result_text text,
    result_url text,
    created_at timestamptz not null default now()
);

create table if not exists vaccines (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null references patients(id) on delete cascade,
    vaccine_name text not null,
    dose text not null,
    application_date date,
    status text not null,
    health_unit_name text,
    created_at timestamptz not null default now()
);

create table if not exists medications (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    dosage text,
    presentation text,
    created_at timestamptz not null default now()
);

create table if not exists medication_stock (
    id uuid primary key default gen_random_uuid(),
    medication_id uuid not null references medications(id) on delete cascade,
    health_unit_id uuid not null references health_units(id) on delete cascade,
    quantity integer not null default 0 check (quantity >= 0),
    updated_at timestamptz not null default now(),
    unique (medication_id, health_unit_id)
);

create table if not exists sessions (
    id text primary key,
    patient_id uuid not null references patients(id) on delete cascade,
    token_hash text unique not null,
    created_at timestamptz not null default now(),
    last_activity_at timestamptz not null default now(),
    absolute_expires_at timestamptz not null,
    revoked boolean not null default false
);

create index if not exists idx_sessions_token_hash on sessions(token_hash);
create index if not exists idx_sessions_patient on sessions(patient_id);
create index if not exists idx_patients_cns on patients(cns);
create index if not exists idx_appointments_patient on appointments(patient_id);
create index if not exists idx_exams_patient on exams(patient_id);
create index if not exists idx_vaccines_patient on vaccines(patient_id);
create index if not exists idx_medication_stock_medication on medication_stock(medication_id);

alter table sessions enable row level security;
