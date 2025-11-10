# -*- coding: utf-8 -*-
import time, random, requests
from typing import Dict, Any, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as UrllibRetry

# Global session with connection pooling for better performance
_session = None

def _get_session():
    """Get or create global session with connection pooling"""
    global _session
    if _session is None:
        _session = requests.Session()
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # We handle retries ourselves
        )
        _session.mount("http://", adapter)
        _session.mount("https://", adapter)
    return _session


def _knob(name:str, default):
    from services.core.config import load as load_config
    c = load_config()
    return c.get('resilience', {}).get(name, default)

RETRY_STATUS = {429, 500, 502, 503, 504}

def _sleep(i:int):
    # base_backoff_sec with full jitter; capped
    base = min((_knob('base_backoff_sec', 1.2) ** i), _knob('max_backoff_sec', 30.0))
    time.sleep(random.random() * base)

def request_json(method:str, url:str, *, headers:Dict[str,str]=None, params:Dict[str,Any]=None,
                 json_body:Any=None, data:Any=None, timeout=None) -> Tuple[bool, Any, str, int, Dict[str,str]]:
    sess = _get_session()  # Use pooled session instead of creating new one
    max_attempts = int(_knob('max_attempts', 5))
    timeout = timeout or (_knob('conn_timeout', 15), _knob('read_timeout', 60))
    last_err, last_code, last_headers = "", 0, {}
    for attempt in range(1, max_attempts+1):
        try:
            r = sess.request(method=method, url=url, headers=headers, params=params, json=json_body,
                             data=data, timeout=timeout)
            last_code = r.status_code; last_headers = dict(r.headers or {})
            if 200 <= r.status_code < 300:
                try:
                    return True, (r.json() if r.content else {}), "", r.status_code, last_headers
                except Exception:
                    return True, r.text, "", r.status_code, last_headers
            if r.status_code in RETRY_STATUS:
                last_err = f"HTTP {r.status_code}: {r.text[:300]}"
                _sleep(attempt)
                continue
            return False, None, f"HTTP {r.status_code}: {r.text[:500]}", r.status_code, last_headers
        except requests.RequestException as e:
            last_err = f"REQ ERR: {e}"
            _sleep(attempt)
            continue
    return False, None, last_err or "exhausted", last_code, last_headers
