# -*- coding: utf-8 -*-
import base64
import time
from typing import Optional

import requests

from services.core.api_config import IMAGE_GEN_TIMEOUT, VERTEX_AI_IMAGE_MODEL, gemini_image_endpoint
from services.core.api_key_rotator import APIKeyRotationError, APIKeyRotator
from services.core.key_manager import get_all_keys, refresh


class ImageGenError(Exception):
    """Image generation error"""
    pass


def _extract_image_from_response(data: dict) -> bytes:
    """
    Extract image bytes from Gemini API response
    
    Args:
        data: JSON response from Gemini API
        
    Returns:
        Image as bytes
        
    Raises:
        ImageGenError: If image data cannot be extracted
    """
    candidates = data.get("candidates", [])
    if not candidates:
        raise ImageGenError("No candidates in response")

    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise ImageGenError("No parts in candidate")

    # Look for inline_data with image
    for part in parts:
        if "inline_data" in part:
            mime_type = part["inline_data"].get("mime_type", "")
            if mime_type.startswith("image/"):
                b64_data = part["inline_data"].get("data", "")
                if b64_data:
                    image_bytes = base64.b64decode(b64_data)

                    # Validate image size - a valid image should be at least 1KB
                    MIN_VALID_IMAGE_SIZE = 1024  # 1KB
                    if len(image_bytes) < MIN_VALID_IMAGE_SIZE:
                        raise ImageGenError(
                            f"Image data too small ({len(image_bytes)} bytes < {MIN_VALID_IMAGE_SIZE} bytes), "
                            f"likely an error response"
                        )

                    return image_bytes

    raise ImageGenError("No image data found in response")


