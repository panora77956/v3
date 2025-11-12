# -*- coding: utf-8 -*-
"""
Google Veo Video Download Service
Implements video download using Google Veo API endpoints with quality selection support.
"""

import os
import time
from http.client import IncompleteRead
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError, RequestException, Timeout
from urllib3.exceptions import IncompleteRead as Urllib3IncompleteRead


class VeoDownloader:
    """
    Download videos from Google Veo API with quality selection and auto-download support.
    Supports 720p and 1080p quality options.
    """

    def __init__(self, api_key: str, log_callback=None):
        """
        Initialize VeoDownloader.

        Args:
            api_key: Google API key for authentication
            log_callback: Optional callback function for logging
        """
        self.api_key = api_key
        self.log = log_callback or print
        self.base_url = "https://aisandbox-pa.googleapis.com"

    def _headers(self) -> dict:
        """Generate headers for API requests"""
        return {
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json; charset=utf-8",
            "origin": "https://labs.google",
            "referer": "https://labs.google/",
            "user-agent": "Mozilla/5.0"
        }

    def generate_video_async(
        self,
        prompt: str,
        aspect_ratio: str = "VIDEO_ASPECT_RATIO_LANDSCAPE",
        model_key: str = "veo_3_1_t2v_fast_ultra",
        quality: str = "1080p",
        num_videos: int = 1,
        project_id: Optional[str] = None
    ) -> List[str]:
        """
        Generate video asynchronously using batchAsyncGenerateVideoText endpoint.

        Args:
            prompt: Text prompt for video generation
            aspect_ratio: Video aspect ratio
            model_key: Video model to use
            quality: Video quality ("720p" or "1080p")
            num_videos: Number of videos to generate (max 4)
            project_id: Optional project ID

        Returns:
            List of operation names for status checking
        """
        url = f"{self.base_url}/v1/video:batchAsyncGenerateVideoText"

        # Limit to 4 videos per batch
        num_videos = min(num_videos, 4)

        # Build requests
        requests_list = []
        for i in range(num_videos):
            seed = int(time.time() * 1000) + i
            request_item = {
                "aspectRatio": aspect_ratio,
                "seed": seed,
                "videoModelKey": model_key,
                "textInput": {"prompt": prompt}
            }
            requests_list.append(request_item)

        payload = {"requests": requests_list}
        if project_id:
            payload["clientContext"] = {"projectId": project_id}

        try:
            self.log(f"[Veo] Generating {num_videos} video(s) at {quality}...")
            response = requests.post(url, headers=self._headers(), json=payload, timeout=(20, 180))
            response.raise_for_status()

            data = response.json()
            operations = data.get("operations", [])
            operation_names = []

            for op in operations:
                name = (op.get("operation") or {}).get("name") or op.get("name") or ""
                if name:
                    operation_names.append(name)

            self.log(f"[Veo] Started {len(operation_names)} generation operations")
            return operation_names

        except Exception as e:
            self.log(f"[Veo] Error generating video: {e}")
            raise

    def check_generation_status(self, operation_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Check status of video generation using batchCheckAsyncVideoGenerationStatus endpoint.

        Args:
            operation_names: List of operation names to check

        Returns:
            Dictionary mapping operation names to their status and URLs
        """
        if not operation_names:
            return {}

        url = f"{self.base_url}/v1/video:batchCheckAsyncVideoGenerationStatus"

        # Build operations payload
        operations = [{"operation": {"name": name}} for name in operation_names]
        payload = {"operations": operations}

        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=(20, 180))
            response.raise_for_status()

            data = response.json()
            results = {}

            for item in data.get("operations", []):
                op_name = (item.get("operation") or {}).get("name") or item.get("name") or ""
                if not op_name:
                    continue

                # Determine status
                status = self._normalize_status(item)

                # Extract URLs
                video_urls = self._extract_video_urls(item)

                results[op_name] = {
                    "status": status,
                    "video_urls": video_urls,
                    "raw": item
                }

            return results

        except Exception as e:
            self.log(f"[Veo] Error checking status: {e}")
            return {}

    def _normalize_status(self, item: dict) -> str:
        """Normalize status from API response"""
        if item.get("done") is True:
            if item.get("error"):
                return "FAILED"
            return "COMPLETED"

        status = item.get("status") or ""
        if status in ("MEDIA_GENERATION_STATUS_SUCCEEDED", "SUCCEEDED", "SUCCESS"):
            return "COMPLETED"
        if status in ("MEDIA_GENERATION_STATUS_FAILED", "FAILED", "ERROR"):
            return "FAILED"
        return "PROCESSING"

    def _extract_video_urls(self, item: dict) -> List[str]:
        """Extract video URLs from API response"""
        urls = []

        # Check response field
        response = item.get("response", {})
        if response:
            urls.extend(self._collect_urls(response))

        # Check root level
        urls.extend(self._collect_urls(item))

        # Deduplicate and prioritize video URLs
        video_urls = []
        seen = set()
        for url in urls:
            if "/video/" in url and url not in seen:
                video_urls.append(url)
                seen.add(url)

        return video_urls

    def _collect_urls(self, obj: Any) -> List[str]:
        """Recursively collect URLs from object"""
        urls = []
        url_keys = {
            "gcsUrl", "gcsUri", "signedUrl", "signedUri",
            "downloadUrl", "downloadUri", "videoUrl",
            "url", "uri", "fileUri"
        }

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in url_keys and isinstance(value, str):
                    is_valid_url = (
                        value.startswith("http://") or
                        value.startswith("https://") or
                        value.startswith("gs://")
                    )
                    if is_valid_url:
                        urls.append(value)
                else:
                    urls.extend(self._collect_urls(value))
        elif isinstance(obj, list):
            for item in obj:
                urls.extend(self._collect_urls(item))

        return urls

    def download_video(
        self,
        url: str,
        output_path: str,
        timeout: int = 300,
        max_retries: int = 3
    ) -> bool:
        """
        Download video from URL to output path with automatic retry on transient failures.

        Args:
            url: Video URL to download
            output_path: Local path to save video
            timeout: Download timeout in seconds
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            True if download succeeded, False otherwise
        """
        self.log(f"[Veo] Downloading video: {os.path.basename(output_path)}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        last_exception = None

        for attempt in range(max_retries):
            try:
                # Download with streaming
                with requests.get(url, stream=True, timeout=timeout, allow_redirects=True) as r:
                    r.raise_for_status()

                    total = int(r.headers.get('content-length', 0))
                    downloaded = 0

                    with open(output_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)

                    # Log progress
                    if total > 0:
                        progress = (downloaded / total) * 100
                        self.log(f"[Veo] Downloaded {downloaded}/{total} bytes ({progress:.1f}%)")

                # Verify download
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    self.log("[Veo] Download verification failed - file empty or missing")
                    # Clean up empty or corrupted file
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                            self.log("[Veo] Removed corrupted file")
                        except OSError:
                            pass
                    return False

                self.log(f"[Veo] Download complete: {output_path}")
                return True

            except (IncompleteRead, Urllib3IncompleteRead, ChunkedEncodingError) as e:
                # Handle incomplete read errors (connection broken during download)
                last_exception = e
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.log(
                        f"[Veo] Incomplete download, retrying in {wait_time}s... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    self.log(f"[Veo] Download failed after {max_retries} attempts: {e}")

            except (ConnectionError, Timeout) as e:
                # Handle connection and timeout errors
                last_exception = e
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.log(
                        f"[Veo] Connection error, retrying in {wait_time}s... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    self.log(f"[Veo] Download failed after {max_retries} attempts: {e}")

            except RequestException as e:
                # Handle other request exceptions
                last_exception = e
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass

                # Check if it's a DNS resolution error
                if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        self.log(
                            f"[Veo] DNS resolution error, retrying in {wait_time}s... "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        self.log(f"[Veo] Download failed after {max_retries} attempts: {e}")
                else:
                    # For other request exceptions, fail immediately
                    self.log(f"[Veo] Download error: {e}")
                    return False

            except Exception as e:
                # Handle unexpected errors - don't retry
                self.log(f"[Veo] Unexpected download error: {e}")
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                return False

        # If we've exhausted all retries, log and return False
        if last_exception:
            self.log(f"[Veo] Download failed after {max_retries} attempts: {last_exception}")

        return False

    def poll_and_download(
        self,
        operation_names: List[str],
        output_dir: str,
        filename_prefix: str = "video",
        quality: str = "1080p",
        max_polls: int = 120,
        poll_interval: int = 5
    ) -> List[Tuple[str, str]]:
        """
        Poll operation status and auto-download completed videos.

        Args:
            operation_names: List of operation names to poll
            output_dir: Directory to save downloaded videos
            filename_prefix: Prefix for output filenames
            quality: Quality indicator for filename
            max_polls: Maximum number of polling attempts
            poll_interval: Seconds between polls

        Returns:
            List of tuples (operation_name, local_path) for completed downloads
        """
        completed = []
        pending = operation_names.copy()

        for poll_count in range(max_polls):
            if not pending:
                break

            self.log(f"[Veo] Polling status (attempt {poll_count + 1}/{max_polls})...")
            statuses = self.check_generation_status(pending)

            still_pending = []
            for op_name in pending:
                status_info = statuses.get(op_name, {})
                status = status_info.get("status", "PROCESSING")

                if status == "COMPLETED":
                    video_urls = status_info.get("video_urls", [])
                    if video_urls:
                        # Download first video URL
                        url = video_urls[0]
                        filename = f"{filename_prefix}_{quality}_{len(completed) + 1}.mp4"
                        output_path = os.path.join(output_dir, filename)

                        if self.download_video(url, output_path):
                            completed.append((op_name, output_path))
                            self.log(f"[Veo] Completed: {filename}")
                        else:
                            self.log(f"[Veo] Download failed for {op_name}")
                    else:
                        self.log(f"[Veo] No video URL for completed operation {op_name}")
                elif status == "FAILED":
                    self.log(f"[Veo] Generation failed: {op_name}")
                else:
                    # Still processing
                    still_pending.append(op_name)

            pending = still_pending

            if pending:
                time.sleep(poll_interval)

        if pending:
            msg = f"[Veo] Warning: {len(pending)} operations still pending"
            msg += f" after {max_polls} polls"
            self.log(msg)

        return completed
