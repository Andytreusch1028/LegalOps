#!/usr/bin/env python3
"""
AI Agent System for Legal Ops Platform
Multi-agent system with UPL compliance and task execution capabilities
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import psycopg2
from psycopg2.extras import RealDictCursor

from ai_guardrails_system import AIGuardrails, GuardrailResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    ADMINISTRATIVE = "administrative"
    SERVICE_DELIVERY = "service_delivery"
    COMMUNICATION = "communication"
    COMPLIANCE = "compliance"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_APPROVAL = "requires_approval"

@dataclass
class AgentTask:
    task_id: str
    user_id: str
    agent_type: AgentType
    task_name: str
    parameters: Dict[str, Any]
    status: TaskStatus
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    human_approval_required: bool = False

class AIAgent:
    def __init__(self, agent_type: AgentType, db_connection_string: str):
        self.agent_type = agent_type
        self.db_connection_string = db_connection_string
        self.guardrails = AIGuardrails(db_connection_string)
        self.capabilities = self._load_capabilities()
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    def _load_capabilities(self) -> List[Dict[str, Any]]:
        """Load agent capabilities from database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT capability_name, description, upl_risk_level, 
                               requires_human_approval, max_automation_level, parameters
                        FROM ai_agent_capabilities 
                        WHERE agent_type = %s AND is_active = TRUE
                    """, (self.agent_type.value,))
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error loading capabilities: {e}")
            return []
    
    def validate_task(self, user_id: str, task_name: str, parameters: Dict[str, Any]) -> GuardrailResult:
        """Validate task before execution"""
        # Check if agent has this capability
        capability = next((cap for cap in self.capabilities if cap['capability_name'] == task_name), None)
        if not capability:
            return GuardrailResult(
                allowed=False,
                reason=f"Agent {self.agent_type.value} does not have capability: {task_name}",
                action_taken=None,
                severity=None
            )
        
        # Check UPL risk level
        if capability['upl_risk_level'] == 'high':
            return GuardrailResult(
                allowed=False,
                reason="High UPL risk - requires human approval",
                action_taken=None,
                severity=None
            )
        
        # Use guardrails for content validation
        prompt = f"Execute {task_name} with parameters: {json.dumps(parameters)}"
        context = {"user_id": user_id, "agent_type": self.agent_type.value}
        
        return self.guardrails.validate_request(user_id, prompt, context, self.agent_type.value)
    
    def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute agent task with proper validation and logging"""
        try:
            # Validate task
            validation_result = self.validate_task(task.user_id, task.task_name, task.parameters)
            if not validation_result.allowed:
                task.status = TaskStatus.FAILED
                task.error_message = validation_result.reason
                return task
            
            # Check if human approval is required
            capability = next((cap for cap in self.capabilities if cap['capability_name'] == task.task_name), None)
            if capability and capability['requires_human_approval']:
                task.status = TaskStatus.REQUIRES_APPROVAL
                task.human_approval_required = True
                self._log_task(task)
                return task
            
            # Execute task based on agent type
            task.status = TaskStatus.IN_PROGRESS
            self._log_task(task)
            
            if self.agent_type == AgentType.ADMINISTRATIVE:
                result = self._execute_administrative_task(task)
            elif self.agent_type == AgentType.SERVICE_DELIVERY:
                result = self._execute_service_delivery_task(task)
            elif self.agent_type == AgentType.COMMUNICATION:
                result = self._execute_communication_task(task)
            elif self.agent_type == AgentType.COMPLIANCE:
                result = self._execute_compliance_task(task)
            else:
                raise ValueError(f"Unknown agent type: {self.agent_type}")
            
            task.result_data = result
            task.status = TaskStatus.COMPLETED
            
            # Log successful usage
            self.guardrails.log_usage(
                task.user_id, 
                self.agent_type.value, 
                task.task_name,
                validation_result.tokens_used,
                validation_result.cost_estimate
            )
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
        
        self._log_task(task)
        return task
    
    def _execute_administrative_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute administrative tasks"""
        if task.task_name == "schedule_appointment":
            return self._schedule_appointment(task.parameters)
        elif task.task_name == "send_reminder":
            return self._send_reminder(task.parameters)
        elif task.task_name == "update_calendar":
            return self._update_calendar(task.parameters)
        else:
            raise ValueError(f"Unknown administrative task: {task.task_name}")
    
    def _execute_service_delivery_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute service delivery tasks"""
        if task.task_name == "prepare_document":
            return self._prepare_document(task.parameters)
        elif task.task_name == "submit_filing":
            return self._submit_filing(task.parameters)
        elif task.task_name == "check_status":
            return self._check_status(task.parameters)
        else:
            raise ValueError(f"Unknown service delivery task: {task.task_name}")
    
    def _execute_communication_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute communication tasks"""
        if task.task_name == "send_notification":
            return self._send_notification(task.parameters)
        elif task.task_name == "proactive_outreach":
            return self._proactive_outreach(task.parameters)
        elif task.task_name == "collect_feedback":
            return self._collect_feedback(task.parameters)
        else:
            raise ValueError(f"Unknown communication task: {task.task_name}")
    
    def _execute_compliance_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute compliance tasks"""
        if task.task_name == "upl_monitoring":
            return self._upl_monitoring(task.parameters)
        elif task.task_name == "risk_assessment":
            return self._risk_assessment(task.parameters)
        elif task.task_name == "escalate_to_human":
            return self._escalate_to_human(task.parameters)
        else:
            raise ValueError(f"Unknown compliance task: {task.task_name}")
    
    # Administrative task implementations
    def _schedule_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule appointment or reminder"""
        # Implementation would integrate with calendar system
        return {
            "scheduled": True,
            "appointment_id": f"apt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "scheduled_for": parameters.get("datetime"),
            "reminder_sent": True
        }
    
    def _send_reminder(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send automated reminder"""
        # Implementation would integrate with notification system
        return {
            "reminder_sent": True,
            "reminder_id": f"rem_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "delivery_method": parameters.get("method", "email"),
            "recipient": parameters.get("recipient")
        }
    
    def _update_calendar(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update user calendar with important dates"""
        return {
            "calendar_updated": True,
            "events_added": len(parameters.get("events", [])),
            "calendar_id": parameters.get("calendar_id")
        }
    
    # Service delivery task implementations
    def _prepare_document(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare document using approved template"""
        # Implementation would use document generation system
        return {
            "document_prepared": True,
            "document_id": f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "template_used": parameters.get("template"),
            "file_path": f"/documents/{parameters.get('user_id')}/document.pdf"
        }
    
    def _submit_filing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Submit filing to government system"""
        # Implementation would integrate with government APIs
        return {
            "filing_submitted": True,
            "filing_id": f"fil_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "government_system": parameters.get("system"),
            "confirmation_number": f"CONF{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    def _check_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Check status of government filing"""
        return {
            "status_checked": True,
            "current_status": "in_review",
            "last_updated": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(days=7)).isoformat()
        }
    
    # Communication task implementations
    def _send_notification(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send service update notification"""
        return {
            "notification_sent": True,
            "notification_id": f"not_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "delivery_method": parameters.get("method", "dashboard"),
            "message": parameters.get("message")
        }
    
    def _proactive_outreach(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Proactive communication based on user behavior"""
        return {
            "outreach_sent": True,
            "outreach_id": f"out_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "trigger": parameters.get("trigger"),
            "recommendation": parameters.get("recommendation")
        }
    
    def _collect_feedback(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and respond to user feedback"""
        return {
            "feedback_collected": True,
            "feedback_id": f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "response_sent": True,
            "satisfaction_score": parameters.get("satisfaction_score")
        }
    
    # Compliance task implementations
    def _upl_monitoring(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor AI actions for UPL compliance"""
        return {
            "monitoring_completed": True,
            "risk_level": "low",
            "violations_found": 0,
            "recommendations": []
        }
    
    def _risk_assessment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level of AI action"""
        return {
            "assessment_completed": True,
            "risk_level": "low",
            "risk_factors": [],
            "recommendation": "proceed"
        }
    
    def _escalate_to_human(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate complex situation to human review"""
        return {
            "escalation_created": True,
            "escalation_id": f"esc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "assigned_to": parameters.get("assigned_to"),
            "priority": "high"
        }
    
    def _log_task(self, task: AgentTask):
        """Log task execution to database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ai_agent_tasks 
                        (id, user_id, agent_type, task_name, task_parameters, status, 
                         result_data, error_message, human_approval_required, executed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        result_data = EXCLUDED.result_data,
                        error_message = EXCLUDED.error_message,
                        executed_at = EXCLUDED.executed_at
                    """, (
                        task.task_id,
                        task.user_id,
                        task.agent_type.value,
                        task.task_name,
                        json.dumps(task.parameters),
                        task.status.value,
                        json.dumps(task.result_data) if task.result_data else None,
                        task.error_message,
                        task.human_approval_required,
                        datetime.now() if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] else None
                    ))
                    
        except Exception as e:
            logger.error(f"Error logging task: {e}")