def _try_vertex_ai_image_generation(prompt: str, aspect_ratio: str = "1:1", reference_images: list = None, log_fn=None) -> Optional[bytes]:
    """
    Try to generate image using Vertex AI if enabled
    
    Args:
        prompt: Image generation prompt
        aspect_ratio: Image aspect ratio (e.g., "9:16", "16:9", "1:1")
        reference_images: Optional list of reference image paths for product consistency
        log_fn: Optional callback function for logging
        
    Returns:
        Generated image bytes or None if Vertex AI is not available/enabled
    """
    def log(msg):
        if log_fn:
            log_fn(msg)

    try:
        # Load config to check if Vertex AI is enabled
        from utils import config as cfg
        config = cfg.load()

        vertex_config = config.get('vertex_ai', {})

        # Check if Vertex AI is enabled
        if not vertex_config.get('enabled', False):
            # Vertex AI is disabled - this is not an error, just use AI Studio API
            return None

        # Vertex AI is enabled, now try to import required modules
        try:
            from google import genai
            from google.genai import types

            from services.vertex_service_account_manager import get_vertex_account_manager

            account_mgr = get_vertex_account_manager()
            account_mgr.load_from_config(config)

            # Get next enabled account
            account = account_mgr.get_next_account()

            if not account:
                log("[IMAGE GEN] Không có Vertex AI service account khả dụng")
                return None

            log(f"[IMAGE GEN] Đang thử Vertex AI với account: {account.name}")

            # Handle service account credentials if provided
            import os
            import tempfile
            temp_creds_file = None
            if account.credentials_json:
                temp_creds_file = tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.json',
                    delete=False
                )
                temp_creds_file.write(account.credentials_json)
                temp_creds_file.close()
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_creds_file.name

            try:
                # Initialize Vertex AI client using google-genai SDK
                log("[IMAGE GEN] Khởi tạo Vertex AI client với Gemini model...")

                client = genai.Client(
                    vertexai=True,
                    project=account.project_id,
                    location=account.location
                )

                # Use configured Vertex AI image model (gemini-2.5-flash-image)
                model_name = VERTEX_AI_IMAGE_MODEL

                log(f"[IMAGE GEN] Gọi Vertex AI Gemini ({model_name}) với aspect ratio {aspect_ratio}...")

                # Build contents array with text prompt and optional reference images
                contents_parts = []
                
                # Add text prompt
                contents_parts.append(types.Part(text=prompt))
                
                # Add reference images if provided (for product consistency)
                if reference_images:
                    log(f"[IMAGE GEN] Thêm {len(reference_images)} ảnh tham chiếu cho tính nhất quán sản phẩm")
                    for img_path in reference_images[:2]:  # Limit to 2 reference images
                        try:
                            with open(img_path, 'rb') as img_file:
                                img_bytes = img_file.read()
                                # Add as inline data
                                contents_parts.append(types.Part(
                                    inline_data=types.Blob(
                                        mime_type='image/jpeg',
                                        data=img_bytes
                                    )
                                ))
                        except Exception as img_err:
                            log(f"[IMAGE GEN] ⚠️ Không thể đọc ảnh tham chiếu {img_path}: {img_err}")

                # Build generation config with aspect ratio
                config_params = {
                    "temperature": 0.9,
                    "top_k": 40,
                    "top_p": 0.95,
                }
                
                # Add aspect ratio to image_config if supported
                # Note: aspect_ratio support depends on the model version
                if aspect_ratio and aspect_ratio != "1:1":
                    # Map aspect ratios to Vertex AI format
                    aspect_map = {
                        "9:16": "9:16",
                        "16:9": "16:9",
                        "4:5": "3:4",  # Closest supported ratio
                        "3:4": "3:4",
                        "1:1": "1:1",
                    }
                    vertex_aspect = aspect_map.get(aspect_ratio, "1:1")
                    if vertex_aspect != aspect_ratio:
                        log(f"[IMAGE GEN] Chuyển đổi aspect ratio {aspect_ratio} → {vertex_aspect} (Vertex AI)")
                    
                    # Try to add aspect_ratio to config (may not be supported by all model versions)
                    try:
                        config_params["image_config"] = {"aspect_ratio": vertex_aspect}
                    except Exception:
                        # If not supported, fall back to prompt-based approach
                        log(f"[IMAGE GEN] Model không hỗ trợ image_config, sử dụng prompt hints")

                # Generate image using Gemini model
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents_parts,
                    config=types.GenerateContentConfig(**config_params)
                )

                # Extract image bytes from response
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        parts = candidate.content.parts
                        for part in parts:
                            # Look for inline_data with image
                            if hasattr(part, 'inline_data') and part.inline_data is not None:
                                mime_type = part.inline_data.mime_type
                                if mime_type and mime_type.startswith('image/'):
                                    # The data format depends on the SDK version and API used:
                                    # - Vertex AI: returns raw bytes directly
                                    # - AI Studio: returns base64-encoded string
                                    import base64

                                    data = part.inline_data.data

                                    # Check if data is already bytes or needs decoding
                                    if isinstance(data, bytes):
                                        # Already in bytes format (Vertex AI)
                                        image_bytes = data
                                    else:
                                        # Need to decode from base64 string (AI Studio)
                                        image_bytes = base64.b64decode(data)

                                    # Validate image size - a valid image should be at least 1KB
                                    # If too small (e.g., 65 bytes), it's likely an error
                                    MIN_VALID_IMAGE_SIZE = 1024  # 1KB
                                    if len(image_bytes) < MIN_VALID_IMAGE_SIZE:
                                        size_msg = (
                                            f"[IMAGE GEN] ⚠️ Vertex AI trả về dữ liệu quá nhỏ "
                                            f"({len(image_bytes)} bytes < {MIN_VALID_IMAGE_SIZE} bytes)"
                                        )
                                        log(size_msg)
                                        log(
                                            "[IMAGE GEN] Dữ liệu có thể không phải ảnh hợp lệ, "
                                            "bỏ qua và thử AI Studio API"
                                        )
                                        return None

                                    success_msg = (
                                        f"[IMAGE GEN] ✓ Vertex AI tạo ảnh thành công với Gemini "
                                        f"({len(image_bytes)} bytes)"
                                    )
                                    log(success_msg)
                                    return image_bytes

                log("[IMAGE GEN] Vertex AI không trả về ảnh")
                return None

            finally:
                # Clean up temp credentials file
                if temp_creds_file:
                    try:
                        os.unlink(temp_creds_file.name)
                    except Exception:
                        pass

        except ImportError as ie:
            log(f"[IMAGE GEN] Vertex AI được bật nhưng thiếu dependencies: {ie}")
            log("[IMAGE GEN] Chạy: pip install google-genai>=0.3.0")
            return None
        except Exception as e:
            # Extract detailed error information for better debugging
            error_msg = str(e)

            # Check if it's a rate limit error (429 RESOURCE_EXHAUSTED)
            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg or 'Resource exhausted' in error_msg:
                # Try to extract error details from the exception
                error_details = error_msg

                # Parse JSON error if available
                import json
                import re

                # Try to find JSON object with nested structure
                # Look for pattern: {'error': {...}}
                json_match = re.search(r'\{[\'"]error[\'"]\s*:\s*\{[^}]+\}\}', error_msg)
                if json_match:
                    try:
                        # Replace single quotes with double quotes for valid JSON
                        json_str = json_match.group(0).replace("'", '"')
                        error_json = json.loads(json_str)
                        if 'error' in error_json:
                            error_info = error_json['error']
                            code = error_info.get('code', 'N/A')
                            status = error_info.get('status', 'N/A')
                            message = error_info.get('message', 'N/A')
                            error_details = f"{code} {status}. {error_json}"
                    except Exception:
                        # If JSON parsing fails, just use the original message
                        pass

                log(f"[IMAGE GEN] Lỗi Vertex AI: {error_details}, chuyển sang AI Studio API")
            else:
                log(f"[IMAGE GEN] Lỗi Vertex AI: {e}, chuyển sang AI Studio API")

            return None

    except Exception as e:
        log(f"[IMAGE GEN] Lỗi khi kiểm tra Vertex AI: {e}")
        return None


