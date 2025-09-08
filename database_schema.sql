-- Legal Ops Platform Database Schema
-- PostgreSQL Database for Heavy Production Load
-- Designed for thousands of concurrent users and comprehensive dashboard functionality

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================================================
-- CORE USER MANAGEMENT
-- ============================================================================

-- Users table with comprehensive profile and preferences
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    company_name VARCHAR(255),
    business_type VARCHAR(100),
    business_stage VARCHAR(50), -- startup, established, growing, enterprise
    state_of_formation VARCHAR(2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE,
    
    -- Dashboard preferences
    dashboard_layout JSONB DEFAULT '{}',
    notification_preferences JSONB DEFAULT '{"email": true, "push": true, "sms": false}',
    communication_preferences JSONB DEFAULT '{"ai_assistance": true, "human_support": true}',
    
    -- Business intelligence data
    total_services_used INTEGER DEFAULT 0,
    total_money_saved DECIMAL(10,2) DEFAULT 0,
    total_time_saved INTEGER DEFAULT 0, -- in hours
    business_health_score INTEGER DEFAULT 0, -- 0-100
    
    -- Indexes for performance
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- User roles and permissions
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- customer, admin, employee, partner
    permissions JSONB DEFAULT '{}',
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- SERVICE MANAGEMENT
-- ============================================================================

-- Service catalog with flexible configuration
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- business_formation, real_estate, healthcare, etc.
    tier VARCHAR(50) NOT NULL, -- basic, premium, enterprise
    price DECIMAL(10,2) NOT NULL,
    setup_fee DECIMAL(10,2) DEFAULT 0,
    recurring_fee DECIMAL(10,2) DEFAULT 0,
    billing_cycle VARCHAR(20), -- one_time, monthly, annual
    
    -- Service configuration
    features JSONB DEFAULT '{}',
    deliverables JSONB DEFAULT '[]',
    requirements JSONB DEFAULT '[]',
    timeline_days INTEGER,
    automation_level VARCHAR(50), -- fully_automated, semi_automated, manual
    
    -- UPL compliance
    upl_risk_level VARCHAR(20) DEFAULT 'low', -- low, medium, high
    compliance_requirements JSONB DEFAULT '[]',
    required_disclaimers TEXT[],
    
    -- Status and metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User service subscriptions
CREATE TABLE user_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id),
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, paused, cancelled, completed
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    next_billing_date TIMESTAMP WITH TIME ZONE,
    
    -- Service-specific data
    service_data JSONB DEFAULT '{}',
    progress_percentage INTEGER DEFAULT 0,
    current_stage VARCHAR(100),
    estimated_completion TIMESTAMP WITH TIME ZONE,
    
    -- Billing
    total_paid DECIMAL(10,2) DEFAULT 0,
    last_payment_date TIMESTAMP WITH TIME ZONE,
    payment_method_id VARCHAR(255),
    
    -- Performance tracking
    time_saved INTEGER DEFAULT 0, -- in hours
    money_saved DECIMAL(10,2) DEFAULT 0,
    user_satisfaction_score INTEGER, -- 1-5
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- DASHBOARD AND COMMUNICATION SYSTEM
-- ============================================================================

-- User dashboard widgets and layout
CREATE TABLE dashboard_widgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    widget_type VARCHAR(100) NOT NULL, -- service_status, compliance_calendar, documents, etc.
    widget_config JSONB DEFAULT '{}',
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER DEFAULT 4,
    height INTEGER DEFAULT 3,
    is_visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Communication hub - all user interactions
CREATE TABLE user_communications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    communication_type VARCHAR(50) NOT NULL, -- ai_chat, human_support, notification, announcement
    channel VARCHAR(50) NOT NULL, -- dashboard, email, sms, push
    subject VARCHAR(255),
    message TEXT NOT NULL,
    response_to UUID REFERENCES user_communications(id),
    
    -- AI-specific fields
    ai_model VARCHAR(100),
    ai_confidence DECIMAL(3,2), -- 0.00 to 1.00
    ai_escalated BOOLEAN DEFAULT FALSE,
    human_reviewed BOOLEAN DEFAULT FALSE,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'sent', -- sent, delivered, read, responded
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    read_at TIMESTAMP WITH TIME ZONE,
    responded_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI conversation sessions
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    context JSONB DEFAULT '{}', -- user's current services, business info, etc.
    conversation_summary TEXT,
    total_messages INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Service recommendations (AI-generated)
