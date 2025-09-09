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

-- AI agent system indexes
CREATE INDEX idx_ai_agent_tasks_user_id ON ai_agent_tasks(user_id);
CREATE INDEX idx_ai_agent_tasks_agent_type ON ai_agent_tasks(agent_type);
CREATE INDEX idx_ai_agent_tasks_status ON ai_agent_tasks(status);
CREATE INDEX idx_ai_agent_tasks_created_at ON ai_agent_tasks(created_at);

-- AI usage control indexes
CREATE INDEX idx_ai_usage_limits_user_id ON ai_usage_limits(user_id);
CREATE INDEX idx_ai_usage_limits_type ON ai_usage_limits(limit_type);
CREATE INDEX idx_ai_usage_limits_reset ON ai_usage_limits(last_reset);

CREATE INDEX idx_ai_usage_log_user_id ON ai_usage_log(user_id);
CREATE INDEX idx_ai_usage_log_created_at ON ai_usage_log(created_at);
CREATE INDEX idx_ai_usage_log_agent_type ON ai_usage_log(agent_type);

-- AI abuse detection indexes
CREATE INDEX idx_ai_abuse_user_id ON ai_abuse_detection(user_id);
CREATE INDEX idx_ai_abuse_violation_type ON ai_abuse_detection(violation_type);
CREATE INDEX idx_ai_abuse_severity ON ai_abuse_detection(severity);
CREATE INDEX idx_ai_abuse_detected_at ON ai_abuse_detection(detected_at);

-- AI escalation indexes
CREATE INDEX idx_ai_escalations_user_id ON ai_escalations(user_id);
CREATE INDEX idx_ai_escalations_agent_type ON ai_escalations(agent_type);
CREATE INDEX idx_ai_escalations_reason ON ai_escalations(escalation_reason);
CREATE INDEX idx_ai_escalations_escalated_at ON ai_escalations(escalated_at);

-- Modern authentication indexes
CREATE INDEX idx_authentication_methods_user_id ON authentication_methods(user_id);
CREATE INDEX idx_authentication_methods_type ON authentication_methods(method_type);
CREATE INDEX idx_passkey_credentials_user_id ON passkey_credentials(user_id);
CREATE INDEX idx_passkey_credentials_credential_id ON passkey_credentials(credential_id);
CREATE INDEX idx_magic_link_tokens_token_hash ON magic_link_tokens(token_hash);
CREATE INDEX idx_magic_link_tokens_expires_at ON magic_link_tokens(expires_at);
CREATE INDEX idx_authentication_sessions_user_id ON authentication_sessions(user_id);
CREATE INDEX idx_authentication_sessions_token ON authentication_sessions(session_token);
CREATE INDEX idx_trusted_devices_user_id ON trusted_devices(user_id);
CREATE INDEX idx_authentication_risk_user_id ON authentication_risk(user_id);

-- Security indexes
CREATE INDEX idx_user_security_settings_user_id ON user_security_settings(user_id);
CREATE INDEX idx_security_audit_log_user_id ON security_audit_log(user_id);
CREATE INDEX idx_security_audit_log_event_type ON security_audit_log(event_type);
CREATE INDEX idx_security_audit_log_created_at ON security_audit_log(created_at);
CREATE INDEX idx_data_access_log_user_id ON data_access_log(user_id);
CREATE INDEX idx_data_access_log_data_type ON data_access_log(data_type);
CREATE INDEX idx_user_privacy_settings_user_id ON user_privacy_settings(user_id);

-- Vertical dashboard indexes
CREATE INDEX idx_dashboard_types_service_category ON dashboard_types(service_category);
CREATE INDEX idx_dashboard_configurations_type_id ON dashboard_configurations(dashboard_type_id);
CREATE INDEX idx_user_dashboard_assignments_user_id ON user_dashboard_assignments(user_id);
CREATE INDEX idx_dashboard_widgets_category ON dashboard_widgets(widget_category);
CREATE INDEX idx_user_widget_customizations_user_id ON user_widget_customizations(user_id);

-- AI agent foundation indexes
CREATE INDEX idx_ai_agent_types_category ON ai_agent_types(agent_category);
CREATE INDEX idx_ai_agent_vertical_configs_agent_type ON ai_agent_vertical_configs(agent_type_id);
CREATE INDEX idx_ai_agent_vertical_configs_service_category ON ai_agent_vertical_configs(service_category);

-- Workflow foundation indexes
CREATE INDEX idx_workflow_templates_service_category ON workflow_templates(service_category);
CREATE INDEX idx_user_workflow_instances_user_id ON user_workflow_instances(user_id);
CREATE INDEX idx_user_workflow_instances_template_id ON user_workflow_instances(workflow_template_id);

-- Document foundation indexes
CREATE INDEX idx_document_template_categories_service_category ON document_template_categories(service_category);