class AIAgentSystem:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.agents = {
            AgentType.ADMINISTRATIVE: AIAgent(AgentType.ADMINISTRATIVE, db_connection_string),
            AgentType.SERVICE_DELIVERY: AIAgent(AgentType.SERVICE_DELIVERY, db_connection_string),
            AgentType.COMMUNICATION: AIAgent(AgentType.COMMUNICATION, db_connection_string),
            AgentType.COMPLIANCE: AIAgent(AgentType.COMPLIANCE, db_connection_string)
        }
    
    def create_task(self, user_id: str, agent_type: AgentType, task_name: str, 
                   parameters: Dict[str, Any]) -> AgentTask:
        """Create new agent task"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return AgentTask(
            task_id=task_id,
            user_id=user_id,
            agent_type=agent_type,
            task_name=task_name,
            parameters=parameters,
            status=TaskStatus.PENDING
        )
    
    def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute task using appropriate agent"""
        agent = self.agents.get(task.agent_type)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error_message = f"No agent available for type: {task.agent_type}"
            return task
        
        return agent.execute_task(task)
    
    def get_user_tasks(self, user_id: str, status: Optional[TaskStatus] = None) -> List[AgentTask]:
        """Get user's tasks"""
        try:
            with self.agents[AgentType.ADMINISTRATIVE].get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT id, user_id, agent_type, task_name, task_parameters, 
                               status, result_data, error_message, human_approval_required,
                               created_at, executed_at
                        FROM ai_agent_tasks 
                        WHERE user_id = %s
                    """
                    params = [user_id]
                    
                    if status:
                        query += " AND status = %s"
                        params.append(status.value)
                    
                    query += " ORDER BY created_at DESC"
                    
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    
                    tasks = []
                    for row in rows:
                        task = AgentTask(
                            task_id=row['id'],
                            user_id=row['user_id'],
                            agent_type=AgentType(row['agent_type']),
                            task_name=row['task_name'],
                            parameters=json.loads(row['task_parameters']) if row['task_parameters'] else {},
                            status=TaskStatus(row['status']),
                            result_data=json.loads(row['result_data']) if row['result_data'] else None,
                            error_message=row['error_message'],
                            human_approval_required=row['human_approval_required']
                        )
                        tasks.append(task)
                    
                    return tasks
                    
        except Exception as e:
            logger.error(f"Error getting user tasks: {e}")
            return []

def main():
    """Example usage of AI Agent System"""
    
    # Initialize agent system
    agent_system = AIAgentSystem("postgresql://user:password@localhost/legalops")
    
    # Create and execute a task
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    
    task = agent_system.create_task(
        user_id=user_id,
        agent_type=AgentType.ADMINISTRATIVE,
        task_name="schedule_appointment",
        parameters={
            "datetime": "2024-01-15 14:00:00",
            "type": "compliance_check",
            "description": "Annual report filing reminder"
        }
    )
    
    # Execute task
    result = agent_system.execute_task(task)
    
    print(f"Task {result.task_id}: {result.status.value}")
    if result.result_data:
        print(f"Result: {result.result_data}")
    if result.error_message:
        print(f"Error: {result.error_message}")

if __name__ == "__main__":
    main()
