# -*- coding: utf-8 -*-
"""
Vertex AI Service Account Manager
Manages multiple GCP service accounts for Vertex AI authentication
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class VertexServiceAccount:
    """Represents a Vertex AI service account"""
    name: str
    project_id: str
    credentials_json: str  # Full JSON content as string
    location: str = "us-central1"
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VertexServiceAccount':
        """Create from dictionary"""
        return cls(**data)
    
    def get_credentials_dict(self) -> Dict:
        """Parse credentials JSON string to dict"""
        try:
            return json.loads(self.credentials_json)
        except json.JSONDecodeError:
            return {}


class VertexServiceAccountManager:
    """Manages multiple Vertex AI service accounts"""
    
    def __init__(self):
        self.accounts: List[VertexServiceAccount] = []
        self.current_index = 0  # For round-robin
        
    def load_from_config(self, config: Dict):
        """Load service accounts from config"""
        self.accounts = []
        vertex_config = config.get('vertex_ai', {})
        
        # Load service accounts if they exist
        accounts_data = vertex_config.get('service_accounts', [])
        for account_data in accounts_data:
            try:
                account = VertexServiceAccount.from_dict(account_data)
                self.accounts.append(account)
            except Exception as e:
                print(f"[VertexAccountMgr] Failed to load account: {e}")
        
        # Fallback: create account from old config format if no accounts exist
        if not self.accounts:
            project_id = vertex_config.get('project_id', '')
            if project_id:
                # Create a placeholder account without credentials
                # (will use Application Default Credentials)
                self.accounts.append(VertexServiceAccount(
                    name="Default Account",
                    project_id=project_id,
                    credentials_json="",  # Empty = use ADC
                    location=vertex_config.get('location', 'us-central1'),
                    enabled=vertex_config.get('enabled', False)
                ))
    
    def save_to_config(self, config: Dict):
        """Save service accounts to config"""
        if 'vertex_ai' not in config:
            config['vertex_ai'] = {}
        
        # Save accounts
        config['vertex_ai']['service_accounts'] = [
            account.to_dict() for account in self.accounts
        ]
        
        # Also keep enabled flag and use_vertex_first at top level for compatibility
        config['vertex_ai']['enabled'] = any(acc.enabled for acc in self.accounts)
        
        # Set default location from first account if exists
        if self.accounts:
            config['vertex_ai']['location'] = self.accounts[0].location
    
    def get_all_accounts(self) -> List[VertexServiceAccount]:
        """Get all service accounts"""
        return self.accounts
    
    def get_enabled_accounts(self) -> List[VertexServiceAccount]:
        """Get only enabled service accounts"""
        return [acc for acc in self.accounts if acc.enabled]
    
    def add_account(self, account: VertexServiceAccount):
        """Add a new service account"""
        self.accounts.append(account)
    
    def update_account(self, index: int, account: VertexServiceAccount):
        """Update an existing service account"""
        if 0 <= index < len(self.accounts):
            self.accounts[index] = account
    
    def remove_account(self, index: int):
        """Remove a service account"""
        if 0 <= index < len(self.accounts):
            del self.accounts[index]
    
    def enable_account(self, index: int):
        """Enable a service account"""
        if 0 <= index < len(self.accounts):
            self.accounts[index].enabled = True
    
    def disable_account(self, index: int):
        """Disable a service account"""
        if 0 <= index < len(self.accounts):
            self.accounts[index].enabled = False
    
    def get_next_account(self) -> Optional[VertexServiceAccount]:
        """
        Get next enabled account using round-robin
        Returns None if no enabled accounts
        """
        enabled = self.get_enabled_accounts()
        if not enabled:
            return None
        
        # Round-robin through enabled accounts
        account = enabled[self.current_index % len(enabled)]
        self.current_index += 1
        
        return account
    
    def validate_credentials_json(self, json_str: str) -> tuple[bool, str]:
        """
        Validate service account credentials JSON
        
        Returns:
            (is_valid, error_message)
        """
        try:
            creds = json.loads(json_str)
            
            # Check required fields
            required_fields = [
                'type', 'project_id', 'private_key_id', 'private_key',
                'client_email', 'client_id', 'auth_uri', 'token_uri'
            ]
            
            missing = [f for f in required_fields if f not in creds]
            if missing:
                return False, f"Missing required fields: {', '.join(missing)}"
            
            # Check type
            if creds.get('type') != 'service_account':
                return False, f"Invalid type: {creds.get('type')}. Expected 'service_account'"
            
            # Check private key format
            private_key = creds.get('private_key', '')
            if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                return False, "Invalid private key format"
            
            return True, "Valid"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"


# Global instance
_vertex_account_manager = None


def get_vertex_account_manager() -> VertexServiceAccountManager:
    """Get global vertex account manager instance"""
    global _vertex_account_manager
    if _vertex_account_manager is None:
        _vertex_account_manager = VertexServiceAccountManager()
    return _vertex_account_manager