-- Service registry indexes
CREATE INDEX idx_service_registry_service_key ON service_registry(service_key);
CREATE INDEX idx_service_registry_category ON service_registry(service_category);
CREATE INDEX idx_service_registry_type ON service_registry(service_type);
CREATE INDEX idx_service_registry_enabled ON service_registry(is_enabled);
CREATE INDEX idx_service_features_service_id ON service_features(service_id);
CREATE INDEX idx_service_features_feature_key ON service_features(feature_key);
CREATE INDEX idx_service_pricing_service_id ON service_pricing(service_id);
CREATE INDEX idx_user_service_access_user_id ON user_service_access(user_id);
CREATE INDEX idx_user_service_access_service_id ON user_service_access(service_id);
CREATE INDEX idx_plugin_registry_plugin_key ON plugin_registry(plugin_key);
CREATE INDEX idx_plugin_registry_type ON plugin_registry(plugin_type);
CREATE INDEX idx_service_usage_analytics_service_id ON service_usage_analytics(service_id);
CREATE INDEX idx_service_usage_analytics_user_id ON service_usage_analytics(user_id);
CREATE INDEX idx_service_usage_analytics_timestamp ON service_usage_analytics(timestamp);

-- Marketing web indexes
CREATE INDEX idx_marketing_campaigns_type ON marketing_campaigns(campaign_type);
CREATE INDEX idx_marketing_campaigns_status ON marketing_campaigns(status);
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_content_pages_slug ON content_pages(page_slug);
CREATE INDEX idx_content_pages_type ON content_pages(page_type);
CREATE INDEX idx_content_pages_published ON content_pages(is_published);

-- User dashboard indexes
CREATE INDEX idx_user_dashboard_preferences_user_id ON user_dashboard_preferences(user_id);
CREATE INDEX idx_user_activity_log_user_id ON user_activity_log(user_id);
CREATE INDEX idx_user_activity_log_type ON user_activity_log(activity_type);
CREATE INDEX idx_user_notifications_user_id ON user_notifications(user_id);
CREATE INDEX idx_user_notifications_read ON user_notifications(is_read);

-- Admin dashboard indexes
CREATE INDEX idx_admin_analytics_metric_name ON admin_analytics(metric_name);
CREATE INDEX idx_admin_analytics_date ON admin_analytics(date_recorded);
CREATE INDEX idx_system_alerts_type ON system_alerts(alert_type);
CREATE INDEX idx_system_alerts_resolved ON system_alerts(is_resolved);
CREATE INDEX idx_admin_roles_name ON admin_roles(role_name);
CREATE INDEX idx_user_admin_roles_user_id ON user_admin_roles(user_id);
CREATE INDEX idx_user_admin_roles_role_id ON user_admin_roles(role_id);

-- Delivery system indexes
CREATE INDEX idx_workflow_instances_user_id ON workflow_instances(user_id);
CREATE INDEX idx_workflow_instances_status ON workflow_instances(status);
CREATE INDEX idx_workflow_instances_assigned_to ON workflow_instances(assigned_to);
CREATE INDEX idx_employee_tasks_assigned_to ON employee_tasks(assigned_to);
CREATE INDEX idx_employee_tasks_status ON employee_tasks(status);
CREATE INDEX idx_employee_tasks_due_date ON employee_tasks(due_date);
CREATE INDEX idx_quality_reviews_task_id ON quality_reviews(task_id);
CREATE INDEX idx_quality_reviews_reviewer_id ON quality_reviews(reviewer_id);
CREATE INDEX idx_employee_performance_employee_id ON employee_performance(employee_id);
CREATE INDEX idx_employee_performance_period ON employee_performance(period_start, period_end);

-- Lifecycle tracking indexes
CREATE INDEX idx_service_lifecycle_user_id ON service_lifecycle(user_id);
CREATE INDEX idx_service_lifecycle_service_id ON service_lifecycle(service_id);
CREATE INDEX idx_service_lifecycle_stage ON service_lifecycle(current_stage);
CREATE INDEX idx_lifecycle_events_lifecycle_id ON lifecycle_events(lifecycle_id);
CREATE INDEX idx_lifecycle_events_type ON lifecycle_events(event_type);
CREATE INDEX idx_service_delivery_metrics_service_id ON service_delivery_metrics(service_id);
CREATE INDEX idx_service_delivery_metrics_date ON service_delivery_metrics(measurement_date);

-- UI components indexes
CREATE INDEX idx_ui_components_component_id ON ui_components(component_id);
CREATE INDEX idx_ui_components_service_key ON ui_components(service_key);
CREATE INDEX idx_ui_components_type ON ui_components(component_type);
CREATE INDEX idx_ui_components_enabled ON ui_components(is_enabled);

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
-- AI AGENT SYSTEM AND GUARDRAILS
-- ============================================================================

-- AI agent capabilities and permissions
CREATE TABLE ai_agent_capabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50) NOT NULL, -- administrative, service_delivery, communication, compliance
    capability_name VARCHAR(100) NOT NULL,
    description TEXT,
    upl_risk_level VARCHAR(20) DEFAULT 'low', -- low, medium, high
    requires_human_approval BOOLEAN DEFAULT FALSE,
    max_automation_level VARCHAR(50), -- fully_automated, semi_automated, manual_only
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI agent task execution log
CREATE TABLE ai_agent_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    task_parameters JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed, requires_approval
    result_data JSONB DEFAULT '{}',
    error_message TEXT,
    human_approval_required BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI usage limits and cost control
CREATE TABLE ai_usage_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    limit_type VARCHAR(50) NOT NULL, -- daily_tokens, monthly_tokens, daily_requests, monthly_requests
    limit_value INTEGER NOT NULL,
    current_usage INTEGER DEFAULT 0,
    reset_period VARCHAR(20) NOT NULL, -- daily, monthly
    last_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI usage tracking and cost monitoring
