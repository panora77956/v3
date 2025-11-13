# -*- coding: utf-8 -*-
import requests, time, random, json
from typing import List, Optional
from services.core.key_manager import get_all_keys, refresh
from services.core.api_config import GEMINI_TEXT_MODEL, gemini_text_endpoint

class MissingAPIKey(Exception): pass

class GeminiClient:
    """
    Gemini Client with Vertex AI support
    
    This client now supports both AI Studio (with API keys) and Vertex AI (with GCP project).
    It will automatically try Vertex AI first if configured, then fallback to AI Studio.
    """
    
    def __init__(self, model: str = None, api_key: Optional[str] = None, use_vertex: bool = True):
        """
        Initialize Gemini client
        
        Args:
            model: Model name (optional, defaults to GEMINI_TEXT_MODEL)
            api_key: API key override (optional)
            use_vertex: Try to use Vertex AI first (default: True)
        """
        refresh()
        keys: List[str] = get_all_keys('google')
        if api_key: keys = [api_key] + [k for k in keys if k != api_key]
        self.keys = list(dict.fromkeys(keys))
        
        # Initialize Vertex AI client if enabled
        self.vertex_client = None
        self.use_vertex = use_vertex
        
        if use_vertex:
            try:
                self.vertex_client = self._init_vertex_ai(model)
            except Exception as e:
                print(f"[GeminiClient] Could not initialize Vertex AI: {e}")
                print(f"[GeminiClient] Falling back to AI Studio API")
        
        # Fallback to AI Studio if Vertex AI not available or disabled
        if not self.vertex_client and not self.keys:
            raise MissingAPIKey("Chưa nhập Google API Key trong Cài đặt và Vertex AI chưa được cấu hình.")
        
        if self.keys:
            random.shuffle(self.keys)
        
        self.rr = 0
        self.model = model or GEMINI_TEXT_MODEL
    
    def _init_vertex_ai(self, model: Optional[str]):
        """
        Initialize Vertex AI client if configuration is available
        Uses service account manager for round-robin across multiple accounts
        
        Returns:
            VertexAIClient instance or None
        """
        try:
            # Load config from user config file (not project config.json)
            from utils import config as cfg
            config = cfg.load()
            
            vertex_config = config.get('vertex_ai', {})
            
            # Check if Vertex AI is enabled
            if not vertex_config.get('enabled', False):
                return None
            
            # Try to use service account manager
            try:
                from services.vertex_service_account_manager import get_vertex_account_manager
                
                account_mgr = get_vertex_account_manager()
                account_mgr.load_from_config(config)
                
                # Get next enabled account
                account = account_mgr.get_next_account()
                
                if account:
                    # Import and create Vertex AI client with service account
                    from services.vertex_ai_client import VertexAIClient
                    from services.core.api_config import VERTEX_AI_TEXT_MODEL
                    
                    vertex_model = model or VERTEX_AI_TEXT_MODEL
                    api_key = self.keys[0] if self.keys else None
                    
                    client = VertexAIClient(
                        model=vertex_model,
                        project_id=account.project_id,
                        location=account.location,
                        api_key=api_key,
                        use_vertex=True,
                        credentials_json=account.credentials_json if account.credentials_json else None
                    )
                    
                    print(f"[GeminiClient] Vertex AI initialized with account: {account.name}")
                    return client
                else:
                    print("[GeminiClient] No enabled Vertex AI service accounts found")
                    return None
                    
            except ImportError:
                # Fallback to old config format if service account manager not available
                project_id = vertex_config.get('project_id', '')
                location = vertex_config.get('location', 'us-central1')
                
                if not project_id:
                    print("[GeminiClient] Vertex AI enabled but project_id not configured")
                    return None
                
                from services.vertex_ai_client import VertexAIClient
                from services.core.api_config import VERTEX_AI_TEXT_MODEL
                
                vertex_model = model or VERTEX_AI_TEXT_MODEL
                api_key = self.keys[0] if self.keys else None
                
                client = VertexAIClient(
                    model=vertex_model,
                    project_id=project_id,
                    location=location,
                    api_key=api_key,
                    use_vertex=True
                )
                
                print(f"[GeminiClient] Vertex AI initialized successfully (legacy config)")
                return client
            
        except Exception as e:
            print(f"[GeminiClient] Failed to initialize Vertex AI: {e}")
            return None
    
    def _next_key(self):
        k = self.keys[self.rr % len(self.keys)]
        self.rr += 1
        return k
    
    def _endpoint(self, key):
        if self.model == GEMINI_TEXT_MODEL:
            return gemini_text_endpoint(key)
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={key}"
    
    def generate(self, system_text: str, user_text: str, timeout: int = 180) -> str:
        """
        Generate content using Gemini (Vertex AI or AI Studio)
        
        Args:
            system_text: System instruction
            user_text: User prompt
            timeout: Request timeout in seconds
            
        Returns:
            Generated text
        """
        # Try Vertex AI first if available
        if self.vertex_client:
            try:
                return self.vertex_client.generate_content(
                    prompt=user_text,
                    system_instruction=system_text,
                    temperature=0.9,
                    timeout=timeout,
                    max_retries=5
                )
            except Exception as e:
                print(f"[GeminiClient] Vertex AI failed: {e}")
                print(f"[GeminiClient] Falling back to AI Studio API")
                # Continue to AI Studio fallback below
        
        # Fallback to AI Studio with API keys
        if not self.keys:
            raise MissingAPIKey("No API keys available and Vertex AI failed")
        
        last = None
        for i in range(5):
            key = self._next_key()
            try:
                body = {
                    "system_instruction": {"parts": [{"text": system_text}]},
                    "contents": [{"role": "user", "parts": [{"text": user_text}]}]
                }
                r = requests.post(self._endpoint(key), json=body, timeout=timeout)
                if r.status_code in (429, 408) or r.status_code >= 500:
                    raise requests.HTTPError(str(r.status_code), response=r)
                r.raise_for_status()
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except requests.RequestException as e:
                last = e
                time.sleep(1.5 * (i + 1))
                continue
        
        if last:
            raise last
        raise RuntimeError("Gemini không phản hồi")
