"""Shared video download logic"""
import os, requests

class VideoDownloader:
    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def download(self, url: str, output_path: str, timeout=300, bearer_token=None) -> str:
        """
        Download video from URL to output path.

        Args:
            url: Video URL to download
            output_path: Local path to save video
            timeout: Download timeout in seconds
            bearer_token: Optional bearer token for authentication
                          (required for multi-account downloads)

        Returns:
            Path to downloaded file
        """
        self.log(f"[Download] {os.path.basename(output_path)}")

        # Build headers with optional authentication
        headers = {}
        if bearer_token:
            headers = {
                "authorization": f"Bearer {bearer_token}",
                "user-agent": "Mozilla/5.0"
            }

        with requests.get(
            url, stream=True, timeout=timeout,
            allow_redirects=True, headers=headers
        ) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("Download failed")
        self.log("[Download] ✓ Complete")
        return output_path