def generate_image_gemini(prompt: str, timeout: int = None, retry_delay: float = 15.0, enforce_rate_limit: bool = True, log_callback=None) -> bytes:
    """
    Generate image using Gemini Flash Image model with APIKeyRotator (PR#5)
    Now supports Vertex AI with automatic fallback to AI Studio API
    
    Args:
        prompt: Text prompt for image generation
        timeout: Request timeout in seconds (default from api_config)
        retry_delay: Base delay before first API call (15.0s for Gemini free tier safety)
        enforce_rate_limit: If True, wait before first API call (default True)
        log_callback: Optional callback function for logging (receives string messages)
        
    Returns:
        Generated image as bytes
        
    Raises:
        ImageGenError: If generation fails
    """
    def log(msg):
        if log_callback:
            log_callback(msg)

    # Try Vertex AI first if enabled
    vertex_result = _try_vertex_ai_image_generation(
        prompt=prompt,
        aspect_ratio="1:1",  # Default aspect ratio
        reference_images=None,
        log_fn=log_callback
    )
    if vertex_result:
        return vertex_result

    # Fallback to AI Studio API with key rotation
    timeout = timeout or IMAGE_GEN_TIMEOUT
    refresh()
    keys = get_all_keys('google')
    if not keys:
        raise ImageGenError("No Google API keys available")

    log(f"[DEBUG] Tìm thấy {len(keys)} Google API keys")

    # Enforce rate limit before first call
    if enforce_rate_limit:
        log(f"[RATE LIMIT] Đợi {retry_delay}s trước khi gọi API...")
        time.sleep(retry_delay)

    # PR#5: Define API call function for APIKeyRotator
    def api_call_with_key(api_key: str) -> bytes:
        """Make API call with given key"""
        url = gemini_image_endpoint(api_key)

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "topK": 40,
                "topP": 0.95,
            }
        }

        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()

        data = response.json()

        # Extract image data using helper
        return _extract_image_from_response(data)

    # PR#5: Use APIKeyRotator
    try:
        rotator = APIKeyRotator(keys, log_callback=log)
        return rotator.execute(api_call_with_key)
    except APIKeyRotationError as e:
        raise ImageGenError(str(e))


