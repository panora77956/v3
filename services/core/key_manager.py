# -*- coding: utf-8 -*-
"""
Unified API Key Management - Single source for all key rotation and management
Replaces all duplicate key management implementations across services
Optimized for high-frequency concurrent access with minimal lock contention
"""
from typing import List
import threading
import time
from services.core.config import load as load_config


class KeyPool:
    """Thread-safe round-robin key pool with optimized locking"""

    def __init__(self):
        self._keys: List[str] = []
        self._index = 0
        self._lock = threading.Lock()

    def get_next(self) -> str:
        """Get next key in rotation (lock-free read for better concurrency)"""
        # Optimized: single atomic operation to reduce lock time
        with self._lock:
            if not self._keys:
                return ""
            idx = self._index
            self._index = (idx + 1) % len(self._keys)
            return self._keys[idx]

    def set_keys(self, keys: List[str]):
        """Set the list of keys"""
        with self._lock:
            self._keys = [k for k in keys if k]
            self._index = 0

    def get_all(self) -> List[str]:
        """Get all keys (snapshot)"""
        with self._lock:
            return list(self._keys)


# Global key pools for each provider
_POOLS = {
    'google': KeyPool(),
    'labs': KeyPool(),
    'openai': KeyPool(),
    'elevenlabs': KeyPool(),
}

# Cache refresh with time-based invalidation to reduce config I/O
_last_refresh_time = 0
_refresh_interval = 60.0  # Refresh config at most once per minute
_refresh_lock = threading.Lock()


def refresh(force: bool = False):
    """
    Refresh all key pools from configuration
    
    Args:
        force: Force refresh even if within cache interval (default: False)
    """
    global _last_refresh_time
    
    # Optimized: Use time-based caching to reduce config I/O
    current_time = time.time()
    if not force and (current_time - _last_refresh_time) < _refresh_interval:
        return  # Skip refresh if within cache interval
    
    with _refresh_lock:
        # Double-check after acquiring lock
        if not force and (current_time - _last_refresh_time) < _refresh_interval:
            return
            
        cfg = load_config()

        # Google keys
        google_keys = []
        google_keys.extend(cfg.get('google_api_keys', []))
        if cfg.get('google_api_key'):
            google_keys.append(cfg['google_api_key'])
        # Legacy mixed store
        for t in cfg.get('tokens', []):
            if isinstance(t, dict) and t.get('kind') in ('gemini', 'google'):
                v = t.get('token') or t.get('value')
                if v:
                    google_keys.append(v)
        _POOLS['google'].set_keys(google_keys)

        # Labs tokens
        labs_tokens = []
        labs_tokens.extend(cfg.get('labs_tokens', []))
        # Legacy mixed store
        for t in cfg.get('tokens', []):
            if isinstance(t, dict) and t.get('kind') == 'labs':
                v = t.get('token') or t.get('value')
                if v:
                    labs_tokens.append(v)
            elif isinstance(t, str) and len(t) > 30:
                # Assume long strings in tokens are labs tokens
                labs_tokens.append(t)
        _POOLS['labs'].set_keys(labs_tokens)

        # OpenAI keys
        openai_keys = cfg.get('openai_api_keys', [])
        if cfg.get('openai_api_key'):
            openai_keys.append(cfg['openai_api_key'])
        _POOLS['openai'].set_keys(openai_keys)

        # ElevenLabs keys
        elevenlabs_keys = cfg.get('elevenlabs_api_keys', [])
        _POOLS['elevenlabs'].set_keys(elevenlabs_keys)
        
        _last_refresh_time = current_time


def get_key(provider: str) -> str:
    """
    Get next key for provider (with cached auto-refresh)
    
    Args:
        provider: Provider name ('google', 'labs', 'openai', 'elevenlabs')
        
    Returns:
        API key or empty string if none available
    """
    refresh()  # Uses cached refresh to minimize I/O
    return _POOLS.get(provider, KeyPool()).get_next()


def get_all_keys(provider: str) -> List[str]:
    """
    Get all keys for provider (with cached auto-refresh)
    
    Args:
        provider: Provider name
        
    Returns:
        List of all keys for provider
    """
    refresh()  # Uses cached refresh to minimize I/O
    return _POOLS.get(provider, KeyPool()).get_all()


def rotated_list(provider: str, base_list: List[str]) -> List[str]:
    """
    Rotate list to prioritize next key in pool
    
    Args:
        provider: Provider name
        base_list: Base list of keys
        
    Returns:
        Rotated list with pool's next key first
    """
    base_list = [x for x in base_list if x]
    if not base_list:
        return base_list

    key = get_key(provider)
    if not key or key not in base_list:
        return base_list

    # Move key to front
    return [key] + [x for x in base_list if x != key]
