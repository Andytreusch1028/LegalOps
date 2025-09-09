#!/usr/bin/env python3
"""
Modular UI Manager for Legal Ops Platform
Manages dynamic UI components based on available services
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentType(Enum):
    PAGE = "page"
    WIDGET = "widget"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    NAVIGATION = "navigation"

class ComponentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

@dataclass
class UIComponent:
    component_id: str
    service_key: str
    component_name: str
    component_type: ComponentType
    component_config: Dict[str, Any]
    dependencies: List[str]
    is_enabled: bool
    display_order: int
    render_function: str  # Function name to render the component

class ModularUIManager:
    def __init__(self, db_connection_string: str, service_registry):
        self.db_connection_string = db_connection_string
        self.service_registry = service_registry
        self._component_registry = {}
        self._navigation_cache = {}
        self._dashboard_cache = {}
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    def register_component(self, component: UIComponent) -> bool:
        """Register a UI component"""
        try:
            # Validate component
            if not self._validate_component(component):
                return False
            
            # Store in component registry
            self._component_registry[component.component_id] = component
            
            # Store in database
            self._store_component_in_db(component)
            
            logger.info(f"Component {component.component_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering component: {e}")
            return False
    
    def get_available_components(self, user_id: str, component_type: ComponentType = None) -> List[UIComponent]:
        """Get available components for a user"""
        try:
            # Get user's available services
            available_services = self.service_registry.get_available_services(user_id)
            available_service_keys = {s["service_key"] for s in available_services}
            
            # Filter components based on available services
            available_components = []
            for component in self._component_registry.values():
                if not component.is_enabled:
                    continue
                
                if component_type and component.component_type != component_type:
                    continue
                
                # Check if service is available to user
                if component.service_key not in available_service_keys:
                    continue
                
                # Check dependencies
                if not self._check_component_dependencies(component, available_service_keys):
                    continue
                
                available_components.append(component)
            
            # Sort by display order
            available_components.sort(key=lambda x: x.display_order)
            
            return available_components
            
        except Exception as e:
            logger.error(f"Error getting available components: {e}")
            return []
    
    def generate_navigation(self, user_id: str) -> Dict[str, Any]:
        """Generate navigation structure for a user"""
        try:
            # Check cache first
            cache_key = f"nav_{user_id}"
            if cache_key in self._navigation_cache:
                return self._navigation_cache[cache_key]
            
            # Get available services
            available_services = self.service_registry.get_available_services(user_id)
            
            # Build navigation structure
            navigation = {
                "main": [],
                "services": [],
                "admin": []
            }
            
            # Core navigation items (always available)
            navigation["main"] = [
                {
                    "key": "dashboard",
                    "label": "Dashboard",
                    "icon": "dashboard",
                    "path": "/dashboard",
                    "is_core": True
                },
                {
                    "key": "profile",
                    "label": "Profile",
                    "icon": "user",
                    "path": "/profile",
                    "is_core": True
                }
            ]
            
            # Service-based navigation
            service_categories = self._group_services_by_category(available_services)
            
            for category, services in service_categories.items():
                if len(services) == 1:
                    # Single service - direct link
                    service = services[0]
                    navigation["services"].append({
                        "key": service["service_key"],
                        "label": service["service_name"],
                        "icon": service["service_config"].get("icon", "service"),
                        "color": service["service_config"].get("color", "#6B7280"),
                        "path": f"/services/{service['service_key']}",
                        "is_core": False,
                        "description": service["service_config"].get("description", "")
                    })
                else:
                    # Multiple services - dropdown menu
                    navigation["services"].append({
                        "key": category,
                        "label": self._format_category_name(category),
                        "icon": self._get_category_icon(category),
                        "children": [
                            {
                                "key": service["service_key"],
                                "label": service["service_name"],
                                "icon": service["service_config"].get("icon", "service"),
                                "path": f"/services/{service['service_key']}",
                                "is_core": False
                            }
                            for service in services
                        ],
                        "is_core": False
                    })
            
            # Admin navigation (if user has admin access)
            if self._user_has_admin_access(user_id):
                navigation["admin"] = [
                    {
                        "key": "service_management",
                        "label": "Service Management",
                        "icon": "settings",
                        "path": "/admin/services",
                        "is_core": False
                    },
                    {
                        "key": "user_management",
                        "label": "User Management",
                        "icon": "users",
                        "path": "/admin/users",
                        "is_core": False
                    },
                    {
                        "key": "analytics",
                        "label": "Analytics",
                        "icon": "chart",
                        "path": "/admin/analytics",
                        "is_core": False
                    }
                ]
            
            # Cache the result
            self._navigation_cache[cache_key] = navigation
            
            return navigation
            
        except Exception as e:
            logger.error(f"Error generating navigation: {e}")
            return {"main": [], "services": [], "admin": []}
    
    def generate_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Generate dashboard layout for a user"""
        try:
            # Check cache first
            cache_key = f"dashboard_{user_id}"
            if cache_key in self._dashboard_cache:
                return self._dashboard_cache[cache_key]
            
            # Get available components
            available_components = self.get_available_components(user_id)
            
            # Group components by type and service
            dashboard_sections = {
                "quick_actions": [],
                "service_overview": [],
                "recent_activity": [],
                "notifications": [],
                "analytics": []
            }
            
            for component in available_components:
                if component.component_type == ComponentType.WIDGET:
                    section = component.component_config.get("dashboard_section", "service_overview")
                    if section in dashboard_sections:
                        dashboard_sections[section].append({
                            "component_id": component.component_id,
                            "component_name": component.component_name,
                            "service_key": component.service_key,
                            "config": component.component_config,
                            "render_function": component.render_function
                        })
            
            # Get user's recent activity
            recent_activity = self._get_user_recent_activity(user_id)
            
            # Get user's notifications
            notifications = self._get_user_notifications(user_id)
            
            dashboard = {
                "sections": dashboard_sections,
                "recent_activity": recent_activity,
                "notifications": notifications,
                "user_preferences": self._get_user_dashboard_preferences(user_id)
            }
            
            # Cache the result
            self._dashboard_cache[cache_key] = dashboard
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            return {"sections": {}, "recent_activity": [], "notifications": []}
    
    def render_component(self, component_id: str, user_id: str, props: Dict[str, Any] = None) -> Dict[str, Any]:
        """Render a specific component"""
        try:
            component = self._component_registry.get(component_id)
            if not component:
                return {"error": "Component not found"}
            
            # Check if user has access to the service
            available_services = self.service_registry.get_available_services(user_id)
            if not any(s["service_key"] == component.service_key for s in available_services):
                return {"error": "Access denied"}
            
            # Check component dependencies
            available_service_keys = {s["service_key"] for s in available_services}
            if not self._check_component_dependencies(component, available_service_keys):
                return {"error": "Dependencies not met"}
            
            # Render component (in a real implementation, this would call the actual render function)
            render_result = {
                "component_id": component_id,
                "component_name": component.component_name,
                "service_key": component.service_key,
                "rendered_content": f"Rendered {component.component_name}",
                "props": props or {},
                "config": component.component_config
            }
            
            return render_result
            
        except Exception as e:
            logger.error(f"Error rendering component: {e}")
            return {"error": str(e)}
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user's UI preferences"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_dashboard_preferences (user_id, preferences)
                        VALUES (%s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET preferences = %s, updated_at = NOW()
                    """, (user_id, json.dumps(preferences), json.dumps(preferences)))
            
            # Clear cache
            self._clear_user_cache(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    def get_service_dashboard(self, user_id: str, service_key: str) -> Dict[str, Any]:
        """Get dashboard for a specific service"""
        try:
            # Check if user has access to the service
            available_services = self.service_registry.get_available_services(user_id)
            if not any(s["service_key"] == service_key for s in available_services):
                return {"error": "Access denied"}
            
            # Get service-specific components
            service_components = [
                c for c in self._component_registry.values()
                if c.service_key == service_key and c.is_enabled
            ]
            
            # Get service information
            service_info = self.service_registry.get_service_by_key(service_key)
            if not service_info:
                return {"error": "Service not found"}
            
            # Get service features
            service_features = self.service_registry.get_service_features(service_key)
            
            # Get user's service-specific data
            service_data = self._get_user_service_data(user_id, service_key)
            
            dashboard = {
                "service_info": service_info,
                "service_features": service_features,
                "components": [
                    {
                        "component_id": c.component_id,
                        "component_name": c.component_name,
                        "component_type": c.component_type.value,
                        "config": c.component_config,
                        "render_function": c.render_function
                    }
                    for c in service_components
                ],
                "user_data": service_data,
                "navigation": self._get_service_navigation(service_key)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting service dashboard: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    def _validate_component(self, component: UIComponent) -> bool:
        """Validate component definition"""
        if not component.component_id:
            logger.error("Component ID is required")
            return False
        
        if not component.service_key:
            logger.error("Service key is required")
            return False
        
        if not component.component_name:
            logger.error("Component name is required")
            return False
        
        return True
    
    def _store_component_in_db(self, component: UIComponent):
        """Store component in database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ui_components 
                        (component_id, service_key, component_name, component_type, 
                         component_config, dependencies, is_enabled, display_order, render_function)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (component_id) 
                        DO UPDATE SET 
                            component_config = %s,
                            dependencies = %s,
                            is_enabled = %s,
                            display_order = %s,
                            render_function = %s,
                            updated_at = NOW()
                    """, (
                        component.component_id,
                        component.service_key,
                        component.component_name,
                        component.component_type.value,
                        json.dumps(component.component_config),
                        json.dumps(component.dependencies),
                        component.is_enabled,
                        component.display_order,
                        component.render_function,
                        json.dumps(component.component_config),
                        json.dumps(component.dependencies),
                        component.is_enabled,
                        component.display_order,
                        component.render_function
                    ))
        except Exception as e:
            logger.error(f"Error storing component in database: {e}")
    
    def _check_component_dependencies(self, component: UIComponent, available_services: set) -> bool:
        """Check if component dependencies are met"""
        for dependency in component.dependencies:
            if dependency not in available_services:
                return False
        return True
    
    def _group_services_by_category(self, services: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group services by category"""
        categories = {}
        for service in services:
            category = service["service_category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(service)
        return categories
    
    def _format_category_name(self, category: str) -> str:
        """Format category name for display"""
        return category.replace("_", " ").title()
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for category"""
        icons = {
            "business": "briefcase",
            "legal": "scale",
            "compliance": "shield-check",
            "core": "cog"
        }
        return icons.get(category, "folder")
    
    def _user_has_admin_access(self, user_id: str) -> bool:
        """Check if user has admin access"""
        # In a real implementation, this would check user roles/permissions
        return False  # Simplified for now
    
    def _get_user_recent_activity(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's recent activity"""
        # In a real implementation, this would query the database
        return []
    
    def _get_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's notifications"""
        # In a real implementation, this would query the database
        return []
    
    def _get_user_dashboard_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's dashboard preferences"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT preferences FROM user_dashboard_preferences 
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        return json.loads(result["preferences"])
                    
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting user dashboard preferences: {e}")
            return {}
    
    def _get_user_service_data(self, user_id: str, service_key: str) -> Dict[str, Any]:
        """Get user's data for a specific service"""
        # In a real implementation, this would query service-specific data
        return {}
    
    def _get_service_navigation(self, service_key: str) -> List[Dict[str, Any]]:
        """Get navigation for a specific service"""
        # In a real implementation, this would return service-specific navigation
        return []
    
    def _clear_user_cache(self, user_id: str):
        """Clear cache for a specific user"""
        cache_keys_to_remove = [key for key in self._navigation_cache.keys() if key.endswith(f"_{user_id}")]
        for key in cache_keys_to_remove:
            del self._navigation_cache[key]
        
        cache_keys_to_remove = [key for key in self._dashboard_cache.keys() if key.endswith(f"_{user_id}")]
        for key in cache_keys_to_remove:
            del self._dashboard_cache[key]

def main():
    """Example usage of Modular UI Manager"""
    
    # Initialize UI manager
    from service_registry_system import ServiceRegistry
    service_registry = ServiceRegistry("postgresql://user:password@localhost/legalops")
    ui_manager = ModularUIManager("postgresql://user:password@localhost/legalops", service_registry)
    
    # Example: Register a component
    component = UIComponent(
        component_id="business_formation_dashboard",
        service_key="business_formation",
        component_name="Business Formation Dashboard",
        component_type=ComponentType.PAGE,
        component_config={
            "dashboard_section": "service_overview",
            "icon": "business",
            "color": "#3B82F6"
        },
        dependencies=["authentication", "database"],
        is_enabled=True,
        display_order=1,
        render_function="render_business_formation_dashboard"
    )
    
    success = ui_manager.register_component(component)
    print(f"Component registered: {success}")
    
    # Example: Generate navigation
    navigation = ui_manager.generate_navigation("user123")
    print(f"Navigation generated: {len(navigation['services'])} services")
    
    # Example: Generate dashboard
    dashboard = ui_manager.generate_dashboard("user123")
    print(f"Dashboard generated: {len(dashboard['sections'])} sections")

if __name__ == "__main__":
    main()
