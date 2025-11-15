# -*- coding: utf-8 -*-
"""
Google Labs Flow Image Generation Service
Supports generating images from reference images + prompts using Flow API
Uses the same OAuth tokens configured in Settings for Google Labs video generation
"""
import base64
import random
import time
from typing import Callable, List, Optional

import requests

# Support both package and flat layouts
try:
    from services.endpoints import FLOW_IMAGE_GEN_URL
except Exception:
    from endpoints import FLOW_IMAGE_GEN_URL


class FlowImageError(Exception):
    """Flow Image API error"""
    pass


def get_flow_tokens_and_project() -> tuple:
    """
    Get OAuth tokens and project ID from account manager
    Uses the same tokens configured for Google Labs video generation

    Returns:
        Tuple of (tokens: List[str], project_id: str)

    Raises:
        FlowImageError: If no accounts are configured
    """
    try:
        from services.account_manager import get_account_manager
    except ImportError:
        raise FlowImageError(
            "Cannot import account_manager module.\n"
            "Không thể import module account_manager."
        )

    # Get account manager
    account_mgr = get_account_manager()

    # Get enabled accounts
    enabled_accounts = account_mgr.get_enabled_accounts() if account_mgr else []

    if not enabled_accounts:
        raise FlowImageError(
            "Chưa cấu hình Google Labs accounts / No Google Labs accounts configured.\n"
            "\n"
            "Vui lòng cấu hình OAuth tokens trong tab Cài đặt (Settings):\n"
            "Please configure OAuth tokens in the Settings tab:\n"
            "\n"
            "1. Mở tab Cài đặt (Settings)\n"
            "   Open the Settings tab\n"
            "\n"
            "2. Tìm phần 'Google Labs Accounts (Multi-Account)'\n"
            "   Find the 'Google Labs Accounts (Multi-Account)' section\n"
            "\n"
            "3. Thêm account với OAuth Flow tokens từ labs.google.com\n"
            "   Add an account with OAuth Flow tokens from labs.google.com\n"
            "\n"
            "LƯU Ý: Tokens này dùng chung cho cả tạo video và tạo ảnh Flow.\n"
            "NOTE: These tokens are shared for both video generation and Flow image generation."
        )

    # Get first enabled account
    account = enabled_accounts[0]

    if not account.tokens:
        raise FlowImageError(
            f"Account '{account.name}' không có OAuth tokens.\n"
            f"Account '{account.name}' has no OAuth tokens.\n"
            "\n"
            "Vui lòng thêm tokens trong tab Cài đặt (Settings).\n"
            "Please add tokens in the Settings tab."
        )

    return account.tokens, account.project_id


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

    log("[INFO] Flow: Note - Reference image upload not fully implemented yet")
    log("[INFO] Flow: Will use image path for local processing")

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
        aspect_ratio: Image aspect ratio (PORTRAIT, LANDSCAPE, or SQUARE)
        num_images: Number of images to generate (default 4)
        log_callback: Optional logging callback

    Returns:
        Generated image bytes (first result) or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)

    try:
        # Get tokens and project ID from account manager (same as video generation)
        tokens, project_id = get_flow_tokens_and_project()

        # Use first token (can be enhanced to rotate through tokens)
        bearer_token = tokens[0] if tokens else None
        if not bearer_token:
            raise FlowImageError("No OAuth tokens available in account")

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
            except Exception:
                log(f"[ERROR] Response: {response.text[:200]}")
            return None

        data = response.json()

        # Parse response to get image URLs
        # Response: {"responses": [{"imageGenerationResponse": ...}]}
        try:
            if "responses" in data and len(data["responses"]) > 0:
                first_response = data["responses"][0]

                if "imageGenerationResponse" in first_response:
                    gen_response = first_response["imageGenerationResponse"]

                    generated = gen_response.get("generatedImages", [])
                    if generated:
                        first_image = generated[0]

                        # Get image URL (could be gcsUrl, signedUrl, or downloadUrl)
                        image_url = (
                            first_image.get("gcsUrl") or
                            first_image.get("signedUrl") or
                            first_image.get("downloadUrl")
                        )

                        if image_url:
                            log("[INFO] Flow: Downloading generated image...")

                            # Download the image
                            img_response = requests.get(image_url, timeout=60)

                            if img_response.status_code == 200:
                                size = len(img_response.content)
                                log(f"[INFO] Flow: Image generated ({size} bytes)")
                                return img_response.content
                            else:
                                status = img_response.status_code
                                log(f"[ERROR] Flow: Download failed ({status})")
                                return None

            log("[ERROR] Flow: No images in response")
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
