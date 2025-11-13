# -*- coding: utf-8 -*-
"""
Vertex AI Client - Wrapper for Google Cloud Vertex AI Gemini API
This module provides a unified interface for using Vertex AI's Gemini models
"""

import os
import time
import json
import tempfile
from typing import Optional, List, Dict, Any

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None


class VertexAIClient:
    """
    Vertex AI Gemini API client with intelligent fallback to AI Studio
    
    Features:
    - Supports both Vertex AI (with GCP project) and AI Studio (with API key)
    - Supports service account JSON credentials
    - Automatic retry with exponential backoff
    - Rate limiting protection
    - Better error handling for 503 errors
    """
    
    def __init__(
        self, 
        model: str = "gemini-2.5-flash",
        project_id: Optional[str] = None,
        location: str = "us-central1",
        api_key: Optional[str] = None,
        use_vertex: bool = True,
        credentials_json: Optional[str] = None
    ):
        """
        Initialize Vertex AI client
        
        Args:
            model: Model name (e.g., "gemini-2.5-flash", "gemini-1.5-pro")
            project_id: GCP project ID (required for Vertex AI)
            location: GCP region (default: us-central1)
            api_key: Google API key (for AI Studio fallback)
            use_vertex: Try to use Vertex AI first (default: True)
            credentials_json: Service account JSON string (optional, for Vertex AI)
        """
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-genai library not installed. "
                "Install it with: pip install google-genai>=0.3.0"
            )
        
        self.model = model
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location or os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.api_key = api_key
        self.use_vertex = use_vertex
        self.credentials_json = credentials_json
        self.client = None
        self._temp_creds_file = None  # Track temporary credentials file
        
        # Initialize client
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate client (Vertex AI or AI Studio)"""
        
        # Try Vertex AI first if configured
        if self.use_vertex and self.project_id:
            try:
                # Set environment variables for Vertex AI
                os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
                os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
                os.environ['GOOGLE_CLOUD_LOCATION'] = self.location
                
                # Handle service account credentials if provided
                if self.credentials_json:
                    # Create temporary file for credentials
                    self._temp_creds_file = tempfile.NamedTemporaryFile(
                        mode='w',
                        suffix='.json',
                        delete=False
                    )
                    self._temp_creds_file.write(self.credentials_json)
                    self._temp_creds_file.close()
                    
                    # Set environment variable to use this credentials file
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self._temp_creds_file.name
                    print(f"[VertexAI] Using service account credentials")
                
                # Initialize Vertex AI client
                self.client = genai.Client(
                    vertexai=True,
                    project=self.project_id,
                    location=self.location
                )
                self.client_type = "vertex_ai"
                print(f"[VertexAI] Initialized Vertex AI client for project {self.project_id} in {self.location}")
                return
            except Exception as e:
                print(f"[VertexAI] Could not initialize Vertex AI client: {e}")
                print(f"[VertexAI] Falling back to AI Studio API")
                # Clean up temp file if created
                self._cleanup_temp_file()
        
        # Fallback to AI Studio
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.client_type = "ai_studio"
                print(f"[VertexAI] Initialized AI Studio client")
                return
            except Exception as e:
                raise RuntimeError(f"Failed to initialize AI Studio client: {e}")
        
        raise RuntimeError(
            "No valid authentication method found. "
            "Provide either project_id (for Vertex AI) or api_key (for AI Studio)"
        )
    
    def _cleanup_temp_file(self):
        """Clean up temporary credentials file"""
        if self._temp_creds_file:
            try:
                os.unlink(self._temp_creds_file.name)
            except Exception:
                pass
            self._temp_creds_file = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self._cleanup_temp_file()
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.9,
        max_output_tokens: int = 8192,
        timeout: int = 180,
        max_retries: int = 5
    ) -> str:
        """
        Generate content using Gemini model
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for 503 errors
            
        Returns:
            Generated text content
            
        Raises:
            RuntimeError: If generation fails after all retries
        """
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Build generation config
                generation_config = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json"
                )
                
                # Build contents
                if system_instruction:
                    contents = [
                        types.Content(
                            role="user",
                            parts=[types.Part(text=prompt)]
                        )
                    ]
                    # Add system instruction to config
                    generation_config.system_instruction = types.Content(
                        parts=[types.Part(text=system_instruction)]
                    )
                else:
                    contents = prompt
                
                # Generate content
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=generation_config
                )
                
                # Extract text from response
                if hasattr(response, 'text'):
                    return response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        parts = candidate.content.parts
                        if parts and hasattr(parts[0], 'text'):
                            return parts[0].text
                
                raise RuntimeError("Could not extract text from response")
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a 503 error
                if '503' in error_str or 'service unavailable' in error_str:
                    if attempt < max_retries - 1:
                        # Exponential backoff for 503 errors
                        backoff = min(10 * (attempt + 1), 60)
                        print(f"[VertexAI] HTTP 503 error on attempt {attempt + 1}/{max_retries}. "
                              f"Retrying in {backoff}s...")
                        time.sleep(backoff)
                        continue
                    else:
                        raise RuntimeError(
                            f"Vertex AI service unavailable after {max_retries} retries (HTTP 503). "
                            f"This is likely due to high load on Google's servers. "
                            f"Please try again in a few minutes."
                        ) from last_error
                
                # Check if it's a rate limit error (429)
                elif '429' in error_str or 'rate limit' in error_str or 'quota' in error_str:
                    if attempt < max_retries - 1:
                        backoff = min(8 + 4 * attempt, 20)
                        print(f"[VertexAI] Rate limit on attempt {attempt + 1}/{max_retries}. "
                              f"Retrying in {backoff}s...")
                        time.sleep(backoff)
                        continue
                    else:
                        raise RuntimeError(
                            f"Rate limit exceeded after {max_retries} retries (HTTP 429). "
                            f"Please wait a few minutes before trying again."
                        ) from last_error
                
                # For other errors, don't retry
                else:
                    raise RuntimeError(f"Vertex AI generation failed: {e}") from e
        
        # Should not reach here, but just in case
        if last_error:
            raise RuntimeError(f"Vertex AI generation failed after {max_retries} retries") from last_error
        else:
            raise RuntimeError("Vertex AI generation failed with unknown error")
    
    def generate_content_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.9,
        max_output_tokens: int = 8192
    ):
        """
        Generate content with streaming (for real-time responses)
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            
        Yields:
            Text chunks as they are generated
        """
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        # Build generation config
        generation_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json"
        )
        
        # Build contents
        if system_instruction:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            ]
            generation_config.system_instruction = types.Content(
                parts=[types.Part(text=system_instruction)]
            )
        else:
            contents = prompt
        
        # Generate content with streaming
        response_stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generation_config
        )
        
        for chunk in response_stream:
            if hasattr(chunk, 'text'):
                yield chunk.text
            elif hasattr(chunk, 'candidates') and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if parts and hasattr(parts[0], 'text'):
                        yield parts[0].text


def create_vertex_ai_client(
    model: str = "gemini-2.5-flash",
    project_id: Optional[str] = None,
    location: str = "us-central1",
    api_key: Optional[str] = None,
    use_vertex: bool = True,
    credentials_json: Optional[str] = None
) -> VertexAIClient:
    """
    Factory function to create a Vertex AI client
    
    Args:
        model: Model name
        project_id: GCP project ID (for Vertex AI)
        location: GCP region
        api_key: Google API key (for AI Studio fallback)
        use_vertex: Try to use Vertex AI first
        credentials_json: Service account JSON string (optional)
        
    Returns:
        VertexAIClient instance
    """
    return VertexAIClient(
        model=model,
        project_id=project_id,
        location=location,
        api_key=api_key,
        use_vertex=use_vertex,
        credentials_json=credentials_json
    )