CREATE TABLE service_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommended_service_id UUID NOT NULL REFERENCES services(id),
    recommendation_type VARCHAR(50) NOT NULL, -- ai_generated, manual, cross_sell
    confidence_score DECIMAL(3,2) NOT NULL, -- 0.00 to 1.00
    reasoning TEXT,
    business_impact TEXT,
    estimated_savings DECIMAL(10,2),
    estimated_time_savings INTEGER, -- in hours
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, viewed, interested, purchased, dismissed
    viewed_at TIMESTAMP WITH TIME ZONE,
    dismissed_at TIMESTAMP WITH TIME ZONE,
    purchased_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User feedback and suggestions
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL, -- product_suggestion, improvement_request, bug_report, feature_request
    category VARCHAR(100), -- service_specific, dashboard, communication, billing
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    
    -- Related entities
    service_id UUID REFERENCES services(id),
    communication_id UUID REFERENCES user_communications(id),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'submitted', -- submitted, under_review, in_progress, completed, rejected
    assigned_to UUID REFERENCES users(id),
    resolution_notes TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Voting and engagement
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SERVICE-SPECIFIC TABLES
-- ============================================================================

-- Business Formation Services
CREATE TABLE business_formations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_service_id UUID NOT NULL REFERENCES user_services(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(50) NOT NULL, -- llc, corporation, partnership, etc.
    state_of_formation VARCHAR(2) NOT NULL,
    registered_agent VARCHAR(255),
    business_address JSONB NOT NULL,
    mailing_address JSONB,
    
    -- Formation details
    formation_date DATE,
    ein VARCHAR(20),
    state_filing_number VARCHAR(100),
    sunbiz_status VARCHAR(50),
    
    -- Documents
    articles_of_incorporation_url VARCHAR(500),
    operating_agreement_url VARCHAR(500),
    ein_letter_url VARCHAR(500),
    
    -- Compliance tracking
    annual_report_due DATE,
    registered_agent_renewal_due DATE,
    next_compliance_check DATE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Real Estate Services
CREATE TABLE real_estate_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_service_id UUID NOT NULL REFERENCES user_services(id) ON DELETE CASCADE,
    property_address JSONB NOT NULL,
    property_type VARCHAR(50) NOT NULL, -- residential, commercial, land
    transaction_type VARCHAR(50) NOT NULL, -- purchase, sale, lease, management
    
    -- Transaction details
    contract_date DATE,
    closing_date DATE,
    purchase_price DECIMAL(12,2),
    down_payment DECIMAL(12,2),
    financing_type VARCHAR(50),
    
    -- Parties involved
    buyer_info JSONB,
    seller_info JSONB,
    agent_info JSONB,
    lender_info JSONB,
    
    -- Documents and compliance
    required_documents JSONB DEFAULT '[]',
    completed_documents JSONB DEFAULT '[]',
    compliance_deadlines JSONB DEFAULT '[]',
    
    -- Status tracking
    current_stage VARCHAR(100),
    next_deadline DATE,
    completion_percentage INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Healthcare Compliance Services
CREATE TABLE healthcare_compliance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_service_id UUID NOT NULL REFERENCES user_services(id) ON DELETE CASCADE,
    practice_name VARCHAR(255) NOT NULL,
    practice_type VARCHAR(100) NOT NULL, -- medical, dental, mental_health, etc.
    license_type VARCHAR(100),
    license_number VARCHAR(100),
    license_expiration DATE,
    
    -- Compliance requirements
    hipaa_compliance_status VARCHAR(50),
    hipaa_risk_assessment_date DATE,
    hipaa_training_completion_date DATE,
    
    -- Regulatory tracking
    state_licenses JSONB DEFAULT '[]',
    federal_registrations JSONB DEFAULT '[]',
    insurance_requirements JSONB DEFAULT '[]',
    
    -- Audit and monitoring
    last_compliance_audit DATE,
    next_audit_due DATE,
    compliance_score INTEGER, -- 0-100
    risk_level VARCHAR(20), -- low, medium, high
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- DOCUMENT MANAGEMENT
-- ============================================================================

-- Document templates and generated documents
CREATE TABLE document_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    service_id UUID REFERENCES services(id),
    template_type VARCHAR(50) NOT NULL, -- standard, custom, ai_generated
    
    -- Template content
    template_content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    validation_rules JSONB DEFAULT '{}',
    
    -- UPL compliance
    upl_risk_level VARCHAR(20) DEFAULT 'low',
    required_disclaimers TEXT[],
    attorney_review_required BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated documents for users
CREATE TABLE user_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_service_id UUID REFERENCES user_services(id),
    template_id UUID REFERENCES document_templates(id),
    
    -- Document details
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    
    -- Content and data
    document_data JSONB DEFAULT '{}',
    variables_used JSONB DEFAULT '{}',
    
    -- Status and tracking
    status VARCHAR(50) DEFAULT 'generated', -- generated, reviewed, approved, filed, rejected
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    filed_at TIMESTAMP WITH TIME ZONE,
    
    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    access_level VARCHAR(20) DEFAULT 'private', -- private, shared, public
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- COMPLIANCE AND AUDIT SYSTEM
-- ============================================================================

-- UPL compliance monitoring
CREATE TABLE compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    check_type VARCHAR(100) NOT NULL, -- upl_monitoring, service_delivery, communication
    entity_type VARCHAR(50) NOT NULL, -- user, service, communication, document
    entity_id UUID NOT NULL,
    
    -- Check details
    check_criteria JSONB NOT NULL,
    check_result VARCHAR(50) NOT NULL, -- pass, fail, warning, review_required
    risk_level VARCHAR(20) NOT NULL, -- low, medium, high, critical
    findings TEXT,
    recommendations TEXT,
    
    -- Automated vs manual
    is_automated BOOLEAN DEFAULT TRUE,
    checked_by UUID REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'completed', -- pending, in_progress, completed, requires_action
    action_required BOOLEAN DEFAULT FALSE,
    action_taken TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comprehensive audit log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL, -- user, service, document, communication
    entity_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL, -- created, updated, deleted, viewed, accessed
    
    -- Change tracking
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PERFORMANCE OPTIMIZATION INDEXES
-- ============================================================================

-- User table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_business_type ON users(business_type);
CREATE INDEX idx_users_state ON users(state_of_formation);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

-- User services indexes
CREATE INDEX idx_user_services_user_id ON user_services(user_id);
CREATE INDEX idx_user_services_service_id ON user_services(service_id);
CREATE INDEX idx_user_services_status ON user_services(status);
CREATE INDEX idx_user_services_expires_at ON user_services(expires_at);
CREATE INDEX idx_user_services_user_service ON user_services(user_id, service_id);

-- Communication indexes
CREATE INDEX idx_communications_user_id ON user_communications(user_id);
CREATE INDEX idx_communications_type ON user_communications(communication_type);
CREATE INDEX idx_communications_created_at ON user_communications(created_at);
CREATE INDEX idx_communications_status ON user_communications(status);
CREATE INDEX idx_communications_user_type ON user_communications(user_id, communication_type);

-- AI conversation indexes
CREATE INDEX idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_session_id ON ai_conversations(session_id);
CREATE INDEX idx_ai_conversations_active ON ai_conversations(is_active) WHERE is_active = TRUE;

-- Service recommendations indexes
CREATE INDEX idx_recommendations_user_id ON service_recommendations(user_id);
CREATE INDEX idx_recommendations_status ON service_recommendations(status);
CREATE INDEX idx_recommendations_confidence ON service_recommendations(confidence_score DESC);

-- Business formation indexes
CREATE INDEX idx_business_formations_user_service ON business_formations(user_service_id);
CREATE INDEX idx_business_formations_state ON business_formations(state_of_formation);
CREATE INDEX idx_business_formations_type ON business_formations(business_type);

-- Real estate indexes
CREATE INDEX idx_real_estate_user_service ON real_estate_transactions(user_service_id);
CREATE INDEX idx_real_estate_type ON real_estate_transactions(transaction_type);
CREATE INDEX idx_real_estate_stage ON real_estate_transactions(current_stage);

-- Document indexes
CREATE INDEX idx_user_documents_user_id ON user_documents(user_id);
CREATE INDEX idx_user_documents_service_id ON user_documents(user_service_id);
CREATE INDEX idx_user_documents_type ON user_documents(document_type);
CREATE INDEX idx_user_documents_status ON user_documents(status);

-- Compliance indexes
CREATE INDEX idx_compliance_checks_entity ON compliance_checks(entity_type, entity_id);
CREATE INDEX idx_compliance_checks_result ON compliance_checks(check_result);
CREATE INDEX idx_compliance_checks_risk ON compliance_checks(risk_level);
CREATE INDEX idx_compliance_checks_created_at ON compliance_checks(created_at);

-- Audit log indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Full-text search indexes
CREATE INDEX idx_users_search ON users USING gin(to_tsvector('english', first_name || ' ' || last_name || ' ' || company_name));
CREATE INDEX idx_services_search ON services USING gin(to_tsvector('english', name || ' ' || description));
CREATE INDEX idx_communications_search ON user_communications USING gin(to_tsvector('english', subject || ' ' || message));

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_services_updated_at BEFORE UPDATE ON user_services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dashboard_widgets_updated_at BEFORE UPDATE ON dashboard_widgets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_feedback_updated_at BEFORE UPDATE ON user_feedback FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_business_formations_updated_at BEFORE UPDATE ON business_formations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_real_estate_updated_at BEFORE UPDATE ON real_estate_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_healthcare_compliance_updated_at BEFORE UPDATE ON healthcare_compliance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_document_templates_updated_at BEFORE UPDATE ON document_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PARTITIONING FOR LARGE TABLES (Future scaling)
-- ============================================================================

-- Partition audit_logs by month for better performance
CREATE TABLE audit_logs_y2024m01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE audit_logs_y2024m02 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Add more partitions as needed

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User dashboard summary view
CREATE VIEW user_dashboard_summary AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.company_name,
    u.business_health_score,
    COUNT(us.id) as active_services,
    SUM(us.time_saved) as total_time_saved,
    SUM(us.money_saved) as total_money_saved,
    COUNT(uc.id) as unread_messages,
    COUNT(sr.id) as pending_recommendations
FROM users u
LEFT JOIN user_services us ON u.id = us.user_id AND us.status = 'active'
LEFT JOIN user_communications uc ON u.id = uc.user_id AND uc.status = 'sent' AND uc.read_at IS NULL
LEFT JOIN service_recommendations sr ON u.id = sr.user_id AND sr.status = 'pending'
WHERE u.is_active = TRUE
GROUP BY u.id, u.first_name, u.last_name, u.company_name, u.business_health_score;

-- Service performance view
CREATE VIEW service_performance AS
SELECT 
    s.id,
    s.name,
    s.category,
    COUNT(us.id) as total_subscriptions,
    COUNT(CASE WHEN us.status = 'active' THEN 1 END) as active_subscriptions,
    AVG(us.user_satisfaction_score) as avg_satisfaction,
    SUM(us.time_saved) as total_time_saved,
    SUM(us.money_saved) as total_money_saved
FROM services s
LEFT JOIN user_services us ON s.id = us.service_id
GROUP BY s.id, s.name, s.category;

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert default services
INSERT INTO services (name, description, category, tier, price, features, deliverables, upl_risk_level) VALUES
('Business Formation - LLC', 'Complete LLC formation service with all required documents and filings', 'business_formation', 'basic', 299.00, '{"filing": true, "ein": true, "operating_agreement": true}', '["Articles of Organization", "EIN Application", "Operating Agreement", "Compliance Calendar"]', 'low'),
('Business Formation - Corporation', 'Complete Corporation formation with all required documents and filings', 'business_formation', 'basic', 399.00, '{"filing": true, "ein": true, "bylaws": true}', '["Articles of Incorporation", "EIN Application", "Corporate Bylaws", "Compliance Calendar"]', 'low'),
('Real Estate - Purchase Package', 'Complete real estate purchase documentation and compliance tracking', 'real_estate', 'premium', 499.00, '{"contract_review": true, "closing_docs": true, "compliance_tracking": true}', '["Purchase Agreement", "Closing Documents", "Title Insurance", "Compliance Calendar"]', 'medium'),
('Healthcare - HIPAA Compliance', 'HIPAA compliance package with risk assessment and training', 'healthcare', 'premium', 799.00, '{"risk_assessment": true, "training": true, "policies": true}', '["HIPAA Policies", "Risk Assessment", "Training Materials", "Compliance Calendar"]', 'low');

-- Create admin user (password should be hashed in production)
INSERT INTO users (email, password_hash, first_name, last_name, company_name, business_type, is_verified, is_active) VALUES
('admin@legalops.com', '$2b$12$example_hash', 'Admin', 'User', 'Legal Ops Platform', 'technology', TRUE, TRUE);

-- Grant admin role
INSERT INTO user_roles (user_id, role, permissions) 
SELECT id, 'admin', '{"all": true}' FROM users WHERE email = 'admin@legalops.com';