CREATE TABLE ai_usage_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost_estimate DECIMAL(10,4) DEFAULT 0,
    request_size INTEGER DEFAULT 0,
    response_size INTEGER DEFAULT 0,
    execution_time_ms INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_code VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI abuse detection and violation tracking
CREATE TABLE ai_abuse_detection (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    violation_type VARCHAR(50) NOT NULL, -- off_topic, excessive_usage, inappropriate_content, system_gaming
    violation_details JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'low', -- low, medium, high, critical
    action_taken VARCHAR(50) DEFAULT 'warning', -- warning, throttle, suspend, block
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    resolution_notes TEXT
);

-- AI content filtering rules and patterns
CREATE TABLE ai_content_filters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filter_type VARCHAR(50) NOT NULL, -- keyword_block, pattern_block, context_validation
    filter_name VARCHAR(100) NOT NULL,
    filter_pattern TEXT NOT NULL,
    filter_action VARCHAR(50) NOT NULL, -- block, warn, flag, allow
    severity VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI agent performance and quality metrics
CREATE TABLE ai_agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- response_time, success_rate, user_satisfaction, cost_efficiency
    metric_value DECIMAL(10,4) NOT NULL,
    measurement_period VARCHAR(20) NOT NULL, -- hourly, daily, weekly, monthly
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- AI escalation and human handoff tracking
CREATE TABLE ai_escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    escalation_reason VARCHAR(100) NOT NULL, -- upl_risk, complex_query, user_request, system_error
    escalation_details JSONB DEFAULT '{}',
    original_request TEXT,
    ai_response TEXT,
    human_response TEXT,
    escalated_to UUID REFERENCES users(id),
    escalated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_quality INTEGER, -- 1-5 rating
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MODERN AUTHENTICATION SYSTEM
-- ============================================================================

-- Authentication methods
CREATE TABLE authentication_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    method_type VARCHAR(50) NOT NULL, -- passkey, magic_link, sms, email, password
    method_data JSONB DEFAULT '{}', -- Encrypted method-specific data
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE
);

-- Passkey credentials (WebAuthn/FIDO2)
CREATE TABLE passkey_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    credential_id TEXT NOT NULL UNIQUE, -- Base64 encoded credential ID
    public_key TEXT NOT NULL, -- Base64 encoded public key
    counter INTEGER DEFAULT 0,
    device_name VARCHAR(255), -- User-friendly device name
    device_type VARCHAR(100), -- phone, laptop, tablet, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE
);

-- Magic link tokens
CREATE TABLE magic_link_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Authentication sessions
CREATE TABLE authentication_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    authentication_method VARCHAR(50) NOT NULL,
    device_fingerprint VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    location_data JSONB, -- Country, city, etc.
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Device trust management
CREATE TABLE trusted_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_fingerprint VARCHAR(255) NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(100),
    location_data JSONB,
    trust_level VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    is_trusted BOOLEAN DEFAULT FALSE,
    trust_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Authentication risk assessment
CREATE TABLE authentication_risk (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID REFERENCES authentication_sessions(id),
    risk_factors JSONB DEFAULT '{}', -- New device, unusual location, etc.
    risk_score DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
    risk_level VARCHAR(20) DEFAULT 'low', -- low, medium, high, critical
    additional_verification_required BOOLEAN DEFAULT FALSE,
    blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECURITY & DATA PROTECTION
-- ============================================================================

-- User security settings
CREATE TABLE user_security_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255), -- Encrypted MFA secret
    backup_codes TEXT[], -- Encrypted backup codes
    password_last_changed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    last_login_location JSONB, -- Country, city, etc.
    security_questions JSONB DEFAULT '{}', -- Encrypted security questions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data encryption keys
CREATE TABLE encryption_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_name VARCHAR(100) NOT NULL UNIQUE,
    key_type VARCHAR(50) NOT NULL, -- user_data, documents, communications
    encrypted_key TEXT NOT NULL, -- Encrypted with master key
    key_version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Audit trail for security events
CREATE TABLE security_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(100) NOT NULL, -- login, logout, password_change, data_access
    event_details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    risk_level VARCHAR(20) DEFAULT 'low', -- low, medium, high, critical
    blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data access logs
CREATE TABLE data_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    data_type VARCHAR(100) NOT NULL, -- personal_info, documents, communications
    data_id UUID NOT NULL, -- ID of accessed data
    access_type VARCHAR(50) NOT NULL, -- read, write, delete, export
    access_reason VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data retention policies
CREATE TABLE data_retention_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_type VARCHAR(100) NOT NULL,
    retention_period_days INTEGER NOT NULL,
    auto_delete BOOLEAN DEFAULT FALSE,
    legal_hold BOOLEAN DEFAULT FALSE, -- Prevent deletion for legal reasons
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Privacy settings
CREATE TABLE user_privacy_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data_sharing_preferences JSONB DEFAULT '{}',
    marketing_consent BOOLEAN DEFAULT FALSE,
    analytics_consent BOOLEAN DEFAULT FALSE,
    third_party_sharing BOOLEAN DEFAULT FALSE,
    data_portability BOOLEAN DEFAULT TRUE,
    right_to_deletion BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- VERTICAL DASHBOARD FOUNDATION
-- ============================================================================

