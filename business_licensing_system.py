#!/usr/bin/env python3
"""
Business Licensing System for Legal Ops Platform
Handles EIN acquisition, business licenses, and permit applications
"""

import requests
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

class LicenseType(Enum):
    EIN = "ein"
    CITY_BUSINESS = "city_business"
    COUNTY_BUSINESS = "county_business"
    STATE_BUSINESS = "state_business"
    HEALTH_PERMIT = "health_permit"
    BUILDING_PERMIT = "building_permit"
    PROFESSIONAL = "professional"
    ENVIRONMENTAL = "environmental"
    FEDERAL = "federal"

class LicenseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    RENEWAL_REQUIRED = "renewal_required"

@dataclass
class LicenseApplication:
    user_id: str
    license_type: LicenseType
    business_name: str
    business_type: str
    location: Dict[str, str]  # city, state, county, zip
    application_data: Dict[str, Any]
    status: LicenseStatus = LicenseStatus.PENDING
    application_id: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class BusinessLicensingSystem:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.irs_api_key = "your_irs_api_key"  # In production, use environment variable
        self.state_apis = {
            "FL": "https://api.floridabusiness.org/licenses",
            "CA": "https://api.calbusiness.org/licenses",
            "NY": "https://api.nybusiness.org/licenses"
        }
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    # EIN Acquisition
    def apply_for_ein(self, user_id: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply for Employer Identification Number (EIN)"""
        try:
            # Prepare EIN application data
            ein_data = {
                "business_name": business_data["business_name"],
                "business_type": business_data["business_type"],
                "address": business_data["address"],
                "responsible_party": business_data["responsible_party"],
                "ssn_or_ein": business_data.get("ssn_or_ein"),
                "business_purpose": business_data.get("business_purpose", "General business operations")
            }
            
            # Submit to IRS (in production, use actual IRS API)
            ein_result = self._submit_ein_application(ein_data)
            
            # Store application in database
            application_id = self._store_license_application(
                user_id, LicenseType.EIN, business_data, ein_result
            )
            
            return {
                "success": True,
                "application_id": application_id,
                "tracking_number": ein_result.get("tracking_number"),
                "estimated_completion": ein_result.get("estimated_completion"),
                "status": "submitted"
            }
            
        except Exception as e:
            logger.error(f"Error applying for EIN: {e}")
            return {"success": False, "error": str(e)}
    
    def _submit_ein_application(self, ein_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit EIN application to IRS"""
        # In production, integrate with actual IRS API
        # For now, simulate the process
        
        tracking_number = f"EIN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        estimated_completion = datetime.now() + timedelta(days=1)
        
        return {
            "tracking_number": tracking_number,
            "estimated_completion": estimated_completion,
            "status": "submitted",
            "confirmation_number": f"CONF{tracking_number}"
        }
    
    # Business License Applications
    def apply_for_business_license(self, user_id: str, license_type: LicenseType, 
                                 business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply for business license"""
        try:
            # Determine which agency to submit to
            agency_info = self._get_license_agency(license_type, business_data["location"])
            
            # Prepare application data
            application_data = self._prepare_license_application(license_type, business_data)
            
            # Submit application
            result = self._submit_license_application(agency_info, application_data)
            
            # Store in database
            application_id = self._store_license_application(
                user_id, license_type, business_data, result
            )
            
            return {
                "success": True,
                "application_id": application_id,
                "tracking_number": result.get("tracking_number"),
                "estimated_completion": result.get("estimated_completion"),
                "status": "submitted",
                "agency": agency_info["name"]
            }
            
        except Exception as e:
            logger.error(f"Error applying for business license: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_license_agency(self, license_type: LicenseType, location: Dict[str, str]) -> Dict[str, Any]:
        """Get the appropriate agency for license type and location"""
        agencies = {
            LicenseType.CITY_BUSINESS: {
                "name": f"{location['city']} Business License Office",
                "url": f"https://{location['city'].lower().replace(' ', '')}.gov/business-license",
                "processing_time": "3-5 business days"
            },
            LicenseType.COUNTY_BUSINESS: {
                "name": f"{location['county']} County Business License Office",
                "url": f"https://{location['county'].lower().replace(' ', '')}county.gov/business",
                "processing_time": "5-7 business days"
            },
            LicenseType.STATE_BUSINESS: {
                "name": f"{location['state']} Department of Business Regulation",
                "url": f"https://{location['state'].lower()}.gov/business-license",
                "processing_time": "7-10 business days"
            },
            LicenseType.HEALTH_PERMIT: {
                "name": f"{location['county']} Health Department",
                "url": f"https://{location['county'].lower().replace(' ', '')}health.gov/permits",
                "processing_time": "10-14 business days"
            },
            LicenseType.BUILDING_PERMIT: {
                "name": f"{location['city']} Building Department",
                "url": f"https://{location['city'].lower().replace(' ', '')}.gov/building",
                "processing_time": "14-21 business days"
            }
        }
        
        return agencies.get(license_type, {
            "name": "General Business License Office",
            "url": "https://business.gov/license",
            "processing_time": "10-15 business days"
        })
    
    def _prepare_license_application(self, license_type: LicenseType, 
                                   business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare license application data based on type"""
        base_data = {
            "business_name": business_data["business_name"],
            "business_type": business_data["business_type"],
            "address": business_data["address"],
            "contact_info": business_data["contact_info"],
            "ein": business_data.get("ein"),
            "application_date": datetime.now().isoformat()
        }
        
        # Add type-specific requirements
        if license_type == LicenseType.HEALTH_PERMIT:
            base_data.update({
                "food_service_type": business_data.get("food_service_type"),
                "seating_capacity": business_data.get("seating_capacity"),
                "kitchen_equipment": business_data.get("kitchen_equipment"),
                "waste_disposal": business_data.get("waste_disposal")
            })
        
        elif license_type == LicenseType.BUILDING_PERMIT:
            base_data.update({
                "construction_type": business_data.get("construction_type"),
                "project_value": business_data.get("project_value"),
                "contractor_license": business_data.get("contractor_license"),
                "architectural_plans": business_data.get("architectural_plans")
            })
        
        elif license_type == LicenseType.PROFESSIONAL:
            base_data.update({
                "profession": business_data.get("profession"),
                "education": business_data.get("education"),
                "experience": business_data.get("experience"),
                "certifications": business_data.get("certifications")
            })
        
        return base_data
    
    def _submit_license_application(self, agency_info: Dict[str, Any], 
                                  application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit license application to appropriate agency"""
        # In production, integrate with actual agency APIs
        # For now, simulate the process
        
        tracking_number = f"LIC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        processing_days = int(agency_info["processing_time"].split('-')[0])
        estimated_completion = datetime.now() + timedelta(days=processing_days)
        
        return {
            "tracking_number": tracking_number,
            "estimated_completion": estimated_completion,
            "status": "submitted",
            "agency_reference": f"REF{tracking_number}"
        }
    
    # License Management
    def get_user_licenses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all licenses for a user"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM user_licenses 
                        WHERE user_id = %s 
                        ORDER BY created_at DESC
                    """, (user_id,))
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting user licenses: {e}")
            return []
    
    def check_license_status(self, application_id: str) -> Dict[str, Any]:
        """Check the status of a license application"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM user_licenses 
                        WHERE application_id = %s
                    """, (application_id,))
                    
                    result = cursor.fetchone()
                    if not result:
                        return {"success": False, "error": "Application not found"}
                    
                    # In production, check with actual agency APIs
                    status_update = self._check_agency_status(result)
                    
                    # Update status if changed
                    if status_update["status"] != result["status"]:
                        self._update_license_status(application_id, status_update)
                    
                    return {
                        "success": True,
                        "status": status_update["status"],
                        "tracking_number": result["tracking_number"],
                        "estimated_completion": result["estimated_completion"],
                        "last_updated": result["updated_at"]
                    }
                    
        except Exception as e:
            logger.error(f"Error checking license status: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_agency_status(self, license_record: Dict[str, Any]) -> Dict[str, Any]:
        """Check status with the issuing agency"""
        # In production, integrate with actual agency APIs
        # For now, simulate status updates based on time elapsed
        
        created_at = license_record["created_at"]
        days_elapsed = (datetime.now() - created_at).days
        
        if days_elapsed < 1:
            status = "submitted"
        elif days_elapsed < 3:
            status = "under_review"
        elif days_elapsed < 7:
            status = "pending_approval"
        else:
            status = "approved"
        
        return {"status": status}
    
    def _update_license_status(self, application_id: str, status_update: Dict[str, Any]):
        """Update license status in database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_licenses 
                        SET status = %s, updated_at = NOW()
                        WHERE application_id = %s
                    """, (status_update["status"], application_id))
                    
        except Exception as e:
            logger.error(f"Error updating license status: {e}")
    
    # License Renewals
    def get_expiring_licenses(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get licenses expiring within specified days"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT ul.*, u.email, u.first_name, u.last_name
                        FROM user_licenses ul
                        JOIN users u ON ul.user_id = u.id
                        WHERE ul.expiration_date <= %s 
                        AND ul.status = 'active'
                        ORDER BY ul.expiration_date ASC
                    """, (datetime.now() + timedelta(days=days_ahead),))
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting expiring licenses: {e}")
            return []
    
    def initiate_license_renewal(self, license_id: str) -> Dict[str, Any]:
        """Initiate license renewal process"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get license details
                    cursor.execute("""
                        SELECT * FROM user_licenses WHERE id = %s
                    """, (license_id,))
                    
                    license_record = cursor.fetchone()
                    if not license_record:
                        return {"success": False, "error": "License not found"}
                    
                    # Create renewal application
                    renewal_data = {
                        "original_license_id": license_id,
                        "license_type": license_record["license_type"],
                        "business_data": license_record["business_data"],
                        "renewal_fee": self._calculate_renewal_fee(license_record["license_type"])
                    }
                    
                    # Submit renewal application
                    renewal_result = self._submit_renewal_application(renewal_data)
                    
                    # Update license status
                    cursor.execute("""
                        UPDATE user_licenses 
                        SET status = 'renewal_pending', updated_at = NOW()
                        WHERE id = %s
                    """, (license_id,))
                    
                    return {
                        "success": True,
                        "renewal_application_id": renewal_result["application_id"],
                        "renewal_fee": renewal_data["renewal_fee"],
                        "estimated_completion": renewal_result["estimated_completion"]
                    }
                    
        except Exception as e:
            logger.error(f"Error initiating license renewal: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_renewal_fee(self, license_type: str) -> float:
        """Calculate renewal fee based on license type"""
        fees = {
            "city_business": 50.00,
            "county_business": 75.00,
            "state_business": 100.00,
            "health_permit": 150.00,
            "building_permit": 200.00,
            "professional": 300.00,
            "environmental": 400.00,
            "federal": 500.00
        }
        
        return fees.get(license_type, 100.00)
    
    def _submit_renewal_application(self, renewal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit renewal application to appropriate agency"""
        # In production, integrate with actual agency APIs
        tracking_number = f"REN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        estimated_completion = datetime.now() + timedelta(days=14)
        
        return {
            "application_id": tracking_number,
            "tracking_number": tracking_number,
            "estimated_completion": estimated_completion,
            "status": "submitted"
        }
    
    # Database Operations
    def _store_license_application(self, user_id: str, license_type: LicenseType, 
                                 business_data: Dict[str, Any], 
                                 application_result: Dict[str, Any]) -> str:
        """Store license application in database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_licenses 
                        (user_id, license_type, business_name, business_type, 
                         business_data, status, tracking_number, 
                         estimated_completion, application_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        user_id,
                        license_type.value,
                        business_data["business_name"],
                        business_data["business_type"],
                        json.dumps(business_data),
                        "pending",
                        application_result.get("tracking_number"),
                        application_result.get("estimated_completion"),
                        json.dumps(application_result)
                    ))
                    
                    return cursor.fetchone()["id"]
                    
        except Exception as e:
            logger.error(f"Error storing license application: {e}")
            return None
    
    # Compliance Monitoring
    def get_compliance_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get compliance alerts for a user"""
        try:
            alerts = []
            
            # Check for expiring licenses
            expiring_licenses = self._get_user_expiring_licenses(user_id, 30)
            for license_record in expiring_licenses:
                alerts.append({
                    "type": "license_expiration",
                    "severity": "high" if license_record["days_until_expiration"] <= 7 else "medium",
                    "message": f"License {license_record['license_type']} expires in {license_record['days_until_expiration']} days",
                    "license_id": license_record["id"],
                    "action_required": "renewal"
                })
            
            # Check for missing required licenses
            missing_licenses = self._check_missing_licenses(user_id)
            for missing_license in missing_licenses:
                alerts.append({
                    "type": "missing_license",
                    "severity": "high",
                    "message": f"Required license {missing_license['license_type']} is missing",
                    "action_required": "application"
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting compliance alerts: {e}")
            return []
    
    def _get_user_expiring_licenses(self, user_id: str, days_ahead: int) -> List[Dict[str, Any]]:
        """Get user's licenses expiring within specified days"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT *, 
                        (expiration_date - CURRENT_DATE) as days_until_expiration
                        FROM user_licenses 
                        WHERE user_id = %s 
                        AND expiration_date <= %s 
                        AND status = 'active'
                        ORDER BY expiration_date ASC
                    """, (user_id, datetime.now() + timedelta(days=days_ahead)))
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting expiring licenses: {e}")
            return []
    
    def _check_missing_licenses(self, user_id: str) -> List[Dict[str, Any]]:
        """Check for missing required licenses based on business type"""
        try:
            # Get user's business information
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT business_type, location FROM users WHERE id = %s
                    """, (user_id,))
                    
                    user_data = cursor.fetchone()
                    if not user_data:
                        return []
                    
                    # Get required licenses for business type
                    required_licenses = self._get_required_licenses(
                        user_data["business_type"], 
                        json.loads(user_data["location"])
                    )
                    
                    # Get user's existing licenses
                    cursor.execute("""
                        SELECT license_type FROM user_licenses 
                        WHERE user_id = %s AND status = 'active'
                    """, (user_id,))
                    
                    existing_licenses = [row["license_type"] for row in cursor.fetchall()]
                    
                    # Find missing licenses
                    missing_licenses = []
                    for required_license in required_licenses:
                        if required_license["license_type"] not in existing_licenses:
                            missing_licenses.append(required_license)
                    
                    return missing_licenses
                    
        except Exception as e:
            logger.error(f"Error checking missing licenses: {e}")
            return []
    
    def _get_required_licenses(self, business_type: str, location: Dict[str, str]) -> List[Dict[str, Any]]:
        """Get required licenses for a business type and location"""
        # This would be a comprehensive mapping of business types to required licenses
        # For now, return basic requirements
        
        base_licenses = [
            {"license_type": "state_business", "required": True, "description": "State business license"},
            {"license_type": "city_business", "required": True, "description": "City business license"}
        ]
        
        # Add industry-specific requirements
        if business_type in ["restaurant", "food_service", "catering"]:
            base_licenses.append({
                "license_type": "health_permit",
                "required": True,
                "description": "Health department permit"
            })
        
        if business_type in ["construction", "contractor", "general_contractor"]:
            base_licenses.append({
                "license_type": "building_permit",
                "required": True,
                "description": "Building permit"
            })
        
        return base_licenses

def main():
    """Example usage of Business Licensing System"""
    
    # Initialize licensing system
    licensing_system = BusinessLicensingSystem("postgresql://user:password@localhost/legalops")
    
    # Example: Apply for EIN
    business_data = {
        "business_name": "Acme Consulting LLC",
        "business_type": "LLC",
        "address": {
            "street": "123 Main St",
            "city": "Miami",
            "state": "FL",
            "zip": "33101"
        },
        "responsible_party": {
            "name": "John Doe",
            "ssn": "123-45-6789"
        }
    }
    
    ein_result = licensing_system.apply_for_ein("user123", business_data)
    print(f"EIN Application: {ein_result}")
    
    # Example: Apply for business license
    license_result = licensing_system.apply_for_business_license(
        "user123", LicenseType.CITY_BUSINESS, business_data
    )
    print(f"Business License Application: {license_result}")
    
    # Example: Check compliance alerts
    alerts = licensing_system.get_compliance_alerts("user123")
    print(f"Compliance Alerts: {alerts}")

if __name__ == "__main__":
    main()
