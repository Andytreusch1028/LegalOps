#!/usr/bin/env python3
"""
Service Registry System for Legal Ops Platform
Manages dynamic service registration, dependencies, and lifecycle
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

class ServiceType(Enum):
    CORE = "core"
    ADDON = "addon"
    PLUGIN = "plugin"

class ServiceStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

@dataclass
class ServiceDefinition:
    service_key: str
    service_name: str
    service_category: str
    service_type: ServiceType
    version: str
    is_enabled: bool
    is_core: bool
    display_order: int
    service_config: Dict[str, Any]
    dependencies: List[str]
    conflicts: List[str]
    features: List[Dict[str, Any]]
    pricing: List[Dict[str, Any]]

class ServiceRegistry:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self._service_cache = {}
        self._dependency_graph = {}
        self._last_cache_update = None
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    def register_service(self, service_definition: ServiceDefinition) -> str:
        """Register a new service in the system"""
        try:
            # Validate service definition
            if not self._validate_service_definition(service_definition):
                return None
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if service already exists
                    cursor.execute("""
                        SELECT id FROM service_registry WHERE service_key = %s
                    """, (service_definition.service_key,))
                    
                    existing_service = cursor.fetchone()
                    if existing_service:
                        logger.warning(f"Service {service_definition.service_key} already exists")
                        return existing_service["id"]
                    
                    # Insert service
                    cursor.execute("""
                        INSERT INTO service_registry 
                        (service_key, service_name, service_category, service_type, 
                         version, is_enabled, is_core, display_order, 
                         service_config, dependencies, conflicts)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        service_definition.service_key,
                        service_definition.service_name,
                        service_definition.service_category,
                        service_definition.service_type.value,
                        service_definition.version,
                        service_definition.is_enabled,
                        service_definition.is_core,
                        service_definition.display_order,
                        json.dumps(service_definition.service_config),
                        json.dumps(service_definition.dependencies),
                        json.dumps(service_definition.conflicts)
                    ))
                    
                    service_id = cursor.fetchone()["id"]
                    
                    # Register service features
                    for feature in service_definition.features:
                        self._register_service_feature(service_id, feature)
                    
                    # Register service pricing
                    for pricing in service_definition.pricing:
                        self._register_service_pricing(service_id, pricing)
                    
                    # Update cache
                    self._refresh_service_cache()
                    
                    logger.info(f"Service {service_definition.service_key} registered successfully")
                    return service_id
                    
        except Exception as e:
            logger.error(f"Error registering service: {e}")
            return None
    
    def enable_service(self, service_key: str) -> bool:
        """Enable a service"""
        try:
            # Check dependencies
            if not self._check_dependencies(service_key):
                logger.error(f"Dependencies not met for service {service_key}")
                return False
            
            # Check conflicts
            if not self._check_conflicts(service_key):
                logger.error(f"Conflicts detected for service {service_key}")
                return False
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE service_registry 
                        SET is_enabled = TRUE, updated_at = NOW()
                        WHERE service_key = %s
                    """, (service_key,))
                    
                    if cursor.rowcount == 0:
                        logger.error(f"Service {service_key} not found")
                        return False
            
            self._refresh_service_cache()
            logger.info(f"Service {service_key} enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling service: {e}")
            return False
    
    def disable_service(self, service_key: str) -> bool:
        """Disable a service"""
        try:
            # Check if service is core
            if self._is_core_service(service_key):
                logger.warning(f"Cannot disable core service: {service_key}")
                return False
            
            # Check if other services depend on this
            dependents = self._get_dependent_services(service_key)
            if dependents:
                logger.warning(f"Cannot disable service {service_key} - other services depend on it: {dependents}")
                return False
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE service_registry 
                        SET is_enabled = FALSE, updated_at = NOW()
                        WHERE service_key = %s
                    """, (service_key,))
                    
                    if cursor.rowcount == 0:
                        logger.error(f"Service {service_key} not found")
                        return False
            
            self._refresh_service_cache()
            logger.info(f"Service {service_key} disabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling service: {e}")
            return False
    
    def get_available_services(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get available services for a user"""
        try:
            # Use cache if available and recent
            if self._service_cache and self._last_cache_update:
                cache_age = datetime.now() - self._last_cache_update
                if cache_age < timedelta(minutes=5):  # Cache for 5 minutes
                    return self._get_user_services_from_cache(user_id)
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if user_id:
                        # Get services available to specific user
                        cursor.execute("""
                            SELECT sr.*, usa.access_level, usa.expires_at
                            FROM service_registry sr
                            LEFT JOIN user_service_access usa ON sr.id = usa.service_id AND usa.user_id = %s
                            WHERE sr.is_enabled = TRUE
                            ORDER BY sr.display_order, sr.service_name
                        """, (user_id,))
                    else:
                        # Get all enabled services
                        cursor.execute("""
                            SELECT * FROM service_registry 
                            WHERE is_enabled = TRUE
                            ORDER BY display_order, service_name
                        """)
                    
                    services = [dict(row) for row in cursor.fetchall()]
                    
                    # Update cache
                    self._service_cache = {s["service_key"]: s for s in services}
                    self._last_cache_update = datetime.now()
                    
                    return services
                    
        except Exception as e:
            logger.error(f"Error getting available services: {e}")
            return []
    
    def get_service_by_key(self, service_key: str) -> Optional[Dict[str, Any]]:
        """Get service by key"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM service_registry WHERE service_key = %s
                    """, (service_key,))
                    
                    result = cursor.fetchone()
                    return dict(result) if result else None
                    
        except Exception as e:
            logger.error(f"Error getting service by key: {e}")
            return None
    
    def get_service_features(self, service_key: str) -> List[Dict[str, Any]]:
        """Get features for a service"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT sf.* FROM service_features sf
                        JOIN service_registry sr ON sf.service_id = sr.id
                        WHERE sr.service_key = %s AND sf.is_enabled = TRUE
                        ORDER BY sf.feature_name
                    """, (service_key,))
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting service features: {e}")
            return []
    
    def get_service_pricing(self, service_key: str) -> List[Dict[str, Any]]:
        """Get pricing for a service"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT sp.* FROM service_pricing sp
                        JOIN service_registry sr ON sp.service_id = sr.id
                        WHERE sr.service_key = %s AND sp.is_active = TRUE
                        ORDER BY sp.price
                    """, (service_key,))
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting service pricing: {e}")
            return []
    
    def grant_user_access(self, user_id: str, service_key: str, 
                         access_level: str = "full", expires_at: datetime = None) -> bool:
        """Grant user access to a service"""
        try:
            service = self.get_service_by_key(service_key)
            if not service:
                logger.error(f"Service {service_key} not found")
                return False
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_service_access 
                        (user_id, service_id, access_level, expires_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (user_id, service_id) 
                        DO UPDATE SET 
                            access_level = %s,
                            expires_at = %s,
                            is_active = TRUE
                    """, (
                        user_id, service["id"], access_level, expires_at,
                        access_level, expires_at
                    ))
            
            logger.info(f"Access granted to user {user_id} for service {service_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error granting user access: {e}")
            return False
    
    def revoke_user_access(self, user_id: str, service_key: str) -> bool:
        """Revoke user access to a service"""
        try:
            service = self.get_service_by_key(service_key)
            if not service:
                logger.error(f"Service {service_key} not found")
                return False
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_service_access 
                        SET is_active = FALSE
                        WHERE user_id = %s AND service_id = %s
                    """, (user_id, service["id"]))
            
            logger.info(f"Access revoked for user {user_id} to service {service_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking user access: {e}")
            return False
    
    def get_service_dependencies(self, service_key: str) -> List[str]:
        """Get dependencies for a service"""
        try:
            service = self.get_service_by_key(service_key)
            if not service:
                return []
            
            dependencies = json.loads(service["dependencies"])
            return dependencies
            
        except Exception as e:
            logger.error(f"Error getting service dependencies: {e}")
            return []
    
    def get_dependent_services(self, service_key: str) -> List[str]:
        """Get services that depend on the given service"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT service_key FROM service_registry 
                        WHERE dependencies::text LIKE %s AND is_enabled = TRUE
                    """, (f'%"{service_key}"%',))
                    
                    return [row["service_key"] for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting dependent services: {e}")
            return []
    
    def check_service_health(self, service_key: str) -> Dict[str, Any]:
        """Check the health of a service"""
        try:
            service = self.get_service_by_key(service_key)
            if not service:
                return {"healthy": False, "error": "Service not found"}
            
            health_status = {
                "service_key": service_key,
                "healthy": True,
                "status": "enabled" if service["is_enabled"] else "disabled",
                "version": service["version"],
                "last_updated": service["updated_at"],
                "dependencies_met": self._check_dependencies(service_key),
                "conflicts_resolved": self._check_conflicts(service_key)
            }
            
            # Check if dependencies are met
            if not health_status["dependencies_met"]:
                health_status["healthy"] = False
                health_status["error"] = "Dependencies not met"
            
            # Check if conflicts are resolved
            if not health_status["conflicts_resolved"]:
                health_status["healthy"] = False
                health_status["error"] = "Conflicts detected"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking service health: {e}")
            return {"healthy": False, "error": str(e)}
    
    def get_service_analytics(self, service_key: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a service"""
        try:
            service = self.get_service_by_key(service_key)
            if not service:
                return {}
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get usage statistics
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_usage,
                            COUNT(DISTINCT user_id) as unique_users,
                            usage_type,
                            DATE(timestamp) as usage_date
                        FROM service_usage_analytics 
                        WHERE service_id = %s 
                        AND timestamp >= %s
                        GROUP BY usage_type, DATE(timestamp)
                        ORDER BY usage_date DESC
                    """, (service["id"], datetime.now() - timedelta(days=days)))
                    
                    usage_stats = [dict(row) for row in cursor.fetchall()]
                    
                    # Get user access statistics
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_access,
                            access_level,
                            COUNT(CASE WHEN expires_at IS NULL OR expires_at > NOW() THEN 1 END) as active_access
                        FROM user_service_access 
                        WHERE service_id = %s
                        GROUP BY access_level
                    """, (service["id"],))
                    
                    access_stats = [dict(row) for row in cursor.fetchall()]
                    
                    return {
                        "service_key": service_key,
                        "usage_stats": usage_stats,
                        "access_stats": access_stats,
                        "period_days": days
                    }
                    
        except Exception as e:
            logger.error(f"Error getting service analytics: {e}")
            return {}
    
    # Private helper methods
    def _validate_service_definition(self, service_definition: ServiceDefinition) -> bool:
        """Validate service definition"""
        if not service_definition.service_key:
            logger.error("Service key is required")
            return False
        
        if not service_definition.service_name:
            logger.error("Service name is required")
            return False
        
        if not service_definition.service_category:
            logger.error("Service category is required")
            return False
        
        return True
    
    def _register_service_feature(self, service_id: str, feature: Dict[str, Any]):
        """Register a service feature"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO service_features 
                        (service_id, feature_key, feature_name, feature_type, 
                         is_enabled, feature_config)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        service_id,
                        feature["feature_key"],
                        feature["feature_name"],
                        feature["feature_type"],
                        feature.get("is_enabled", True),
                        json.dumps(feature.get("feature_config", {}))
                    ))
        except Exception as e:
            logger.error(f"Error registering service feature: {e}")
    
    def _register_service_pricing(self, service_id: str, pricing: Dict[str, Any]):
        """Register service pricing"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO service_pricing 
                        (service_id, pricing_tier, price, billing_cycle, is_active)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        service_id,
                        pricing["pricing_tier"],
                        pricing["price"],
                        pricing["billing_cycle"],
                        pricing.get("is_active", True)
                    ))
        except Exception as e:
            logger.error(f"Error registering service pricing: {e}")
    
    def _check_dependencies(self, service_key: str) -> bool:
        """Check if all dependencies are enabled"""
        try:
            service = self.get_service_by_key(service_key)
            if not service or not service["dependencies"]:
                return True
            
            dependencies = json.loads(service["dependencies"])
            for dep in dependencies:
                dep_service = self.get_service_by_key(dep)
                if not dep_service or not dep_service["is_enabled"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False
    
    def _check_conflicts(self, service_key: str) -> bool:
        """Check for service conflicts"""
        try:
            service = self.get_service_by_key(service_key)
            if not service or not service["conflicts"]:
                return True
            
            conflicts = json.loads(service["conflicts"])
            for conflict in conflicts:
                conflict_service = self.get_service_by_key(conflict)
                if conflict_service and conflict_service["is_enabled"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking conflicts: {e}")
            return False
    
    def _is_core_service(self, service_key: str) -> bool:
        """Check if service is core"""
        try:
            service = self.get_service_by_key(service_key)
            return service and service["is_core"]
        except Exception as e:
            logger.error(f"Error checking if service is core: {e}")
            return False
    
    def _get_dependent_services(self, service_key: str) -> List[str]:
        """Get services that depend on the given service"""
        return self.get_dependent_services(service_key)
    
    def _refresh_service_cache(self):
        """Refresh the service cache"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM service_registry 
                        WHERE is_enabled = TRUE
                        ORDER BY display_order, service_name
                    """)
                    
                    services = [dict(row) for row in cursor.fetchall()]
                    self._service_cache = {s["service_key"]: s for s in services}
                    self._last_cache_update = datetime.now()
                    
        except Exception as e:
            logger.error(f"Error refreshing service cache: {e}")
    
    def _get_user_services_from_cache(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user services from cache"""
        # This is a simplified version - in production, you'd need to handle
        # user-specific access levels and permissions
        return list(self._service_cache.values())

def main():
    """Example usage of Service Registry System"""
    
    # Initialize service registry
    service_registry = ServiceRegistry("postgresql://user:password@localhost/legalops")
    
    # Example: Register a new service
    new_service = ServiceDefinition(
        service_key="new_legal_service",
        service_name="New Legal Service",
        service_category="legal",
        service_type=ServiceType.ADDON,
        version="1.0.0",
        is_enabled=True,
        is_core=False,
        display_order=11,
        service_config={
            "icon": "legal",
            "color": "#10B981",
            "description": "A new legal service"
        },
        dependencies=["authentication", "database"],
        conflicts=[],
        features=[
            {
                "feature_key": "document_generation",
                "feature_name": "Document Generation",
                "feature_type": "workflow",
                "is_enabled": True
            }
        ],
        pricing=[
            {
                "pricing_tier": "basic",
                "price": 199.00,
                "billing_cycle": "one_time"
            }
        ]
    )
    
    service_id = service_registry.register_service(new_service)
    print(f"Service registered with ID: {service_id}")
    
    # Example: Enable service
    success = service_registry.enable_service("new_legal_service")
    print(f"Service enabled: {success}")
    
    # Example: Get available services
    services = service_registry.get_available_services()
    print(f"Available services: {len(services)}")
    
    # Example: Check service health
    health = service_registry.check_service_health("business_formation")
    print(f"Service health: {health}")

if __name__ == "__main__":
    main()