-- Dashboard types and configurations
CREATE TABLE dashboard_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dashboard_name VARCHAR(100) NOT NULL UNIQUE,
    service_category VARCHAR(100) NOT NULL,
    dashboard_type VARCHAR(50) NOT NULL, -- basic, vertical, enterprise
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dashboard configurations (JSON-based for flexibility)
CREATE TABLE dashboard_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dashboard_type_id UUID NOT NULL REFERENCES dashboard_types(id),
    configuration_name VARCHAR(100) NOT NULL,
    configuration_data JSONB NOT NULL, -- workflow stages, features, AI agents
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User dashboard assignments
CREATE TABLE user_dashboard_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    dashboard_type_id UUID NOT NULL REFERENCES dashboard_types(id),
    dashboard_config_id UUID REFERENCES dashboard_configurations(id),
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Dashboard widgets (reusable across all dashboards)
CREATE TABLE dashboard_widgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    widget_name VARCHAR(100) NOT NULL UNIQUE,
    widget_type VARCHAR(50) NOT NULL, -- chart, table, form, workflow, ai_chat
    widget_category VARCHAR(50) NOT NULL, -- general, vertical_specific
    widget_config JSONB DEFAULT '{}',
    is_reusable BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User widget customizations
CREATE TABLE user_widget_customizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    widget_id UUID NOT NULL REFERENCES dashboard_widgets(id),
    dashboard_type_id UUID REFERENCES dashboard_types(id),
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER DEFAULT 4,
    height INTEGER DEFAULT 3,
    widget_settings JSONB DEFAULT '{}',
    is_visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- AI AGENT FOUNDATION (VERTICAL-READY)
-- ============================================================================

-- AI agent types (extensible for verticals)
CREATE TABLE ai_agent_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    agent_category VARCHAR(50) NOT NULL, -- general, vertical_specific
    agent_description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI agent configurations per vertical
CREATE TABLE ai_agent_vertical_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type_id UUID NOT NULL REFERENCES ai_agent_types(id),
    service_category VARCHAR(100) NOT NULL,
    agent_config JSONB DEFAULT '{}',
    automation_rules JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- WORKFLOW FOUNDATION (VERTICAL-READY)
-- ============================================================================

-- Workflow templates (reusable across verticals)
CREATE TABLE workflow_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(100) NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    workflow_stages JSONB NOT NULL, -- array of stage objects
    stage_connections JSONB DEFAULT '{}', -- how stages connect
    ai_agent_integration JSONB DEFAULT '{}', -- which agents handle which stages
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User workflow instances
CREATE TABLE user_workflow_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    workflow_template_id UUID NOT NULL REFERENCES workflow_templates(id),
    instance_name VARCHAR(255) NOT NULL,
    current_stage VARCHAR(100),
    stage_data JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active', -- active, completed, paused, cancelled
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- DOCUMENT FOUNDATION (VERTICAL-READY)
-- ============================================================================

-- Document template categories
CREATE TABLE document_template_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_name VARCHAR(100) NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    parent_category_id UUID REFERENCES document_template_categories(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SERVICE REGISTRY SYSTEM
-- ============================================================================

-- Service registry for dynamic service management
CREATE TABLE service_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_key VARCHAR(100) NOT NULL UNIQUE, -- business_formation, real_estate, etc.
    service_name VARCHAR(255) NOT NULL,
    service_category VARCHAR(100) NOT NULL, -- business, legal, compliance
    service_type VARCHAR(50) NOT NULL, -- core, addon, plugin
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    is_enabled BOOLEAN DEFAULT TRUE,
    is_core BOOLEAN DEFAULT FALSE, -- Cannot be disabled
    display_order INTEGER DEFAULT 0,
    service_config JSONB DEFAULT '{}',
    dependencies JSONB DEFAULT '[]', -- Other services this depends on
    conflicts JSONB DEFAULT '[]', -- Services that conflict with this
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service features and capabilities
CREATE TABLE service_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES service_registry(id) ON DELETE CASCADE,
    feature_key VARCHAR(100) NOT NULL,
    feature_name VARCHAR(255) NOT NULL,
    feature_type VARCHAR(50) NOT NULL, -- api, ui, workflow, integration
    is_enabled BOOLEAN DEFAULT TRUE,
    feature_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service pricing and availability
CREATE TABLE service_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES service_registry(id) ON DELETE CASCADE,
    pricing_tier VARCHAR(50) NOT NULL, -- basic, premium, enterprise
    price DECIMAL(10,2) NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL, -- one_time, monthly, yearly
    is_active BOOLEAN DEFAULT TRUE,
    effective_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User service access and permissions
CREATE TABLE user_service_access (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES service_registry(id) ON DELETE CASCADE,
    access_level VARCHAR(50) NOT NULL, -- full, limited, trial
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    access_config JSONB DEFAULT '{}'
);

-- Plugin registry for modular functionality
CREATE TABLE plugin_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plugin_key VARCHAR(100) NOT NULL UNIQUE,
    plugin_name VARCHAR(255) NOT NULL,
    plugin_version VARCHAR(20) NOT NULL,
    plugin_type VARCHAR(50) NOT NULL, -- service, integration, ui_component
    is_installed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    plugin_config JSONB DEFAULT '{}',
    dependencies JSONB DEFAULT '[]',
    installation_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service usage analytics
CREATE TABLE service_usage_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES service_registry(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    usage_type VARCHAR(50) NOT NULL, -- api_call, ui_interaction, workflow_execution
    usage_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT
);

-- Service configuration templates
CREATE TABLE service_config_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES service_registry(id) ON DELETE CASCADE,
    template_name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- default, custom, industry_specific
    template_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MARKETING WEB INTERFACE
-- ============================================================================

-- Marketing campaigns
CREATE TABLE marketing_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_name VARCHAR(255) NOT NULL,
    campaign_type VARCHAR(50) NOT NULL, -- seo, sem, social, email
    status VARCHAR(20) DEFAULT 'active',
    budget DECIMAL(10,2),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lead management
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    phone VARCHAR(20),
    lead_source VARCHAR(100),
    lead_score INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'new',
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content management
CREATE TABLE content_pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    page_title VARCHAR(255) NOT NULL,
    page_slug VARCHAR(255) NOT NULL UNIQUE,
    page_type VARCHAR(50) NOT NULL, -- landing, blog, service, faq
    content TEXT,
    meta_description TEXT,
    meta_keywords TEXT,
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER DASHBOARD INTERFACE
-- ============================================================================

-- User dashboard preferences
CREATE TABLE user_dashboard_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User activity tracking
CREATE TABLE user_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User notifications
CREATE TABLE user_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ADMIN DASHBOARD INTERFACE
-- ============================================================================

-- Admin analytics
CREATE TABLE admin_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2),
    metric_data JSONB DEFAULT '{}',
    date_recorded DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System alerts
