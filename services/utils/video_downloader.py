"""Shared video download logic"""
import os
import time
from http.client import IncompleteRead

import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError, RequestException, Timeout
from urllib3.exceptions import IncompleteRead as Urllib3IncompleteRead


class VideoDownloader:
    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def download(
        self, url: str, output_path: str, timeout=300, bearer_token=None, max_retries=3
    ) -> str:
        """
        Download video from URL to output path with automatic retry on transient failures.

        Args:
            url: Video URL to download
            output_path: Local path to save video
            timeout: Download timeout in seconds
            bearer_token: Optional bearer token for authentication
                          (required for multi-account downloads)
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Path to downloaded file

        Raises:
            Exception: If download fails after all retries
        """
        self.log(f"[Download] {os.path.basename(output_path)}")

        # Build headers with optional authentication
        headers = {}
        if bearer_token:
            headers = {
                "authorization": f"Bearer {bearer_token}",
                "user-agent": "Mozilla/5.0"
            }

        last_exception = None

        for attempt in range(max_retries):
            try:
                with requests.get(
                    url, stream=True, timeout=timeout,
                    allow_redirects=True, headers=headers
                ) as r:
                    r.raise_for_status()
                    with open(output_path, 'wb') as f:
                        for chunk in r.iter_content(8192):
                            if chunk:
                                f.write(chunk)

                # Verify download completed successfully
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    raise Exception("Download failed: file is empty or missing")

                self.log("[Download] ✓ Complete")
                return output_path

            except (IncompleteRead, Urllib3IncompleteRead, ChunkedEncodingError) as e:
                # Handle incomplete read errors (connection broken during download)
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.log(
                        f"[WARN] Incomplete download, retrying in {wait_time}s... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    self.log(f"[ERR] Download failed after {max_retries} attempts: {e}")

            except (ConnectionError, Timeout) as e:
                # Handle connection and timeout errors
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.log(
                        f"[WARN] Connection error, retrying in {wait_time}s... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    self.log(f"[ERR] Download failed after {max_retries} attempts: {e}")

            except RequestException as e:
                # Handle other request exceptions
                last_exception = e
                # Check if it's a DNS resolution error
                if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        self.log(
                            f"[WARN] DNS resolution error, retrying in {wait_time}s... "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        self.log(f"[ERR] Download failed after {max_retries} attempts: {e}")
                else:
                    # For other request exceptions, fail immediately
                    self.log(f"[ERR] Download error: {e}")
                    raise

            except Exception as e:
                # Handle unexpected errors - don't retry
                self.log(f"[ERR] Unexpected download error: {e}")
                raise

        # If we've exhausted all retries, raise the last exception
        if last_exception:
            raise Exception(f"Download failed after {max_retries} attempts: {last_exception}")
        else:
            raise Exception("Download failed")
