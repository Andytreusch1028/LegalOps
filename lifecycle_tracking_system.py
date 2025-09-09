#!/usr/bin/env python3
"""
Lifecycle Tracking System for Legal Ops Platform
Tracks product/service lifecycle from lead to completion
"""

import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LifecycleStage(Enum):
    LEAD_GENERATION = "lead_generation"
    LEAD_QUALIFICATION = "lead_qualification"
    SALES_PROCESS = "sales_process"
    ONBOARDING = "onboarding"
    SERVICE_DELIVERY = "service_delivery"
    QUALITY_REVIEW = "quality_review"
    COMPLETION = "completion"
    HANDOFF = "handoff"
    ONGOING_SUPPORT = "ongoing_support"

class LifecycleStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

@dataclass
class LifecycleEvent:
    event_type: str
    event_data: Dict[str, Any]
    triggered_by: str = None
    timestamp: datetime = None

class LifecycleTrackingSystem:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    # Lifecycle Management
    def create_lifecycle(self, user_id: str, service_id: str, 
                        initial_stage: LifecycleStage = LifecycleStage.LEAD_GENERATION) -> str:
        """Create a new service lifecycle"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO service_lifecycle 
                        (user_id, service_id, current_stage, stage_data)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (
                        user_id, service_id, initial_stage.value, 
                        json.dumps({"created_at": datetime.now().isoformat()})
                    ))
                    
                    lifecycle_id = cursor.fetchone()["id"]
                    
                    # Log initial event
                    self._log_lifecycle_event(
                        lifecycle_id, "lifecycle_created", 
                        {"stage": initial_stage.value}, None
                    )
                    
                    logger.info(f"Lifecycle {lifecycle_id} created for user {user_id}")
                    return lifecycle_id
                    
        except Exception as e:
            logger.error(f"Error creating lifecycle: {e}")
            return None
    
    def update_lifecycle_stage(self, lifecycle_id: str, new_stage: LifecycleStage, 
                              stage_data: Dict[str, Any] = None, 
                              triggered_by: str = None) -> bool:
        """Update lifecycle stage"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get current stage
                    cursor.execute("""
                        SELECT current_stage, stage_data FROM service_lifecycle 
                        WHERE id = %s
                    """, (lifecycle_id,))
                    
                    result = cursor.fetchone()
                    if not result:
                        return False
                    
                    current_stage = result["current_stage"]
                    existing_data = json.loads(result["stage_data"]) if result["stage_data"] else {}
                    
                    # Update stage data
                    if stage_data:
                        existing_data.update(stage_data)
                    
                    # Add stage transition info
                    existing_data["stage_transitions"] = existing_data.get("stage_transitions", [])
                    existing_data["stage_transitions"].append({
                        "from_stage": current_stage,
                        "to_stage": new_stage.value,
                        "timestamp": datetime.now().isoformat(),
                        "triggered_by": triggered_by
                    })
                    
                    # Update lifecycle
                    cursor.execute("""
                        UPDATE service_lifecycle 
                        SET current_stage = %s, stage_data = %s
                        WHERE id = %s
                    """, (new_stage.value, json.dumps(existing_data), lifecycle_id))
                    
                    # Log stage transition event
                    self._log_lifecycle_event(
                        lifecycle_id, "stage_transition",
                        {
                            "from_stage": current_stage,
                            "to_stage": new_stage.value,
                            "stage_data": stage_data
                        },
                        triggered_by
                    )
                    
                    logger.info(f"Lifecycle {lifecycle_id} moved from {current_stage} to {new_stage.value}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating lifecycle stage: {e}")
            return False
    
    def get_lifecycle_status(self, lifecycle_id: str) -> Dict[str, Any]:
        """Get lifecycle status and progress"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT sl.*, u.email as user_email, s.name as service_name
                        FROM service_lifecycle sl
                        JOIN users u ON sl.user_id = u.id
                        JOIN services s ON sl.service_id = s.id
                        WHERE sl.id = %s
                    """, (lifecycle_id,))
                    
                    lifecycle = cursor.fetchone()
                    if not lifecycle:
                        return {"error": "Lifecycle not found"}
                    
                    # Get lifecycle events
                    cursor.execute("""
                        SELECT * FROM lifecycle_events 
                        WHERE lifecycle_id = %s
                        ORDER BY created_at DESC
                        LIMIT 10
                    """, (lifecycle_id,))
                    
                    recent_events = [dict(row) for row in cursor.fetchall()]
                    
                    # Calculate progress
                    stage_data = json.loads(lifecycle["stage_data"]) if lifecycle["stage_data"] else {}
                    progress_percentage = self._calculate_progress(lifecycle["current_stage"])
                    
                    # Get estimated completion
                    estimated_completion = self._estimate_completion(lifecycle_id)
                    
                    return {
                        "lifecycle_id": lifecycle_id,
                        "user_email": lifecycle["user_email"],
                        "service_name": lifecycle["service_name"],
                        "current_stage": lifecycle["current_stage"],
                        "progress_percentage": progress_percentage,
                        "stage_data": stage_data,
                        "recent_events": recent_events,
                        "started_at": lifecycle["started_at"],
                        "estimated_completion": estimated_completion,
                        "is_completed": lifecycle["completed_at"] is not None
                    }
                    
        except Exception as e:
            logger.error(f"Error getting lifecycle status: {e}")
            return {"error": str(e)}
    
    def get_user_lifecycles(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all lifecycles for a user"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT sl.*, s.name as service_name, s.category as service_category
                        FROM service_lifecycle sl
                        JOIN services s ON sl.service_id = s.id
                        WHERE sl.user_id = %s
                        ORDER BY sl.created_at DESC
                    """, (user_id,))
                    
                    lifecycles = []
                    for row in cursor.fetchall():
                        lifecycle = dict(row)
                        lifecycle["progress_percentage"] = self._calculate_progress(lifecycle["current_stage"])
                        lifecycles.append(lifecycle)
                    
                    return lifecycles
                    
        except Exception as e:
            logger.error(f"Error getting user lifecycles: {e}")
            return []
    
    # Event Tracking
    def log_lifecycle_event(self, lifecycle_id: str, event_type: str, 
                           event_data: Dict[str, Any], triggered_by: str = None) -> str:
        """Log a lifecycle event"""
        return self._log_lifecycle_event(lifecycle_id, event_type, event_data, triggered_by)
    
    def _log_lifecycle_event(self, lifecycle_id: str, event_type: str, 
                            event_data: Dict[str, Any], triggered_by: str = None) -> str:
        """Internal method to log lifecycle event"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO lifecycle_events 
                        (lifecycle_id, event_type, event_data, triggered_by)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (
                        lifecycle_id, event_type, json.dumps(event_data), triggered_by
                    ))
                    
                    event_id = cursor.fetchone()["id"]
                    logger.info(f"Lifecycle event {event_id} logged for lifecycle {lifecycle_id}")
                    return event_id
                    
        except Exception as e:
            logger.error(f"Error logging lifecycle event: {e}")
            return None
    
    def get_lifecycle_events(self, lifecycle_id: str, 
                           event_type: str = None) -> List[Dict[str, Any]]:
        """Get lifecycle events"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT le.*, u.email as triggered_by_email
                        FROM lifecycle_events le
                        LEFT JOIN users u ON le.triggered_by = u.id
                        WHERE le.lifecycle_id = %s
                    """
                    params = [lifecycle_id]
                    
                    if event_type:
                        query += " AND le.event_type = %s"
                        params.append(event_type)
                    
                    query += " ORDER BY le.created_at DESC"
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting lifecycle events: {e}")
            return []
    
    # Analytics and Reporting
    def get_lifecycle_analytics(self, service_id: str = None, 
                              period_days: int = 30) -> Dict[str, Any]:
        """Get lifecycle analytics"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Base query
                    base_query = """
                        SELECT sl.*, s.name as service_name
                        FROM service_lifecycle sl
                        JOIN services s ON sl.service_id = s.id
                        WHERE sl.created_at >= %s
                    """
                    params = [datetime.now() - timedelta(days=period_days)]
                    
                    if service_id:
                        base_query += " AND sl.service_id = %s"
                        params.append(service_id)
                    
                    cursor.execute(base_query, params)
                    lifecycles = [dict(row) for row in cursor.fetchall()]
                    
                    if not lifecycles:
                        return {"error": "No lifecycles found"}
                    
                    # Calculate metrics
                    total_lifecycles = len(lifecycles)
                    completed_lifecycles = len([l for l in lifecycles if l["completed_at"]])
                    completion_rate = (completed_lifecycles / total_lifecycles * 100) if total_lifecycles > 0 else 0
                    
                    # Average time to completion
                    completed_times = []
                    for lifecycle in lifecycles:
                        if lifecycle["completed_at"]:
                            duration = lifecycle["completed_at"] - lifecycle["started_at"]
                            completed_times.append(duration.total_seconds() / 3600)  # hours
                    
                    avg_completion_time = sum(completed_times) / len(completed_times) if completed_times else 0
                    
                    # Stage distribution
                    stage_distribution = {}
                    for lifecycle in lifecycles:
                        stage = lifecycle["current_stage"]
                        stage_distribution[stage] = stage_distribution.get(stage, 0) + 1
                    
                    # Service breakdown
                    service_breakdown = {}
                    for lifecycle in lifecycles:
                        service_name = lifecycle["service_name"]
                        if service_name not in service_breakdown:
                            service_breakdown[service_name] = {
                                "total": 0,
                                "completed": 0,
                                "avg_time": 0
                            }
                        
                        service_breakdown[service_name]["total"] += 1
                        if lifecycle["completed_at"]:
                            service_breakdown[service_name]["completed"] += 1
                    
                    # Calculate completion rates by service
                    for service_name, metrics in service_breakdown.items():
                        metrics["completion_rate"] = (metrics["completed"] / metrics["total"] * 100) if metrics["total"] > 0 else 0
                    
                    return {
                        "total_lifecycles": total_lifecycles,
                        "completed_lifecycles": completed_lifecycles,
                        "completion_rate": completion_rate,
                        "average_completion_time_hours": avg_completion_time,
                        "stage_distribution": stage_distribution,
                        "service_breakdown": service_breakdown,
                        "period_days": period_days
                    }
                    
        except Exception as e:
            logger.error(f"Error getting lifecycle analytics: {e}")
            return {"error": str(e)}
    
    def get_stage_performance_metrics(self, stage: LifecycleStage, 
                                    period_days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific stage"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get lifecycles in this stage
                    cursor.execute("""
                        SELECT sl.*, s.name as service_name
                        FROM service_lifecycle sl
                        JOIN services s ON sl.service_id = s.id
                        WHERE sl.current_stage = %s
                        AND sl.created_at >= %s
                    """, (stage.value, datetime.now() - timedelta(days=period_days)))
                    
                    lifecycles = [dict(row) for row in cursor.fetchall()]
                    
                    if not lifecycles:
                        return {"error": f"No lifecycles found in stage {stage.value}"}
                    
                    # Calculate stage duration
                    stage_durations = []
                    for lifecycle in lifecycles:
                        stage_data = json.loads(lifecycle["stage_data"]) if lifecycle["stage_data"] else {}
                        transitions = stage_data.get("stage_transitions", [])
                        
                        # Find when this stage started
                        stage_start = None
                        for transition in transitions:
                            if transition["to_stage"] == stage.value:
                                stage_start = datetime.fromisoformat(transition["timestamp"])
                                break
                        
                        if stage_start:
                            if lifecycle["completed_at"]:
                                duration = lifecycle["completed_at"] - stage_start
                            else:
                                duration = datetime.now() - stage_start
                            
                            stage_durations.append(duration.total_seconds() / 3600)  # hours
                    
                    avg_stage_duration = sum(stage_durations) / len(stage_durations) if stage_durations else 0
                    
                    # Get bottlenecks (lifecycles stuck in this stage)
                    stuck_threshold = avg_stage_duration * 2  # 2x average duration
                    stuck_lifecycles = [d for d in stage_durations if d > stuck_threshold]
                    
                    return {
                        "stage": stage.value,
                        "total_lifecycles": len(lifecycles),
                        "average_duration_hours": avg_stage_duration,
                        "stuck_lifecycles": len(stuck_lifecycles),
                        "bottleneck_percentage": (len(stuck_lifecycles) / len(lifecycles) * 100) if lifecycles else 0,
                        "period_days": period_days
                    }
                    
        except Exception as e:
            logger.error(f"Error getting stage performance metrics: {e}")
            return {"error": str(e)}
    
    # Delivery Metrics
    def record_delivery_metric(self, service_id: str, metric_name: str, 
                              metric_value: float, metric_unit: str = None) -> bool:
        """Record a service delivery metric"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO service_delivery_metrics 
                        (service_id, metric_name, metric_value, metric_unit)
                        VALUES (%s, %s, %s, %s)
                    """, (service_id, metric_name, metric_value, metric_unit))
                    
                    logger.info(f"Delivery metric recorded: {metric_name} = {metric_value}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error recording delivery metric: {e}")
            return False
    
    def get_delivery_metrics(self, service_id: str = None, 
                           metric_name: str = None,
                           period_days: int = 30) -> List[Dict[str, Any]]:
        """Get service delivery metrics"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT sdm.*, s.name as service_name
                        FROM service_delivery_metrics sdm
                        JOIN services s ON sdm.service_id = s.id
                        WHERE sdm.measurement_date >= %s
                    """
                    params = [date.today() - timedelta(days=period_days)]
                    
                    if service_id:
                        query += " AND sdm.service_id = %s"
                        params.append(service_id)
                    
                    if metric_name:
                        query += " AND sdm.metric_name = %s"
                        params.append(metric_name)
                    
                    query += " ORDER BY sdm.measurement_date DESC, sdm.created_at DESC"
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting delivery metrics: {e}")
            return []
    
    # Private helper methods
    def _calculate_progress(self, current_stage: str) -> int:
        """Calculate progress percentage based on current stage"""
        stage_progress = {
            "lead_generation": 10,
            "lead_qualification": 20,
            "sales_process": 30,
            "onboarding": 40,
            "service_delivery": 60,
            "quality_review": 80,
            "completion": 90,
            "handoff": 95,
            "ongoing_support": 100
        }
        
        return stage_progress.get(current_stage, 0)
    
    def _estimate_completion(self, lifecycle_id: str) -> datetime:
        """Estimate lifecycle completion time"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get average completion time for similar lifecycles
                    cursor.execute("""
                        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - started_at))/3600) as avg_hours
                        FROM service_lifecycle 
                        WHERE service_id = (
                            SELECT service_id FROM service_lifecycle WHERE id = %s
                        )
                        AND completed_at IS NOT NULL
                    """, (lifecycle_id,))
                    
                    result = cursor.fetchone()
                    if result and result["avg_hours"]:
                        avg_hours = result["avg_hours"]
                        return datetime.now() + timedelta(hours=avg_hours)
                    
                    return datetime.now() + timedelta(days=14)  # Default estimate
                    
        except Exception as e:
            logger.error(f"Error estimating completion: {e}")
            return datetime.now() + timedelta(days=14)

def main():
    """Example usage of Lifecycle Tracking System"""
    
    # Initialize lifecycle tracking system
    lifecycle_tracker = LifecycleTrackingSystem("postgresql://user:password@localhost/legalops")
    
    # Example: Create lifecycle
    lifecycle_id = lifecycle_tracker.create_lifecycle(
        "user123", "service456", LifecycleStage.LEAD_GENERATION
    )
    print(f"Lifecycle created: {lifecycle_id}")
    
    # Example: Update stage
    success = lifecycle_tracker.update_lifecycle_stage(
        lifecycle_id, LifecycleStage.SERVICE_DELIVERY, 
        {"assigned_to": "employee123"}, "admin456"
    )
    print(f"Stage updated: {success}")
    
    # Example: Get lifecycle status
    status = lifecycle_tracker.get_lifecycle_status(lifecycle_id)
    print(f"Lifecycle status: {status}")
    
    # Example: Get analytics
    analytics = lifecycle_tracker.get_lifecycle_analytics(period_days=30)
    print(f"Analytics: {analytics}")

if __name__ == "__main__":
    main()