CREATE TABLE system_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Admin user roles
CREATE TABLE admin_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(100) NOT NULL UNIQUE,
    role_description TEXT,
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User role assignments
CREATE TABLE user_admin_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES admin_roles(id),
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- DELIVERY SYSTEM INTERFACE
-- ============================================================================

-- Workflow instances
CREATE TABLE workflow_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_template_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    current_stage VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    assigned_to UUID REFERENCES users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee tasks
CREATE TABLE employee_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_instance_id UUID REFERENCES workflow_instances(id),
    assigned_to UUID NOT NULL REFERENCES users(id),
    task_type VARCHAR(100) NOT NULL,
    task_description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'pending',
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_spent INTEGER DEFAULT 0, -- minutes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quality control reviews
CREATE TABLE quality_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES employee_tasks(id),
    reviewer_id UUID NOT NULL REFERENCES users(id),
    review_type VARCHAR(50) NOT NULL, -- initial, final, audit
    review_status VARCHAR(50) DEFAULT 'pending',
    review_notes TEXT,
    quality_score INTEGER, -- 1-10
    approved BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee performance metrics
CREATE TABLE employee_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES users(id),
    metric_period VARCHAR(20) NOT NULL, -- daily, weekly, monthly
    tasks_completed INTEGER DEFAULT 0,
    average_quality_score DECIMAL(3,2),
    average_completion_time INTEGER, -- minutes
    customer_satisfaction DECIMAL(3,2),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- LIFECYCLE TRACKING SYSTEM
-- ============================================================================

