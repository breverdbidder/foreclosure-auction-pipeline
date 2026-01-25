-- AI Council Analyses Schema
-- Deploy to Supabase for council session persistence

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main council analyses table
CREATE TABLE IF NOT EXISTS council_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    council_id TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL CHECK (platform IN ('zonewise', 'spd', 'biddeed')),
    subject TEXT NOT NULL,
    query TEXT NOT NULL,
    recommendation TEXT,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    action_items JSONB DEFAULT '[]'::jsonb,
    execution_time_ms INTEGER,
    token_usage JSONB DEFAULT '{}'::jsonb,
    shared_reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for platform queries
CREATE INDEX IF NOT EXISTS idx_council_platform ON council_analyses(platform);

-- Index for recent analyses
CREATE INDEX IF NOT EXISTS idx_council_created ON council_analyses(created_at DESC);

-- Index for subject searches
CREATE INDEX IF NOT EXISTS idx_council_subject ON council_analyses(subject);

-- Agent outputs table (for detailed tracking)
CREATE TABLE IF NOT EXISTS council_agent_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    council_id TEXT NOT NULL REFERENCES council_analyses(council_id),
    agent_name TEXT NOT NULL,
    agent_role TEXT NOT NULL CHECK (agent_role IN ('specialist', 'bull_case', 'bear_case', 'analyst', 'synthesizer')),
    output TEXT NOT NULL,
    model_used TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_tier TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for agent outputs by council
CREATE INDEX IF NOT EXISTS idx_agent_council ON council_agent_outputs(council_id);

-- Debate logs table
CREATE TABLE IF NOT EXISTS council_debates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    council_id TEXT NOT NULL REFERENCES council_analyses(council_id),
    round_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_council_analyses_updated_at ON council_analyses;
CREATE TRIGGER update_council_analyses_updated_at
    BEFORE UPDATE ON council_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- RLS Policies (enable if using Supabase Auth)
-- ALTER TABLE council_analyses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE council_agent_outputs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE council_debates ENABLE ROW LEVEL SECURITY;

-- View for council summary
CREATE OR REPLACE VIEW council_summary AS
SELECT 
    ca.council_id,
    ca.platform,
    ca.subject,
    ca.query,
    ca.confidence,
    ca.execution_time_ms,
    (ca.token_usage->>'total_input')::integer as input_tokens,
    (ca.token_usage->>'total_output')::integer as output_tokens,
    ca.created_at,
    COUNT(cao.id) as agent_count
FROM council_analyses ca
LEFT JOIN council_agent_outputs cao ON ca.council_id = cao.council_id
GROUP BY ca.id, ca.council_id, ca.platform, ca.subject, ca.query, 
         ca.confidence, ca.execution_time_ms, ca.token_usage, ca.created_at
ORDER BY ca.created_at DESC;

-- Sample query functions
-- Get recent councils by platform
CREATE OR REPLACE FUNCTION get_recent_councils(
    p_platform TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    council_id TEXT,
    platform TEXT,
    subject TEXT,
    confidence DECIMAL,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ca.council_id,
        ca.platform,
        ca.subject,
        ca.confidence,
        ca.created_at
    FROM council_analyses ca
    WHERE (p_platform IS NULL OR ca.platform = p_platform)
    ORDER BY ca.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Get average confidence by platform
CREATE OR REPLACE FUNCTION get_platform_stats()
RETURNS TABLE (
    platform TEXT,
    total_analyses BIGINT,
    avg_confidence DECIMAL,
    avg_execution_ms DECIMAL,
    total_tokens BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ca.platform,
        COUNT(*)::BIGINT as total_analyses,
        ROUND(AVG(ca.confidence)::DECIMAL, 2) as avg_confidence,
        ROUND(AVG(ca.execution_time_ms)::DECIMAL, 0) as avg_execution_ms,
        SUM((ca.token_usage->>'total_input')::integer + (ca.token_usage->>'total_output')::integer)::BIGINT as total_tokens
    FROM council_analyses ca
    GROUP BY ca.platform;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE council_analyses IS 'AI Council analysis sessions with recommendations';
COMMENT ON TABLE council_agent_outputs IS 'Individual agent outputs for each council session';
COMMENT ON TABLE council_debates IS 'Debate round logs between perspective agents';
