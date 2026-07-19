CREATE TABLE IF NOT EXISTS work_sessions (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	started_at TIMESTAMPTZ not NULL DEFAULT NOW(),
	ended_at TIMESTAMPTZ
);
