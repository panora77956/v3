# -*- coding: utf-8 -*-
"""
Whisk Service - Complete implementation with correct API flow
Based on real curl analysis from labs.google
"""
import requests
import base64
import time
import uuid
from typing import Optional, Callable


class WhiskError(Exception):
    """Whisk API error"""
    pass


def get_session_cookies() -> str:
    """
    Get session cookies from config
    Returns cookie string for requests
    
    CRITICAL: This requires actual browser session cookies from labs.google, 
    NOT regular API keys. Session cookies must be extracted from browser after
    logging into https://labs.google/fx/tools/whisk
    
    To obtain session cookies:
    1. Open browser and login to labs.google
    2. Navigate to https://labs.google/fx/tools/whisk
    3. Open Developer Tools (F12) -> Application -> Cookies
    4. Copy the value of "__Secure-next-auth.session-token"
    5. Add to config as 'labs_session_token'
    """
    from services.core.config import load as load_config
    
    # Try to get session token from config
    cfg = load_config()
    session_token = cfg.get('labs_session_token') or cfg.get('whisk_session_token')
    
    if session_token:
        return f"__Secure-next-auth.session-token={session_token}"
    
    # FIXED: Don't fallback to regular API keys - they won't work as session cookies
    # Fail early with clear error message instead of causing 401 errors
    raise WhiskError(
        "Chưa cấu hình session token cho Whisk / No Whisk session token configured.\n"
        "Vui lòng thêm 'labs_session_token' vào config.json với session cookie thực từ trình duyệt.\n"
        "Please configure 'labs_session_token' in config.json with actual browser session cookie.\n"
        "\n"
        "Hướng dẫn lấy session cookie / How to obtain session cookie:\n"
        "1. Mở trình duyệt và đăng nhập vào labs.google / Open browser and login to labs.google\n"
        "2. Truy cập https://labs.google/fx/tools/whisk\n"
        "3. Mở Developer Tools (F12) → Application → Cookies\n"
        "4. Copy giá trị của '__Secure-next-auth.session-token' / Copy value of '__Secure-next-auth.session-token'\n"
        "5. Thêm vào config.json như: \"labs_session_token\": \"<giá trị cookie>\" / Add to config.json as 'labs_session_token'\n"
        "\n"
        "LƯU Ý: API keys thông thường KHÔNG hoạt động - phải dùng session cookies thực từ trình duyệt.\n"
        "NOTE: Regular Google API keys will NOT work - you must use actual session cookies from browser."
    )


def get_bearer_token() -> str:
    """
    Get bearer token (OAuth token) from config for Whisk API
    
    CRITICAL: This requires actual OAuth bearer token from Google Labs API,
    NOT regular API keys. Bearer tokens are obtained through OAuth flow.
    
    To obtain bearer token:
    1. Open browser and login to labs.google
    2. Navigate to https://labs.google/fx/tools/whisk
    3. Open Developer Tools (F12) -> Network tab
    4. Make a generation request
    5. Find request to "aisandbox-pa.googleapis.com"
    6. Copy Authorization header value (starts with "Bearer ")
    7. Add to config as 'whisk_bearer_token' (without "Bearer " prefix)
    
    Note: Bearer tokens typically expire after some time and need to be refreshed.
    """
    from services.core.config import load as load_config
    
    # Try to get bearer token from config
    cfg = load_config()
    bearer_token = cfg.get('whisk_bearer_token') or cfg.get('labs_bearer_token')
    
    if bearer_token:
        return bearer_token
    
    # FIXED: Don't fallback to regular API keys - they won't work as OAuth bearer tokens
    # Fail early with clear error message instead of causing 401 errors
    raise WhiskError(
        "Chưa cấu hình Bearer token cho Whisk API / No Bearer token configured for Whisk API.\n"
        "Vui lòng thêm 'whisk_bearer_token' vào config.json với OAuth bearer token thực.\n"
        "Please configure 'whisk_bearer_token' in config.json with actual OAuth bearer token.\n"
        "\n"
        "Hướng dẫn lấy bearer token / How to obtain bearer token:\n"
        "1. Mở trình duyệt và đăng nhập vào labs.google / Open browser and login to labs.google\n"
        "2. Truy cập https://labs.google/fx/tools/whisk\n"
        "3. Mở Developer Tools (F12) → Network tab\n"
        "4. Thực hiện một yêu cầu tạo ảnh / Make a generation request\n"
        "5. Tìm request đến 'aisandbox-pa.googleapis.com' / Find request to 'aisandbox-pa.googleapis.com'\n"
        "6. Copy giá trị Authorization header (bắt đầu bằng 'Bearer ') / Copy Authorization header value (starts with 'Bearer ')\n"
        "7. Thêm vào config.json như: \"whisk_bearer_token\": \"<token>\" (không cần 'Bearer ' prefix)\n"
        "   Add to config.json as 'whisk_bearer_token' (without 'Bearer ' prefix)\n"
        "\n"
        "LƯU Ý: Bearer tokens thường hết hạn sau một thời gian và cần được làm mới.\n"
        "NOTE: Bearer tokens typically expire after some time and need to be refreshed.\n"
        "LƯU Ý: API keys thông thường KHÔNG hoạt động - phải dùng OAuth bearer tokens thực.\n"
        "NOTE: Regular Google API keys will NOT work - you must use actual OAuth bearer tokens."
    )


