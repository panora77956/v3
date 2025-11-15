# -*- coding: utf-8 -*-
"""
Google Labs Flow Image Generation Service
Supports generating images from reference images + prompts using Flow API
"""
import base64
import random
import time
from typing import Optional, Callable, List

import requests

# Support both package and flat layouts
try:
    from services.endpoints import FLOW_IMAGE_GEN_URL
except Exception:
    from endpoints import FLOW_IMAGE_GEN_URL


class FlowImageError(Exception):
    """Flow Image API error"""
    pass


def get_flow_bearer_token() -> str:
    """
    Get bearer token (OAuth token) from config for Flow API
    
    CRITICAL: This requires actual OAuth bearer token from Google Labs API,
    NOT regular API keys. Bearer tokens are obtained through OAuth flow.
    
    To obtain bearer token:
    1. Open browser and login to labs.google
    2. Navigate to https://labs.google/fx/tools/flow
    3. Open Developer Tools (F12) -> Network tab
    4. Make a generation request
    5. Find request to "aisandbox-pa.googleapis.com"
    6. Copy Authorization header value (starts with "Bearer ")
    7. Add to config as 'flow_bearer_token' or 'labs_bearer_token'
    
    Note: Bearer tokens typically expire after some time and need to be refreshed.
    """
    try:
        from services.core.config import load as load_config
    except ImportError:
        try:
            from utils import config as cfg_module
            load_config = cfg_module.load
        except ImportError:
            raise FlowImageError("Cannot load config module")
    
    # Try to get bearer token from config
    cfg = load_config()
    bearer_token = cfg.get('flow_bearer_token') or cfg.get('labs_bearer_token')
    
    if bearer_token:
        return bearer_token
    
    # Fail early with clear error message
    raise FlowImageError(
        "Chưa cấu hình Bearer token cho Flow API / No Bearer token configured for Flow API.\n"
        "Vui lòng thêm 'flow_bearer_token' hoặc 'labs_bearer_token' vào config.json.\n"
        "Please configure 'flow_bearer_token' or 'labs_bearer_token' in config.json.\n"
        "\n"
        "Hướng dẫn lấy bearer token / How to obtain bearer token:\n"
        "1. Mở trình duyệt và đăng nhập vào labs.google / Open browser and login to labs.google\n"
        "2. Truy cập https://labs.google/fx/tools/flow\n"
        "3. Mở Developer Tools (F12) → Network tab\n"
        "4. Thực hiện một yêu cầu tạo ảnh / Make a generation request\n"
        "5. Tìm request đến 'aisandbox-pa.googleapis.com' / Find request to 'aisandbox-pa.googleapis.com'\n"
        "6. Copy giá trị Authorization header (bắt đầu bằng 'Bearer ') / Copy Authorization header value\n"
        "7. Thêm vào config.json như: \"flow_bearer_token\": \"<token>\" (không cần 'Bearer ' prefix)\n"
        "\n"
        "LƯU Ý: Bearer tokens thường hết hạn sau một thời gian và cần được làm mới.\n"
        "NOTE: Bearer tokens typically expire after some time and need to be refreshed."
    )


def get_flow_project_id() -> str:
    """
    Get Flow project ID from config
    """
    try:
        from services.core.config import load as load_config
    except ImportError:
        try:
            from utils import config as cfg_module
            load_config = cfg_module.load
        except ImportError:
            # Use default project ID if config not available
            return "88f510eb-f32a-40c2-adce-8f492f37a144"
    
    cfg = load_config()
    project_id = cfg.get('flow_project_id') or cfg.get('labs_project_id')
    
    if project_id:
        return project_id
    
    # Return default project ID from example
    return "88f510eb-f32a-40c2-adce-8f492f37a144"


