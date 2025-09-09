#!/usr/bin/env python3
"""
AI Guardrails System for Legal Ops Platform
Comprehensive protection against misuse, cost overruns, and UPL violations
"""

import re
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ViolationType(Enum):
    OFF_TOPIC = "off_topic"
    EXCESSIVE_USAGE = "excessive_usage"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SYSTEM_GAMING = "system_gaming"
    UPL_VIOLATION = "upl_violation"

class ActionType(Enum):
    WARNING = "warning"
    THROTTLE = "throttle"
    SUSPEND = "suspend"
    BLOCK = "block"

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class GuardrailResult:
    allowed: bool
    reason: str
    action_taken: Optional[ActionType] = None
    severity: Optional[Severity] = None
    cost_estimate: float = 0.0
    tokens_used: int = 0

class AIGuardrails:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.off_topic_keywords = [
            'code', 'programming', 'python', 'javascript', 'java', 'c++', 'html', 'css',
            'sql', 'database', 'api', 'github', 'git', 'bitcoin', 'crypto', 'cryptocurrency',
            'trading', 'investment', 'stock', 'forex', 'gambling', 'casino', 'personal',
            'relationship', 'dating', 'marriage', 'divorce', 'therapy', 'medical', 'health',
            'mental', 'hack', 'hacking', 'illegal', 'fraud', 'scam', 'steal', 'theft',
            'drug', 'weapon'
        ]
        
        self.legal_business_keywords = [
            'business', 'llc', 'corporation', 'filing', 'compliance', 'real estate',
            'property', 'contract', 'agreement', 'healthcare', 'hipaa', 'license',
            'permit', 'formation', 'registered agent', 'annual report', 'operating agreement',
            'articles of incorporation', 'bylaws', 'ein', 'tax', 'payroll', 'employment'
        ]
        
        # Cost estimates (per 1000 tokens)
        self.cost_per_1k_tokens = {
            'gpt-4': 0.03,
            'gpt-3.5-turbo': 0.002,
            'claude-3': 0.015
        }
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    def check_usage_limits(self, user_id: str, agent_type: str, estimated_tokens: int) -> GuardrailResult:
        """Check if user has exceeded usage limits"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get user's current usage limits
                    cursor.execute("""
                        SELECT limit_type, limit_value, current_usage, reset_period, last_reset
                        FROM ai_usage_limits 
                        WHERE user_id = %s AND is_active = TRUE
                    """, (user_id,))
                    
                    limits = cursor.fetchall()
                    
                    for limit in limits:
                        limit_type = limit['limit_type']
                        limit_value = limit['limit_value']
                        current_usage = limit['current_usage']
                        reset_period = limit['reset_period']
                        last_reset = limit['last_reset']
                        
                        # Check if reset period has passed
                        now = datetime.now()
                        if reset_period == 'daily':
                            if (now - last_reset).days >= 1:
                                # Reset daily usage
                                cursor.execute("""
                                    UPDATE ai_usage_limits 
                                    SET current_usage = 0, last_reset = NOW() 
                                    WHERE user_id = %s AND limit_type = %s
                                """, (user_id, limit_type))
                                current_usage = 0
                        elif reset_period == 'monthly':
                            if (now - last_reset).days >= 30:
                                # Reset monthly usage
                                cursor.execute("""
                                    UPDATE ai_usage_limits 
                                    SET current_usage = 0, last_reset = NOW() 
                                    WHERE user_id = %s AND limit_type = %s
                                """, (user_id, limit_type))
                                current_usage = 0
                        
                        # Check if adding estimated tokens would exceed limit
                        if limit_type in ['daily_tokens', 'monthly_tokens']:
                            if current_usage + estimated_tokens > limit_value:
                                return GuardrailResult(
                                    allowed=False,
                                    reason=f"Token limit exceeded: {current_usage + estimated_tokens}/{limit_value}",
                                    action_taken=ActionType.THROTTLE,
                                    severity=Severity.HIGH
                                )
                        
                        elif limit_type in ['daily_requests', 'monthly_requests']:
                            if current_usage + 1 > limit_value:
                                return GuardrailResult(
                                    allowed=False,
                                    reason=f"Request limit exceeded: {current_usage + 1}/{limit_value}",
                                    action_taken=ActionType.THROTTLE,
                                    severity=Severity.HIGH
                                )
                    
                    return GuardrailResult(allowed=True, reason="Usage within limits")
                    
        except Exception as e:
            logger.error(f"Error checking usage limits: {e}")
            return GuardrailResult(
                allowed=False,
                reason="Error checking usage limits",
                action_taken=ActionType.BLOCK,
                severity=Severity.CRITICAL
            )
    
    def validate_content(self, user_id: str, prompt: str, context: Dict[str, Any]) -> GuardrailResult:
        """Validate content for off-topic or inappropriate requests"""
        try:
            prompt_lower = prompt.lower()
            
            # Check for off-topic keywords
            for keyword in self.off_topic_keywords:
                if keyword in prompt_lower:
                    self.log_violation(user_id, ViolationType.OFF_TOPIC, {
                        'keyword': keyword,
                        'prompt': prompt[:200]  # Truncate for logging
                    })
                    return GuardrailResult(
                        allowed=False,
                        reason=f"Request contains off-topic keyword: {keyword}",
                        action_taken=ActionType.BLOCK,
                        severity=Severity.HIGH
                    )
            
            # Check if request is related to legal business
            legal_relevance = any(keyword in prompt_lower for keyword in self.legal_business_keywords)
            if not legal_relevance:
                # Check if user has active legal services
                with self.get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) as service_count
                            FROM user_services 
                            WHERE user_id = %s AND status = 'active'
                        """, (user_id,))
                        
                        result = cursor.fetchone()
                        if result['service_count'] == 0:
                            return GuardrailResult(
                                allowed=False,
                                reason="Request not related to legal business services",
                                action_taken=ActionType.BLOCK,
                                severity=Severity.MEDIUM
                            )
            
            # Check for UPL risk indicators
            upl_risk_phrases = [
                'legal advice', 'what should i do', 'is this legal', 'can i sue',
                'should i file', 'what are my rights', 'legal opinion', 'attorney'
            ]
            
            for phrase in upl_risk_phrases:
                if phrase in prompt_lower:
                    self.log_violation(user_id, ViolationType.UPL_VIOLATION, {
                        'phrase': phrase,
                        'prompt': prompt[:200]
                    })
                    return GuardrailResult(
                        allowed=False,
                        reason="Request may involve legal advice - requires human review",
                        action_taken=ActionType.SUSPEND,
                        severity=Severity.CRITICAL
                    )
            
            return GuardrailResult(allowed=True, reason="Content validation passed")
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            return GuardrailResult(
                allowed=False,
                reason="Error validating content",
                action_taken=ActionType.BLOCK,
                severity=Severity.CRITICAL
            )
    
    def check_abuse_patterns(self, user_id: str) -> GuardrailResult:
        """Check for abuse patterns in user behavior"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Check recent violations
                    cursor.execute("""
                        SELECT COUNT(*) as violation_count
                        FROM ai_abuse_detection 
                        WHERE user_id = %s 
                        AND detected_at > NOW() - INTERVAL '24 hours'
                        AND severity IN ('high', 'critical')
                    """, (user_id,))
                    
                    result = cursor.fetchone()
                    if result['violation_count'] >= 3:
                        return GuardrailResult(
                            allowed=False,
                            reason="Multiple violations detected in last 24 hours",
                            action_taken=ActionType.SUSPEND,
                            severity=Severity.CRITICAL
                        )
                    
                    # Check for excessive usage patterns
                    cursor.execute("""
                        SELECT COUNT(*) as request_count
                        FROM ai_usage_log 
                        WHERE user_id = %s 
                        AND created_at > NOW() - INTERVAL '1 hour'
                    """, (user_id,))
                    
                    result = cursor.fetchone()
                    if result['request_count'] > 50:  # More than 50 requests per hour
                        self.log_violation(user_id, ViolationType.EXCESSIVE_USAGE, {
                            'requests_per_hour': result['request_count']
                        })
                        return GuardrailResult(
                            allowed=False,
                            reason="Excessive usage detected",
                            action_taken=ActionType.THROTTLE,
                            severity=Severity.HIGH
                        )
                    
                    return GuardrailResult(allowed=True, reason="No abuse patterns detected")
                    
        except Exception as e:
            logger.error(f"Error checking abuse patterns: {e}")
            return GuardrailResult(
                allowed=False,
                reason="Error checking abuse patterns",
                action_taken=ActionType.BLOCK,
                severity=Severity.CRITICAL
            )
    
    def log_violation(self, user_id: str, violation_type: ViolationType, details: Dict[str, Any]):
        """Log a violation for tracking and analysis"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ai_abuse_detection 
                        (user_id, violation_type, violation_details, severity, action_taken)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        violation_type.value,
                        json.dumps(details),
                        'high' if violation_type in [ViolationType.UPL_VIOLATION, ViolationType.SYSTEM_GAMING] else 'medium',
                        'warning'
                    ))
                    
        except Exception as e:
            logger.error(f"Error logging violation: {e}")
    
    def log_usage(self, user_id: str, agent_type: str, action_type: str, 
                  tokens_used: int, cost_estimate: float, success: bool = True):
        """Log AI usage for cost tracking and analysis"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Log usage
                    cursor.execute("""
                        INSERT INTO ai_usage_log 
                        (user_id, agent_type, action_type, tokens_used, cost_estimate, success)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, agent_type, action_type, tokens_used, cost_estimate, success))
                    
                    # Update usage limits
                    cursor.execute("""
                        UPDATE ai_usage_limits 
                        SET current_usage = current_usage + %s
                        WHERE user_id = %s AND limit_type IN ('daily_tokens', 'monthly_tokens')
                    """, (tokens_used, user_id))
                    
                    cursor.execute("""
                        UPDATE ai_usage_limits 
                        SET current_usage = current_usage + 1
                        WHERE user_id = %s AND limit_type IN ('daily_requests', 'monthly_requests')
                    """, (user_id,))
                    
        except Exception as e:
            logger.error(f"Error logging usage: {e}")
    
    def estimate_cost(self, model: str, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate cost for AI request"""
        total_tokens = prompt_tokens + response_tokens
        cost_per_1k = self.cost_per_1k_tokens.get(model, 0.01)  # Default fallback
        return (total_tokens / 1000) * cost_per_1k
    
    def validate_request(self, user_id: str, prompt: str, context: Dict[str, Any], 
                        agent_type: str, model: str = 'gpt-4') -> GuardrailResult:
        """Comprehensive request validation with all guardrails"""
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) // 4 + 100  # Add buffer for response
        
        # Step 1: Check usage limits
        usage_result = self.check_usage_limits(user_id, agent_type, estimated_tokens)
        if not usage_result.allowed:
            return usage_result
        
        # Step 2: Validate content
        content_result = self.validate_content(user_id, prompt, context)
        if not content_result.allowed:
            return content_result
        
        # Step 3: Check abuse patterns
        abuse_result = self.check_abuse_patterns(user_id)
        if not abuse_result.allowed:
            return abuse_result
        
        # Step 4: Calculate cost estimate
        cost_estimate = self.estimate_cost(model, estimated_tokens, 100)
        
        return GuardrailResult(
            allowed=True,
            reason="All guardrails passed",
            cost_estimate=cost_estimate,
            tokens_used=estimated_tokens
        )
    
    def get_user_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive usage summary for user"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get current usage
                    cursor.execute("""
                        SELECT limit_type, limit_value, current_usage, reset_period
                        FROM ai_usage_limits 
                        WHERE user_id = %s AND is_active = TRUE
                    """, (user_id,))
                    
                    limits = cursor.fetchall()
                    
                    # Get recent usage
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_requests,
                            SUM(tokens_used) as total_tokens,
                            SUM(cost_estimate) as total_cost,
                            AVG(execution_time_ms) as avg_response_time
                        FROM ai_usage_log 
                        WHERE user_id = %s 
                        AND created_at > NOW() - INTERVAL '24 hours'
                    """, (user_id,))
                    
                    usage = cursor.fetchone()
                    
                    # Get violations
                    cursor.execute("""
                        SELECT COUNT(*) as violation_count
                        FROM ai_abuse_detection 
                        WHERE user_id = %s 
                        AND detected_at > NOW() - INTERVAL '30 days'
                    """, (user_id,))
                    
                    violations = cursor.fetchone()
                    
                    return {
                        'limits': [dict(limit) for limit in limits],
                        'usage_24h': dict(usage) if usage else {},
                        'violations_30d': violations['violation_count'] if violations else 0
                    }
                    
        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            return {}

def main():
    """Example usage of AI Guardrails System"""
    
    # Initialize guardrails
    guardrails = AIGuardrails("postgresql://user:password@localhost/legalops")
    
    # Example request validation
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    prompt = "Help me prepare my LLC operating agreement"
    context = {"user_services": ["business_formation"], "business_type": "llc"}
    
    result = guardrails.validate_request(user_id, prompt, context, "service_delivery")
    
    if result.allowed:
        print(f"✅ Request approved: {result.reason}")
        print(f"💰 Estimated cost: ${result.cost_estimate:.4f}")
        print(f"🔢 Estimated tokens: {result.tokens_used}")
        
        # Log successful usage
        guardrails.log_usage(user_id, "service_delivery", "prepare_document", 
                           result.tokens_used, result.cost_estimate)
    else:
        print(f"❌ Request blocked: {result.reason}")
        print(f"🚨 Action taken: {result.action_taken.value}")
        print(f"⚠️ Severity: {result.severity.value}")

if __name__ == "__main__":
    main()
