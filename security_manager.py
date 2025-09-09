#!/usr/bin/env python3
"""
Security Manager for Legal Ops Platform
Handles encryption, password hashing, MFA, and security event logging
"""

import os
import secrets
import hashlib
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyotp
import qrcode
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    ACCOUNT_LOCKED = "account_locked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    user_id: Optional[str]
    event_type: SecurityEventType
    event_details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    blocked: bool = False

class SecurityManager:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.master_key = self._get_master_key()
        self.fernet = Fernet(self.master_key)
        self.pepper = os.getenv('PASSWORD_PEPPER', 'default_pepper_change_in_production')
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    def _get_master_key(self):
        """Get or generate master encryption key"""
        key = os.getenv('MASTER_ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # In production, store securely in AWS KMS or Azure Key Vault
            logger.warning("Using generated master key - store securely in production!")
        return key
    
    # Data Encryption/Decryption
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive user data"""
        if not data:
            return data
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive user data"""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def generate_encryption_key(self, key_name: str, key_type: str) -> str:
        """Generate new encryption key"""
        try:
            key = Fernet.generate_key()
            encrypted_key = self.fernet.encrypt(key)
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO encryption_keys 
                        (key_name, key_type, encrypted_key, expires_at)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        key_name,
                        key_type,
                        encrypted_key.decode(),
                        datetime.utcnow() + timedelta(days=365)  # 1 year expiration
                    ))
            
            return key.decode()
            
        except Exception as e:
            logger.error(f"Error generating encryption key: {e}")
            return None
    
    # Password Management
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt and pepper"""
        try:
            # Add pepper to password
            peppered_password = password + self.pepper
            
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(peppered_password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            return None
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            # Add pepper to password
            peppered_password = password + self.pepper
            return bcrypt.checkpw(peppered_password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        issues = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        else:
            score += 1
        
        # Character variety checks
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        else:
            score += 1
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain at least one special character")
        else:
            score += 1
        
        # Common password check
        common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890", "abc123"
        ]
        
        if password.lower() in common_passwords:
            issues.append("Password is too common")
            score = 0
        
        # Determine strength
        if score >= 4:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "valid": len(issues) == 0,
            "strength": strength,
            "score": score,
            "issues": issues
        }
    
    # Multi-Factor Authentication (MFA)
    def generate_mfa_secret(self) -> str:
        """Generate MFA secret"""
        return pyotp.random_base32()
    
    def generate_mfa_qr_code(self, user_email: str, secret: str) -> str:
        """Generate QR code for MFA setup"""
        try:
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user_email,
                issuer_name="Legal Ops Platform"
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 string
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating MFA QR code: {e}")
            return None
    
    def verify_mfa_code(self, secret: str, code: str) -> bool:
        """Verify MFA code"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)  # Allow 1 window of tolerance
        except Exception as e:
            logger.error(f"MFA verification failed: {e}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for MFA"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    def setup_user_mfa(self, user_id: str, secret: str, backup_codes: List[str]) -> bool:
        """Setup MFA for user"""
        try:
            encrypted_secret = self.encrypt_sensitive_data(secret)
            encrypted_codes = [self.encrypt_sensitive_data(code) for code in backup_codes]
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_security_settings 
                        (user_id, mfa_enabled, mfa_secret, backup_codes)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET 
                            mfa_enabled = %s,
                            mfa_secret = %s,
                            backup_codes = %s,
                            updated_at = NOW()
                    """, (
                        user_id, True, encrypted_secret, encrypted_codes,
                        True, encrypted_secret, encrypted_codes
                    ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up MFA: {e}")
            return False
    
    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """Verify backup code"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT backup_codes FROM user_security_settings 
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    result = cursor.fetchone()
                    if not result:
                        return False
                    
                    encrypted_codes = result['backup_codes']
                    if not encrypted_codes:
                        return False
                    
                    # Check if code matches any backup code
                    for encrypted_code in encrypted_codes:
                        decrypted_code = self.decrypt_sensitive_data(encrypted_code)
                        if decrypted_code == code.upper():
                            # Remove used backup code
                            encrypted_codes.remove(encrypted_code)
                            cursor.execute("""
                                UPDATE user_security_settings 
                                SET backup_codes = %s, updated_at = NOW()
                                WHERE user_id = %s
                            """, (encrypted_codes, user_id))
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying backup code: {e}")
            return False
    
    # Security Event Logging
    def log_security_event(self, event: SecurityEvent):
        """Log security events for monitoring"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO security_audit_log 
                        (user_id, event_type, event_details, ip_address, 
                         user_agent, session_id, risk_level, blocked)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        event.user_id,
                        event.event_type.value,
                        json.dumps(event.event_details),
                        event.ip_address,
                        event.user_agent,
                        event.session_id,
                        event.risk_level.value,
                        event.blocked
                    ))
            
            # Log to application log as well
            logger.info(f"Security event: {event.event_type.value} for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def log_data_access(self, user_id: str, data_type: str, data_id: str, 
                       access_type: str, access_reason: str = None,
                       ip_address: str = None, user_agent: str = None):
        """Log data access events"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO data_access_log 
                        (user_id, data_type, data_id, access_type, 
                         access_reason, ip_address, user_agent)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id, data_type, data_id, access_type,
                        access_reason, ip_address, user_agent
                    ))
            
        except Exception as e:
            logger.error(f"Error logging data access: {e}")
    
    # Account Security
    def check_account_lockout(self, user_id: str) -> Dict[str, Any]:
        """Check if account is locked out"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT failed_login_attempts, account_locked_until
                        FROM user_security_settings 
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    result = cursor.fetchone()
                    if not result:
                        return {"locked": False, "attempts": 0}
                    
                    attempts = result['failed_login_attempts'] or 0
                    locked_until = result['account_locked_until']
                    
                    if locked_until and datetime.utcnow() < locked_until:
                        return {
                            "locked": True,
                            "attempts": attempts,
                            "locked_until": locked_until
                        }
                    
                    return {"locked": False, "attempts": attempts}
                    
        except Exception as e:
            logger.error(f"Error checking account lockout: {e}")
            return {"locked": False, "attempts": 0}
    
    def increment_failed_login(self, user_id: str) -> bool:
        """Increment failed login attempts"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_security_settings 
                        (user_id, failed_login_attempts)
                        VALUES (%s, 1)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET 
                            failed_login_attempts = user_security_settings.failed_login_attempts + 1,
                            updated_at = NOW()
                    """, (user_id,))
                    
                    # Check if we need to lock account
                    cursor.execute("""
                        SELECT failed_login_attempts FROM user_security_settings 
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    result = cursor.fetchone()
                    if result and result['failed_login_attempts'] >= 5:
                        # Lock account for 30 minutes
                        lock_until = datetime.utcnow() + timedelta(minutes=30)
                        cursor.execute("""
                            UPDATE user_security_settings 
                            SET account_locked_until = %s, updated_at = NOW()
                            WHERE user_id = %s
                        """, (lock_until, user_id))
                        
                        # Log security event
                        self.log_security_event(SecurityEvent(
                            user_id=user_id,
                            event_type=SecurityEventType.ACCOUNT_LOCKED,
                            event_details={"reason": "too_many_failed_attempts"},
                            risk_level=RiskLevel.HIGH,
                            blocked=True
                        ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing failed login: {e}")
            return False
    
    def reset_failed_login_attempts(self, user_id: str):
        """Reset failed login attempts"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_security_settings 
                        SET failed_login_attempts = 0, account_locked_until = NULL, 
                            updated_at = NOW()
                        WHERE user_id = %s
                    """, (user_id,))
                    
        except Exception as e:
            logger.error(f"Error resetting failed login attempts: {e}")
    
    # Privacy and Data Management
    def get_user_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user privacy settings"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM user_privacy_settings 
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        return dict(result)
                    else:
                        # Return default settings
                        return {
                            "data_sharing_preferences": {},
                            "marketing_consent": False,
                            "analytics_consent": False,
                            "third_party_sharing": False,
                            "data_portability": True,
                            "right_to_deletion": True
                        }
                        
        except Exception as e:
            logger.error(f"Error getting privacy settings: {e}")
            return {}
    
    def update_user_privacy_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """Update user privacy settings"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_privacy_settings 
                        (user_id, data_sharing_preferences, marketing_consent, 
                         analytics_consent, third_party_sharing, data_portability, 
                         right_to_deletion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET 
                            data_sharing_preferences = %s,
                            marketing_consent = %s,
                            analytics_consent = %s,
                            third_party_sharing = %s,
                            data_portability = %s,
                            right_to_deletion = %s,
                            updated_at = NOW()
                    """, (
                        user_id,
                        json.dumps(settings.get('data_sharing_preferences', {})),
                        settings.get('marketing_consent', False),
                        settings.get('analytics_consent', False),
                        settings.get('third_party_sharing', False),
                        settings.get('data_portability', True),
                        settings.get('right_to_deletion', True),
                        json.dumps(settings.get('data_sharing_preferences', {})),
                        settings.get('marketing_consent', False),
                        settings.get('analytics_consent', False),
                        settings.get('third_party_sharing', False),
                        settings.get('data_portability', True),
                        settings.get('right_to_deletion', True)
                    ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating privacy settings: {e}")
            return False
    
    # Data Retention
    def get_data_retention_policies(self) -> List[Dict[str, Any]]:
        """Get data retention policies"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM data_retention_policies 
                        WHERE is_active = TRUE
                        ORDER BY data_type
                    """)
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting retention policies: {e}")
            return []
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data based on retention policies"""
        try:
            policies = self.get_data_retention_policies()
            cleanup_stats = {}
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    for policy in policies:
                        data_type = policy['data_type']
                        retention_days = policy['retention_period_days']
                        auto_delete = policy['auto_delete']
                        
                        if not auto_delete:
                            continue
                        
                        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                        
                        # Clean up based on data type
                        if data_type == 'ai_usage_log':
                            cursor.execute("""
                                DELETE FROM ai_usage_log 
                                WHERE created_at < %s
                            """, (cutoff_date,))
                            cleanup_stats[data_type] = cursor.rowcount
                        
                        elif data_type == 'data_access_log':
                            cursor.execute("""
                                DELETE FROM data_access_log 
                                WHERE created_at < %s
                            """, (cutoff_date,))
                            cleanup_stats[data_type] = cursor.rowcount
                        
                        # Add more data types as needed
            
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")
            return {}

def main():
    """Example usage of Security Manager"""
    
    # Initialize security manager
    security_manager = SecurityManager("postgresql://user:password@localhost/legalops")
    
    # Example: Hash password
    password = "SecurePassword123!"
    hashed = security_manager.hash_password(password)
    print(f"Password hashed: {hashed}")
    
    # Example: Verify password
    is_valid = security_manager.verify_password(password, hashed)
    print(f"Password valid: {is_valid}")
    
    # Example: Generate MFA secret
    secret = security_manager.generate_mfa_secret()
    print(f"MFA secret: {secret}")
    
    # Example: Generate QR code
    qr_code = security_manager.generate_mfa_qr_code("user@example.com", secret)
    print(f"QR code generated: {qr_code[:50]}...")
    
    # Example: Log security event
    event = SecurityEvent(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        event_type=SecurityEventType.LOGIN,
        event_details={"method": "password", "success": True},
        ip_address="192.168.1.1",
        risk_level=RiskLevel.LOW
    )
    security_manager.log_security_event(event)
    print("Security event logged")

if __name__ == "__main__":
    main()