-- Service lifecycle tracking
CREATE TABLE service_lifecycle (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    service_id UUID NOT NULL REFERENCES services(id),
    current_stage VARCHAR(100) NOT NULL,
    stage_data JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lifecycle events
CREATE TABLE lifecycle_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lifecycle_id UUID NOT NULL REFERENCES service_lifecycle(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    triggered_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service delivery metrics
CREATE TABLE service_delivery_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES services(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2),
    metric_unit VARCHAR(50),
    measurement_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- UI COMPONENTS SYSTEM
-- ============================================================================

-- UI components registry
CREATE TABLE ui_components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id VARCHAR(100) NOT NULL UNIQUE,
    service_key VARCHAR(100) NOT NULL,
    component_name VARCHAR(255) NOT NULL,
    component_type VARCHAR(50) NOT NULL, -- page, widget, workflow, integration
    component_config JSONB DEFAULT '{}',
    dependencies JSONB DEFAULT '[]',
    is_enabled BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    render_function VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert default services
INSERT INTO services (name, description, category, tier, price, features, deliverables, upl_risk_level) VALUES
('Essential Startup Package', 'Complete business startup with EIN, entity formation, and basic licenses', 'business_formation', 'essential', 399.00, '{"ein": true, "entity_formation": true, "state_tax": true, "basic_license": true, "registered_agent": true}', '["EIN Confirmation", "Formation Documents", "State Tax Registration", "Business License", "Operating Agreement", "Compliance Calendar"]', 'low'),
('Comprehensive Startup Package', 'Complete startup with EIN, entity formation, and local licenses', 'business_formation', 'comprehensive', 699.00, '{"ein": true, "entity_formation": true, "state_tax": true, "city_license": true, "county_license": true, "dba": true, "banking_guidance": true, "insurance_guidance": true}', '["EIN Confirmation", "Formation Documents", "City/County Licenses", "DBA Registration", "Banking Setup Guide", "Insurance Recommendations", "Legal Website Templates", "Employee Handbook"]', 'low'),
('Premium Startup Package', 'Complete startup with EIN, entity formation, and industry-specific licenses', 'business_formation', 'premium', 1299.00, '{"ein": true, "entity_formation": true, "industry_licenses": true, "building_permits": true, "environmental_permits": true, "professional_licenses": true, "compliance_monitoring": true}', '["EIN Confirmation", "Formation Documents", "Industry Licenses", "Building Permits", "Environmental Permits", "Professional Licenses", "Business Plan", "1-Year Compliance Monitoring"]', 'low'),
('Restaurant & Food Service Package', 'Specialized package for food businesses with health permits and certifications', 'business_formation', 'industry_specific', 1499.00, '{"ein": true, "entity_formation": true, "health_permit": true, "food_handler_cert": true, "liquor_license": true, "fire_inspection": true, "waste_management": true}', '["EIN Confirmation", "Formation Documents", "Health Department Permit", "Food Handler Certifications", "Liquor License Application", "Fire Inspection", "Waste Management Permit", "Menu Compliance Guide"]', 'low'),
('Healthcare Practice Package', 'Specialized package for medical practices with professional licensing', 'business_formation', 'industry_specific', 1799.00, '{"ein": true, "entity_formation": true, "medical_license": true, "hipaa_compliance": true, "medicare_enrollment": true, "dea_registration": true, "medical_waste": true}', '["EIN Confirmation", "Formation Documents", "Medical License Application", "HIPAA Compliance Setup", "Medicare/Medicaid Enrollment", "DEA Registration", "Medical Waste Permit", "Patient Privacy Policies"]', 'low'),
('Construction Company Package', 'Specialized package for construction businesses with contractor licensing', 'business_formation', 'industry_specific', 1399.00, '{"ein": true, "entity_formation": true, "contractor_license": true, "building_permits": true, "environmental_permits": true, "workers_comp": true, "bonding": true}', '["EIN Confirmation", "Formation Documents", "General Contractor License", "Building Permits", "Environmental Permits", "Workers Compensation", "Bonding Services", "Safety Compliance Guide"]', 'low'),
('Retail & E-commerce Package', 'Specialized package for retail businesses with sales tax and e-commerce compliance', 'business_formation', 'industry_specific', 999.00, '{"ein": true, "entity_formation": true, "sales_tax": true, "ecommerce_compliance": true, "product_liability": true, "payment_processing": true}', '["EIN Confirmation", "Formation Documents", "Sales Tax Registration", "E-commerce Compliance", "Product Liability Insurance", "Payment Processing Setup", "Customer Privacy Policies", "Inventory Management"]', 'low'),
('Real Estate - Purchase Package', 'Complete real estate purchase documentation and compliance tracking', 'real_estate', 'premium', 499.00, '{"contract_review": true, "closing_docs": true, "compliance_tracking": true}', '["Purchase Agreement", "Closing Documents", "Title Insurance", "Compliance Calendar"]', 'medium'),
('Healthcare - HIPAA Compliance', 'HIPAA compliance package with risk assessment and training', 'healthcare', 'premium', 799.00, '{"risk_assessment": true, "training": true, "policies": true}', '["HIPAA Policies", "Risk Assessment", "Training Materials", "Compliance Calendar"]', 'low');

-- Create admin user (password should be hashed in production)
INSERT INTO users (email, password_hash, first_name, last_name, company_name, business_type, is_verified, is_active) VALUES
('admin@legalops.com', '$2b$12$example_hash', 'Admin', 'User', 'Legal Ops Platform', 'technology', TRUE, TRUE);

-- Grant admin role
INSERT INTO user_roles (user_id, role, permissions) 
SELECT id, 'admin', '{"all": true}' FROM users WHERE email = 'admin@legalops.com';

-- Insert AI agent capabilities
INSERT INTO ai_agent_capabilities (agent_type, capability_name, description, upl_risk_level, requires_human_approval, max_automation_level) VALUES
('administrative', 'schedule_appointment', 'Schedule appointments and reminders for compliance deadlines', 'low', FALSE, 'fully_automated'),
('administrative', 'send_reminder', 'Send automated reminders for upcoming deadlines', 'low', FALSE, 'fully_automated'),
('administrative', 'update_calendar', 'Update user calendar with important dates', 'low', FALSE, 'fully_automated'),
('service_delivery', 'prepare_document', 'Prepare documents using approved templates', 'low', FALSE, 'semi_automated'),
('service_delivery', 'submit_filing', 'Submit filings to government systems', 'medium', TRUE, 'semi_automated'),
('service_delivery', 'check_status', 'Check status of government filings', 'low', FALSE, 'fully_automated'),
('communication', 'send_notification', 'Send service updates and notifications', 'low', FALSE, 'fully_automated'),
('communication', 'proactive_outreach', 'Proactive communication based on user behavior', 'low', FALSE, 'semi_automated'),
('communication', 'collect_feedback', 'Collect and respond to user feedback', 'low', FALSE, 'semi_automated'),
('compliance', 'upl_monitoring', 'Monitor all AI actions for UPL compliance', 'high', TRUE, 'fully_automated'),
('compliance', 'risk_assessment', 'Assess risk level of AI actions', 'high', TRUE, 'semi_automated'),
('compliance', 'escalate_to_human', 'Escalate complex situations to human review', 'high', TRUE, 'fully_automated');

-- Insert default AI usage limits by user tier
INSERT INTO ai_usage_limits (user_id, limit_type, limit_value, reset_period) 
SELECT u.id, 'daily_requests', 50, 'daily' FROM users u WHERE u.email = 'admin@legalops.com';

INSERT INTO ai_usage_limits (user_id, limit_type, limit_value, reset_period) 
SELECT u.id, 'monthly_tokens', 100000, 'monthly' FROM users u WHERE u.email = 'admin@legalops.com';

-- Insert content filtering rules
INSERT INTO ai_content_filters (filter_type, filter_name, filter_pattern, filter_action, severity) VALUES
('keyword_block', 'coding_keywords', 'code|programming|python|javascript|java|c\+\+|html|css|sql|database|api|github|git', 'block', 'high'),
('keyword_block', 'crypto_trading', 'bitcoin|crypto|cryptocurrency|trading|investment|stock|forex|gambling|casino', 'block', 'high'),
('keyword_block', 'personal_topics', 'personal|relationship|dating|marriage|divorce|therapy|medical|health|mental', 'block', 'medium'),
('keyword_block', 'illegal_activities', 'hack|hacking|illegal|fraud|scam|steal|theft|drug|weapon', 'block', 'critical'),
('context_validation', 'legal_business_only', 'business|llc|corporation|filing|compliance|real estate|property|contract|agreement|healthcare|hipaa|license|permit', 'allow', 'low');

-- Insert dashboard types
INSERT INTO dashboard_types (dashboard_name, service_category, dashboard_type, sort_order) VALUES
('General Dashboard', 'general', 'basic', 1),
('Business Formation Dashboard', 'business_formation', 'vertical', 2),
('Registered Agent Dashboard', 'registered_agent', 'vertical', 3),
('Construction Dashboard', 'construction', 'vertical', 4),
('Healthcare Dashboard', 'healthcare', 'vertical', 5),
('Food & Beverage Dashboard', 'food_beverage', 'vertical', 6),
('Education Dashboard', 'education', 'vertical', 7),
('Retail Dashboard', 'retail_ecommerce', 'vertical', 8);

-- Insert AI agent types
INSERT INTO ai_agent_types (agent_name, agent_category, agent_description) VALUES
('Communication Agent', 'general', 'Handles all user communication and notifications'),
('Administrative Agent', 'general', 'Manages scheduling, reminders, and administrative tasks'),
('Service Delivery Agent', 'general', 'Executes service delivery tasks and document generation'),
('Compliance Agent', 'general', 'Monitors compliance and regulatory requirements'),
('Construction Agent', 'vertical_specific', 'Specialized for construction project management'),
('Healthcare Agent', 'vertical_specific', 'Specialized for healthcare compliance'),
('Food Safety Agent', 'vertical_specific', 'Specialized for food & beverage compliance');

-- Insert reusable widgets
INSERT INTO dashboard_widgets (widget_name, widget_type, widget_category, widget_config) VALUES
('Project Status', 'workflow', 'general', '{"display_type": "progress_bar", "show_milestones": true}'),
('Financial Summary', 'chart', 'general', '{"chart_type": "donut", "show_trends": true}'),
('Recent Activity', 'table', 'general', '{"columns": ["date", "action", "status"], "limit": 10}'),
('AI Chat', 'ai_chat', 'general', '{"agent_type": "communication", "context_aware": true}'),
('Compliance Calendar', 'calendar', 'general', '{"show_deadlines": true, "show_reminders": true}'),
('Document Library', 'table', 'general', '{"show_download": true, "show_versions": true}'),
('Workflow Tracker', 'workflow', 'vertical_specific', '{"interactive": true, "show_stages": true}'),
('Project Timeline', 'chart', 'vertical_specific', '{"chart_type": "gantt", "show_dependencies": true}');

-- Insert document template categories
INSERT INTO document_template_categories (category_name, service_category, sort_order) VALUES
('Business Formation', 'business_formation', 1),
('Registered Agent', 'registered_agent', 2),
('Construction Contracts', 'construction', 3),
('Healthcare Compliance', 'healthcare', 4),
('Food Safety', 'food_beverage', 5),
('Education Forms', 'education', 6),
('Retail Compliance', 'retail_ecommerce', 7);

-- Insert data retention policies
INSERT INTO data_retention_policies (data_type, retention_period_days, auto_delete) VALUES
('user_communications', 2555, TRUE), -- 7 years
('audit_logs', 2555, TRUE), -- 7 years
('user_documents', 2555, TRUE), -- 7 years
('ai_usage_log', 365, TRUE), -- 1 year
('security_audit_log', 2555, TRUE), -- 7 years
('data_access_log', 365, TRUE); -- 1 year

-- Insert core services into service registry
INSERT INTO service_registry (service_key, service_name, service_category, service_type, version, is_enabled, is_core, display_order, service_config, dependencies, conflicts) VALUES
('authentication', 'Authentication System', 'core', 'core', '1.0.0', TRUE, TRUE, 1, '{"icon": "shield", "color": "#10B981", "description": "User authentication and security"}', '[]', '[]'),
('database', 'Database System', 'core', 'core', '1.0.0', TRUE, TRUE, 2, '{"icon": "database", "color": "#6B7280", "description": "Core database functionality"}', '[]', '[]'),
('business_formation', 'Business Formation', 'business', 'core', '1.0.0', TRUE, TRUE, 3, '{"icon": "business", "color": "#3B82F6", "description": "Complete business formation services"}', '["authentication", "database"]', '[]'),
('registered_agent', 'Registered Agent Services', 'business', 'core', '1.0.0', TRUE, FALSE, 4, '{"icon": "mail", "color": "#8B5CF6", "description": "Registered agent and mail forwarding services"}', '["authentication", "database"]', '[]'),
('real_estate', 'Real Estate Services', 'legal', 'addon', '1.0.0', TRUE, FALSE, 5, '{"icon": "home", "color": "#F59E0B", "description": "Real estate transaction services"}', '["authentication", "database"]', '[]'),
('healthcare', 'Healthcare Services', 'legal', 'addon', '1.0.0', TRUE, FALSE, 6, '{"icon": "medical", "color": "#EF4444", "description": "Healthcare compliance and licensing"}', '["authentication", "database"]', '[]'),
('construction', 'Construction Services', 'legal', 'addon', '1.0.0', TRUE, FALSE, 7, '{"icon": "construction", "color": "#84CC16", "description": "Construction project management and compliance"}', '["authentication", "database"]', '[]'),
('food_beverage', 'Food & Beverage Services', 'legal', 'addon', '1.0.0', TRUE, FALSE, 8, '{"icon": "restaurant", "color": "#F97316", "description": "Food service licensing and compliance"}', '["authentication", "database"]', '[]'),
('education', 'Education Services', 'legal', 'addon', '1.0.0', TRUE, FALSE, 9, '{"icon": "education", "color": "#06B6D4", "description": "Educational institution compliance"}', '["authentication", "database"]', '[]'),
('retail_ecommerce', 'Retail & E-commerce Services', 'legal', 'addon', '1.0.0', TRUE, FALSE, 10, '{"icon": "shopping", "color": "#EC4899", "description": "Retail and e-commerce compliance"}', '["authentication", "database"]', '[]');

-- Insert service features for business formation
INSERT INTO service_features (service_id, feature_key, feature_name, feature_type, is_enabled, feature_config) 
SELECT sr.id, 'ein_acquisition', 'EIN Acquisition', 'workflow', TRUE, '{"automated": true, "processing_time": "1-2 days"}'
FROM service_registry sr WHERE sr.service_key = 'business_formation';

INSERT INTO service_features (service_id, feature_key, feature_name, feature_type, is_enabled, feature_config) 
SELECT sr.id, 'license_application', 'License Applications', 'workflow', TRUE, '{"automated": true, "processing_time": "3-7 days"}'
FROM service_registry sr WHERE sr.service_key = 'business_formation';

INSERT INTO service_features (service_id, feature_key, feature_name, feature_type, is_enabled, feature_config) 
SELECT sr.id, 'entity_formation', 'Entity Formation', 'workflow', TRUE, '{"automated": true, "processing_time": "1-3 days"}'
FROM service_registry sr WHERE sr.service_key = 'business_formation';

-- Insert service pricing for business formation
INSERT INTO service_pricing (service_id, pricing_tier, price, billing_cycle, is_active) 
SELECT sr.id, 'essential', 399.00, 'one_time', TRUE
FROM service_registry sr WHERE sr.service_key = 'business_formation';

INSERT INTO service_pricing (service_id, pricing_tier, price, billing_cycle, is_active) 
SELECT sr.id, 'comprehensive', 699.00, 'one_time', TRUE
FROM service_registry sr WHERE sr.service_key = 'business_formation';

INSERT INTO service_pricing (service_id, pricing_tier, price, billing_cycle, is_active) 
SELECT sr.id, 'premium', 1299.00, 'one_time', TRUE
FROM service_registry sr WHERE sr.service_key = 'business_formation';

-- Insert add-on services
INSERT INTO services (name, description, category, tier, price, features, deliverables, upl_risk_level) VALUES
('EIN Only Service', 'Employer Identification Number acquisition', 'business_formation', 'addon', 99.00, '{"ein": true}', '["EIN Confirmation Letter"]', 'low'),
('City Business License', 'City-level business operation license', 'business_formation', 'addon', 149.00, '{"city_license": true}', '["City Business License"]', 'low'),
('County Business License', 'County-level business operation license', 'business_formation', 'addon', 149.00, '{"county_license": true}', '["County Business License"]', 'low'),
('Health Department Permit', 'Health department permit for food service', 'business_formation', 'addon', 199.00, '{"health_permit": true}', '["Health Department Permit"]', 'low'),
('Building Permit', 'Building and construction permit', 'business_formation', 'addon', 299.00, '{"building_permit": true}', '["Building Permit"]', 'low'),
('Professional License Application', 'Industry-specific professional license', 'business_formation', 'addon', 399.00, '{"professional_license": true}', '["Professional License Application"]', 'low'),
('Environmental Permit', 'Environmental compliance permit', 'business_formation', 'addon', 599.00, '{"environmental_permit": true}', '["Environmental Permit"]', 'low'),
('Federal License Application', 'Federal agency license application', 'business_formation', 'addon', 799.00, '{"federal_license": true}', '["Federal License Application"]', 'low'),
('License Renewal Service', 'Annual license renewal service', 'business_formation', 'addon', 199.00, '{"license_renewal": true}', '["License Renewal Confirmation"]', 'low'),
('Compliance Monitoring', 'Ongoing compliance tracking and alerts', 'business_formation', 'addon', 299.00, '{"compliance_monitoring": true}', '["Compliance Calendar", "Renewal Alerts"]', 'low');
