"""
Secure Token Management System for NEXUS
Encrypted storage and management of API tokens and credentials
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from datetime import datetime, timezone, timedelta
import base64
from pathlib import Path

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Secure token management with encryption
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize token manager
        
        Args:
            encryption_key: Base64 encryption key (auto-generated if not provided)
        """
        self.storage_path = Path("/app/backend/.tokens")
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize encryption
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            key_path = self.storage_path / ".key"
            if key_path.exists():
                self.key = key_path.read_bytes()
            else:
                self.key = Fernet.generate_key()
                key_path.write_bytes(self.key)
                key_path.chmod(0o600)
        
        self.cipher = Fernet(self.key)
        logger.info("Token Manager initialized with encryption")
    
    def store_token(
        self,
        service: str,
        token: str,
        metadata: Optional[Dict] = None,
        expires_in_days: Optional[int] = None
    ) -> bool:
        """
        Store an encrypted token
        
        Args:
            service: Service name (e.g., 'github', 'cloudflare')
            token: The token to store
            metadata: Additional metadata
            expires_in_days: Token expiration in days
            
        Returns:
            Success status
        """
        try:
            # Encrypt token
            encrypted_token = self.cipher.encrypt(token.encode())
            
            # Prepare token data
            token_data = {
                "service": service,
                "encrypted_token": base64.b64encode(encrypted_token).decode(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
                "expires_at": None
            }
            
            if expires_in_days:
                expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
                token_data["expires_at"] = expires_at.isoformat()
            
            # Save to file
            token_file = self.storage_path / f"{service}.token"
            token_file.write_text(json.dumps(token_data, indent=2))
            token_file.chmod(0o600)
            
            logger.info(f"Token stored for {service}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store token for {service}: {e}")
            return False
    
    def get_token(self, service: str) -> Optional[str]:
        """
        Retrieve and decrypt a token
        
        Args:
            service: Service name
            
        Returns:
            Decrypted token or None
        """
        try:
            token_file = self.storage_path / f"{service}.token"
            if not token_file.exists():
                return None
            
            token_data = json.loads(token_file.read_text())
            
            # Check expiration
            if token_data.get("expires_at"):
                expires_at = datetime.fromisoformat(token_data["expires_at"])
                if datetime.now(timezone.utc) > expires_at:
                    logger.warning(f"Token for {service} has expired")
                    return None
            
            # Decrypt token
            encrypted_token = base64.b64decode(token_data["encrypted_token"])
            decrypted_token = self.cipher.decrypt(encrypted_token).decode()
            
            return decrypted_token
            
        except Exception as e:
            logger.error(f"Failed to retrieve token for {service}: {e}")
            return None
    
    def list_tokens(self) -> Dict[str, Dict]:
        """List all stored tokens (metadata only, no token values)"""
        tokens = {}
        
        for token_file in self.storage_path.glob("*.token"):
            try:
                token_data = json.loads(token_file.read_text())
                service = token_data["service"]
                
                # Return metadata only
                tokens[service] = {
                    "created_at": token_data["created_at"],
                    "expires_at": token_data.get("expires_at"),
                    "metadata": token_data.get("metadata", {}),
                    "status": self._check_token_status(token_data)
                }
            except Exception as e:
                logger.error(f"Error reading {token_file}: {e}")
        
        return tokens
    
    def _check_token_status(self, token_data: Dict) -> str:
        """Check if token is valid, expired, or expiring soon"""
        if not token_data.get("expires_at"):
            return "active"
        
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        now = datetime.now(timezone.utc)
        
        if now > expires_at:
            return "expired"
        elif (expires_at - now).days < 7:
            return "expiring_soon"
        else:
            return "active"
    
    def delete_token(self, service: str) -> bool:
        """Delete a stored token"""
        try:
            token_file = self.storage_path / f"{service}.token"
            if token_file.exists():
                token_file.unlink()
                logger.info(f"Token deleted for {service}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete token for {service}: {e}")
            return False
    
    def rotate_token(
        self,
        service: str,
        new_token: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Rotate a token (delete old, store new)"""
        self.delete_token(service)
        return self.store_token(service, new_token, metadata)
    
    def export_to_env(self, service: str, env_var_name: str) -> bool:
        """
        Export token to environment variable
        
        Args:
            service: Service name
            env_var_name: Environment variable name
            
        Returns:
            Success status
        """
        token = self.get_token(service)
        if token:
            os.environ[env_var_name] = token
            logger.info(f"Token exported to {env_var_name}")
            return True
        return False


# Singleton
_token_manager = None

def get_token_manager() -> TokenManager:
    """Get token manager singleton"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
