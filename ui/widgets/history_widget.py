# ui/widgets/history_widget.py
"""
History Widget - Reusable widget for displaying video creation history
Author: chamnv-dev
Date: 2025-01-09
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices

try:
    from services.history_service import get_history_service, HistoryEntry
except ImportError:
    print("⚠️ Warning: history_service not found")
    get_history_service = None
    HistoryEntry = None


class HistoryWidget(QWidget):
    """Widget for displaying video creation history"""
    
    def __init__(self, panel_type: str = "text2video", parent=None):
        """
        Initialize history widget
        
        Args:
            panel_type: Type of panel ("text2video" or "videobanhang")
            parent: Parent widget
        """
        super().__init__(parent)
        self.panel_type = panel_type
        self.history_service = get_history_service() if get_history_service else None
        self._build_ui()
        self._load_history()
    
    def _build_ui(self):
        """Build the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📜 Lịch sử tạo video")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #1E88E5;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Tìm kiếm...")
        self.search_box.setMaximumWidth(200)
        self.search_box.setMinimumHeight(32)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QLineEdit:focus { border: 2px solid #1E88E5; }
        """)
        self.search_box.textChanged.connect(self._on_search)
        header_layout.addWidget(self.search_box)
        
        # Refresh button
        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setMinimumHeight(32)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        btn_refresh.clicked.connect(self._load_history)
        header_layout.addWidget(btn_refresh)
        
        # Clear history button
        btn_clear = QPushButton("🗑️ Xóa lịch sử")
        btn_clear.setMinimumHeight(32)
        btn_clear.setStyleSheet("""
            QPushButton {
                background: #E53935;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background: #F44336; }
        """)
        btn_clear.clicked.connect(self._clear_history)
        header_layout.addWidget(btn_clear)
        
        layout.addLayout(header_layout)
        
        # Info label
        self.info_label = QLabel()
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setStyleSheet("color: #757575; padding: 4px;")
        layout.addWidget(self.info_label)
        
        # History table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Ngày giờ",
            "Ý tưởng",
            "Phong cách",
            "Thể loại",
            "Số video",
            "Thư mục",
            "Hành động"
        ])
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #E3F2FD;
                color: #1E88E5;
            }
            QHeaderView::section {
                background: #F5F5F5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #1E88E5;
                font-weight: bold;
                color: #424242;
            }
        """)
        
        # Configure columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date/Time
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Idea (flexible)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Style
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Genre
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Video count
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Folder (flexible)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
    
    def _load_history(self):
        """Load history from service"""
        if not self.history_service:
            self.table.setRowCount(0)
            self.info_label.setText("⚠️ Dịch vụ lịch sử không khả dụng")
            return
        
        # Get history entries
        entries = self.history_service.get_history(panel_type=self.panel_type)
        
        # Update info label
        self.info_label.setText(f"📊 Tổng số: {len(entries)} mục")
        
        # Populate table
        self._populate_table(entries)
    
    def _populate_table(self, entries):
        """Populate table with history entries"""
        self.table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Date/Time
            time_item = QTableWidgetItem(entry.timestamp)
            time_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 0, time_item)
            
            # Idea (truncate if too long)
            idea_text = entry.idea[:100] + "..." if len(entry.idea) > 100 else entry.idea
            idea_item = QTableWidgetItem(idea_text)
            idea_item.setToolTip(entry.idea)  # Full text in tooltip
            idea_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 1, idea_item)
            
            # Style
            style_item = QTableWidgetItem(entry.style)
            style_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 2, style_item)
            
            # Genre
            genre_item = QTableWidgetItem(entry.genre or "—")
            genre_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 3, genre_item)
            
            # Video count
            count_item = QTableWidgetItem(str(entry.video_count))
            count_item.setTextAlignment(Qt.AlignCenter)
            count_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            if entry.video_count > 0:
                count_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 4, count_item)
            
            # Folder (truncate if too long)
            folder_text = entry.folder_path
            if len(folder_text) > 50:
                folder_text = "..." + folder_text[-47:]
            folder_item = QTableWidgetItem(folder_text)
            folder_item.setToolTip(entry.folder_path)  # Full path in tooltip
            folder_item.setFont(QFont("Courier New", 9))
            self.table.setItem(row, 5, folder_item)
            
            # Actions - Create button widget
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)
            
            # Open folder button
            btn_open = QPushButton("📂 Mở")
            btn_open.setMaximumWidth(80)
            btn_open.setMinimumHeight(28)
            btn_open.setStyleSheet("""
                QPushButton {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover { background: #66BB6A; }
                QPushButton:disabled { background: #CCCCCC; }
            """)
            
            # Enable/disable based on folder existence
            if entry.folder_path and os.path.exists(entry.folder_path):
                btn_open.clicked.connect(
                    lambda checked, path=entry.folder_path: self._open_folder(path)
                )
            else:
                btn_open.setEnabled(False)
                btn_open.setToolTip("Thư mục không tồn tại")
            
            actions_layout.addWidget(btn_open)
            
            # Delete button
            btn_delete = QPushButton("🗑️")
            btn_delete.setMaximumWidth(40)
            btn_delete.setMinimumHeight(28)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background: #E53935;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px;
                }
                QPushButton:hover { background: #F44336; }
            """)
            btn_delete.clicked.connect(
                lambda checked, ts=entry.timestamp: self._delete_entry(ts)
            )
            actions_layout.addWidget(btn_delete)
            
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 6, actions_widget)
            
        # Auto-resize rows
        self.table.resizeRowsToContents()
    
    def _open_folder(self, folder_path: str):
        """Open folder in file explorer"""
        try:
            if os.path.exists(folder_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            else:
                QMessageBox.warning(
                    self,
                    "Lỗi",
                    f"Thư mục không tồn tại:\n{folder_path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể mở thư mục:\n{e}"
            )
    
    def _delete_entry(self, timestamp: str):
        """Delete a history entry"""
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa mục này khỏi lịch sử?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.history_service:
                if self.history_service.delete_entry(timestamp):
                    self._load_history()
                    QMessageBox.information(
                        self,
                        "Thành công",
                        "Đã xóa mục khỏi lịch sử"
                    )
    
    def _clear_history(self):
        """Clear all history for this panel"""
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa TOÀN BỘ lịch sử?\n"
            "Hành động này không thể hoàn tác!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.history_service:
                self.history_service.clear_history(panel_type=self.panel_type)
                self._load_history()
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Đã xóa toàn bộ lịch sử"
                )
    
    def _on_search(self, text: str):
        """Filter table based on search text"""
        if not self.history_service:
            return
        
        # Get all entries
        all_entries = self.history_service.get_history(panel_type=self.panel_type)
        
        # Filter entries
        if text.strip():
            search_text = text.lower()
            filtered_entries = [
                entry for entry in all_entries
                if (search_text in entry.idea.lower() or
                    search_text in entry.style.lower() or
                    (entry.genre and search_text in entry.genre.lower()) or
                    search_text in entry.folder_path.lower())
            ]
        else:
            filtered_entries = all_entries
        
        # Update info label
        if text.strip():
            self.info_label.setText(
                f"🔍 Tìm thấy: {len(filtered_entries)}/{len(all_entries)} mục"
            )
        else:
            self.info_label.setText(f"📊 Tổng số: {len(all_entries)} mục")
        
        # Repopulate table
        self._populate_table(filtered_entries)
    
    def refresh(self):
        """Refresh history display"""
        self._load_history()
