# ui/video_merge_panel.py
"""
Video Merge Panel - Ghép video
Allows users to:
- Select folder containing videos or individual video files
- Merge videos with transition effects between scenes
- Add audio from file or folder
- Support 4K and 8K resolution output

Author: Video Super Ultra Team
Date: 2025-11-12
Version: 1.0.0
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from utils.video_utils import check_ffmpeg_available, get_video_duration


# Styling constants
FONT_H2 = QFont("Segoe UI", 15, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)


class VideoMergeWorker(QThread):
    """Background worker for video merging operations"""
    
    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(bool, str)  # Success, message/error
    
    def __init__(self, video_files: List[str], output_path: str, 
                 audio_file: Optional[str] = None,
                 transition: str = "none",
                 resolution: str = "original",
                 parent=None):
        super().__init__(parent)
        self.video_files = video_files
        self.output_path = output_path
        self.audio_file = audio_file
        self.transition = transition
        self.resolution = resolution
        self._is_cancelled = False
        
    def cancel(self):
        """Cancel the merge operation"""
        self._is_cancelled = True
        
    def run(self):
        """Execute video merge in background"""
        try:
            if self._is_cancelled:
                self.finished.emit(False, "Đã hủy")
                return
                
            self.progress.emit(f"🎬 Bắt đầu ghép {len(self.video_files)} video...")
            
            # Step 1: Merge videos
            if self.transition == "none":
                self._merge_simple()
            else:
                self._merge_with_transitions()
                
            if self._is_cancelled:
                self.finished.emit(False, "Đã hủy")
                return
                
            # Step 2: Add audio if provided
            if self.audio_file:
                self.progress.emit("🎵 Thêm audio vào video...")
                self._add_audio()
                
            if self._is_cancelled:
                self.finished.emit(False, "Đã hủy")
                return
                
            # Step 3: Scale resolution if needed
            if self.resolution != "original":
                self.progress.emit(f"📐 Chuyển đổi độ phân giải sang {self.resolution}...")
                self._scale_resolution()
                
            self.progress.emit("✅ Hoàn thành!")
            self.finished.emit(True, f"Video đã được lưu tại: {self.output_path}")
            
        except Exception as e:
            self.progress.emit(f"❌ Lỗi: {str(e)}")
            self.finished.emit(False, str(e))
            
    def _merge_simple(self):
        """Simple concatenation without transitions"""
        self.progress.emit("📝 Tạo danh sách video...")
        
        # Create temporary concat file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            concat_file = f.name
            for video_path in self.video_files:
                abs_path = os.path.abspath(video_path)
                f.write(f"file '{abs_path}'\n")
        
        try:
            temp_output = self.output_path + ".temp.mp4"
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                temp_output
            ]
            
            self.progress.emit("🔄 Đang ghép video...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            
            # Move temp file to final output
            if os.path.exists(temp_output):
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
                os.rename(temp_output, self.output_path)
                
        finally:
            # Clean up temp file
            try:
                os.unlink(concat_file)
            except:
                pass
                
    def _merge_with_transitions(self):
        """Merge videos with transition effects"""
        self.progress.emit(f"🎨 Thêm hiệu ứng chuyển cảnh '{self.transition}'...")
        
        # Map transition names to xfade filter types
        transition_map = {
            "fade": "fade",
            "wipeleft": "wipeleft",
            "wiperight": "wiperight",
            "wipeup": "wipeup",
            "wipedown": "wipedown",
            "slideleft": "slideleft",
            "slideright": "slideright",
            "slideup": "slideup",
            "slidedown": "slidedown",
            "circlecrop": "circlecrop",
            "dissolve": "dissolve"
        }
        
        xfade_type = transition_map.get(self.transition, "fade")
        transition_duration = 0.5  # 0.5 second transition
        
        # Build complex filter for xfade
        filter_parts = []
        inputs = []
        
        for i, video_path in enumerate(self.video_files):
            inputs.extend(['-i', video_path])
        
        # Build xfade filter chain
        if len(self.video_files) == 1:
            # Single video, no transition needed
            filter_complex = "[0:v]copy[v]"
        else:
            # Multiple videos with transitions
            prev_label = "[0:v]"
            for i in range(1, len(self.video_files)):
                if i == 1:
                    # First transition
                    offset = get_video_duration(self.video_files[0]) - transition_duration
                    filter_parts.append(
                        f"{prev_label}[{i}:v]xfade=transition={xfade_type}:duration={transition_duration}:offset={offset}[v{i}]"
                    )
                    prev_label = f"[v{i}]"
                else:
                    # Subsequent transitions
                    cumulative_offset = sum(
                        get_video_duration(self.video_files[j]) for j in range(i)
                    ) - (i * transition_duration)
                    filter_parts.append(
                        f"{prev_label}[{i}:v]xfade=transition={xfade_type}:duration={transition_duration}:offset={cumulative_offset}[v{i}]"
                    )
                    prev_label = f"[v{i}]"
            
            # Rename final output
            final_idx = len(self.video_files) - 1
            filter_complex = ";".join(filter_parts)
            if final_idx > 1:
                filter_complex = filter_complex.replace(f"[v{final_idx}]", "[v]")
            else:
                filter_complex = filter_complex.replace("[v1]", "[v]")
        
        temp_output = self.output_path + ".temp.mp4"
        
        # Build ffmpeg command
        cmd = ['ffmpeg'] + inputs + [
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-y',
            temp_output
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1200  # 20 minute timeout for complex operations
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg transition failed: {result.stderr}")
        
        # Move temp file to final output
        if os.path.exists(temp_output):
            if os.path.exists(self.output_path):
                os.remove(self.output_path)
            os.rename(temp_output, self.output_path)
            
    def _add_audio(self):
        """Add audio track to video"""
        if not self.audio_file or not os.path.exists(self.audio_file):
            return
            
        temp_input = self.output_path + ".temp_video.mp4"
        os.rename(self.output_path, temp_input)
        
        # Build ffmpeg command to add audio
        cmd = [
            'ffmpeg',
            '-i', temp_input,
            '-i', self.audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',  # End when shortest input ends
            '-y',
            self.output_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            # Restore original if failed
            os.rename(temp_input, self.output_path)
            raise RuntimeError(f"Failed to add audio: {result.stderr}")
        
        # Clean up temp file
        try:
            os.unlink(temp_input)
        except:
            pass
            
    def _scale_resolution(self):
        """Scale video to target resolution"""
        resolution_map = {
            "720p": "1280:720",
            "1080p": "1920:1080",
            "2k": "2560:1440",
            "4k": "3840:2160",
            "8k": "7680:4320"
        }
        
        scale = resolution_map.get(self.resolution)
        if not scale:
            return
            
        temp_input = self.output_path + ".temp_scale.mp4"
        os.rename(self.output_path, temp_input)
        
        # Build ffmpeg command to scale
        cmd = [
            'ffmpeg',
            '-i', temp_input,
            '-vf', f'scale={scale}',
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',  # High quality for 4K/8K
            '-c:a', 'copy',
            '-y',
            self.output_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout for 4K/8K
        )
        
        if result.returncode != 0:
            # Restore original if failed
            os.rename(temp_input, self.output_path)
            raise RuntimeError(f"Failed to scale resolution: {result.stderr}")
        
        # Clean up temp file
        try:
            os.unlink(temp_input)
        except:
            pass


class VideoMergePanel(QWidget):
    """
    Video Merge Panel - Tab ghép video
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_files = []
        self.audio_file = None
        self.worker = None
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🎬 Ghép Video - Video Merging")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #7C4DFF; padding: 10px;")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Ghép nhiều video thành một video duy nhất với hiệu ứng chuyển cảnh và audio. "
            "Hỗ trợ xuất ở độ phân giải cao (4K, 8K)."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 5px;")
        main_layout.addWidget(desc)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Section 1: Video Files
        video_group = self._create_video_section()
        content_layout.addWidget(video_group)
        
        # Section 2: Audio
        audio_group = self._create_audio_section()
        content_layout.addWidget(audio_group)
        
        # Section 3: Merge Settings
        settings_group = self._create_settings_section()
        content_layout.addWidget(settings_group)
        
        # Section 4: Output
        output_group = self._create_output_section()
        content_layout.addWidget(output_group)
        
        content_layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Progress section
        progress_group = self._create_progress_section()
        main_layout.addWidget(progress_group)
        
        # Action buttons
        button_layout = self._create_action_buttons()
        main_layout.addLayout(button_layout)
        
    def _create_video_section(self):
        """Create video selection section"""
        group = QGroupBox("📹 Chọn Video Files")
        group.setFont(FONT_H2)
        layout = QVBoxLayout(group)
        
        # Buttons row
        btn_row = QHBoxLayout()
        
        self.btn_add_videos = QPushButton("➕ Thêm video")
        self.btn_add_videos.clicked.connect(self._add_videos)
        btn_row.addWidget(self.btn_add_videos)
        
        self.btn_add_folder = QPushButton("📁 Thêm từ thư mục")
        self.btn_add_folder.clicked.connect(self._add_from_folder)
        btn_row.addWidget(self.btn_add_folder)
        
        self.btn_clear_videos = QPushButton("🗑️ Xóa tất cả")
        self.btn_clear_videos.clicked.connect(self._clear_videos)
        btn_row.addWidget(self.btn_clear_videos)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Video list
        self.video_list = QListWidget()
        self.video_list.setMinimumHeight(150)
        layout.addWidget(self.video_list)
        
        # Count label
        self.video_count_label = QLabel("Số video: 0")
        self.video_count_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.video_count_label)
        
        return group
        
    def _create_audio_section(self):
        """Create audio selection section"""
        group = QGroupBox("🎵 Audio (tùy chọn)")
        group.setFont(FONT_H2)
        layout = QVBoxLayout(group)
        
        # Buttons row
        btn_row = QHBoxLayout()
        
        self.btn_add_audio = QPushButton("➕ Chọn file audio")
        self.btn_add_audio.clicked.connect(self._add_audio)
        btn_row.addWidget(self.btn_add_audio)
        
        self.btn_clear_audio = QPushButton("🗑️ Xóa audio")
        self.btn_clear_audio.clicked.connect(self._clear_audio)
        btn_row.addWidget(self.btn_clear_audio)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Audio info
        self.audio_label = QLabel("Chưa chọn file audio")
        self.audio_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(self.audio_label)
        
        return group
        
    def _create_settings_section(self):
        """Create merge settings section"""
        group = QGroupBox("⚙️ Cài đặt ghép video")
        group.setFont(FONT_H2)
        layout = QFormLayout(group)
        layout.setSpacing(10)
        
        # Transition effect
        self.cb_transition = QComboBox()
        self.cb_transition.addItem("Không có hiệu ứng", "none")
        self.cb_transition.addItem("Fade (Mờ dần)", "fade")
        self.cb_transition.addItem("Wipe Left (Quét trái)", "wipeleft")
        self.cb_transition.addItem("Wipe Right (Quét phải)", "wiperight")
        self.cb_transition.addItem("Wipe Up (Quét lên)", "wipeup")
        self.cb_transition.addItem("Wipe Down (Quét xuống)", "wipedown")
        self.cb_transition.addItem("Slide Left (Trượt trái)", "slideleft")
        self.cb_transition.addItem("Slide Right (Trượt phải)", "slideright")
        self.cb_transition.addItem("Circle Crop (Vòng tròn)", "circlecrop")
        self.cb_transition.addItem("Dissolve (Hòa tan)", "dissolve")
        layout.addRow("Hiệu ứng chuyển cảnh:", self.cb_transition)
        
        # Resolution
        self.cb_resolution = QComboBox()
        self.cb_resolution.addItem("Giữ nguyên độ phân giải", "original")
        self.cb_resolution.addItem("720p (HD)", "720p")
        self.cb_resolution.addItem("1080p (Full HD)", "1080p")
        self.cb_resolution.addItem("2K (1440p)", "2k")
        self.cb_resolution.addItem("4K (2160p)", "4k")
        self.cb_resolution.addItem("8K (4320p)", "8k")
        layout.addRow("Độ phân giải:", self.cb_resolution)
        
        return group
        
    def _create_output_section(self):
        """Create output settings section"""
        group = QGroupBox("💾 Lưu kết quả")
        group.setFont(FONT_H2)
        layout = QVBoxLayout(group)
        
        # Output path
        path_row = QHBoxLayout()
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Chọn vị trí lưu video...")
        path_row.addWidget(self.output_path)
        
        self.btn_browse_output = QPushButton("📁 Chọn")
        self.btn_browse_output.clicked.connect(self._browse_output)
        path_row.addWidget(self.btn_browse_output)
        
        layout.addLayout(path_row)
        
        return group
        
    def _create_progress_section(self):
        """Create progress display section"""
        group = QGroupBox("📊 Tiến trình")
        group.setFont(FONT_H2)
        layout = QVBoxLayout(group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log text
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setPlaceholderText("Nhật ký xử lý sẽ hiển thị ở đây...")
        layout.addWidget(self.log_text)
        
        return group
        
    def _create_action_buttons(self):
        """Create action buttons"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        self.btn_merge = QPushButton("🎬 Ghép Video")
        self.btn_merge.setMinimumHeight(45)
        self.btn_merge.setMinimumWidth(150)
        self.btn_merge.setStyleSheet("""
            QPushButton {
                background-color: #7C4DFF;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #6A3DE8;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.btn_merge.clicked.connect(self._start_merge)
        layout.addWidget(self.btn_merge)
        
        self.btn_cancel = QPushButton("⏹️ Hủy")
        self.btn_cancel.setMinimumHeight(45)
        self.btn_cancel.setMinimumWidth(100)
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._cancel_merge)
        layout.addWidget(self.btn_cancel)
        
        layout.addStretch()
        
        return layout
        
    def _add_videos(self):
        """Add video files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Chọn video files",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*)"
        )
        
        if files:
            for file in files:
                if file not in self.video_files:
                    self.video_files.append(file)
                    self.video_list.addItem(os.path.basename(file))
            
            self._update_video_count()
            self._append_log(f"✅ Đã thêm {len(files)} video")
            
    def _add_from_folder(self):
        """Add all videos from a folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục chứa video"
        )
        
        if folder:
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
            added = 0
            
            for file in sorted(os.listdir(folder)):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in video_extensions:
                        if file_path not in self.video_files:
                            self.video_files.append(file_path)
                            self.video_list.addItem(file)
                            added += 1
            
            self._update_video_count()
            self._append_log(f"✅ Đã thêm {added} video từ thư mục")
            
    def _clear_videos(self):
        """Clear all videos"""
        self.video_files.clear()
        self.video_list.clear()
        self._update_video_count()
        self._append_log("🗑️ Đã xóa tất cả video")
        
    def _add_audio(self):
        """Add audio file"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file audio",
            "",
            "Audio Files (*.mp3 *.wav *.aac *.m4a *.ogg);;All Files (*)"
        )
        
        if file:
            self.audio_file = file
            self.audio_label.setText(f"✅ {os.path.basename(file)}")
            self.audio_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
            self._append_log(f"✅ Đã chọn audio: {os.path.basename(file)}")
            
    def _clear_audio(self):
        """Clear audio"""
        self.audio_file = None
        self.audio_label.setText("Chưa chọn file audio")
        self.audio_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        self._append_log("🗑️ Đã xóa audio")
        
    def _browse_output(self):
        """Browse output location"""
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Chọn vị trí lưu video",
            "",
            "MP4 Video (*.mp4)"
        )
        
        if file:
            if not file.endswith('.mp4'):
                file += '.mp4'
            self.output_path.setText(file)
            
    def _update_video_count(self):
        """Update video count label"""
        count = len(self.video_files)
        self.video_count_label.setText(f"Số video: {count}")
        
    def _append_log(self, message: str):
        """Append message to log"""
        self.log_text.append(message)
        
    def _start_merge(self):
        """Start video merge process"""
        # Validate inputs
        if len(self.video_files) < 2:
            QMessageBox.warning(
                self,
                "Thiếu video",
                "Vui lòng chọn ít nhất 2 video để ghép."
            )
            return
            
        output_path = self.output_path.text().strip()
        if not output_path:
            QMessageBox.warning(
                self,
                "Thiếu đường dẫn",
                "Vui lòng chọn vị trí lưu video."
            )
            return
            
        # Check ffmpeg
        if not check_ffmpeg_available():
            QMessageBox.critical(
                self,
                "Thiếu FFmpeg",
                "FFmpeg chưa được cài đặt. Vui lòng cài đặt FFmpeg để sử dụng tính năng này."
            )
            return
            
        # Get settings
        transition = self.cb_transition.currentData()
        resolution = self.cb_resolution.currentData()
        
        # Clear log
        self.log_text.clear()
        self._append_log("=" * 50)
        self._append_log("🎬 BẮT ĐẦU GHÉP VIDEO")
        self._append_log("=" * 50)
        self._append_log(f"📹 Số video: {len(self.video_files)}")
        self._append_log(f"🎨 Hiệu ứng: {self.cb_transition.currentText()}")
        self._append_log(f"📐 Độ phân giải: {self.cb_resolution.currentText()}")
        if self.audio_file:
            self._append_log(f"🎵 Audio: {os.path.basename(self.audio_file)}")
        self._append_log("=" * 50)
        
        # Disable UI
        self.btn_merge.setVisible(False)
        self.btn_cancel.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Create worker
        self.worker = VideoMergeWorker(
            self.video_files,
            output_path,
            self.audio_file,
            transition,
            resolution
        )
        self.worker.progress.connect(self._append_log)
        self.worker.finished.connect(self._merge_finished)
        self.worker.start()
        
    def _cancel_merge(self):
        """Cancel merge operation"""
        if self.worker:
            self.worker.cancel()
            self._append_log("⏹️ Đang hủy...")
            
    def _merge_finished(self, success: bool, message: str):
        """Handle merge completion"""
        self.progress_bar.setVisible(False)
        self.btn_merge.setVisible(True)
        self.btn_cancel.setVisible(False)
        
        if success:
            QMessageBox.information(
                self,
                "Thành công",
                message
            )
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Ghép video thất bại:\n{message}"
            )
