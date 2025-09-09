#!/usr/bin/env python3
"""
Delivery System Manager for Legal Ops Platform
Manages employee workflows, task assignment, and quality control
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class WorkflowStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    task_id: str
    workflow_instance_id: str
    assigned_to: str
    task_type: str
    task_description: str
    priority: TaskPriority
    status: TaskStatus
    due_date: datetime
    time_spent: int = 0
    created_at: datetime = None

@dataclass
class WorkflowInstance:
    workflow_id: str
    user_id: str
    service_id: str
    current_stage: str
    status: WorkflowStatus
    assigned_to: str = None
    started_at: datetime = None
    completed_at: datetime = None

class DeliverySystemManager:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    # Workflow Management
    def create_workflow_instance(self, user_id: str, service_id: str, 
                               workflow_template_id: str) -> str:
        """Create a new workflow instance"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO workflow_instances 
                        (workflow_template_id, user_id, current_stage, status)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (workflow_template_id, user_id, "initiation", "active"))
                    
                    workflow_id = cursor.fetchone()["id"]
                    
                    # Create initial tasks
                    self._create_initial_tasks(workflow_id, service_id)
                    
                    logger.info(f"Workflow instance {workflow_id} created for user {user_id}")
                    return workflow_id
                    
        except Exception as e:
            logger.error(f"Error creating workflow instance: {e}")
            return None
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status and progress"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT wi.*, u.email as user_email, s.name as service_name
                        FROM workflow_instances wi
                        JOIN users u ON wi.user_id = u.id
                        JOIN services s ON wi.service_id = s.id
                        WHERE wi.id = %s
                    """, (workflow_id,))
                    
                    workflow = cursor.fetchone()
                    if not workflow:
                        return {"error": "Workflow not found"}
                    
                    # Get tasks for this workflow
                    cursor.execute("""
                        SELECT et.*, u.email as assigned_to_email
                        FROM employee_tasks et
                        LEFT JOIN users u ON et.assigned_to = u.id
                        WHERE et.workflow_instance_id = %s
                        ORDER BY et.created_at
                    """, (workflow_id,))
                    
                    tasks = [dict(row) for row in cursor.fetchall()]
                    
                    # Calculate progress
                    total_tasks = len(tasks)
                    completed_tasks = len([t for t in tasks if t["status"] == "completed"])
                    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                    
                    return {
                        "workflow_id": workflow_id,
                        "user_email": workflow["user_email"],
                        "service_name": workflow["service_name"],
                        "current_stage": workflow["current_stage"],
                        "status": workflow["status"],
                        "progress_percentage": progress_percentage,
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "tasks": tasks,
                        "started_at": workflow["started_at"],
                        "estimated_completion": self._estimate_completion(workflow_id)
                    }
                    
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"error": str(e)}
    
    def assign_workflow(self, workflow_id: str, employee_id: str) -> bool:
        """Assign workflow to an employee"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE workflow_instances 
                        SET assigned_to = %s
                        WHERE id = %s
                    """, (employee_id, workflow_id))
                    
                    # Assign all pending tasks to the employee
                    cursor.execute("""
                        UPDATE employee_tasks 
                        SET assigned_to = %s
                        WHERE workflow_instance_id = %s AND status = 'pending'
                    """, (employee_id, workflow_id))
                    
                    logger.info(f"Workflow {workflow_id} assigned to employee {employee_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error assigning workflow: {e}")
            return False
    
    # Task Management
    def create_task(self, workflow_instance_id: str, task_type: str, 
                   task_description: str, priority: TaskPriority = TaskPriority.MEDIUM,
                   due_date: datetime = None) -> str:
        """Create a new task"""
        try:
            if not due_date:
                due_date = datetime.now() + timedelta(days=3)  # Default 3 days
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO employee_tasks 
                        (workflow_instance_id, task_type, task_description, 
                         priority, due_date, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        workflow_instance_id, task_type, task_description,
                        priority.value, due_date, TaskStatus.PENDING.value
                    ))
                    
                    task_id = cursor.fetchone()["id"]
                    logger.info(f"Task {task_id} created")
                    return task_id
                    
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def assign_task(self, task_id: str, employee_id: str) -> bool:
        """Assign task to an employee"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE employee_tasks 
                        SET assigned_to = %s, status = %s
                        WHERE id = %s
                    """, (employee_id, TaskStatus.IN_PROGRESS.value, task_id))
                    
                    logger.info(f"Task {task_id} assigned to employee {employee_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return False
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          time_spent: int = 0, notes: str = None) -> bool:
        """Update task status"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    update_data = {
                        "status": status.value,
                        "time_spent": time_spent
                    }
                    
                    if status == TaskStatus.COMPLETED:
                        update_data["completed_at"] = datetime.now()
                    
                    cursor.execute("""
                        UPDATE employee_tasks 
                        SET status = %s, time_spent = %s, completed_at = %s
                        WHERE id = %s
                    """, (
                        status.value, time_spent, 
                        datetime.now() if status == TaskStatus.COMPLETED else None,
                        task_id
                    ))
                    
                    # If task is completed, check if workflow is complete
                    if status == TaskStatus.COMPLETED:
                        self._check_workflow_completion(task_id)
                    
                    logger.info(f"Task {task_id} status updated to {status.value}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False
    
    def get_employee_tasks(self, employee_id: str, status: TaskStatus = None) -> List[Dict[str, Any]]:
        """Get tasks assigned to an employee"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT et.*, wi.user_id, u.email as user_email, s.name as service_name
                        FROM employee_tasks et
                        JOIN workflow_instances wi ON et.workflow_instance_id = wi.id
                        JOIN users u ON wi.user_id = u.id
                        JOIN services s ON wi.service_id = s.id
                        WHERE et.assigned_to = %s
                    """
                    params = [employee_id]
                    
                    if status:
                        query += " AND et.status = %s"
                        params.append(status.value)
                    
                    query += " ORDER BY et.priority DESC, et.due_date ASC"
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting employee tasks: {e}")
            return []
    
    def get_task_queue(self, employee_id: str) -> Dict[str, Any]:
        """Get employee's task queue with priorities"""
        try:
            tasks = self.get_employee_tasks(employee_id)
            
            # Group tasks by priority
            task_queue = {
                "urgent": [],
                "high": [],
                "medium": [],
                "low": []
            }
            
            for task in tasks:
                priority = task["priority"].lower()
                if priority in task_queue:
                    task_queue[priority].append(task)
            
            # Calculate workload
            total_tasks = len(tasks)
            pending_tasks = len([t for t in tasks if t["status"] == "pending"])
            in_progress_tasks = len([t for t in tasks if t["status"] == "in_progress"])
            overdue_tasks = len([t for t in tasks if t["due_date"] and t["due_date"] < datetime.now() and t["status"] != "completed"])
            
            return {
                "task_queue": task_queue,
                "workload_summary": {
                    "total_tasks": total_tasks,
                    "pending_tasks": pending_tasks,
                    "in_progress_tasks": in_progress_tasks,
                    "overdue_tasks": overdue_tasks
                },
                "employee_id": employee_id
            }
            
        except Exception as e:
            logger.error(f"Error getting task queue: {e}")
            return {}
    
    # Quality Control
    def create_quality_review(self, task_id: str, reviewer_id: str, 
                            review_type: str = "final") -> str:
        """Create a quality review for a task"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO quality_reviews 
                        (task_id, reviewer_id, review_type, review_status)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (task_id, reviewer_id, review_type, "pending"))
                    
                    review_id = cursor.fetchone()["id"]
                    logger.info(f"Quality review {review_id} created for task {task_id}")
                    return review_id
                    
        except Exception as e:
            logger.error(f"Error creating quality review: {e}")
            return None
    
    def complete_quality_review(self, review_id: str, quality_score: int, 
                              approved: bool, review_notes: str = None) -> bool:
        """Complete a quality review"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE quality_reviews 
                        SET review_status = %s, quality_score = %s, 
                            approved = %s, review_notes = %s, reviewed_at = NOW()
                        WHERE id = %s
                    """, ("completed", quality_score, approved, review_notes, review_id))
                    
                    # Get task ID to update task status
                    cursor.execute("""
                        SELECT task_id FROM quality_reviews WHERE id = %s
                    """, (review_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        task_id = result["task_id"]
                        
                        # Update task status based on review
                        new_status = TaskStatus.APPROVED.value if approved else TaskStatus.REJECTED.value
                        cursor.execute("""
                            UPDATE employee_tasks 
                            SET status = %s
                            WHERE id = %s
                        """, (new_status, task_id))
                    
                    logger.info(f"Quality review {review_id} completed")
                    return True
                    
        except Exception as e:
            logger.error(f"Error completing quality review: {e}")
            return False
    
    def get_quality_metrics(self, employee_id: str = None, 
                          period_days: int = 30) -> Dict[str, Any]:
        """Get quality control metrics"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Base query for quality reviews
                    base_query = """
                        SELECT qr.*, et.assigned_to, et.task_type
                        FROM quality_reviews qr
                        JOIN employee_tasks et ON qr.task_id = et.id
                        WHERE qr.reviewed_at >= %s
                    """
                    params = [datetime.now() - timedelta(days=period_days)]
                    
                    if employee_id:
                        base_query += " AND et.assigned_to = %s"
                        params.append(employee_id)
                    
                    cursor.execute(base_query, params)
                    reviews = [dict(row) for row in cursor.fetchall()]
                    
                    if not reviews:
                        return {"error": "No quality reviews found"}
                    
                    # Calculate metrics
                    total_reviews = len(reviews)
                    approved_reviews = len([r for r in reviews if r["approved"]])
                    average_score = sum(r["quality_score"] for r in reviews if r["quality_score"]) / total_reviews
                    
                    # Group by task type
                    task_type_metrics = {}
                    for review in reviews:
                        task_type = review["task_type"]
                        if task_type not in task_type_metrics:
                            task_type_metrics[task_type] = {
                                "total": 0,
                                "approved": 0,
                                "scores": []
                            }
                        
                        task_type_metrics[task_type]["total"] += 1
                        if review["approved"]:
                            task_type_metrics[task_type]["approved"] += 1
                        if review["quality_score"]:
                            task_type_metrics[task_type]["scores"].append(review["quality_score"])
                    
                    # Calculate approval rates by task type
                    for task_type, metrics in task_type_metrics.items():
                        metrics["approval_rate"] = (metrics["approved"] / metrics["total"] * 100) if metrics["total"] > 0 else 0
                        metrics["average_score"] = sum(metrics["scores"]) / len(metrics["scores"]) if metrics["scores"] else 0
                    
                    return {
                        "total_reviews": total_reviews,
                        "approval_rate": (approved_reviews / total_reviews * 100) if total_reviews > 0 else 0,
                        "average_quality_score": average_score,
                        "task_type_metrics": task_type_metrics,
                        "period_days": period_days
                    }
                    
        except Exception as e:
            logger.error(f"Error getting quality metrics: {e}")
            return {"error": str(e)}
    
    # Performance Tracking
    def track_employee_performance(self, employee_id: str, 
                                 period_start: date, period_end: date) -> Dict[str, Any]:
        """Track employee performance for a period"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get completed tasks
                    cursor.execute("""
                        SELECT COUNT(*) as tasks_completed,
                               AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/60) as avg_completion_time
                        FROM employee_tasks 
                        WHERE assigned_to = %s 
                        AND completed_at BETWEEN %s AND %s
                        AND status = 'completed'
                    """, (employee_id, period_start, period_end))
                    
                    task_metrics = cursor.fetchone()
                    
                    # Get quality scores
                    cursor.execute("""
                        SELECT AVG(qr.quality_score) as avg_quality_score
                        FROM quality_reviews qr
                        JOIN employee_tasks et ON qr.task_id = et.id
                        WHERE et.assigned_to = %s 
                        AND qr.reviewed_at BETWEEN %s AND %s
                        AND qr.approved = true
                    """, (employee_id, period_start, period_end))
                    
                    quality_metrics = cursor.fetchone()
                    
                    # Get customer satisfaction (if available)
                    cursor.execute("""
                        SELECT AVG(feedback_score) as avg_satisfaction
                        FROM user_feedback 
                        WHERE employee_id = %s 
                        AND created_at BETWEEN %s AND %s
                    """, (employee_id, period_start, period_end))
                    
                    satisfaction_metrics = cursor.fetchone()
                    
                    # Store performance data
                    cursor.execute("""
                        INSERT INTO employee_performance 
                        (employee_id, metric_period, tasks_completed, 
                         average_quality_score, average_completion_time, 
                         customer_satisfaction, period_start, period_end)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (employee_id, period_start, period_end) 
                        DO UPDATE SET 
                            tasks_completed = %s,
                            average_quality_score = %s,
                            average_completion_time = %s,
                            customer_satisfaction = %s
                    """, (
                        employee_id, "monthly",
                        task_metrics["tasks_completed"] or 0,
                        quality_metrics["avg_quality_score"] or 0,
                        task_metrics["avg_completion_time"] or 0,
                        satisfaction_metrics["avg_satisfaction"] or 0,
                        period_start, period_end,
                        task_metrics["tasks_completed"] or 0,
                        quality_metrics["avg_quality_score"] or 0,
                        task_metrics["avg_completion_time"] or 0,
                        satisfaction_metrics["avg_satisfaction"] or 0
                    ))
                    
                    return {
                        "employee_id": employee_id,
                        "period_start": period_start,
                        "period_end": period_end,
                        "tasks_completed": task_metrics["tasks_completed"] or 0,
                        "average_quality_score": quality_metrics["avg_quality_score"] or 0,
                        "average_completion_time": task_metrics["avg_completion_time"] or 0,
                        "customer_satisfaction": satisfaction_metrics["avg_satisfaction"] or 0
                    }
                    
        except Exception as e:
            logger.error(f"Error tracking employee performance: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    def _create_initial_tasks(self, workflow_id: str, service_id: str):
        """Create initial tasks for a workflow"""
        try:
            # Get service-specific task templates
            task_templates = self._get_task_templates(service_id)
            
            for template in task_templates:
                self.create_task(
                    workflow_id,
                    template["task_type"],
                    template["description"],
                    TaskPriority(template.get("priority", "medium")),
                    datetime.now() + timedelta(days=template.get("due_days", 3))
                )
                
        except Exception as e:
            logger.error(f"Error creating initial tasks: {e}")
    
    def _get_task_templates(self, service_id: str) -> List[Dict[str, Any]]:
        """Get task templates for a service"""
        # In a real implementation, this would query the database
        # For now, return default templates
        return [
            {
                "task_type": "document_review",
                "description": "Review and prepare required documents",
                "priority": "high",
                "due_days": 2
            },
            {
                "task_type": "application_submission",
                "description": "Submit application to appropriate agency",
                "priority": "high",
                "due_days": 3
            },
            {
                "task_type": "follow_up",
                "description": "Follow up on application status",
                "priority": "medium",
                "due_days": 5
            }
        ]
    
    def _check_workflow_completion(self, task_id: str):
        """Check if workflow is complete after task completion"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get workflow instance ID
                    cursor.execute("""
                        SELECT workflow_instance_id FROM employee_tasks WHERE id = %s
                    """, (task_id,))
                    
                    result = cursor.fetchone()
                    if not result:
                        return
                    
                    workflow_id = result["workflow_instance_id"]
                    
                    # Check if all tasks are completed
                    cursor.execute("""
                        SELECT COUNT(*) as total_tasks,
                               COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks
                        FROM employee_tasks 
                        WHERE workflow_instance_id = %s
                    """, (workflow_id,))
                    
                    task_counts = cursor.fetchone()
                    
                    if task_counts["total_tasks"] == task_counts["completed_tasks"]:
                        # Mark workflow as completed
                        cursor.execute("""
                            UPDATE workflow_instances 
                            SET status = %s, completed_at = NOW()
                            WHERE id = %s
                        """, ("completed", workflow_id))
                        
                        logger.info(f"Workflow {workflow_id} completed")
                        
        except Exception as e:
            logger.error(f"Error checking workflow completion: {e}")
    
    def _estimate_completion(self, workflow_id: str) -> datetime:
        """Estimate workflow completion time"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/3600) as avg_hours
                        FROM employee_tasks 
                        WHERE workflow_instance_id = %s AND status = 'completed'
                    """, (workflow_id,))
                    
                    result = cursor.fetchone()
                    if result and result["avg_hours"]:
                        avg_hours = result["avg_hours"]
                        return datetime.now() + timedelta(hours=avg_hours)
                    
                    return datetime.now() + timedelta(days=7)  # Default estimate
                    
        except Exception as e:
            logger.error(f"Error estimating completion: {e}")
            return datetime.now() + timedelta(days=7)

def main():
    """Example usage of Delivery System Manager"""
    
    # Initialize delivery system manager
    delivery_manager = DeliverySystemManager("postgresql://user:password@localhost/legalops")
    
    # Example: Create workflow instance
    workflow_id = delivery_manager.create_workflow_instance(
        "user123", "service456", "template789"
    )
    print(f"Workflow created: {workflow_id}")
    
    # Example: Assign workflow to employee
    success = delivery_manager.assign_workflow(workflow_id, "employee123")
    print(f"Workflow assigned: {success}")
    
    # Example: Get employee task queue
    task_queue = delivery_manager.get_task_queue("employee123")
    print(f"Task queue: {task_queue}")
    
    # Example: Get quality metrics
    quality_metrics = delivery_manager.get_quality_metrics("employee123")
    print(f"Quality metrics: {quality_metrics}")

if __name__ == "__main__":
    main()