def caption_image(image_path: str, log_callback: Optional[Callable] = None) -> Optional[str]:
    """
    Step 1: Caption image using backbone.captionImage
    
    Args:
        image_path: Path to image file
        log_callback: Optional logging callback
        
    Returns:
        Caption text or None
    """
    def log(msg):
        if log_callback:
            log_callback(msg)

    try:
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = f.read()

        b64_image = base64.b64encode(image_data).decode('utf-8')
        data_uri = f"data:image/png;base64,{b64_image}"

        # Generate IDs
        workflow_id = str(uuid.uuid4())
        session_id = f";{int(time.time() * 1000)}"

        url = "https://labs.google/fx/api/trpc/backbone.captionImage"

        # Get session cookies - this may raise WhiskError if not configured
        cookies = get_session_cookies()

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Cookie": cookies,
            "Origin": "https://labs.google",
            "Referer": f"https://labs.google/fx/tools/whisk/project/{workflow_id}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        payload = {
            "json": {
                "clientContext": {
                    "sessionId": session_id,
                    "workflowId": workflow_id
                },
                "captionInput": {
                    "candidatesCount": 1,
                    "mediaInput": {
                        "mediaCategory": "MEDIA_CATEGORY_SUBJECT",
                        "rawBytes": data_uri
                    }
                }
            }
        }

        log(f"[INFO] Whisk: Captioning image...")

        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code != 200:
            log(f"[ERROR] Caption failed with status {response.status_code}")
            return None

        data = response.json()

        # Parse caption from response
        try:
            result = data['result']['data']['json']
            if 'candidates' in result and result['candidates']:
                caption = result['candidates'][0].get('caption', '')
                log(f"[INFO] Whisk: Got caption ({len(caption)} chars)")
                return caption
        except (KeyError, TypeError, IndexError):
            log(f"[ERROR] Could not parse caption from response")
            return None

    except WhiskError as e:
        # Don't truncate WhiskError messages - they contain important setup instructions
        log(f"[ERROR] Whisk configuration error: {str(e)}")
        return None
    except Exception as e:
        log(f"[ERROR] Caption error: {str(e)[:200]}")
        return None


