-- OSPF Demo - Database Initialization
-- This runs automatically when PostgreSQL container starts

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS & AUTH
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    user_type VARCHAR(50) NOT NULL, -- 'investor', 'homeowner', 'tenant'
    kyc_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'verified', 'rejected'
    kyc_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PROPERTIES (The "Blockchain" - immutable record)
-- ============================================
CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address VARCHAR(500) NOT NULL,
    suburb VARCHAR(100),
    state VARCHAR(50),
    postcode VARCHAR(10),
    property_type VARCHAR(50), -- 'house', 'apartment', 'townhouse'
    bedrooms INTEGER,
    bathrooms INTEGER,
    parking INTEGER,
    land_size_sqm DECIMAL(10, 2),
    floor_area_sqm DECIMAL(10, 2),
    year_built INTEGER,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'active', 'sold'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- VALUATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS valuations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id),
    valuation_amount DECIMAL(15, 2) NOT NULL,
    confidence_low DECIMAL(15, 2),
    confidence_high DECIMAL(15, 2),
    valuation_method VARCHAR(100), -- 'ai_avm', 'manual', 'external'
    reasoning TEXT, -- AI explanation
    valued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- ============================================
-- OWNERSHIP (Token representation)
-- ============================================
CREATE TABLE IF NOT EXISTS ownership (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id),
    owner_id UUID REFERENCES users(id),
    ownership_percentage DECIMAL(5, 4) NOT NULL, -- 0.0000 to 1.0000
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acquisition_price DECIMAL(15, 2),
    -- Immutable audit trail
    transaction_hash VARCHAR(255) UNIQUE, -- Mock blockchain hash
    previous_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TRANSACTIONS (Ledger)
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_type VARCHAR(50) NOT NULL, -- 'token_purchase', 'equity_sale', 'rent_payment', 'dividend'
    from_user_id UUID REFERENCES users(id),
    to_user_id UUID REFERENCES users(id),
    property_id UUID REFERENCES properties(id),
    amount DECIMAL(15, 2) NOT NULL,
    token_amount DECIMAL(15, 4), -- For token transactions
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    -- Immutable audit
    transaction_hash VARCHAR(255) UNIQUE,
    previous_hash VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- ============================================
-- TENANT APPLICATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS tenant_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    property_id UUID REFERENCES properties(id),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'screening', 'approved', 'rejected'
    -- AI Screening Results
    screening_score DECIMAL(5, 2),
    screening_confidence DECIMAL(5, 2),
    screening_reasoning TEXT,
    risk_factors JSONB,
    -- Documents
    documents JSONB, -- [{type, url, verified, verification_notes}]
    -- Timing
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    screened_at TIMESTAMP,
    decided_at TIMESTAMP,
    decided_by VARCHAR(50) -- 'ai_auto', 'human_review'
);

-- ============================================
-- LEASES
-- ============================================
CREATE TABLE IF NOT EXISTS leases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id),
    tenant_id UUID REFERENCES users(id),
    rent_amount DECIMAL(10, 2) NOT NULL,
    rent_frequency VARCHAR(50) DEFAULT 'weekly',
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'expired', 'terminated'
    bond_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MAINTENANCE REQUESTS
-- ============================================
CREATE TABLE IF NOT EXISTS maintenance_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id),
    tenant_id UUID REFERENCES users(id),
    description TEXT NOT NULL,
    -- AI Triage
    urgency VARCHAR(50), -- 'emergency', 'urgent', 'routine', 'planned'
    category VARCHAR(100), -- 'plumbing', 'electrical', 'hvac', etc.
    ai_diagnosis TEXT,
    ai_recommended_action TEXT,
    -- Status
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'scheduled', 'in_progress', 'completed'
    assigned_vendor VARCHAR(255),
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    cost DECIMAL(10, 2),
    -- Attachments
    attachments JSONB, -- [{type, url, ai_analysis}]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CONVERSATIONS (AI Property Manager)
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    property_id UUID REFERENCES properties(id),
    context VARCHAR(100), -- 'maintenance', 'lease', 'general', 'application'
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    -- AI metadata
    model_used VARCHAR(100),
    tokens_used INTEGER,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DAO PROPOSALS (Mock Governance)
-- ============================================
CREATE TABLE IF NOT EXISTS proposals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    proposal_type VARCHAR(100), -- 'property_acquisition', 'policy_change', 'parameter_update'
    proposer_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'passed', 'rejected', 'executed'
    votes_for DECIMAL(20, 4) DEFAULT 0,
    votes_against DECIMAL(20, 4) DEFAULT 0,
    voting_ends_at TIMESTAMP,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proposal_id UUID REFERENCES proposals(id),
    voter_id UUID REFERENCES users(id),
    vote_weight DECIMAL(20, 4) NOT NULL, -- Based on token holdings
    vote_direction VARCHAR(10) NOT NULL, -- 'for', 'against'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(proposal_id, voter_id)
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_ownership_property ON ownership(property_id);
CREATE INDEX IF NOT EXISTS idx_ownership_owner ON ownership(owner_id);
CREATE INDEX IF NOT EXISTS idx_transactions_property ON transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(from_user_id, to_user_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_property ON maintenance_requests(property_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);

-- ============================================
-- SEED DATA (Demo)
-- ============================================
-- Insert demo users
INSERT INTO users (id, email, full_name, user_type, kyc_status) VALUES
    ('11111111-1111-1111-1111-111111111111', 'investor@demo.com', 'Alice Investor', 'investor', 'verified'),
    ('22222222-2222-2222-2222-222222222222', 'homeowner@demo.com', 'Bob Homeowner', 'homeowner', 'verified'),
    ('33333333-3333-3333-3333-333333333333', 'tenant@demo.com', 'Carol Tenant', 'tenant', 'verified')
ON CONFLICT (id) DO NOTHING;

-- Insert demo property
INSERT INTO properties (id, address, suburb, state, postcode, property_type, bedrooms, bathrooms, parking, status) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '123 Demo Street', 'Sydney', 'NSW', '2000', 'apartment', 2, 1, 1, 'active')
ON CONFLICT (id) DO NOTHING;

-- Insert demo valuation
INSERT INTO valuations (property_id, valuation_amount, confidence_low, confidence_high, valuation_method, reasoning) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 850000.00, 800000.00, 900000.00, 'ai_avm', 'Based on comparable sales in Sydney CBD area, property condition, and current market trends.')
ON CONFLICT DO NOTHING;

-- Insert demo ownership (homeowner has 60%, network has 40%)
INSERT INTO ownership (property_id, owner_id, ownership_percentage, transaction_hash) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222222', 0.6000, 'genesis_homeowner'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 0.4000, 'genesis_investor')
ON CONFLICT DO NOTHING;

-- Database initialized successfully