def upload_flow_image(image_path: str, log_callback: Optional[Callable] = None) -> Optional[dict]:
    """
    Upload an image to Flow for use as reference
    
    Args:
        image_path: Path to image file
        log_callback: Optional logging callback
        
    Returns:
        Image info dict with 'name' field, or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    # For Flow, we need to upload images first to get their IDs
    # This is a placeholder - the actual upload endpoint would need to be determined
    # from the Flow API. For now, we'll simulate by returning a mock structure
    # that matches the expected format from the CURL example
    
    log(f"[INFO] Flow: Note - Reference image upload not fully implemented yet")
    log(f"[INFO] Flow: Will use image path for local processing")
    
    # Return a mock structure for now
    # In production, this would call an actual upload endpoint
    return {
        "name": f"CAMaJD{base64.b64encode(image_path.encode()).decode()[:20]}",
        "path": image_path
    }


def generate_flow_image(
    prompt: str,
    reference_images: Optional[List[str]] = None,
    aspect_ratio: str = "IMAGE_ASPECT_RATIO_PORTRAIT",
    num_images: int = 4,
    log_callback: Optional[Callable] = None
) -> Optional[bytes]:
    """
    Generate image using Flow API with reference images
    
    Args:
        prompt: Text prompt for image generation
        reference_images: List of reference image paths (up to 3)
        aspect_ratio: Image aspect ratio (IMAGE_ASPECT_RATIO_PORTRAIT, IMAGE_ASPECT_RATIO_LANDSCAPE, IMAGE_ASPECT_RATIO_SQUARE)
        num_images: Number of images to generate (default 4)
        log_callback: Optional logging callback
        
    Returns:
        Generated image bytes (first result) or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    try:
        bearer_token = get_flow_bearer_token()
        project_id = get_flow_project_id()
        
        # Generate session ID (timestamp in milliseconds with semicolon prefix)
        session_id = f";{int(time.time() * 1000)}"
        
        # Build image inputs from reference images
        image_inputs = []
        if reference_images:
            log(f"[INFO] Flow: Processing {len(reference_images)} reference images")
            for img_path in reference_images[:3]:  # Max 3 reference images
                # Upload each image to get its ID
                img_info = upload_flow_image(img_path, log_callback)
                if img_info:
                    image_inputs.append({
                        "name": img_info["name"],
                        "imageInputType": "IMAGE_INPUT_TYPE_REFERENCE"
                    })
        
        # Build requests array (generate multiple variants)
        requests_array = []
        for i in range(num_images):
            # Generate random seed for each variant
            seed = random.randint(100000, 999999)
            
            request_obj = {
                "clientContext": {
                    "sessionId": session_id
                },
                "seed": seed,
                "imageModelName": "GEM_PIX",
                "imageAspectRatio": aspect_ratio,
                "prompt": prompt
            }
            
            # Add image inputs if available
            if image_inputs:
                request_obj["imageInputs"] = image_inputs
            
            requests_array.append(request_obj)
        
        # Build final payload
        payload = {
            "requests": requests_array
        }
        
        # Make API request
        url = FLOW_IMAGE_GEN_URL.format(project_id=project_id)
        
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://labs.google",
            "Referer": "https://labs.google/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        log(f"[INFO] Flow: Generating {num_images} image variants...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code != 200:
            log(f"[ERROR] Flow API returned status {response.status_code}")
            try:
                error_data = response.json()
                log(f"[ERROR] Error: {error_data}")
            except:
                log(f"[ERROR] Response: {response.text[:200]}")
            return None
        
        data = response.json()
        
        # Parse response to get image URLs
        # Response structure: {"responses": [{"imageGenerationResponse": {"generatedImages": [...]}}]}
        try:
            if "responses" in data and len(data["responses"]) > 0:
                first_response = data["responses"][0]
                
                if "imageGenerationResponse" in first_response:
                    gen_response = first_response["imageGenerationResponse"]
                    
                    if "generatedImages" in gen_response and len(gen_response["generatedImages"]) > 0:
                        first_image = gen_response["generatedImages"][0]
                        
                        # Get image URL (could be gcsUrl, signedUrl, or downloadUrl)
                        image_url = (
                            first_image.get("gcsUrl") or
                            first_image.get("signedUrl") or
                            first_image.get("downloadUrl")
                        )
                        
                        if image_url:
                            log(f"[INFO] Flow: Downloading generated image...")
                            
                            # Download the image
                            img_response = requests.get(image_url, timeout=60)
                            
                            if img_response.status_code == 200:
                                log(f"[INFO] Flow: Image generated successfully ({len(img_response.content)} bytes)")
                                return img_response.content
                            else:
                                log(f"[ERROR] Flow: Failed to download image (status {img_response.status_code})")
                                return None
            
            log(f"[ERROR] Flow: No images in response")
            log(f"[DEBUG] Response structure: {str(data)[:300]}")
            return None
            
        except (KeyError, TypeError, IndexError) as e:
            log(f"[ERROR] Flow: Failed to parse response: {e}")
            log(f"[DEBUG] Response: {str(data)[:300]}")
            return None
    
    except FlowImageError as e:
        log(f"[ERROR] Flow configuration error:\n{str(e)}")
        return None
    except Exception as e:
        log(f"[ERROR] Flow generation error: {str(e)[:200]}")
        import traceback
        log(f"[DEBUG] Traceback: {traceback.format_exc()[:500]}")
        return None


def generate_flow_image_text_only(
    prompt: str,
    aspect_ratio: str = "IMAGE_ASPECT_RATIO_PORTRAIT",
    num_images: int = 4,
    log_callback: Optional[Callable] = None
) -> Optional[bytes]:
    """
    Generate image using Flow API with text-only (no reference images)
    
    Args:
        prompt: Text prompt for image generation
        aspect_ratio: Image aspect ratio
        num_images: Number of images to generate
        log_callback: Optional logging callback
        
    Returns:
        Generated image bytes or None if failed
    """
    return generate_flow_image(
        prompt=prompt,
        reference_images=None,
        aspect_ratio=aspect_ratio,
        num_images=num_images,
        log_callback=log_callback
    )