# New implementation: Intelligent rate-limited image generation with API key rotation
def generate_image_with_rate_limit(
    prompt: str = None,
    text: str = None,
    api_keys: list = None,
    model: str = "gemini",
    aspect_ratio: str = "1:1",
    size: str = None,
    delay_before: float = 0,
    rate_limit_delay: float = 10.0,
    max_calls_per_minute: int = 6,
    logger = None,
    log_callback = None,
    reference_images: list = None,
) -> Optional[bytes]:
    """
    Generate image with intelligent API key rotation and rate limiting
    
    This function uses the new APIKeyRotationManager to handle:
    - Per-key usage tracking and cooldowns
    - Exponential backoff (2s, 4s, 8s) on rate limits
    - 60s cooldown after exhausting retries on a key
    - Minimum 2s interval between calls on same key
    - Smart rotation that skips rate-limited keys
    
    Args:
        prompt: Image generation prompt (alternative to 'text', one is required)
        text: Image generation prompt (alternative to 'prompt', one is required)
        api_keys: List of API keys to rotate through (optional, uses config if not provided)
        model: Model to use (gemini, dalle, imagen_4, etc.)
        aspect_ratio: Image aspect ratio (e.g., "9:16", "16:9", "1:1", "4:5")
        logger: Optional callback function for logging (alias for log_callback)
        log_callback: Optional callback function for logging
        reference_images: Reference images for generation (optional)
        
        # Legacy parameters (kept for backwards compatibility, currently not used):
        size: Image size (legacy parameter for DALL-E, not currently used)
        delay_before: Seconds to wait before call (not used - rotation manager handles delays)
        rate_limit_delay: Minimum seconds between calls (not used - rotation manager handles this)
        max_calls_per_minute: Maximum API calls per minute (not used - rotation manager handles this)
    
    Returns:
        Generated image bytes or None if generation fails
        
    Note:
        - Either 'prompt' or 'text' parameter must be provided
        - For Imagen 4: Automatically normalizes 4:5 to 3:4 (closest supported ratio)
        - For Gemini: Accepts any aspect ratio from UI
        - Legacy parameters (size, delay_before, rate_limit_delay, max_calls_per_minute) are 
          accepted for backward compatibility but are not used by the current implementation
    """
    # Support both 'prompt' and 'text' parameter names for backward compatibility
    if prompt is None and text is None:
        raise ValueError("Either 'prompt' or 'text' parameter is required")

    # Use whichever is provided, preferring 'prompt' if both are given
    actual_prompt = prompt if prompt is not None else text

    # Support both logger and log_callback parameter names
    log_fn = logger or log_callback

    def log(msg):
        if log_fn:
            log_fn(msg)

    # Load API keys if not provided
    if not api_keys:
        from services.core.key_manager import get_all_keys, refresh
        refresh()
        api_keys = get_all_keys('google')

    if not api_keys:
        log("[ERROR] No Google API keys available")
        return None

    log(f"[IMAGE GEN] Using {len(api_keys)} API keys with intelligent rotation")

    # Normalize aspect ratio for Imagen 4
    normalized_ratio = aspect_ratio
    if model.lower() == 'imagen_4':
        # Imagen 4 doesn't support 4:5, normalize to 3:4
        if aspect_ratio == "4:5":
            normalized_ratio = "3:4"
            log(f"[ASPECT RATIO] Normalized {aspect_ratio} to {normalized_ratio} for Imagen 4")

    # Call appropriate generation function with key rotation
    try:
        if model.lower() in ("gemini", "imagen_4"):
            log(f"[IMAGE GEN] Tạo ảnh với {model}...")

            # Try Vertex AI first if enabled
            vertex_result = _try_vertex_ai_image_generation(
                prompt=actual_prompt,
                aspect_ratio=aspect_ratio,
                reference_images=reference_images,
                log_fn=log_fn
            )
            if vertex_result:
                log("[IMAGE GEN] ✓ Sử dụng Vertex AI")
                return vertex_result

            # Build generation config with aspect ratio hint if provided
            generation_config = {
                "temperature": 0.9,
                "topK": 40,
                "topP": 0.95,
            }

            # Add aspect ratio to prompt for better results
            # Note: Gemini doesn't have explicit aspect_ratio parameter, so we enhance the prompt
            aspect_hint = ""
            if aspect_ratio and aspect_ratio != "1:1":
                if aspect_ratio in ("9:16", "4:5"):
                    aspect_hint = " (portrait orientation, vertical format)"
                elif aspect_ratio in ("16:9", "21:9"):
                    aspect_hint = " (landscape orientation, horizontal format)"

            enhanced_prompt = actual_prompt + aspect_hint if aspect_hint else actual_prompt

            # Build parts array for API payload
            parts = [{"text": enhanced_prompt}]

            # Use APIKeyRotator for key rotation with shared API call logic
            def api_call_with_key(api_key: str) -> bytes:
                """Make API call with given key"""
                url = gemini_image_endpoint(api_key)

                payload = {
                    "contents": [{
                        "parts": parts
                    }],
                    "generationConfig": generation_config
                }

                response = requests.post(url, json=payload, timeout=IMAGE_GEN_TIMEOUT)
                response.raise_for_status()

                data = response.json()

                # Extract image data using helper
                return _extract_image_from_response(data)

            # Use APIKeyRotator with provided keys
            try:
                rotator = APIKeyRotator(api_keys, log_callback=log_fn)
                return rotator.execute(api_call_with_key)
            except APIKeyRotationError as e:
                # All Gemini keys exhausted - check if it's due to rate limits
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or '429' in error_msg or 'quota' in error_msg:
                    log("[RATE LIMIT] All Gemini API keys are rate limited!")
                    log("[INFO] Attempting fallback to Whisk API...")

                    # Try Whisk as fallback if reference images are available
                    if reference_images and len(reference_images) > 0:
                        try:
                            from services import whisk_service
                            whisk_result = whisk_service.generate_image(
                                prompt=actual_prompt,
                                model_image=reference_images[0] if len(reference_images) > 0 else None,
                                product_image=reference_images[1] if len(reference_images) > 1 else None,
                                debug_callback=log_fn
                            )
                            if whisk_result:
                                log("[SUCCESS] Whisk fallback succeeded!")
                                return whisk_result
                            else:
                                log("[ERROR] Whisk fallback returned no data")
                        except Exception as whisk_err:
                            log(f"[ERROR] Whisk fallback failed: {str(whisk_err)[:100]}")
                    else:
                        log("[SKIP] Whisk requires reference images (not provided)")

                # Re-raise the original error if Whisk fallback didn't work
                raise

        elif model.lower() == "dalle":
            log("[IMAGE GEN] Tạo ảnh với DALL-E...")
            # Import DALL-E client if available
            try:
                from services.openai.dalle_client import generate_image
                return generate_image(actual_prompt, size=size)
            except ImportError:
                log("[ERROR] DALL-E client không khả dụng")
                return None

        elif model.lower() == "whisk":
            log("[IMAGE GEN] Tạo ảnh với Whisk...")
            # Whisk requires reference images
            if not reference_images or len(reference_images) == 0:
                log("[ERROR] Whisk requires reference images (model_paths/prod_paths)")
                return None

            try:
                from services import whisk_service

                # Convert aspect ratio to Whisk format
                whisk_aspect_ratio = "IMAGE_ASPECT_RATIO_PORTRAIT"
                if aspect_ratio:
                    if aspect_ratio in ("9:16", "4:5"):
                        whisk_aspect_ratio = "IMAGE_ASPECT_RATIO_PORTRAIT"
                    elif aspect_ratio in ("16:9", "21:9"):
                        whisk_aspect_ratio = "IMAGE_ASPECT_RATIO_LANDSCAPE"
                    elif aspect_ratio == "1:1":
                        whisk_aspect_ratio = "IMAGE_ASPECT_RATIO_SQUARE"

                result = whisk_service.generate_image(
                    prompt=actual_prompt,
                    model_image=reference_images[0] if len(reference_images) > 0 else None,
                    product_image=reference_images[1] if len(reference_images) > 1 else None,
                    aspect_ratio=whisk_aspect_ratio,
                    debug_callback=log_fn
                )

                if result:
                    log("[SUCCESS] Whisk generation complete!")
                    return result
                else:
                    log("[ERROR] Whisk returned no data")
                    return None

            except ImportError:
                log("[ERROR] Whisk service không khả dụng")
                return None
            except Exception as e:
                log(f"[ERROR] Whisk generation failed: {str(e)[:100]}")
                return None

        else:
            log(f"[ERROR] Unsupported model: {model}")
            return None

    except Exception as e:
        log(f"[ERROR] Image generation failed: {str(e)[:200]}")
        return None
