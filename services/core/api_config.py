# -*- coding: utf-8 -*-
"""
API Configuration - Single Source of Truth for all API models and endpoints
"""

# Models
GEMINI_TEXT_MODEL = "gemini-2.5-flash"
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"  # FIXED: was "imagen-3.0-generate-001"

# Vertex AI Models (for production use)
VERTEX_AI_TEXT_MODEL = "gemini-2.5-flash"  # Same as AI Studio for consistency
VERTEX_AI_IMAGE_MODEL = "gemini-2.5-flash-image"  # Image generation model

# Base URLs
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"  # AI Studio API
VERTEX_AI_BASE = "https://aiplatform.googleapis.com/v1"  # Vertex AI API
WHISK_BASE = "https://labs.google/fx/api/trpc"
LABS_BASE = "https://aisandbox-pa.googleapis.com"

# Default Vertex AI Configuration
DEFAULT_VERTEX_AI_LOCATION = "us-central1"

# Timeouts (in seconds)
DEFAULT_TIMEOUT = 120
TEXT_GEN_TIMEOUT = 180
IMAGE_GEN_TIMEOUT = 180
VIDEO_GEN_TIMEOUT = 300


def gemini_text_endpoint(key: str) -> str:
    """
    Get Gemini text generation endpoint (AI Studio)
    
    Args:
        key: Google API key
        
    Returns:
        Full endpoint URL with API key
    """
    return f"{GEMINI_BASE}/models/{GEMINI_TEXT_MODEL}:generateContent?key={key}"


def gemini_image_endpoint(key: str) -> str:
    """
    Get Gemini image generation endpoint (AI Studio)
    
    Args:
        key: Google API key
        
    Returns:
        Full endpoint URL with API key
    """
    return f"{GEMINI_BASE}/models/{GEMINI_IMAGE_MODEL}:generateContent?key={key}"


def vertex_ai_endpoint(project_id: str, location: str, model: str) -> str:
    """
    Get Vertex AI endpoint
    
    Args:
        project_id: GCP project ID
        location: GCP region (e.g., us-central1)
        model: Model name
        
    Returns:
        Full Vertex AI endpoint URL
    """
    return f"{VERTEX_AI_BASE}/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"
