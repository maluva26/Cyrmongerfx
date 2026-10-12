-- Cyrmonger Algo Fx - Supabase PostgreSQL Schema
-- Generated from Django models. Run via Supabase SQL Editor or psql.
-- All primary keys are UUID. All timestamps are TIMESTAMPTZ (UTC).

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Custom user (managed by Django AUTH_USER_MODEL = "accounts.User")
-- Django auth migrations create: auth_user (unused), auth_group, auth_permission, django_content_type, django_migrations
-- accounts.User is created by Django in the `user` table.

CREATE TABLE IF NOT EXISTS chart_upload (
    chart_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    storage_ref VARCHAR(500) NULL,
    instrument VARCHAR(40) NULL,
    timeframe VARCHAR(20) NULL,
    mime_type VARCHAR(80) NOT NULL,
    size_bytes INTEGER NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PROCESSED','REJECTED','REMOVED')),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    retention_until TIMESTAMPTZ NULL
);

CREATE TABLE IF NOT EXISTS analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chart_id UUID NOT NULL REFERENCES chart_upload(chart_id) ON DELETE CASCADE,
    model_version VARCHAR(60) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PROCESSING' CHECK (status IN ('PROCESSING','COMPLETED','COMPLETED_NO_DETECTION','FAILED','REJECTED')),
    overall_confidence DECIMAL(5,4) NULL CHECK (overall_confidence >= 0 AND overall_confidence <= 1),
    signal_category VARCHAR(10) NULL CHECK (signal_category IN ('BUY','SELL','NEUTRAL')),
    summary TEXT NULL,
    processing_ms INTEGER NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS detection (
    detection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analysis(analysis_id) ON DELETE CASCADE,
    label VARCHAR(80) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    x_min DECIMAL(8,6) NOT NULL CHECK (x_min >= 0 AND x_min < x_max),
    y_min DECIMAL(8,6) NOT NULL CHECK (y_min >= 0 AND y_min < y_max),
    x_max DECIMAL(8,6) NOT NULL CHECK (x_max <= 1),
    y_max DECIMAL(8,6) NOT NULL CHECK (y_max <= 1)
);

CREATE TABLE IF NOT EXISTS lesson (
    lesson_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    category VARCHAR(80) NOT NULL,
    body TEXT NOT NULL,
    illustration_refs JSONB NOT NULL DEFAULT '[]',
    order_index INTEGER NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','PUBLISHED','ARCHIVED')),
    created_by UUID NULL REFERENCES "user"(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS quiz_question (
    question_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID NOT NULL REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    explanation TEXT NOT NULL,
    order_index INTEGER NULL
);

CREATE TABLE IF NOT EXISTS quiz_option (
    option_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL REFERENCES quiz_question(question_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS quiz_attempt (
    attempt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    score DECIMAL(5,2) NULL CHECK (score >= 0 AND score <= 100),
    answers JSONB NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    duration_seconds INTEGER NULL
);

CREATE TABLE IF NOT EXISTS risk_plan (
    risk_plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    account_balance DECIMAL(18,4) NOT NULL CHECK (account_balance > 0),
    risk_percent DECIMAL(5,2) NOT NULL CHECK (risk_percent > 0),
    instrument VARCHAR(40) NULL,
    entry_price DECIMAL(18,8) NULL,
    stop_loss DECIMAL(18,8) NULL,
    take_profit DECIMAL(18,8) NULL,
    risk_amount DECIMAL(18,4) NOT NULL,
    calculated_position_size DECIMAL(18,8) NULL,
    risk_reward_ratio DECIMAL(8,4) NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS journal_entry (
    entry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    analysis_id UUID NULL REFERENCES analysis(analysis_id) ON DELETE SET NULL,
    notes TEXT NULL,
    outcome_value DECIMAL(18,4) NULL,
    outcome_currency VARCHAR(10) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS assistant_conversation (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    title VARCHAR(160) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS assistant_message (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES assistant_conversation(conversation_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user','assistant')),
    content TEXT NOT NULL,
    blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    type VARCHAR(40) NOT NULL CHECK (type IN ('WRONG_DETECTION','ACCESSIBILITY','UPLOAD_FAILURE','CONTENT_UNCLEAR','OTHER')),
    analysis_id UUID NULL REFERENCES analysis(analysis_id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS report (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    report_type VARCHAR(40) NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID NULL REFERENCES "user"(user_id) ON DELETE SET NULL,
    action VARCHAR(80) NOT NULL,
    object_type VARCHAR(120) NOT NULL DEFAULT '',
    object_id VARCHAR(80) NOT NULL DEFAULT '',
    ip VARCHAR(45) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS chart_upload_user_uploaded_idx ON chart_upload(user_id, uploaded_at DESC);
CREATE INDEX IF NOT EXISTS analysis_chart_idx ON analysis(chart_id);
CREATE INDEX IF NOT EXISTS detection_analysis_idx ON detection(analysis_id);
CREATE INDEX IF NOT EXISTS quiz_attempt_user_lesson_idx ON quiz_attempt(user_id, lesson_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS risk_plan_user_created_idx ON risk_plan(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS journal_entry_user_created_idx ON journal_entry(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS lesson_status_order_idx ON lesson(status, order_index);
CREATE INDEX IF NOT EXISTS audit_log_created_idx ON audit_log(created_at);
