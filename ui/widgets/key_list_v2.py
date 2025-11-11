# -*- coding: utf-8 -*-
"""
KeyList V2 - Fixed Version
- Proper spacing (no huge gaps)
- Highlighted input fields
- Better visual hierarchy
- API key validation integration
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class KeyValidationWorker(QThread):
    """Worker thread for validating API keys without blocking UI"""
    result = pyqtSignal(int, bool, str)  # (index, is_valid, message)
    finished_all = pyqtSignal()
    
    def __init__(self, kind, keys):
        super().__init__()
        self.kind = kind
        self.keys = keys
        
    def run(self):
        """Validate all keys and emit results"""
        try:
            from services.key_check_service import check
            for i, key in enumerate(self.keys):
                is_valid, message = check(self.kind, key)
                self.result.emit(i, is_valid, message)
        except Exception as e:
            # If import fails, emit error for all keys
            for i in range(len(self.keys)):
                self.result.emit(i, False, f"Validation error: {str(e)}")
        finally:
            self.finished_all.emit()


class KeyListV2(QWidget):
    """Improved KeyList with compact layout and prominent inputs"""

    def __init__(self, title="", kind="default", initial=None, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.keys = initial or []
        self.validation_status = {}  # Store validation results {key: (is_valid, message)}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Keys display area - with better styling
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(120)
        self.list_widget.setMaximumHeight(180)
        self.list_widget.setFont(QFont("Courier New", 11))
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #FAFAFA;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 6px;
            }
            QListWidget::item {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background: #F5F5F5;
                border-color: #BDBDBD;
            }
            QListWidget::item:selected {
                background: #E3F2FD;
                border-color: #1E88E5;
                color: #1565C0;
            }
        """)
        layout.addWidget(self.list_widget)

        # Populate existing keys
        for key in self.keys:
            self._add_key_item(key)

        # Input area - PROMINENT & CLEAR
        input_label = QLabel(f"➕ Paste {self.kind.upper()} API Key:")
        input_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        input_label.setStyleSheet("color: #424242; margin-top: 4px;")
        layout.addWidget(input_label)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(f"Enter your {self.kind} API key here...")
        self.input_field.setMinimumHeight(40)
        self.input_field.setFont(QFont("Segoe UI", 13))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 3px solid #BDBDBD;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 500;
                color: #212121;
            }
            QLineEdit:focus {
                border: 3px solid #1E88E5;
                background: #F8FCFF;
            }
            QLineEdit::placeholder {
                color: #9E9E9E;
                font-style: italic;
            }
        """)
        self.input_field.returnPressed.connect(self._add_key)
        input_row.addWidget(self.input_field, 1)

        # Add button - prominent
        self.btn_add = QPushButton("➕ Add")
        self.btn_add.setObjectName("btn_primary")
        self.btn_add.setMinimumHeight(40)
        self.btn_add.setMinimumWidth(100)
        self.btn_add.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self._add_key)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: #008080;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #009999;
            }
        """)
        input_row.addWidget(self.btn_add)

        layout.addLayout(input_row)

        # Action buttons row - compact
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        self.btn_import = QPushButton("📁 Import File")
        self.btn_import.setObjectName("btn_import")
        self.btn_import.setMinimumHeight(32)
        self.btn_import.setFont(QFont("Segoe UI", 12))
        self.btn_import.clicked.connect(self._import_file)
        actions_row.addWidget(self.btn_import)

        self.btn_validate = QPushButton("✓ Validate All")
        self.btn_validate.setObjectName("btn_check")
        self.btn_validate.setMinimumHeight(32)
        self.btn_validate.setFont(QFont("Segoe UI", 12))
        self.btn_validate.clicked.connect(self._validate_all)
        actions_row.addWidget(self.btn_validate)

        actions_row.addStretch()
        layout.addLayout(actions_row)

    def _add_key_item(self, key_text):
        """Add key item with COMPACT spacing - NO HUGE GAPS"""
        item = QListWidgetItem()

        # Custom widget for item
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(6, 4, 6, 4)
        item_layout.setSpacing(8)  # ONLY 8px - not huge gap
        
        # Status indicator (initially grey, will be updated on validation)
        status_label = QLabel("●")
        status_label.setFont(QFont("Segoe UI", 16))
        status_label.setToolTip("Not validated yet")
        # Store status label for later updates
        status_label.setObjectName(f"status_{len(self.keys)}")
        status_label.setStyleSheet("color: #9E9E9E; padding: 2px;")  # Grey = unknown
        item_layout.addWidget(status_label)

        # Key text (monospace, selectable)
        key_label = QLabel(self._truncate_key(key_text))
        key_label.setFont(QFont("Courier New", 11))
        key_label.setStyleSheet("color: #424242; padding: 4px;")
        key_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # Enhanced tooltip with validation status
        tooltip = key_text
        if key_text in self.validation_status:
            is_valid, msg = self.validation_status[key_text]
            tooltip += f"\n\nStatus: {'✅ Valid' if is_valid else '❌ Invalid'}\n{msg}"
        key_label.setToolTip(tooltip)
        item_layout.addWidget(key_label, 1)  # stretch=1 takes remaining space

        # Check button - RIGHT NEXT to text (NO gap)
        btn_check = QPushButton("✓")
        btn_check.setFixedSize(32, 32)
        btn_check.setObjectName("btn_check")
        btn_check.setToolTip("Validate this key")
        btn_check.setCursor(Qt.PointingHandCursor)
        btn_check.setFont(QFont("Segoe UI", 14))
        btn_check.clicked.connect(lambda: self._validate_single_key(key_text))
        item_layout.addWidget(btn_check)

        # Delete button - RIGHT NEXT to check button
        btn_delete = QPushButton("🗑")
        btn_delete.setFixedSize(32, 32)
        btn_delete.setObjectName("btn_danger")
        btn_delete.setToolTip("Delete this key")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setFont(QFont("Segoe UI", 14))
        btn_delete.clicked.connect(lambda: self._delete_key_item(item))
        item_layout.addWidget(btn_delete)

        # NO addStretch() here - that's what caused huge gap!

        # Set item
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)

    def _truncate_key(self, key):
        """Truncate key for display: show first 24 and last 12 chars"""
        if len(key) > 40:
            return f"{key[:24]}...{key[-12:]}"
        return key

    def _add_key(self):
        """Add key from input"""
        key = self.input_field.text().strip()
        if not key:
            QMessageBox.warning(self, "Empty Key", "Please enter an API key!")
            return

        if key in self.keys:
            QMessageBox.warning(self, "Duplicate", "This key already exists!")
            return

        self._add_key_item(key)
        self.keys.append(key)
        self.input_field.clear()
        self.input_field.setFocus()

    def _delete_key_item(self, item):
        """Delete key item"""
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        if 0 <= row < len(self.keys):
            self.keys.pop(row)

    def _import_file(self):
        """Import keys from text file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import API Keys", "", "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                count = 0
                for line in f:
                    key = line.strip()
                    if key and key not in self.keys:
                        self._add_key_item(key)
                        self.keys.append(key)
                        count += 1

            QMessageBox.information(self, "Import Success", f"Imported {count} keys!")
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Error: {str(e)}")

    def _validate_single_key(self, key):
        """Validate a single API key"""
        try:
            from services.key_check_service import check
            
            # Disable validate button during check
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Find the index of this key
            if key not in self.keys:
                QMessageBox.warning(self, "Error", "Key not found!")
                return
                
            key_index = self.keys.index(key)
            
            # Perform validation
            is_valid, message = check(self.kind, key)
            
            # Store result
            self.validation_status[key] = (is_valid, message)
            
            # Update UI
            self._update_key_status(key_index, is_valid, message)
            
            # Show result
            status = "✅ Valid" if is_valid else "❌ Invalid"
            QMessageBox.information(
                self, 
                "Validation Result",
                f"Key: {self._truncate_key(key)}\n\nStatus: {status}\n\n{message}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Failed to validate key:\n{str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def _validate_all(self):
        """Validate all keys using background worker"""
        if not self.keys:
            QMessageBox.warning(self, "No Keys", "No keys to validate!")
            return
        
        # Disable button during validation
        self.btn_validate.setEnabled(False)
        self.btn_validate.setText("⏳ Validating...")
        
        # Create and start worker thread
        self.validation_worker = KeyValidationWorker(self.kind, self.keys)
        self.validation_worker.result.connect(self._on_validation_result)
        self.validation_worker.finished_all.connect(self._on_validation_complete)
        self.validation_worker.start()
    
    def _on_validation_result(self, index, is_valid, message):
        """Handle individual key validation result"""
        if 0 <= index < len(self.keys):
            key = self.keys[index]
            self.validation_status[key] = (is_valid, message)
            self._update_key_status(index, is_valid, message)
    
    def _on_validation_complete(self):
        """Handle completion of all validations"""
        self.btn_validate.setEnabled(True)
        self.btn_validate.setText("✓ Validate All")
        
        # Count results
        valid_count = sum(1 for k in self.keys if k in self.validation_status and self.validation_status[k][0])
        invalid_count = len(self.keys) - valid_count
        
        QMessageBox.information(
            self,
            "Validation Complete",
            f"Validated {len(self.keys)} keys:\n\n"
            f"✅ Valid: {valid_count}\n"
            f"❌ Invalid: {invalid_count}"
        )
    
    def _update_key_status(self, index, is_valid, message):
        """Update the visual status indicator for a key"""
        if not (0 <= index < self.list_widget.count()):
            return
            
        item = self.list_widget.item(index)
        item_widget = self.list_widget.itemWidget(item)
        
        if item_widget:
            # Find the status label (first widget in layout)
            layout = item_widget.layout()
            if layout and layout.count() > 0:
                status_label = layout.itemAt(0).widget()
                if isinstance(status_label, QLabel):
                    if is_valid:
                        status_label.setText("●")
                        status_label.setStyleSheet("color: #4CAF50; padding: 2px;")  # Green
                        status_label.setToolTip(f"✅ Valid\n{message}")
                    else:
                        status_label.setText("●")
                        status_label.setStyleSheet("color: #F44336; padding: 2px;")  # Red
                        status_label.setToolTip(f"❌ Invalid\n{message}")
            
            # Also update the key label tooltip
            if layout and layout.count() > 1:
                key_label = layout.itemAt(1).widget()
                if isinstance(key_label, QLabel) and index < len(self.keys):
                    key = self.keys[index]
                    tooltip = key + f"\n\nStatus: {'✅ Valid' if is_valid else '❌ Invalid'}\n{message}"
                    key_label.setToolTip(tooltip)

    def get_keys(self):
        """Get all keys as list"""
        return self.keys.copy()