def upload_image_whisk(image_path: str, workflow_id: str, session_id: str, log_callback: Optional[Callable] = None) -> Optional[str]:
    """
    Step 2: Upload image to Whisk
    
    FIXED: Parse correct nested structure from response
    
    Args:
        image_path: Path to image file
        workflow_id: Workflow UUID
        session_id: Session ID
        log_callback: Optional callback for logging
        
    Returns:
        mediaGenerationId or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)

    try:
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = f.read()

        b64_image = base64.b64encode(image_data).decode('utf-8')
        data_uri = f"data:image/png;base64,{b64_image}"

        url = "https://labs.google/fx/api/trpc/backbone.uploadImage"

        # Get session cookies - this may raise WhiskError if not configured
        cookies = get_session_cookies()

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Cookie": cookies,
            "Origin": "https://labs.google",
            "Referer": f"https://labs.google/fx/tools/whisk/project/{workflow_id}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        payload = {
            "json": {
                "clientContext": {
                    "workflowId": workflow_id,
                    "sessionId": session_id
                },
                "uploadMediaInput": {
                    "mediaCategory": "MEDIA_CATEGORY_SUBJECT",
                    "rawBytes": data_uri
                }
            }
        }

        log(f"[INFO] Whisk: Uploading {image_path.split('/')[-1]}...")

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        log(f"[INFO] Whisk: Upload response status {response.status_code}")

        if response.status_code != 200:
            log(f"[ERROR] Whisk upload failed with status {response.status_code}")
            return None

        data = response.json()

        # CRITICAL FIX: Parse correct nested structure
        # Response: {"result": {"data": {"json": {"result": {"uploadMediaGenerationId": "..."}}}}}
        try:
            media_id = data['result']['data']['json']['result']['uploadMediaGenerationId']
            log(f"[INFO] Whisk: Got mediaGenerationId: {media_id[:30]}...")
            return media_id
        except (KeyError, TypeError) as e:
            log(f"[ERROR] No mediaGenerationId in upload response")
            log(f"[DEBUG] Response structure: {str(data)[:200]}")
            return None

    except FileNotFoundError:
        log(f"[ERROR] Image file not found: {image_path}")
        return None
    except WhiskError as e:
        # Don't truncate WhiskError messages - they contain important setup instructions
        log(f"[ERROR] Whisk configuration error: {str(e)}")
        return None
    except Exception as e:
        log(f"[ERROR] Whisk upload exception: {str(e)[:200]}")
        return None


def run_image_recipe(
    prompt: str,
    recipe_media_inputs: list,
    workflow_id: str,
    session_id: str,
    aspect_ratio: str = "IMAGE_ASPECT_RATIO_PORTRAIT",
    log_callback: Optional[Callable] = None
) -> Optional[bytes]:
    """
    Step 3: Run image recipe with Whisk API
    
    Args:
        prompt: Text prompt for generation
        recipe_media_inputs: List of uploaded media inputs
        workflow_id: Workflow UUID
        session_id: Session ID
        aspect_ratio: Aspect ratio (IMAGE_ASPECT_RATIO_PORTRAIT, IMAGE_ASPECT_RATIO_SQUARE, etc.)
        log_callback: Optional logging callback
        
    Returns:
        Generated image bytes or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    try:
        # Get bearer token for API authentication - this may raise WhiskError if not configured
        bearer_token = get_bearer_token()
        
        url = "https://aisandbox-pa.googleapis.com/v1/whisk:runImageRecipe"
        
        headers = {
            "authorization": f"Bearer {bearer_token}",
            "content-type": "text/plain;charset=UTF-8",
            "origin": "https://labs.google",
            "referer": "https://labs.google/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Generate random seed for image generation
        import random
        seed = random.randint(100000, 999999)
        
        # Correct payload structure matching Google Labs API
        payload = {
            "clientContext": {
                "workflowId": workflow_id,
                "tool": "BACKBONE",
                "sessionId": session_id
            },
            "seed": seed,
            "imageModelSettings": {
                "imageModel": "R2I",
                "aspectRatio": aspect_ratio
            },
            "userInstruction": prompt,
            "recipeMediaInputs": recipe_media_inputs
        }
        
        log("[INFO] Whisk: Running image recipe...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code != 200:
            log(f"[ERROR] Whisk recipe failed with status {response.status_code}")
            log(f"[DEBUG] Response: {response.text[:200]}")
            return None
        
        data = response.json()
        
        # Parse the response to get generation ID or result
        # Response structure may vary, typical patterns:
        # 1. Immediate result with image data
        # 2. Generation ID for polling
        
        try:
            # Try to extract image data if available immediately
            if 'imageRecipeResult' in data:
                result = data['imageRecipeResult']
                
                # Check for direct image data
                if 'generatedImage' in result:
                    img_data = result['generatedImage']
                    if 'rawBytes' in img_data:
                        # Base64 encoded image
                        b64_data = img_data['rawBytes']
                        if b64_data.startswith('data:'):
                            # Extract base64 part from data URI
                            b64_data = b64_data.split(',', 1)[1]
                        return base64.b64decode(b64_data)
                    elif 'signedUrl' in img_data or 'downloadUrl' in img_data:
                        # Download from URL
                        download_url = img_data.get('signedUrl') or img_data.get('downloadUrl')
                        log(f"[INFO] Whisk: Downloading image from URL...")
                        img_response = requests.get(download_url, timeout=60)
                        if img_response.status_code == 200:
                            return img_response.content
                
                # Check for generation ID for polling
                if 'generationId' in result or 'mediaGenerationId' in result:
                    gen_id = result.get('generationId') or result.get('mediaGenerationId')
                    log(f"[INFO] Whisk: Got generation ID: {gen_id[:30]}...")
                    # NOTE: Async generation polling not yet implemented
                    # Whisk API returns generation ID for async requests that need to be polled
                    # This is a known limitation - immediate results only
                    log(f"[LIMITATION] Whisk: Async polling not implemented - only immediate results supported")
                    return None
            
            log(f"[ERROR] Whisk: Unexpected response structure")
            log(f"[DEBUG] Response keys: {list(data.keys())}")
            return None
            
        except (KeyError, TypeError, IndexError) as e:
            log(f"[ERROR] Whisk: Failed to parse response - {str(e)}")
            log(f"[DEBUG] Response: {str(data)[:300]}")
            return None
    
    except WhiskError as e:
        # Don't truncate WhiskError messages - they contain important setup instructions
        log(f"[ERROR] Whisk configuration error: {str(e)}")
        return None        
    except Exception as e:
        log(f"[ERROR] Whisk: runImageRecipe failed - {str(e)[:200]}")
        return None


def generate_image(prompt: str, model_image: Optional[str] = None, product_image: Optional[str] = None, 
                   aspect_ratio: str = "IMAGE_ASPECT_RATIO_PORTRAIT", debug_callback: Optional[Callable] = None) -> Optional[bytes]:
    """
    Generate image using Whisk with reference images
    
    Complete flow:
    1. Caption images
    2. Upload images
    3. Run image recipe
    
    Args:
        prompt: Text prompt
        model_image: Path to model/character reference image
        product_image: Path to product reference image
        aspect_ratio: Aspect ratio (IMAGE_ASPECT_RATIO_PORTRAIT, IMAGE_ASPECT_RATIO_SQUARE, IMAGE_ASPECT_RATIO_LANDSCAPE)
        debug_callback: Callback for debug logging
        
    Returns:
        Generated image as bytes or None if failed
    """
    def log(msg):
        if debug_callback:
            debug_callback(msg)

    try:
        log("[INFO] Whisk: Starting generation...")
        
        # Early validation: Check if required configuration is available
        # This provides clear error messages before attempting API calls
        try:
            # Test if session cookies are configured (needed for caption and upload)
            _ = get_session_cookies()
            # Test if bearer token is configured (needed for image recipe)
            _ = get_bearer_token()
        except WhiskError as config_error:
            # Configuration is missing - provide helpful error message
            log(f"[ERROR] Whisk configuration missing: {str(config_error)}")
            log("[INFO] Whisk requires two types of authentication:")
            log("  1. Session cookie (labs_session_token in config.json)")
            log("  2. Bearer token (whisk_bearer_token in config.json)")
            log("[INFO] See README.md for instructions on obtaining these credentials")
            return None

        # Generate IDs
        workflow_id = str(uuid.uuid4())
        session_id = f";{int(time.time() * 1000)}"

        # Prepare reference images
        images_to_process = []
        if model_image:
            images_to_process.append(model_image)
        if product_image:
            images_to_process.append(product_image)

        if not images_to_process:
            raise WhiskError("No reference images provided")

        log(f"[INFO] Whisk: Processing {len(images_to_process)} reference images...")

        # Step 1 & 2: Caption and upload each image
        recipe_media_inputs = []

        for idx, img_path in enumerate(images_to_process, 1):
            log(f"[INFO] Whisk: Processing image {idx}/{len(images_to_process)}...")

            # Caption
            caption = caption_image(img_path, log)
            if not caption:
                log(f"[WARN] No caption for image {idx}, using default")
                caption = "Reference image"

            # Upload
            media_id = upload_image_whisk(img_path, workflow_id, session_id, log)

            if media_id:
                recipe_media_inputs.append({
                    "caption": caption,
                    "mediaInput": {
                        "mediaCategory": "MEDIA_CATEGORY_SUBJECT",
                        "mediaGenerationId": media_id
                    }
                })
            else:
                log(f"[ERROR] Failed to upload image {idx}")

        if not recipe_media_inputs:
            log("[ERROR] Whisk: No images uploaded successfully")
            raise WhiskError("No images uploaded")

        log(f"[INFO] Whisk: Uploaded {len(recipe_media_inputs)} images successfully")

        # Step 3: Run image recipe with OAuth
        log("[INFO] Whisk: Running image recipe with Bearer token...")
        
        result_image = run_image_recipe(
            prompt=prompt,
            recipe_media_inputs=recipe_media_inputs,
            workflow_id=workflow_id,
            session_id=session_id,
            aspect_ratio=aspect_ratio,
            log_callback=log
        )
        
        if result_image:
            log("[INFO] Whisk: Image generation complete!")
            return result_image
        else:
            log("[WARN] Whisk: Image generation returned no data")
            return None

    except WhiskError as e:
        log(f"[ERROR] Whisk: {str(e)}")
        return None
    except Exception as e:
        log(f"[ERROR] Whisk: Unexpected error - {str(e)[:100]}")
        return None