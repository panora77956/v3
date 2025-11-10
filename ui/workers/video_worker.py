# ui/workers/video_worker.py
"""
Video Generation Worker - Non-blocking video generation using QThread
Prevents UI freezing during video generation API calls
"""
import os
import shutil
import subprocess
import time

from PyQt5.QtCore import QThread, pyqtSignal

from services.account_manager import get_account_manager
from services.google.labs_flow_client import DEFAULT_PROJECT_ID, LabsFlowClient
from services.utils.video_downloader import VideoDownloader
from utils import config as cfg
from utils.filename_sanitizer import sanitize_filename


class VideoGenerationWorker(QThread):
    """
    Background worker for video generation to prevent UI freeze.
    
    Signals:
        progress_updated: Emitted when progress changes (scene_idx, total_scenes, status_message)
        scene_completed: Emitted when a scene video completes (scene_idx, video_path)
        all_completed: Emitted when all scenes complete (list of video_paths)
        error_occurred: Emitted on error (error_message)
        job_card: Emitted for video status updates (card_dict)
        log: Emitted for log messages (log_message)
    """

    # Signals
    progress_updated = pyqtSignal(int, int, str)  # scene_idx, total_scenes, status
    scene_completed = pyqtSignal(int, str)  # scene_idx, video_path
    all_completed = pyqtSignal(list)  # all video_paths
    error_occurred = pyqtSignal(str)  # error_message
    job_card = pyqtSignal(dict)  # card data for UI updates
    log = pyqtSignal(str)  # log messages

    def __init__(self, payload, parent=None):
        """
        Initialize video generation worker.
        
        Args:
            payload: Dictionary containing:
                - scenes: List of scene dictionaries with 'prompt' and 'aspect'
                - copies: Number of video copies per scene
                - model_key: Video model to use
                - title: Project title
                - dir_videos: Output directory for videos
                - upscale_4k: Whether to upscale to 4K
                - auto_download: Whether to auto-download videos
                - quality: Video quality (1080p, 720p, etc.)
            parent: Parent QObject
        """
        super().__init__(parent)
        self.payload = payload
        self.cancelled = False
        self.video_downloader = VideoDownloader(log_callback=lambda msg: self.log.emit(msg))

    def cancel(self):
        """Cancel the video generation operation."""
        self.cancelled = True
        self.log.emit("[INFO] Video generation cancelled by user")

    def _handle_labs_event(self, event):
        """Handle diagnostic events from LabsClient."""
        kind = event.get("kind", "")
        if kind == "video_generator_info":
            gen_type = event.get("generator_type", "Unknown")
            model = event.get("model_key", "")
            aspect = event.get("aspect_ratio", "")
            self.log.emit(f"[INFO] Video Generator: {gen_type} | Model: {model} | Aspect: {aspect}")
        elif kind == "api_call_info":
            endpoint_type = event.get("endpoint_type", "")
            num_req = event.get("num_requests", 0)
            self.log.emit(f"[INFO] API Call: {endpoint_type} endpoint | {num_req} request(s)")
        elif kind == "trying_model":
            model = event.get("model_key", "")
            self.log.emit(f"[DEBUG] Trying model: {model}")
        elif kind == "model_success":
            model = event.get("model_key", "")
            self.log.emit(f"[DEBUG] Model {model} succeeded")
        elif kind == "model_failed":
            model = event.get("model_key", "")
            error = event.get("error", "")
            self.log.emit(f"[WARN] Model {model} failed: {error}")
        elif kind == "operations_result":
            num_ops = event.get("num_operations", 0)
            self.log.emit(f"[DEBUG] API returned {num_ops} operations")
        elif kind == "start_one_result":
            count = event.get("operation_count", 0)
            requested = event.get("requested_copies", 0)
            self.log.emit(f"[INFO] Video generation: {count}/{requested} operations created")
        elif kind == "http_other_err":
            code = event.get("code", "")
            detail = event.get("detail", "")
            self.log.emit(f"[ERROR] HTTP {code}: {detail}")

    def _download(self, url, dst_path, bearer_token=None):
        """
        Download video from URL with optional bearer token authentication.
        
        Args:
            url: Video URL to download
            dst_path: Destination path for downloaded file
            bearer_token: Optional bearer token for authentication (required for multi-account)
        
        Returns:
            True if download succeeded, False otherwise
        """
        try:
            self.video_downloader.download(url, dst_path, bearer_token=bearer_token)
            return True
        except Exception as e:
            self.log.emit(f"[ERR] Download fail: {e}")
            return False

    def _make_thumb(self, video_path, out_dir, scene, copy):
        """Generate thumbnail from video."""
        try:
            os.makedirs(out_dir, exist_ok=True)
            thumb = os.path.join(out_dir, f"thumb_c{scene}_v{copy}.jpg")
            if shutil.which("ffmpeg"):
                cmd = ["ffmpeg", "-y", "-ss", "00:00:00", "-i", video_path,
                       "-frames:v", "1", "-q:v", "3", thumb]
                subprocess.run(cmd, check=True, capture_output=True)
                return thumb
        except Exception as e:
            self.log.emit(f"[WARN] Tạo thumbnail lỗi: {e}")
        return ""

    def run(self):
        """Execute video generation in background thread."""
        try:
            self._run_video()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log.emit(f"[ERR] Worker error: {e}")
            self.log.emit(f"[DEBUG] {error_details}")
            self.error_occurred.emit(str(e))

    def _run_video(self):
        """Main video generation logic."""
        p = self.payload
        st = cfg.load()

        # Ensure config is valid
        if not st or not isinstance(st, dict):
            self.log.emit("[ERROR] Configuration file is invalid or missing!")
            self.error_occurred.emit("Invalid configuration")
            return

        # Get account manager for multi-account support
        account_mgr = get_account_manager()

        # Check if multi-account mode is enabled for parallel processing
        if account_mgr.is_multi_account_enabled():
            enabled_accounts = account_mgr.get_enabled_accounts()
            self.log.emit(
                f"[INFO] Multi-account mode: {len(enabled_accounts)} accounts active"
            )

            # Log each account's details for transparency
            for idx, acc in enumerate(enabled_accounts, 1):
                token_count = len(acc.tokens)
                proj_id_short = (
                    acc.project_id[:12] + "..." if len(acc.project_id) > 12
                    else acc.project_id
                )
                self.log.emit(
                    f"[INFO]   Account {idx}: {acc.name} | "
                    f"Project: {proj_id_short} | Tokens: {token_count}"
                )

            self.log.emit(
                "[INFO] Processing mode: PARALLEL (simultaneous processing across accounts)"
            )
            
            # Use parallel processing for faster generation
            self._run_video_parallel(p, account_mgr)
            return

        copies = p["copies"]
        title = p["title"]
        dir_videos = p["dir_videos"]
        thumbs_dir = os.path.join(dir_videos, "thumbs")

        total_scenes = len(p["scenes"])
        jobs = []
        client_cache = {}

        # Event handler for diagnostic logging
        def on_labs_event(event):
            self._handle_labs_event(event)

        # Start video generation for each scene
        for scene_idx, scene in enumerate(p["scenes"], start=1):
            if self.cancelled:
                self.error_occurred.emit("Generation cancelled by user")
                return

            # Use actual_scene_num if provided (for retry), otherwise use scene_idx
            actual_scene_num = scene.get("actual_scene_num", scene_idx)

            # Update progress: Starting scene
            self.progress_updated.emit(
                actual_scene_num - 1, total_scenes, f"Submitting scene {actual_scene_num}..."
            )

            ratio = scene["aspect"]
            model_key = p.get("model_key", "")

            # Get account for this scene (multi-account or legacy)
            if account_mgr.is_multi_account_enabled():
                # Use round-robin account selection for this scene
                # Use scene_idx - 1 for round-robin (0-indexed), but actual_scene_num for display
                account = account_mgr.get_account_for_scene(scene_idx - 1)
                if not account:
                    self.log.emit("[ERROR] No enabled accounts available!")
                    self.error_occurred.emit("No enabled accounts")
                    return

                tokens = account.tokens
                project_id = account.project_id

                # Validate tokens
                if not tokens:
                    self.log.emit(f"[ERROR] Account '{account.name}' has no tokens!")
                    self.error_occurred.emit(f"Account '{account.name}' has no tokens")
                    return

                # Validate project_id
                if not project_id or not isinstance(project_id, str) or not project_id.strip():
                    self.log.emit(f"[ERROR] Account '{account.name}' has invalid project_id!")
                    self.error_occurred.emit(
                        f"Account '{account.name}' has invalid project_id"
                    )
                    return

                project_id = project_id.strip()
                proj_id_short = (
                    project_id[:12] + "..." if len(project_id) > 12
                    else project_id
                )
                self.log.emit(
                    f"[INFO] Scene {actual_scene_num}: Using account '{account.name}' | "
                    f"Project: {proj_id_short}"
                )
            else:
                # Legacy mode: use old tokens and default_project_id
                tokens = st.get("tokens") or []
                if not tokens:
                    self.log.emit(
                        "[ERROR] No Google Labs tokens configured! "
                        "Please add tokens in API Credentials."
                    )
                    self.error_occurred.emit("No tokens configured")
                    return

                # Get project_id with strict validation and fallback
                project_id = st.get("default_project_id")
                if not project_id or not isinstance(project_id, str) or not project_id.strip():
                    # Use fallback if missing/invalid
                    project_id = DEFAULT_PROJECT_ID
                    self.log.emit(f"[INFO] Using default project_id: {project_id}")
                else:
                    project_id = project_id.strip()
                    self.log.emit(f"[INFO] Using configured project_id: {project_id}")

                # Validate project_id format (should be UUID-like)
                if len(project_id) < 10:
                    self.log.emit(
                        f"[WARN] Project ID '{project_id}' seems invalid (too short), "
                        "using default"
                    )
                    project_id = DEFAULT_PROJECT_ID

            # Create or reuse client for this project_id
            if project_id not in client_cache:
                client_cache[project_id] = LabsFlowClient(tokens, on_event=on_labs_event)
            client = client_cache[project_id]

            # Single API call with copies parameter
            body = {
                "prompt": scene["prompt"],
                "copies": copies,
                "model": model_key,
                "aspect_ratio": ratio
            }
            
            # Store bearer token for multi-account download support
            # Extract the first token from the tokens list if available
            if tokens and len(tokens) > 0:
                body["bearer_token"] = tokens[0]
            
            # Store account info for multi-account batch checking
            if account_mgr.is_multi_account_enabled():
                body["account_name"] = account.name
                body["project_id"] = project_id
                body["tokens"] = tokens
            
            self.log.emit(f"[INFO] Start scene {actual_scene_num} with {copies} copies in one batch…")
            rc = client.start_one(
                body, model_key, ratio, scene["prompt"], copies=copies, project_id=project_id
            )

            if rc > 0:
                # Only create cards for operations that actually exist in the API response
                actual_count = len(body.get("operation_names", []))

                if actual_count < copies:
                    self.log.emit(f"[WARN] Scene {actual_scene_num}: API returned {actual_count} operations but {copies} copies were requested")

                # Create cards only for videos that actually exist
                for copy_idx in range(1, actual_count + 1):
                    card = {
                        "scene": actual_scene_num,
                        "copy": copy_idx,
                        "status": "PROCESSING",
                        "json": scene["prompt"],
                        "url": "",
                        "path": "",
                        "thumb": "",
                        "dir": dir_videos
                    }
                    self.job_card.emit(card)

                    # Store card data with copy index for operation name mapping
                    job_info = {
                        'card': card,
                        'body': body,
                        'scene': actual_scene_num,
                        'copy': copy_idx
                    }
                    jobs.append(job_info)
            else:
                # All copies failed to start
                for copy_idx in range(1, copies + 1):
                    card = {
                        "scene": actual_scene_num,
                        "copy": copy_idx,
                        "status": "FAILED_START",
                        "error_reason": "Failed to start video generation",
                        "json": scene["prompt"],
                        "url": "",
                        "path": "",
                        "thumb": "",
                        "dir": dir_videos
                    }
                    self.job_card.emit(card)

        # Polling loop with improved error handling
        retry_count = {}
        download_retry_count = {}
        max_retries = 3
        max_download_retries = 5

        completed_videos = []

        for poll_round in range(120):
            if self.cancelled:
                self.log.emit("[INFO] Đã dừng xử lý theo yêu cầu người dùng.")
                return

            if not jobs:
                self.log.emit("[INFO] Tất cả video đã hoàn tất hoặc thất bại.")
                break

            # Update progress based on completed jobs
            completed_count = len(completed_videos)
            current_scene = min(completed_count + 1, total_scenes)
            self.progress_updated.emit(
                completed_count,
                total_scenes,
                f"Processing... ({completed_count}/{total_scenes} scenes completed)"
            )

            # Multi-account batch check: group jobs by account
            rs = {}
            
            try:
                if account_mgr.is_multi_account_enabled():
                    # Group jobs by account
                    jobs_by_account = {}
                    jobs_without_account = []
                    
                    for job_info in jobs:
                        job_dict = job_info['body']
                        acc_name = job_dict.get("account_name")
                        if acc_name:
                            if acc_name not in jobs_by_account:
                                jobs_by_account[acc_name] = []
                            jobs_by_account[acc_name].append(job_info)
                        else:
                            jobs_without_account.append(job_info)
                    
                    # Check each account's operations with its own client
                    for acc_name, account_jobs in jobs_by_account.items():
                        # Find the account
                        account = None
                        for acc in account_mgr.get_all_accounts():
                            if acc.name == acc_name:
                                account = acc
                                break
                        
                        if not account:
                            self.log.emit(f"[WARN] Account {acc_name} not found, skipping")
                            continue
                        
                        # Create client for this account
                        account_client = LabsFlowClient(account.tokens, on_event=on_labs_event)
                        
                        # Collect operations and metadata for this account
                        account_names = []
                        account_metadata = {}
                        for job_info in account_jobs:
                            job_dict = job_info['body']
                            account_names.extend(job_dict.get("operation_names", []))
                            op_meta = job_dict.get("operation_metadata", {})
                            if op_meta:
                                account_metadata.update(op_meta)
                        
                        # Check this account's operations with project_id
                        if account_names:
                            try:
                                account_rs = account_client.batch_check_operations(
                                    account_names, account_metadata, project_id=account.project_id
                                )
                                rs.update(account_rs)
                            except Exception as e:
                                self.log.emit(f"[WARN] Check error for {acc_name}: {e}")
                    
                    # Check jobs without account using fallback (if any)
                    if jobs_without_account:
                        fallback_names = []
                        fallback_metadata = {}
                        for job_info in jobs_without_account:
                            job_dict = job_info['body']
                            fallback_names.extend(job_dict.get("operation_names", []))
                            op_meta = job_dict.get("operation_metadata", {})
                            if op_meta:
                                fallback_metadata.update(op_meta)
                        
                        if fallback_names:
                            try:
                                # Use the last client in cache as fallback
                                fallback_client = list(client_cache.values())[-1] if client_cache else None
                                if fallback_client:
                                    fallback_rs = fallback_client.batch_check_operations(fallback_names, fallback_metadata)
                                    rs.update(fallback_rs)
                            except Exception as e:
                                self.log.emit(f"[WARN] Check error for jobs without account: {e}")
                else:
                    # Single-account mode (legacy)
                    names = []
                    metadata = {}
                    for job_info in jobs:
                        job_dict = job_info['body']
                        names.extend(job_dict.get("operation_names", []))
                        op_meta = job_dict.get("operation_metadata", {})
                        if op_meta:
                            metadata.update(op_meta)
                    
                    # Use the last client in cache
                    client = list(client_cache.values())[-1] if client_cache else None
                    if client and names:
                        rs = client.batch_check_operations(names, metadata)
            except Exception as e:
                self.log.emit(f"[WARN] Lỗi kiểm tra trạng thái (vòng {poll_round + 1}): {e}")
                time.sleep(10)
                continue

            new_jobs = []
            for job_info in jobs:
                card = job_info['card']
                job_dict = job_info['body']
                copy_idx = job_info['copy']

                # Get operation names list and map this copy to its operation
                op_names = job_dict.get("operation_names", [])
                if not op_names:
                    if 'no_op_count' not in job_info:
                        job_info['no_op_count'] = 0
                    job_info['no_op_count'] += 1

                    if job_info['no_op_count'] > 3:
                        sc = card['scene']
                        cp = card['copy']
                        self.log.emit(f"[WARN] Cảnh {sc} video {cp}: không có operation name sau 3 lần thử")
                    else:
                        new_jobs.append(job_info)
                    continue

                # Map copy index to the correct operation name
                op_index = copy_idx - 1
                if op_index >= len(op_names):
                    sc = card['scene']
                    cp = card['copy']
                    self.log.emit(f"[ERR] Cảnh {sc} video {cp}: operation index {op_index} out of bounds")
                    card["status"] = "FAILED"
                    card["error_reason"] = "Operation index out of bounds"
                    self.job_card.emit(card)
                    continue

                op_name = op_names[op_index]
                op_result = rs.get(op_name) or {}

                # Check raw API response
                raw_response = op_result.get('raw', {})
                status = raw_response.get('status', '')

                scene = card["scene"]
                copy_num = card["copy"]

                if status == 'MEDIA_GENERATION_STATUS_SUCCESSFUL':
                    # Extract video URL
                    op_metadata = raw_response.get('operation', {}).get('metadata', {})
                    video_info = op_metadata.get('video', {})
                    video_url = video_info.get('fifeUrl', '')

                    if video_url:
                        card["status"] = "READY"
                        card["url"] = video_url

                        self.log.emit(f"[SUCCESS] Scene {scene} Copy {copy_num}: Video ready!")

                        # Update progress: Downloading
                        self.progress_updated.emit(
                            scene - 1,
                            total_scenes,
                            f"Downloading scene {scene} copy {copy_num}..."
                        )

                        # Download video
                        raw_fn = f"{title}_scene{scene}_copy{copy_num}.mp4"
                        fn = sanitize_filename(raw_fn)
                        fp = os.path.join(dir_videos, fn)

                        self.log.emit(f"[INFO] Downloading scene {scene} copy {copy_num}...")

                        # Get bearer token for multi-account download support
                        bearer_token = job_dict.get("bearer_token")

                        try:
                            if self._download(video_url, fp, bearer_token=bearer_token):
                                card["status"] = "DOWNLOADED"
                                card["path"] = fp

                                thumb = self._make_thumb(fp, thumbs_dir, scene, copy_num)
                                card["thumb"] = thumb

                                self.log.emit(f"[SUCCESS] ✓ Downloaded: {os.path.basename(fp)}")

                                # Track completed video and emit signal
                                if fp not in completed_videos:
                                    completed_videos.append(fp)
                                    self.scene_completed.emit(scene, fp)
                            else:
                                # Track download retries
                                download_key = f"{scene}_{copy_num}"
                                retries = download_retry_count.get(download_key, 0)
                                if retries < max_download_retries:
                                    download_retry_count[download_key] = retries + 1
                                    self.log.emit(f"[WARN] Download failed, will retry ({retries + 1}/{max_download_retries})")
                                    card["status"] = "DOWNLOAD_FAILED"
                                    card["url"] = video_url
                                    self.job_card.emit(card)
                                    new_jobs.append(job_info)
                                    continue
                                else:
                                    self.log.emit(f"[ERR] Download failed after {max_download_retries} attempts")
                                    card["status"] = "DOWNLOAD_FAILED"
                                    card["url"] = video_url
                                    card["error_reason"] = "Download failed after retries"
                                    self.job_card.emit(card)
                        except Exception as e:
                            download_key = f"{scene}_{copy_num}"
                            retries = download_retry_count.get(download_key, 0)
                            if retries < max_download_retries:
                                download_retry_count[download_key] = retries + 1
                                self.log.emit(f"[ERR] Download error: {e} - will retry ({retries + 1}/{max_download_retries})")
                                card["status"] = "DOWNLOAD_FAILED"
                                card["url"] = video_url
                                self.job_card.emit(card)
                                new_jobs.append(job_info)
                                continue
                            else:
                                self.log.emit(f"[ERR] Download error after {max_download_retries} attempts: {e}")
                                card["status"] = "DOWNLOAD_FAILED"
                                card["url"] = video_url
                                card["error_reason"] = f"Download error: {str(e)[:50]}"
                                self.job_card.emit(card)

                        self.job_card.emit(card)
                    else:
                        self.log.emit(f"[ERR] Scene {scene} Copy {copy_num}: No video URL in response")
                        card["status"] = "DONE_NO_URL"
                        card["error_reason"] = "No video URL in response"
                        self.job_card.emit(card)

                elif status == 'MEDIA_GENERATION_STATUS_FAILED':
                    # Extract error details
                    error_info = raw_response.get('operation', {}).get('error', {})
                    error_message = error_info.get('message', '')

                    # Categorize the error
                    if 'quota' in error_message.lower() or 'limit' in error_message.lower():
                        error_reason = "Vượt quota API"
                    elif 'policy' in error_message.lower() or 'content' in error_message.lower() or 'safety' in error_message.lower():
                        error_reason = "Nội dung không phù hợp"
                    elif 'timeout' in error_message.lower():
                        error_reason = "Timeout"
                    elif error_message:
                        error_reason = error_message[:80]
                    else:
                        error_reason = "Video generation failed"

                    card["status"] = "FAILED"
                    card["error_reason"] = error_reason
                    self.log.emit(f"[ERR] Scene {scene} Copy {copy_num} FAILED: {error_reason}")
                    self.job_card.emit(card)

                else:
                    # Still processing
                    card["status"] = "PROCESSING"
                    self.job_card.emit(card)
                    new_jobs.append(job_info)

            jobs = new_jobs

            if jobs:
                poll_info = f"vòng {poll_round + 1}/120"
                if poll_round >= 100:
                    self.log.emit(f"[WARN] Đang chờ {len(jobs)} video ({poll_info}) - sắp hết thời gian chờ!")
                else:
                    self.log.emit(f"[INFO] Đang chờ {len(jobs)} video ({poll_info})...")
                time.sleep(5)

        # Handle timeout
        if jobs:
            for job_info in jobs:
                card = job_info['card']
                card["status"] = "TIMEOUT"
                card["error_reason"] = "Video generation timed out"
                self.job_card.emit(card)
                self.log.emit(f"[TIMEOUT] Scene {card['scene']} Copy {card['copy']}: Generation timed out")

        # Emit completion signal
        self.all_completed.emit(completed_videos)
        self.log.emit(f"[INFO] Video generation completed: {len(completed_videos)} videos downloaded")

    def _run_video_parallel(self, p, account_mgr):
        """
        Parallel video generation using multiple accounts with threading.
        Distributes scenes across accounts using round-robin for simultaneous processing.
        This is much faster than sequential processing when multiple accounts are available.
        """
        import threading
        from queue import Queue

        copies = p["copies"]
        title = p["title"]
        dir_videos = p["dir_videos"]
        thumbs_dir = os.path.join(dir_videos, "thumbs")
        
        accounts = account_mgr.get_enabled_accounts()
        num_accounts = len(accounts)
        total_scenes = len(p["scenes"])

        self.log.emit(f"[INFO] 🚀 Parallel mode: {num_accounts} accounts, {total_scenes} scenes")

        # Distribute scenes across accounts using round-robin
        batches = [[] for _ in range(num_accounts)]
        for scene_idx, scene in enumerate(p["scenes"], start=1):
            account_idx = (scene_idx - 1) % num_accounts
            batches[account_idx].append((scene_idx, scene))

        # Results queue for thread-safe communication
        results_queue = Queue()
        all_jobs = []  # Jobs storage protected by jobs_lock for thread-safety
        jobs_lock = threading.Lock()

        # Create and start threads
        threads = []
        for i, (account, batch) in enumerate(zip(accounts, batches)):
            if not batch:
                continue

            thread = threading.Thread(
                target=self._process_scene_batch,
                args=(account, batch, p, results_queue, all_jobs, jobs_lock, i),
                daemon=True,
                name=f"VideoWorker-{account.name}"
            )
            threads.append(thread)
            self.log.emit(f"[INFO] Thread {i+1}: {len(batch)} scenes → {account.name}")
            thread.start()

        # Monitor progress from all threads
        completed_starts = 0

        while completed_starts < total_scenes:
            if self.cancelled:
                self.log.emit("[INFO] Parallel processing cancelled by user")
                break

            try:
                # Wait for results from any thread
                import queue
                msg_type, data = results_queue.get(timeout=1.0)

                if msg_type == "scene_started":
                    scene_idx, job_infos = data
                    completed_starts += 1
                    if job_infos:
                        self.log.emit(
                            f"[INFO] Scene {scene_idx} started ({completed_starts}/{total_scenes})"
                        )
                    else:
                        self.log.emit(
                            f"[ERROR] Scene {scene_idx} failed to start "
                            f"({completed_starts}/{total_scenes})"
                        )
                elif msg_type == "card":
                    # Emit card update
                    self.job_card.emit(data)
                elif msg_type == "log":
                    self.log.emit(data)

            except queue.Empty:
                # Timeout, check if threads still running
                if all(not t.is_alive() for t in threads):
                    break
            except Exception as e:
                self.log.emit(f"[WARN] Progress monitoring error: {e}")
                if all(not t.is_alive() for t in threads):
                    break

        # Wait for all threads to complete scene starts
        for thread in threads:
            thread.join(timeout=60.0)  # 60s timeout for slow network/API

        # Summary of scene starts
        if len(all_jobs) == 0:
            self.log.emit(
                f"[ERROR] All {total_scenes} scenes failed to start. "
                "No video generation jobs were created."
            )
            self.error_occurred.emit("All scenes failed to start")
        else:
            successful_scenes = len(set(job['scene'] for job in all_jobs))
            self.log.emit(
                f"[INFO] {successful_scenes}/{total_scenes} scenes started successfully. "
                f"Starting polling for {len(all_jobs)} jobs..."
            )

        # Polling loop with improved error handling
        retry_count = {}
        download_retry_count = {}
        max_retries = 3
        max_download_retries = 5

        completed_videos = []
        jobs = all_jobs  # Use all jobs from parallel processing

        for poll_round in range(120):
            if self.cancelled:
                self.log.emit("[INFO] Đã dừng xử lý theo yêu cầu người dùng.")
                return

            if not jobs:
                self.log.emit("[INFO] Tất cả video đã hoàn tất hoặc thất bại.")
                break

            # Update progress based on completed jobs
            completed_count = len(completed_videos)
            current_scene = min(completed_count + 1, total_scenes)
            self.progress_updated.emit(
                completed_count,
                total_scenes,
                f"Processing... ({completed_count}/{total_scenes} scenes completed)"
            )

            # Multi-account batch check: group jobs by account
            rs = {}
            
            try:
                # Group jobs by account
                jobs_by_account = {}
                jobs_without_account = []
                
                for job_info in jobs:
                    job_dict = job_info['body']
                    acc_name = job_dict.get("account_name")
                    if acc_name:
                        if acc_name not in jobs_by_account:
                            jobs_by_account[acc_name] = []
                        jobs_by_account[acc_name].append(job_info)
                    else:
                        jobs_without_account.append(job_info)
                
                # Check each account's operations with its own client
                for acc_name, account_jobs in jobs_by_account.items():
                    # Find the account
                    account = None
                    for acc in account_mgr.get_all_accounts():
                        if acc.name == acc_name:
                            account = acc
                            break
                    
                    if not account:
                        self.log.emit(f"[WARN] Account {acc_name} not found, skipping")
                        continue
                    
                    # Create event handler for diagnostic logging
                    def on_labs_event(event):
                        self._handle_labs_event(event)
                    
                    # Create client for this account
                    account_client = LabsFlowClient(account.tokens, on_event=on_labs_event)
                    
                    # Collect operations and metadata for this account
                    account_names = []
                    account_metadata = {}
                    for job_info in account_jobs:
                        job_dict = job_info['body']
                        account_names.extend(job_dict.get("operation_names", []))
                        op_meta = job_dict.get("operation_metadata", {})
                        if op_meta:
                            account_metadata.update(op_meta)
                    
                    # Check this account's operations with project_id
                    if account_names:
                        try:
                            account_rs = account_client.batch_check_operations(
                                account_names, account_metadata, project_id=account.project_id
                            )
                            rs.update(account_rs)
                        except Exception as e:
                            self.log.emit(f"[WARN] Check error for {acc_name}: {e}")
                
                # Check jobs without account using fallback (if any)
                if jobs_without_account:
                    self.log.emit(f"[WARN] {len(jobs_without_account)} jobs without account info")
                    
            except Exception as e:
                self.log.emit(f"[WARN] Lỗi kiểm tra trạng thái (vòng {poll_round + 1}): {e}")
                time.sleep(10)
                continue

            # Process results (same as sequential mode)
            new_jobs = []
            for job_info in jobs:
                card = job_info['card']
                job_dict = job_info['body']
                copy_idx = job_info['copy']

                # Get operation names list and map this copy to its operation
                op_names = job_dict.get("operation_names", [])
                if not op_names:
                    if 'no_op_count' not in job_info:
                        job_info['no_op_count'] = 0
                    job_info['no_op_count'] += 1

                    if job_info['no_op_count'] > 3:
                        sc = card['scene']
                        cp = card['copy']
                        self.log.emit(f"[WARN] Cảnh {sc} video {cp}: không có operation name sau 3 lần thử")
                    else:
                        new_jobs.append(job_info)
                    continue

                # Map copy index to the correct operation name
                op_index = copy_idx - 1
                if op_index >= len(op_names):
                    sc = card['scene']
                    cp = card['copy']
                    self.log.emit(f"[ERR] Cảnh {sc} video {cp}: operation index {op_index} out of bounds")
                    card["status"] = "FAILED"
                    card["error_reason"] = "Operation index out of bounds"
                    self.job_card.emit(card)
                    continue

                op_name = op_names[op_index]
                op_result = rs.get(op_name) or {}

                # Check raw API response
                raw_response = op_result.get('raw', {})
                status = raw_response.get('status', '')

                scene = card["scene"]
                copy_num = card["copy"]

                if status == 'MEDIA_GENERATION_STATUS_SUCCESSFUL':
                    # Extract video URL
                    op_metadata = raw_response.get('operation', {}).get('metadata', {})
                    video_info = op_metadata.get('video', {})
                    video_url = video_info.get('fifeUrl', '')

                    if video_url:
                        card["status"] = "READY"
                        card["url"] = video_url

                        self.log.emit(f"[SUCCESS] Scene {scene} Copy {copy_num}: Video ready!")

                        # Update progress: Downloading
                        self.progress_updated.emit(
                            scene - 1,
                            total_scenes,
                            f"Downloading scene {scene} copy {copy_num}..."
                        )

                        # Download video
                        from utils.filename_sanitizer import sanitize_filename
                        raw_fn = f"{title}_scene{scene}_copy{copy_num}.mp4"
                        fn = sanitize_filename(raw_fn)
                        fp = os.path.join(dir_videos, fn)

                        self.log.emit(f"[INFO] Downloading scene {scene} copy {copy_num}...")

                        # Get bearer token for multi-account download support
                        bearer_token = job_dict.get("bearer_token")

                        try:
                            if self._download(video_url, fp, bearer_token=bearer_token):
                                card["status"] = "DOWNLOADED"
                                card["path"] = fp

                                thumb = self._make_thumb(fp, thumbs_dir, scene, copy_num)
                                card["thumb"] = thumb

                                self.log.emit(f"[SUCCESS] ✓ Downloaded: {os.path.basename(fp)}")

                                # Track completed video and emit signal
                                if fp not in completed_videos:
                                    completed_videos.append(fp)
                                    self.scene_completed.emit(scene, fp)
                            else:
                                # Track download retries
                                download_key = f"{scene}_{copy_num}"
                                retries = download_retry_count.get(download_key, 0)
                                if retries < max_download_retries:
                                    download_retry_count[download_key] = retries + 1
                                    self.log.emit(f"[WARN] Download failed, will retry ({retries + 1}/{max_download_retries})")
                                    card["status"] = "DOWNLOAD_FAILED"
                                    card["url"] = video_url
                                    self.job_card.emit(card)
                                    new_jobs.append(job_info)
                                    continue
                                else:
                                    self.log.emit(f"[ERR] Download failed after {max_download_retries} attempts")
                                    card["status"] = "DOWNLOAD_FAILED"
                                    card["url"] = video_url
                                    card["error_reason"] = "Download failed after retries"
                                    self.job_card.emit(card)
                        except Exception as e:
                            download_key = f"{scene}_{copy_num}"
                            retries = download_retry_count.get(download_key, 0)
                            if retries < max_download_retries:
                                download_retry_count[download_key] = retries + 1
                                self.log.emit(f"[ERR] Download error: {e} - will retry ({retries + 1}/{max_download_retries})")
                                card["status"] = "DOWNLOAD_FAILED"
                                card["url"] = video_url
                                self.job_card.emit(card)
                                new_jobs.append(job_info)
                                continue
                            else:
                                self.log.emit(f"[ERR] Download error after {max_download_retries} attempts: {e}")
                                card["status"] = "DOWNLOAD_FAILED"
                                card["url"] = video_url
                                card["error_reason"] = f"Download error: {str(e)[:50]}"
                                self.job_card.emit(card)

                        self.job_card.emit(card)
                    else:
                        self.log.emit(f"[ERR] Scene {scene} Copy {copy_num}: No video URL in response")
                        card["status"] = "DONE_NO_URL"
                        card["error_reason"] = "No video URL in response"
                        self.job_card.emit(card)

                elif status == 'MEDIA_GENERATION_STATUS_FAILED':
                    # Extract error details
                    error_info = raw_response.get('operation', {}).get('error', {})
                    error_message = error_info.get('message', '')

                    # Categorize the error
                    if 'quota' in error_message.lower() or 'limit' in error_message.lower():
                        error_reason = "Vượt quota API"
                    elif 'policy' in error_message.lower() or 'content' in error_message.lower() or 'safety' in error_message.lower():
                        error_reason = "Nội dung không phù hợp"
                    elif 'timeout' in error_message.lower():
                        error_reason = "Timeout"
                    elif error_message:
                        error_reason = error_message[:80]
                    else:
                        error_reason = "Video generation failed"

                    card["status"] = "FAILED"
                    card["error_reason"] = error_reason
                    self.log.emit(f"[ERR] Scene {scene} Copy {copy_num} FAILED: {error_reason}")
                    self.job_card.emit(card)

                else:
                    # Still processing
                    card["status"] = "PROCESSING"
                    self.job_card.emit(card)
                    new_jobs.append(job_info)

            jobs = new_jobs

            if jobs:
                poll_info = f"vòng {poll_round + 1}/120"
                if poll_round >= 100:
                    self.log.emit(f"[WARN] Đang chờ {len(jobs)} video ({poll_info}) - sắp hết thời gian chờ!")
                else:
                    self.log.emit(f"[INFO] Đang chờ {len(jobs)} video ({poll_info})...")
                time.sleep(5)

        # Handle timeout
        if jobs:
            for job_info in jobs:
                card = job_info['card']
                card["status"] = "TIMEOUT"
                card["error_reason"] = "Video generation timed out"
                self.job_card.emit(card)
                self.log.emit(f"[TIMEOUT] Scene {card['scene']} Copy {card['copy']}: Generation timed out")

        # Emit completion signal
        self.all_completed.emit(completed_videos)
        self.log.emit(f"[INFO] Parallel video generation completed: {len(completed_videos)} videos downloaded")

    def _process_scene_batch(self, account, batch, p, results_queue, all_jobs, jobs_lock, thread_id):
        """
        Process a batch of scenes in a separate thread.
        Each thread handles its scenes sequentially but all threads run in parallel.
        """
        try:
            # Create event handler that sends logs to queue
            def on_labs_event(event):
                # Format log message
                kind = event.get("kind", "")
                if kind == "video_generator_info":
                    gen_type = event.get("generator_type", "Unknown")
                    model = event.get("model_key", "")
                    aspect = event.get("aspect_ratio", "")
                    msg = f"[INFO] Video Generator: {gen_type} | Model: {model} | Aspect: {aspect}"
                    results_queue.put(("log", msg))
                elif kind == "api_call_info":
                    endpoint_type = event.get("endpoint_type", "")
                    num_req = event.get("num_requests", 0)
                    msg = f"[INFO] API Call: {endpoint_type} endpoint | {num_req} request(s)"
                    results_queue.put(("log", msg))

            # Create client for this account
            client = LabsFlowClient(account.tokens, on_event=on_labs_event)

            copies = p["copies"]
            model_key = p.get("model_key", "")
            dir_videos = p["dir_videos"]
            title = p["title"]

            thread_name = f"T{thread_id+1}"

            for scene_idx, scene in batch:
                if self.cancelled:
                    results_queue.put(("log", f"[INFO] {thread_name}: Cancelled by user"))
                    break

                # Use actual_scene_num if provided (for retry), otherwise use scene_idx
                actual_scene_num = scene.get("actual_scene_num", scene_idx)
                ratio = scene["aspect"]

                results_queue.put(("log", f"[INFO] {thread_name}: Processing scene {actual_scene_num}..."))

                # Single API call with copies parameter
                body = {
                    "prompt": scene["prompt"],
                    "copies": copies,
                    "model": model_key,
                    "aspect_ratio": ratio
                }
                
                # Store bearer token for multi-account download support
                if account.tokens and len(account.tokens) > 0:
                    body["bearer_token"] = account.tokens[0]
                
                # Store account info for multi-account batch checking
                body["account_name"] = account.name
                body["project_id"] = account.project_id
                body["tokens"] = account.tokens
                
                try:
                    rc = client.start_one(
                        body, model_key, ratio, scene["prompt"], 
                        copies=copies, project_id=account.project_id
                    )

                    if rc > 0:
                        # Only create cards for operations that actually exist
                        actual_count = len(body.get("operation_names", []))

                        if actual_count < copies:
                            results_queue.put((
                                "log",
                                f"[WARN] Scene {actual_scene_num}: API returned {actual_count} operations but {copies} copies were requested"
                            ))

                        # Create job info for each copy
                        job_infos = []
                        for copy_idx in range(1, actual_count + 1):
                            card = {
                                "scene": actual_scene_num,
                                "copy": copy_idx,
                                "status": "PROCESSING",
                                "json": scene["prompt"],
                                "url": "",
                                "path": "",
                                "thumb": "",
                                "dir": dir_videos
                            }
                            
                            # Emit card to UI
                            results_queue.put(("card", card))

                            # Store job info
                            job_info = {
                                'card': card,
                                'body': body,
                                'scene': actual_scene_num,
                                'copy': copy_idx
                            }
                            job_infos.append(job_info)

                        # Add jobs to shared list (thread-safe)
                        with jobs_lock:
                            all_jobs.extend(job_infos)

                        # Signal scene started
                        results_queue.put(("scene_started", (actual_scene_num, job_infos)))
                        results_queue.put(("log", f"[INFO] {thread_name}: Scene {actual_scene_num} started with {actual_count} copies"))
                    else:
                        # All copies failed to start
                        for copy_idx in range(1, copies + 1):
                            card = {
                                "scene": actual_scene_num,
                                "copy": copy_idx,
                                "status": "FAILED_START",
                                "error_reason": "Failed to start video generation",
                                "json": scene["prompt"],
                                "url": "",
                                "path": "",
                                "thumb": "",
                                "dir": dir_videos
                            }
                            results_queue.put(("card", card))

                        # Signal scene started (but failed)
                        results_queue.put(("scene_started", (actual_scene_num, [])))
                        results_queue.put(("log", f"[ERROR] {thread_name}: Scene {actual_scene_num} failed to start"))

                except Exception as e:
                    results_queue.put(("log", f"[ERROR] {thread_name}: Scene {actual_scene_num} error: {e}"))
                    # Signal scene started (but failed)
                    results_queue.put(("scene_started", (actual_scene_num, [])))

                # Small delay between scenes in same thread to avoid rate limiting
                time.sleep(0.5)

            results_queue.put(("log", f"[INFO] {thread_name}: Batch complete ({len(batch)} scenes)"))

        except Exception as e:
            results_queue.put(("log", f"[ERROR] Thread {thread_id+1} error: {e}"))
