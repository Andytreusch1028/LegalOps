#!/usr/bin/env python3
"""
Modern Authentication System for Legal Ops Platform
Implements passkeys, magic links, and risk-based authentication
"""

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
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationMethod(Enum):
    PASSKEY = "passkey"
    MAGIC_LINK = "magic_link"
    SMS = "sms"
    EMAIL = "email"
    PASSWORD = "password"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuthenticationResult:
    success: bool
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    additional_verification_required: bool = False
    error_message: Optional[str] = None

class ModernAuthenticationManager:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.rp_id = "legalops.com"  # Relying Party ID
        self.rp_name = "Legal Ops Platform"
        self.origin = "https://legalops.com"
        self.master_key = self._get_master_key()
        self.fernet = Fernet(self.master_key)
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_connection_string, cursor_factory=RealDictCursor)
    
    def _get_master_key(self):
        """Get or generate master encryption key"""
        import os
        key = os.getenv('MASTER_ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # In production, store securely
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    # Passkey Management
    def generate_passkey_registration_options(self, user_id: str, username: str) -> Dict[str, Any]:
        """Generate passkey registration options"""
        try:
            # In production, use webauthn library
            # For now, return mock options
            challenge = secrets.token_urlsafe(32)
            
            options = {
                "challenge": challenge,
                "rp": {
                    "id": self.rp_id,
                    "name": self.rp_name
                },
                "user": {
                    "id": user_id,
                    "name": username,
                    "displayName": username
                },
                "pubKeyCredParams": [
                    {"type": "public-key", "alg": -7},  # ES256
                    {"type": "public-key", "alg": -257}  # RS256
                ],
                "authenticatorSelection": {
                    "authenticatorAttachment": "platform",
                    "userVerification": "required",
                    "residentKey": "required"
                },
                "timeout": 60000,
                "attestation": "direct"
            }
            
            # Store challenge for verification
            self._store_challenge(user_id, challenge, "registration")
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating passkey registration options: {e}")
            return {}
    
    def verify_passkey_registration(self, user_id: str, response_data: Dict[str, Any]) -> bool:
        """Verify passkey registration response"""
        try:
            # In production, use webauthn library for verification
            # For now, simulate successful verification
            
            credential_id = response_data.get('id')
            public_key = response_data.get('response', {}).get('publicKey')
            
            if not credential_id or not public_key:
                return False
            
            # Store passkey credential
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO passkey_credentials 
                        (user_id, credential_id, public_key, device_name, device_type)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        credential_id,
                        public_key,
                        response_data.get('device_name', 'Unknown Device'),
                        response_data.get('device_type', 'unknown')
                    ))
            
            # Add passkey as authentication method
            self._add_authentication_method(user_id, AuthenticationMethod.PASSKEY, {
                "credential_id": credential_id,
                "device_name": response_data.get('device_name', 'Unknown Device')
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying passkey registration: {e}")
            return False
    
    def generate_passkey_authentication_options(self, user_id: str) -> Dict[str, Any]:
        """Generate passkey authentication options"""
        try:
            # Get user's passkey credentials
            credentials = self._get_user_passkey_credentials(user_id)
            
            challenge = secrets.token_urlsafe(32)
            
            options = {
                "challenge": challenge,
                "timeout": 60000,
                "rpId": self.rp_id,
                "allowCredentials": credentials,
                "userVerification": "required"
            }
            
            # Store challenge for verification
            self._store_challenge(user_id, challenge, "authentication")
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating passkey authentication options: {e}")
            return {}
    
    def verify_passkey_authentication(self, user_id: str, response_data: Dict[str, Any]) -> AuthenticationResult:
        """Verify passkey authentication response"""
        try:
            # In production, use webauthn library for verification
            # For now, simulate successful verification
            
            credential_id = response_data.get('id')
            if not credential_id:
                return AuthenticationResult(success=False, error_message="Invalid credential")
            
            # Get stored credential
            credential = self._get_passkey_credential(credential_id)
            if not credential:
                return AuthenticationResult(success=False, error_message="Credential not found")
            
            # Verify credential belongs to user
            if credential['user_id'] != user_id:
                return AuthenticationResult(success=False, error_message="Credential mismatch")
            
            # Update last used timestamp
            self._update_passkey_last_used(credential_id)
            
            # Create session
            session_token = self._create_authentication_session(
                user_id, AuthenticationMethod.PASSKEY, response_data
            )
            
            return AuthenticationResult(
                success=True,
                user_id=user_id,
                session_token=session_token,
                risk_level=RiskLevel.LOW
            )
            
        except Exception as e:
            logger.error(f"Error verifying passkey authentication: {e}")
            return AuthenticationResult(success=False, error_message="Authentication failed")
    
    # Magic Link Authentication
    def generate_magic_link(self, user_id: str, email: str) -> str:
        """Generate magic link for authentication"""
        try:
            # Create secure token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Store token in database
            expires_at = datetime.utcnow() + timedelta(minutes=15)
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO magic_link_tokens 
                        (user_id, token_hash, email, expires_at)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, token_hash, email, expires_at))
            
            # Generate magic link
            magic_link = f"https://legalops.com/auth/magic-link?token={token}"
            return magic_link
            
        except Exception as e:
            logger.error(f"Error generating magic link: {e}")
            return None
    
    def verify_magic_link(self, token: str, ip_address: str = None, user_agent: str = None) -> AuthenticationResult:
        """Verify magic link token"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Check token in database
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT user_id, email, expires_at, used_at
                        FROM magic_link_tokens 
                        WHERE token_hash = %s
                    """, (token_hash,))
                    
                    token_data = cursor.fetchone()
            
            if not token_data:
                return AuthenticationResult(success=False, error_message="Invalid token")
            
            if datetime.utcnow() > token_data['expires_at']:
                return AuthenticationResult(success=False, error_message="Token expired")
            
            if token_data['used_at']:
                return AuthenticationResult(success=False, error_message="Token already used")
            
            # Mark token as used
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE magic_link_tokens 
                        SET used_at = NOW(), ip_address = %s, user_agent = %s
                        WHERE token_hash = %s
                    """, (ip_address, user_agent, token_hash))
            
            # Create session
            session_token = self._create_authentication_session(
                token_data['user_id'], AuthenticationMethod.MAGIC_LINK, {
                    "email": token_data['email'],
                    "ip_address": ip_address,
                    "user_agent": user_agent
                }
            )
            
            return AuthenticationResult(
                success=True,
                user_id=token_data['user_id'],
                session_token=session_token,
                risk_level=RiskLevel.LOW
            )
            
        except Exception as e:
            logger.error(f"Error verifying magic link: {e}")
            return AuthenticationResult(success=False, error_message="Authentication failed")
    
    # Risk Assessment
    def assess_authentication_risk(self, user_id: str, ip_address: str, 
                                 user_agent: str, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess authentication risk based on various factors"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Check for new device
            device_fingerprint = self._generate_device_fingerprint(user_agent, ip_address)
            if not self._is_trusted_device(user_id, device_fingerprint):
                risk_score += 0.3
                risk_factors.append("new_device")
            
            # Check for unusual location
            if not self._is_usual_location(user_id, location_data):
                risk_score += 0.4
                risk_factors.append("unusual_location")
            
            # Check for unusual time
            if not self._is_usual_time(user_id):
                risk_score += 0.2
                risk_factors.append("unusual_time")
            
            # Check for suspicious patterns
            if self._has_suspicious_patterns(user_id, ip_address):
                risk_score += 0.5
                risk_factors.append("suspicious_patterns")
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 0.5:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.3:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Store risk assessment
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO authentication_risk 
                        (user_id, risk_factors, risk_score, risk_level, 
                         additional_verification_required, blocked)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        json.dumps(risk_factors),
                        risk_score,
                        risk_level.value,
                        risk_score >= 0.5,
                        risk_score >= 0.8
                    ))
            
            return {
                "risk_score": risk_score,
                "risk_level": risk_level.value,
                "risk_factors": risk_factors,
                "additional_verification_required": risk_score >= 0.5,
                "blocked": risk_score >= 0.8
            }
            
        except Exception as e:
            logger.error(f"Error assessing authentication risk: {e}")
            return {
                "risk_score": 1.0,
                "risk_level": RiskLevel.CRITICAL.value,
                "risk_factors": ["assessment_error"],
                "additional_verification_required": True,
                "blocked": True
            }
    
    # Session Management
    def _create_authentication_session(self, user_id: str, method: AuthenticationMethod, 
                                     context: Dict[str, Any]) -> str:
        """Create authentication session"""
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO authentication_sessions 
                        (user_id, session_token, authentication_method, 
                         device_fingerprint, ip_address, user_agent, 
                         location_data, expires_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        session_token,
                        method.value,
                        context.get('device_fingerprint'),
                        context.get('ip_address'),
                        context.get('user_agent'),
                        json.dumps(context.get('location_data', {})),
                        expires_at
                    ))
            
            return session_token
            
        except Exception as e:
            logger.error(f"Error creating authentication session: {e}")
            return None
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate authentication session"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT user_id, authentication_method, expires_at, is_active
                        FROM authentication_sessions 
                        WHERE session_token = %s
                    """, (session_token,))
                    
                    session_data = cursor.fetchone()
            
            if not session_data:
                return {"valid": False, "error": "Session not found"}
            
            if not session_data['is_active']:
                return {"valid": False, "error": "Session inactive"}
            
            if datetime.utcnow() > session_data['expires_at']:
                return {"valid": False, "error": "Session expired"}
            
            # Update last activity
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE authentication_sessions 
                        SET last_activity = NOW()
                        WHERE session_token = %s
                    """, (session_token,))
            
            return {
                "valid": True,
                "user_id": session_data['user_id'],
                "authentication_method": session_data['authentication_method']
            }
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return {"valid": False, "error": "Session validation failed"}
    
    # Helper Methods
    def _get_user_passkey_credentials(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's passkey credentials"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT credential_id, device_name
                        FROM passkey_credentials 
                        WHERE user_id = %s AND is_active = TRUE
                    """, (user_id,))
                    
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting passkey credentials: {e}")
            return []
    
    def _get_passkey_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get passkey credential by ID"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT user_id, public_key, counter
                        FROM passkey_credentials 
                        WHERE credential_id = %s AND is_active = TRUE
                    """, (credential_id,))
                    
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting passkey credential: {e}")
            return None
    
    def _update_passkey_last_used(self, credential_id: str):
        """Update passkey last used timestamp"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE passkey_credentials 
                        SET last_used = NOW()
                        WHERE credential_id = %s
                    """, (credential_id,))
        except Exception as e:
            logger.error(f"Error updating passkey last used: {e}")
    
    def _generate_device_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Generate device fingerprint"""
        fingerprint_data = f"{user_agent}:{ip_address}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def _is_trusted_device(self, user_id: str, device_fingerprint: str) -> bool:
        """Check if device is trusted"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) as count
                        FROM trusted_devices 
                        WHERE user_id = %s AND device_fingerprint = %s AND is_trusted = TRUE
                    """, (user_id, device_fingerprint))
                    
                    result = cursor.fetchone()
                    return result['count'] > 0
        except Exception as e:
            logger.error(f"Error checking trusted device: {e}")
            return False
    
    def _is_usual_location(self, user_id: str, location_data: Dict[str, Any]) -> bool:
        """Check if location is usual for user"""
        # Simplified implementation - in production, use more sophisticated location analysis
        return True
    
    def _is_usual_time(self, user_id: str) -> bool:
        """Check if login time is usual for user"""
        # Simplified implementation - in production, analyze user's login patterns
        return True
    
    def _has_suspicious_patterns(self, user_id: str, ip_address: str) -> bool:
        """Check for suspicious login patterns"""
        # Simplified implementation - in production, use ML-based anomaly detection
        return False
    
    def _store_challenge(self, user_id: str, challenge: str, challenge_type: str):
        """Store challenge for verification"""
        # In production, store in Redis or similar with expiration
        pass
    
    def _add_authentication_method(self, user_id: str, method: AuthenticationMethod, data: Dict[str, Any]):
        """Add authentication method for user"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO authentication_methods 
                        (user_id, method_type, method_data, is_primary)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, method.value, json.dumps(data), False))
        except Exception as e:
            logger.error(f"Error adding authentication method: {e}")

def main():
    """Example usage of Modern Authentication System"""
    
    # Initialize authentication manager
    auth_manager = ModernAuthenticationManager("postgresql://user:password@localhost/legalops")
    
    # Example: Generate magic link
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    email = "user@example.com"
    
    magic_link = auth_manager.generate_magic_link(user_id, email)
    print(f"Magic link generated: {magic_link}")
    
    # Example: Verify magic link
    result = auth_manager.verify_magic_link("sample_token")
    if result.success:
        print(f"Authentication successful: {result.user_id}")
        print(f"Session token: {result.session_token}")
    else:
        print(f"Authentication failed: {result.error_message}")

if __name__ == "__main__":
    main()
