# -*- coding: utf-8 -*-
"""
Settings Panel V3 Compact - Super compact, 2-column API
Fits in one screen
"""

import datetime
import logging

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.account_manager import LabsAccount, get_account_manager
from ui.widgets.accordion import AccordionSection
from ui.widgets.compact_button import CompactButton
from ui.widgets.key_list_v2 import KeyListV2
from utils import config as cfg
from utils.version import get_version

# Setup logger
logger = logging.getLogger(__name__)

# Typography
FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_SMALL = QFont("Segoe UI", 12)
FONT_MONO = QFont("Courier New", 11)

# Default Project ID constant
DEFAULT_PROJECT_ID = '87b19267-13d6-49cd-a7ed-db19a90c9339'

def _ts():
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

def _line(placeholder='', read_only=False):
    """Create compact line edit"""
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setFont(FONT_BODY)
    e.setMinimumHeight(36)
    e.setMaximumHeight(36)
    e.setReadOnly(read_only)

    if not read_only:
        e.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #1E88E5;
                background: #F8FCFF;
            }
        """)
    else:
        e.setStyleSheet("""
            QLineEdit {
                background: #F5F5F5;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px 12px;
            }
        """)

    return e

def _label(text):
    l = QLabel(text)
    l.setFont(FONT_BODY)
    l.setMinimumHeight(36)
    l.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
    return l

class SettingsPanelV3Compact(QWidget):
    """Settings Panel V3 - Super Compact"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = cfg.load()
        self._migrated = False  # Track migration status
        self._build_ui()

    def showEvent(self, event):
        """Handle panel show - perform auto-migration on first show and reload config"""
        super().showEvent(event)

        # Reload config when panel is shown to display latest saved values
        self.state = cfg.load()
        self._refresh_ui_from_state()

        # Auto-migrate on first show
        if not self._migrated:
            self._auto_migrate_old_config()
            self._migrated = True

    def _auto_migrate_old_config(self):
        """
        Auto-migrate old single-token config to multi-account format
        Called on first Settings panel load
        """
        # Use existing state instead of reloading
        config = self.state

        # Check if old 'tokens' or 'labs_tokens' array exists but no 'labs_accounts'
        old_tokens = config.get('tokens', [])
        old_labs_tokens = config.get('labs_tokens', [])
        existing_accounts = config.get('labs_accounts', [])

        # Combine all old token sources (preserve order, remove duplicates)
        all_old_tokens = list(dict.fromkeys(old_tokens + old_labs_tokens))

        if all_old_tokens and not existing_accounts:
            # Migration needed
            reply = QMessageBox.question(
                self,
                "Migrate Configuration",
                f"Found {len(all_old_tokens)} old token(s).\n\n"
                "Migrate to multi-account format?\n"
                "(Old tokens will be preserved as backup)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # Migrate
                accounts = []
                default_project_id = config.get('flow_project_id', DEFAULT_PROJECT_ID)

                for i, token in enumerate(all_old_tokens):
                    accounts.append({
                        'name': f'Account {i+1} (Migrated)',
                        'tokens': [token],
                        'project_id': default_project_id,
                        'enabled': True
                    })

                # Save migrated config
                config['labs_accounts'] = accounts
                config['tokens_backup'] = all_old_tokens  # Keep backup
                cfg.save(config)

                # Reload state and account table
                self.state = cfg.load()
                if hasattr(self, 'accounts_table') and self.accounts_table is not None:
                    self._load_accounts_table()

                QMessageBox.information(
                    self,
                    "Migration Complete",
                    f"✅ Migrated {len(all_old_tokens)} token(s) to multi-account format.\n\n"
                    "Old tokens backed up as 'tokens_backup' in config."
                )

    def _refresh_ui_from_state(self):
        """Refresh UI fields from current state"""
        if not hasattr(self, 'ed_email'):
            # UI not yet built
            return

        try:
            # Update all fields from state
            self.ed_email.setText(self.state.get('account_email', ''))

            # Storage settings
            storage = (self.state.get('download_storage') or 'local').lower()
            (self.rb_drive if storage == 'gdrive' else self.rb_local).setChecked(True)
            self.ed_local.setText(self.state.get('download_root', ''))
            self.ed_gdrive.setText(self.state.get('gdrive_folder_id', ''))
            self.ed_oauth.setText(self.state.get('google_workspace_oauth_token', ''))

            # API keys
            if hasattr(self, 'w_google'):
                self.w_google.set_keys(self.state.get('google_api_keys') or [])
            if hasattr(self, 'w_eleven'):
                self.w_eleven.set_keys(self.state.get('elevenlabs_api_keys') or [])
            if hasattr(self, 'w_openai'):
                self.w_openai.set_keys(self.state.get('openai_api_keys') or [])

            # Voice and project settings
            self.ed_voice.setText(self.state.get('default_voice_id', '3VnrjnYrskPMDsapTr8X'))
            self.ed_project.setText(self.state.get('flow_project_id', DEFAULT_PROJECT_ID))
            self.ed_sheets_url.setText(self.state.get('system_prompts_url', 'https://docs.google.com/spreadsheets/d/1ohiL6xOBbjC7La2iUdkjrVjG4IEUnVWhI0fRoarD6P0'))

            # Whisk authentication
            self.ed_whisk_session.setText(self.state.get('labs_session_token', ''))
            self.ed_whisk_bearer.setText(self.state.get('whisk_bearer_token', ''))

            # Reload accounts table
            if hasattr(self, 'accounts_table') and self.accounts_table is not None:
                self._load_accounts_table()
        except Exception as e:
            logger.warning(f"Error refreshing UI from state: {e}")

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)  # Compact spacing

        # === ACCOUNT INFO ===
        acc_group = QGroupBox("👤 Account Information")
        acc_group.setFont(FONT_H2)
        acc_layout = QGridLayout(acc_group)
        acc_layout.setVerticalSpacing(8)
        acc_layout.setHorizontalSpacing(12)
        acc_layout.setColumnStretch(1, 1)
        acc_layout.setColumnStretch(3, 1)

        self.ed_email = _line('Email', read_only=True)
        self.ed_email.setText(self.state.get('account_email', ''))

        hwid_text = self.state.get('hardware_id', '')
        self.lb_hwid = _label(hwid_text)
        self.lb_hwid.setFont(FONT_MONO)
        self.lb_hwid.setStyleSheet("background: #F5F5F5; padding: 8px; border-radius: 4px;")

        status_text = self.state.get('license_status', 'Kích Hoạt')
        self.lb_status = _label(status_text)
        if 'kích' in status_text.lower() or 'active' in status_text.lower():
            self.lb_status.setStyleSheet("color: #4CAF50; font-weight: bold;")

        expiry_text = self.state.get('license_expiry', 'Không có hạn sử dụng')
        self.lb_expiry = _label(expiry_text)

        acc_layout.addWidget(_label("Email:"), 0, 0)
        acc_layout.addWidget(self.ed_email, 0, 1)
        acc_layout.addWidget(_label("Hardware ID:"), 0, 2)
        acc_layout.addWidget(self.lb_hwid, 0, 3)

        acc_layout.addWidget(_label("Status:"), 1, 0)
        acc_layout.addWidget(self.lb_status, 1, 1)
        acc_layout.addWidget(_label("Expires:"), 1, 2)
        acc_layout.addWidget(self.lb_expiry, 1, 3)

        root.addWidget(acc_group)

        # === API CREDENTIALS - 2 COLUMNS ===
        api_group = QGroupBox("🔑 API Credentials")
        api_group.setFont(FONT_H2)
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(6)

        hint = QLabel("💡 Click sections to expand. Keys are displayed compactly.")
        hint.setFont(FONT_SMALL)
        hint.setStyleSheet("color: #757575; font-style: italic;")
        api_layout.addWidget(hint)

        # 2-column grid for accordion sections
        accordion_grid = QGridLayout()
        accordion_grid.setSpacing(8)

        # Column 1
        google_section = AccordionSection("Google API Keys (Gemini)")
        g_list = self.state.get('google_api_keys') or []
        self.w_google = KeyListV2(kind='google', initial=g_list)
        google_section.add_content_widget(self.w_google)
        accordion_grid.addWidget(google_section, 0, 0)

        # Column 2
        eleven_section = AccordionSection("Elevenlabs API Keys")
        self.w_eleven = KeyListV2(kind='elevenlabs',
                                  initial=self.state.get('elevenlabs_api_keys') or [])
        eleven_section.add_content_widget(self.w_eleven)

        self.ed_voice = _line('Voice ID')
        self.ed_voice.setText(self.state.get('default_voice_id', '3VnrjnYrskPMDsapTr8X'))
        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("Voice ID:"))
        voice_row.addWidget(self.ed_voice)
        eleven_section.add_content_layout(voice_row)

        accordion_grid.addWidget(eleven_section, 0, 1)

        openai_section = AccordionSection("OpenAI API Keys")
        self.w_openai = KeyListV2(kind='openai',
                                  initial=self.state.get('openai_api_keys') or [])
        openai_section.add_content_widget(self.w_openai)
        accordion_grid.addWidget(openai_section, 1, 1)

        # === MULTI-ACCOUNT MANAGEMENT (ISSUE #4) - Now as AccordionSection ===
        multi_acc_section = AccordionSection("🔑 Google Labs Flow Tokens (Video Generation)")

        # Add hint
        hint2 = QLabel(
            "💡 These are OAuth tokens from labs.google.com (NOT API keys).\n"
            "Use multiple accounts to avoid rate limits and increase processing speed!\n"
            "Each account will process scenes in parallel."
        )
        hint2.setFont(FONT_SMALL)
        hint2.setWordWrap(True)
        hint2.setStyleSheet("color: #666; font-size: 11px; padding: 8px;")
        multi_acc_section.add_content_widget(hint2)

        # Account table
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels(["Enabled", "Account Name", "Project ID", "Tokens"])
        self.accounts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.accounts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.accounts_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.accounts_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.accounts_table.setMaximumHeight(200)
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setToolTip(
            "Add multiple Google Labs accounts here.\n"
            "These use OAuth Flow Tokens from labs.google.com, not API keys.\n"
            "Jobs will be distributed across accounts automatically."
        )
        self.accounts_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        # Load accounts from config
        self._load_accounts_table()

        multi_acc_section.add_content_widget(self.accounts_table)

        # Default Project ID
        proj_row = QHBoxLayout()
        proj_row.setSpacing(8)
        proj_label = QLabel("Default Project ID:")
        proj_label.setFont(FONT_SMALL)
        proj_row.addWidget(proj_label)

        self.ed_project = _line('Project ID for new accounts')
        self.ed_project.setText(self.state.get('flow_project_id', DEFAULT_PROJECT_ID))
        self.ed_project.setToolTip(
            "Default Project ID for new accounts.\n"
            "Each account can have its own Project ID in the table above."
        )
        proj_row.addWidget(self.ed_project, 1)

        proj_info = QLabel("ℹ️ Used as default for new accounts")
        proj_info.setStyleSheet("color: #666; font-size: 10px;")
        proj_row.addWidget(proj_info)

        multi_acc_section.add_content_layout(proj_row)

        # Account management buttons
        acc_buttons = QHBoxLayout()
        acc_buttons.setSpacing(8)

        self.btn_add_account = CompactButton("➕ Add Account")
        self.btn_add_account.setObjectName("btn_primary")
        self.btn_add_account.clicked.connect(self._add_account)
        acc_buttons.addWidget(self.btn_add_account)

        self.btn_edit_account = CompactButton("✏️ Edit Account")
        self.btn_edit_account.clicked.connect(self._edit_account)
        acc_buttons.addWidget(self.btn_edit_account)

        self.btn_remove_account = CompactButton("🗑️ Remove Account")
        self.btn_remove_account.clicked.connect(self._remove_account)
        acc_buttons.addWidget(self.btn_remove_account)

        acc_buttons.addStretch()

        self.lb_account_status = QLabel("")
        self.lb_account_status.setFont(FONT_SMALL)
        self.lb_account_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        acc_buttons.addWidget(self.lb_account_status)

        multi_acc_section.add_content_layout(acc_buttons)

        # Add Multi-Account section to grid (row 2, spanning both columns)
        accordion_grid.addWidget(multi_acc_section, 2, 0, 1, 2)

        # === VERTEX AI CONFIGURATION - AccordionSection ===
        vertex_section = AccordionSection("🚀 Vertex AI Configuration (Khắc phục lỗi 503)")

        # Add hint
        hint_vertex = QLabel(
            "💡 Vertex AI giúp giảm lỗi 503 từ 25% xuống ~2-5%!\n"
            "• Rate limit cao hơn Google AI Studio (60 req/min)\n"
            "• Ổn định hơn cho production\n"
            "• Tự động fallback về AI Studio nếu lỗi\n"
            "• Chi phí: ~$2.25 per 1,000 scripts (free tier $300)"
        )
        hint_vertex.setFont(FONT_SMALL)
        hint_vertex.setWordWrap(True)
        hint_vertex.setStyleSheet("color: #666; font-size: 11px; padding: 8px;")
        vertex_section.add_content_widget(hint_vertex)

        # Load vertex_ai config
        vertex_config = self.state.get('vertex_ai', {})

        # Enable checkbox
        enable_row = QHBoxLayout()
        enable_row.setSpacing(8)
        self.chk_vertex_enabled = QCheckBox("Bật Vertex AI")
        self.chk_vertex_enabled.setChecked(vertex_config.get('enabled', False))
        self.chk_vertex_enabled.setFont(FONT_BODY)
        self.chk_vertex_enabled.setToolTip(
            "Bật để sử dụng Vertex AI thay vì Google AI Studio.\n"
            "Giảm lỗi 503 đáng kể (từ 25% xuống ~2-5%).\n"
            "Cần setup GCP project và service account."
        )
        enable_row.addWidget(self.chk_vertex_enabled)
        enable_row.addStretch()
        vertex_section.add_content_layout(enable_row)

        # Service Accounts hint
        hint_accounts = QLabel(
            "💡 Thêm nhiều service accounts để tận dụng $300 free tier của từng account!\n"
            "Mỗi service account = 1 GCP project với $300 credit.\n"
            "Hệ thống tự động round-robin để phân bổ requests."
        )
        hint_accounts.setFont(FONT_SMALL)
        hint_accounts.setWordWrap(True)
        hint_accounts.setStyleSheet("color: #666; font-size: 10px; padding: 4px;")
        vertex_section.add_content_widget(hint_accounts)

        # Service Accounts table
        self.vertex_accounts_table = QTableWidget()
        self.vertex_accounts_table.setColumnCount(5)
        self.vertex_accounts_table.setHorizontalHeaderLabels(
            ["Enabled", "Account Name", "Project ID", "Region", "Credit"]
        )
        header = self.vertex_accounts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.vertex_accounts_table.setMaximumHeight(150)
        self.vertex_accounts_table.setAlternatingRowColors(True)
        self.vertex_accounts_table.setToolTip(
            "Thêm nhiều service accounts để:\n"
            "• Tận dụng $300 free tier của mỗi account\n"
            "• Round-robin tự động phân bổ requests\n"
            "• Tăng rate limit tổng thể"
        )
        self.vertex_accounts_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)

        # Load service accounts
        self._load_vertex_accounts_table()

        vertex_section.add_content_widget(self.vertex_accounts_table)

        # Service account management buttons
        vertex_buttons = QHBoxLayout()
        vertex_buttons.setSpacing(8)

        self.btn_add_vertex_account = CompactButton("➕ Add Service Account")
        self.btn_add_vertex_account.setObjectName("btn_primary")
        self.btn_add_vertex_account.clicked.connect(self._add_vertex_account)
        vertex_buttons.addWidget(self.btn_add_vertex_account)

        self.btn_edit_vertex_account = CompactButton("✏️ Edit")
        self.btn_edit_vertex_account.clicked.connect(self._edit_vertex_account)
        vertex_buttons.addWidget(self.btn_edit_vertex_account)

        self.btn_remove_vertex_account = CompactButton("🗑️ Remove")
        self.btn_remove_vertex_account.clicked.connect(self._remove_vertex_account)
        vertex_buttons.addWidget(self.btn_remove_vertex_account)

        self.btn_pricing_info = CompactButton("💰 View Pricing Info")
        self.btn_pricing_info.clicked.connect(self._show_pricing_info)
        self.btn_pricing_info.setToolTip(
            "Xem thông tin chi phí và cách tính toán credit cho Vertex AI"
        )
        vertex_buttons.addWidget(self.btn_pricing_info)

        vertex_buttons.addStretch()

        vertex_section.add_content_layout(vertex_buttons)

        # Priority checkbox
        priority_row = QHBoxLayout()
        priority_row.setSpacing(8)
        self.chk_vertex_first = QCheckBox("Ưu tiên Vertex AI (fallback về AI Studio nếu lỗi)")
        self.chk_vertex_first.setChecked(vertex_config.get('use_vertex_first', True))
        self.chk_vertex_first.setFont(FONT_SMALL)
        self.chk_vertex_first.setToolTip(
            "Khi bật: Try Vertex AI trước, fallback về AI Studio nếu lỗi.\n"
            "Khi tắt: Chỉ dùng AI Studio."
        )
        priority_row.addWidget(self.chk_vertex_first)
        priority_row.addStretch()
        vertex_section.add_content_layout(priority_row)

        # Documentation link
        doc_label = QLabel(
            '📖 <a href="file:///docs/VERTEX_AI_SETUP.md">Xem hướng dẫn setup chi tiết</a> | '
            '<a href="https://console.cloud.google.com/vertex-ai">Google Cloud Console</a>'
        )
        doc_label.setFont(FONT_SMALL)
        doc_label.setOpenExternalLinks(True)
        doc_label.setStyleSheet("color: #1976D2; padding: 4px;")
        vertex_section.add_content_widget(doc_label)

        # Status indicator
        self.lb_vertex_status = QLabel("")
        self.lb_vertex_status.setFont(FONT_SMALL)
        self.lb_vertex_status.setStyleSheet("padding: 4px;")
        vertex_section.add_content_widget(self.lb_vertex_status)
        self._update_vertex_status()

        # Add Vertex AI section to grid (row 3, spanning both columns)
        accordion_grid.addWidget(vertex_section, 3, 0, 1, 2)

        # === WHISK AUTHENTICATION (IMAGE GENERATION) - AccordionSection ===
        whisk_section = AccordionSection("🎨 Whisk Authentication (Image Generation)")

        # Add hint
        hint_whisk = QLabel(
            "💡 Whisk requires two types of authentication from labs.google.com:\n"
            "1. Session Token (__Secure-next-auth.session-token cookie)\n"
            "2. Bearer Token (OAuth token from API requests)\n"
            "Both can be obtained from browser Developer Tools when using Whisk."
        )
        hint_whisk.setFont(FONT_SMALL)
        hint_whisk.setWordWrap(True)
        hint_whisk.setStyleSheet("color: #666; font-size: 11px; padding: 8px;")
        whisk_section.add_content_widget(hint_whisk)

        # Session Token input
        session_row = QHBoxLayout()
        session_row.setSpacing(8)
        session_label = QLabel("Session Token:")
        session_label.setFont(FONT_SMALL)
        session_label.setToolTip(
            "__Secure-next-auth.session-token from browser cookies.\n"
            "Get from: labs.google → Developer Tools (F12) → Application → Cookies"
        )
        session_row.addWidget(session_label)

        self.ed_whisk_session = _line('__Secure-next-auth.session-token value')
        self.ed_whisk_session.setText(self.state.get('labs_session_token', ''))
        self.ed_whisk_session.setEchoMode(QLineEdit.Password)
        self.ed_whisk_session.setToolTip(
            "Session cookie from labs.google.com\n"
            "1. Open labs.google and login\n"
            "2. Go to https://labs.google/fx/tools/whisk\n"
            "3. Open Developer Tools (F12) → Application → Cookies\n"
            "4. Copy value of '__Secure-next-auth.session-token'"
        )
        session_row.addWidget(self.ed_whisk_session, 1)

        whisk_section.add_content_layout(session_row)

        # Bearer Token input
        bearer_row = QHBoxLayout()
        bearer_row.setSpacing(8)
        bearer_label = QLabel("Bearer Token:")
        bearer_label.setFont(FONT_SMALL)
        bearer_label.setToolTip(
            "OAuth Bearer token from API requests.\n"
            "Get from: labs.google → Developer Tools (F12) → Network → Authorization header"
        )
        bearer_row.addWidget(bearer_label)

        self.ed_whisk_bearer = _line('Bearer token (without "Bearer " prefix)')
        self.ed_whisk_bearer.setText(self.state.get('whisk_bearer_token', ''))
        self.ed_whisk_bearer.setEchoMode(QLineEdit.Password)
        self.ed_whisk_bearer.setToolTip(
            "Bearer token from labs.google.com API requests\n"
            "1. Open labs.google and login\n"
            "2. Go to https://labs.google/fx/tools/whisk\n"
            "3. Open Developer Tools (F12) → Network tab\n"
            "4. Make a generation request\n"
            "5. Find request to 'aisandbox-pa.googleapis.com'\n"
            "6. Copy Authorization header value (without 'Bearer ' prefix)"
        )
        bearer_row.addWidget(self.ed_whisk_bearer, 1)

        whisk_section.add_content_layout(bearer_row)

        # Note about storage
        storage_note = QLabel(
            "📁 Note: All tokens are stored in config.json and ~/.veo_image2video_cfg.json"
        )
        storage_note.setFont(FONT_SMALL)
        storage_note.setStyleSheet("color: #888; font-size: 10px; font-style: italic; padding: 4px;")
        whisk_section.add_content_widget(storage_note)

        # Add Whisk section to grid (row 4, spanning both columns)
        accordion_grid.addWidget(whisk_section, 4, 0, 1, 2)

        api_layout.addLayout(accordion_grid)

        # Expand/Collapse buttons
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(8)

        btn_expand = CompactButton("📂 Expand All")
        btn_expand.setObjectName("btn_expand")
        btn_expand.clicked.connect(lambda: [
            google_section.set_expanded(True),
            eleven_section.set_expanded(True),
            openai_section.set_expanded(True),
            multi_acc_section.set_expanded(True),
            vertex_section.set_expanded(True),
            whisk_section.set_expanded(True)
        ])
        toggle_row.addWidget(btn_expand)

        btn_collapse = CompactButton("📁 Collapse All")
        btn_collapse.setObjectName("btn_collapse")
        btn_collapse.clicked.connect(lambda: [
            google_section.set_expanded(False),
            eleven_section.set_expanded(False),
            openai_section.set_expanded(False),
            multi_acc_section.set_expanded(False),
            vertex_section.set_expanded(False),
            whisk_section.set_expanded(False)
        ])
        toggle_row.addWidget(btn_collapse)
        toggle_row.addStretch()

        api_layout.addLayout(toggle_row)
        root.addWidget(api_group)

        # === STORAGE - ONE LINE ===
        storage_group = QGroupBox("💾 Storage Settings")
        storage_group.setFont(FONT_H2)
        st_layout = QVBoxLayout(storage_group)
        st_layout.setSpacing(6)

        # Radio + path in one row
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.rb_local = QRadioButton("📁 Local")
        self.rb_drive = QRadioButton("☁️ Drive")
        storage = (self.state.get('download_storage') or 'local').lower()
        (self.rb_drive if storage == 'gdrive' else self.rb_local).setChecked(True)

        row1.addWidget(self.rb_local)
        row1.addWidget(self.rb_drive)
        row1.addWidget(QLabel("Path:"))

        self.ed_local = _line('Select folder...')
        self.ed_local.setText(self.state.get('download_root', ''))
        row1.addWidget(self.ed_local, 1)

        self.btn_browse = CompactButton("📂 Browse")
        self.btn_browse.setObjectName("btn_browse")
        self.btn_browse.setMinimumHeight(36)
        self.btn_browse.clicked.connect(self._pick_dir)
        row1.addWidget(self.btn_browse)

        st_layout.addLayout(row1)

        # Drive settings in one row
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        row2.addWidget(QLabel("Folder ID:"))
        self.ed_gdrive = _line('Folder ID')
        self.ed_gdrive.setText(self.state.get('gdrive_folder_id', ''))
        row2.addWidget(self.ed_gdrive, 1)
        row2.addWidget(QLabel("OAuth:"))
        self.ed_oauth = _line('Token')
        self.ed_oauth.setText(self.state.get('google_workspace_oauth_token', ''))
        row2.addWidget(self.ed_oauth, 1)
        st_layout.addLayout(row2)

        self.rb_local.toggled.connect(self._toggle_storage)
        self._toggle_storage()

        root.addWidget(storage_group)

        # === SYSTEM PROMPTS - ONE LINE ===
        prompts_row = QHBoxLayout()
        prompts_row.setSpacing(8)
        prompts_row.addWidget(QLabel("🔄 Prompts:"))
        self.ed_sheets_url = _line('Google Sheets URL', read_only=False)  # Enhanced: Now editable!
        self.ed_sheets_url.setText(self.state.get('system_prompts_url', 'https://docs.google.com/spreadsheets/d/1ohiL6xOBbjC7La2iUdkjrVjG4IEUnVWhI0fRoarD6P0'))  # Enhanced: Load from config
        prompts_row.addWidget(self.ed_sheets_url, 1)
        self.btn_update_prompts = CompactButton("⬇ Update")
        self.btn_update_prompts.setObjectName("btn_primary")
        self.btn_update_prompts.setMinimumHeight(36)
        self.btn_update_prompts.clicked.connect(self._update_system_prompts)
        prompts_row.addWidget(self.btn_update_prompts)
        root.addLayout(prompts_row)

        self.lb_prompts_status = QLabel("")
        self.lb_prompts_status.setFont(FONT_SMALL)
        root.addWidget(self.lb_prompts_status)

        # === BOTTOM BAR ===
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        self.btn_save = CompactButton("💾 Save Settings")
        self.btn_save.setObjectName("btn_save_luu")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_save.clicked.connect(self._save)
        bottom_row.addWidget(self.btn_save)

        self.lb_saved = QLabel("")
        self.lb_saved.setFont(FONT_SMALL)
        self.lb_saved.setStyleSheet("color: #4CAF50; font-weight: bold;")
        bottom_row.addWidget(self.lb_saved)
        bottom_row.addStretch()

        self.lb_version = QLabel(f"Video Super Ultra v{get_version()}")
        self.lb_version.setFont(FONT_SMALL)
        bottom_row.addWidget(self.lb_version)

        root.addLayout(bottom_row)

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _load_accounts_table(self):
        """Load accounts from config into table"""
        account_mgr = get_account_manager()
        accounts = account_mgr.get_all_accounts()

        self.accounts_table.setRowCount(len(accounts))

        for row, account in enumerate(accounts):
            # Enabled checkbox
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(account.enabled)
            checkbox.stateChanged.connect(lambda state, r=row: self._toggle_account(r, state))
            checkbox_layout.addWidget(checkbox)
            self.accounts_table.setCellWidget(row, 0, checkbox_widget)

            # Account name
            name_item = QTableWidgetItem(account.name)
            self.accounts_table.setItem(row, 1, name_item)

            # Project ID (truncated)
            project_id_display = account.project_id[:16] + "..." if len(account.project_id) > 16 else account.project_id
            project_item = QTableWidgetItem(project_id_display)
            self.accounts_table.setItem(row, 2, project_item)

            # Token count
            token_count = QTableWidgetItem(f"{len(account.tokens)} token(s)")
            self.accounts_table.setItem(row, 3, token_count)

    def _toggle_account(self, row, state):
        """Toggle account enabled state"""
        account_mgr = get_account_manager()
        if state == Qt.Checked:
            account_mgr.enable_account(row)
        else:
            account_mgr.disable_account(row)

    def _add_account(self):
        """Add a new account via dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Google Labs Account (OAuth Flow Tokens)")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        # Account name
        layout.addWidget(_label("Account Name:"))
        ed_name = _line("e.g., Account 1, Production, Testing...")
        layout.addWidget(ed_name)

        # Project ID - Pre-fill with default
        layout.addWidget(_label("Project ID:"))
        ed_project_id = _line("9bb9b09b-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        default_project = self.ed_project.text().strip() or DEFAULT_PROJECT_ID
        ed_project_id.setText(default_project)
        layout.addWidget(ed_project_id)

        # Tokens
        layout.addWidget(_label("OAuth Flow Tokens from labs.google.com (one per line):"))
        ed_tokens = QTextEdit()
        ed_tokens.setPlaceholderText(
            "Paste OAuth Flow Tokens from labs.google.com here, one per line\n"
            "NOTE: These are NOT API keys"
        )
        ed_tokens.setMaximumHeight(120)
        ed_tokens.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Courier New';
                font-size: 11px;
            }
        """)
        layout.addWidget(ed_tokens)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            name = ed_name.text().strip()
            project_id = ed_project_id.text().strip()
            tokens_text = ed_tokens.toPlainText().strip()
            tokens = [line.strip() for line in tokens_text.split('\n') if line.strip()]

            if not name or not project_id or not tokens:
                QMessageBox.warning(self, "Invalid Input", "Please fill all fields")
                return

            account = LabsAccount(name=name, project_id=project_id, tokens=tokens, enabled=True)

            account_mgr = get_account_manager()
            account_mgr.add_account(account)

            self._load_accounts_table()
            self.lb_account_status.setText(f"✓ Added account: {name}")

    def _edit_account(self):
        """Edit selected account"""
        row = self.accounts_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an account to edit")
            return

        account_mgr = get_account_manager()
        account = account_mgr.get_account(row)

        if not account:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Google Labs Account (OAuth Flow Tokens)")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        # Account name
        layout.addWidget(_label("Account Name:"))
        ed_name = _line()
        ed_name.setText(account.name)
        layout.addWidget(ed_name)

        # Project ID
        layout.addWidget(_label("Project ID:"))
        ed_project_id = _line()
        ed_project_id.setText(account.project_id)
        layout.addWidget(ed_project_id)

        # Tokens
        layout.addWidget(_label("OAuth Flow Tokens from labs.google.com (one per line):"))
        ed_tokens = QTextEdit()
        ed_tokens.setPlainText('\n'.join(account.tokens))
        ed_tokens.setMaximumHeight(120)
        ed_tokens.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Courier New';
                font-size: 11px;
            }
        """)
        layout.addWidget(ed_tokens)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            name = ed_name.text().strip()
            project_id = ed_project_id.text().strip()
            tokens_text = ed_tokens.toPlainText().strip()
            tokens = [line.strip() for line in tokens_text.split('\n') if line.strip()]

            if not name or not project_id or not tokens:
                QMessageBox.warning(self, "Invalid Input", "Please fill all fields")
                return

            # Update account
            account.name = name
            account.project_id = project_id
            account.tokens = tokens

            self._load_accounts_table()
            self.lb_account_status.setText(f"✓ Updated account: {name}")

    def _remove_account(self):
        """Remove selected account"""
        row = self.accounts_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an account to remove")
            return

        account_mgr = get_account_manager()
        account = account_mgr.get_account(row)

        if not account:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove account '{account.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            account_mgr.remove_account(row)
            self._load_accounts_table()
            self.lb_account_status.setText(f"✓ Removed account: {account.name}")

    def _toggle_storage(self):
        is_local = self.rb_local.isChecked()
        self.ed_local.setEnabled(is_local)
        self.btn_browse.setEnabled(is_local)
        self.ed_gdrive.setEnabled(not is_local)
        self.ed_oauth.setEnabled(not is_local)

    def _pick_dir(self):
        d = QFileDialog.getExistingDirectory(self, 'Select download folder', '')
        if d:
            self.ed_local.setText(d)

    def _load_vertex_accounts_table(self):
        """Load Vertex AI service accounts from config into table"""
        from services.vertex_service_account_manager import get_vertex_account_manager

        account_mgr = get_vertex_account_manager()
        account_mgr.load_from_config(cfg.load())
        accounts = account_mgr.get_all_accounts()

        self.vertex_accounts_table.setRowCount(len(accounts))

        for row, account in enumerate(accounts):
            # Enabled checkbox
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(account.enabled)
            checkbox.stateChanged.connect(lambda state, r=row: self._toggle_vertex_account(r, state))
            checkbox_layout.addWidget(checkbox)
            self.vertex_accounts_table.setCellWidget(row, 0, checkbox_widget)

            # Account name
            name_item = QTableWidgetItem(account.name)
            self.vertex_accounts_table.setItem(row, 1, name_item)

            # Project ID (truncated)
            project_display = account.project_id[:20] + "..." if len(account.project_id) > 20 else account.project_id
            project_item = QTableWidgetItem(project_display)
            self.vertex_accounts_table.setItem(row, 2, project_item)

            # Region
            region_item = QTableWidgetItem(account.location)
            self.vertex_accounts_table.setItem(row, 3, region_item)

            # Credit check button
            credit_widget = QWidget()
            credit_layout = QHBoxLayout(credit_widget)
            credit_layout.setContentsMargins(2, 2, 2, 2)
            credit_layout.setAlignment(Qt.AlignCenter)
            credit_btn = CompactButton("💰 Check")
            credit_btn.setMaximumWidth(80)
            credit_btn.setToolTip(
                f"Mở GCP Console để kiểm tra credit còn lại\n"
                f"Project: {account.project_id}"
            )
            credit_btn.clicked.connect(
                lambda checked, p=account.project_id, loc=account.location: (
                    self._check_vertex_credit(p, loc)
                )
            )
            credit_layout.addWidget(credit_btn)
            self.vertex_accounts_table.setCellWidget(row, 4, credit_widget)

    def _toggle_vertex_account(self, row, state):
        """Toggle Vertex AI service account enabled state"""
        from services.vertex_service_account_manager import get_vertex_account_manager

        account_mgr = get_vertex_account_manager()
        if state == Qt.Checked:
            account_mgr.enable_account(row)
        else:
            account_mgr.disable_account(row)

    def _add_vertex_account(self):
        """Add new Vertex AI service account"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Vertex AI Service Account")
        dialog.setMinimumWidth(600)

        layout = QVBoxLayout(dialog)

        # Instructions
        inst = QLabel(
            "📝 Nhập thông tin Service Account JSON từ Google Cloud Console:\n\n"
            "1. Tạo Service Account tại console.cloud.google.com\n"
            "2. Enable Vertex AI API\n"
            "3. Tạo và download JSON key file\n"
            "4. Paste nội dung JSON vào đây"
        )
        inst.setWordWrap(True)
        inst.setStyleSheet("color: #666; padding: 8px;")
        layout.addWidget(inst)

        # Name input
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Account Name:"))
        ed_name = _line("My Vertex Account")
        name_row.addWidget(ed_name, 1)
        layout.addLayout(name_row)

        # JSON input
        layout.addWidget(QLabel("Service Account JSON:"))
        ed_json = QTextEdit()
        ed_json.setPlaceholderText('{"type": "service_account", "project_id": "...", ...}')
        ed_json.setMinimumHeight(200)
        ed_json.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New';
                font-size: 10px;
                background: #F5F5F5;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout.addWidget(ed_json)

        # Location input
        loc_row = QHBoxLayout()
        loc_row.addWidget(QLabel("Region:"))
        ed_location = _line("us-central1")
        ed_location.setText("us-central1")
        loc_row.addWidget(ed_location, 1)
        layout.addLayout(loc_row)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            name = ed_name.text().strip()
            json_str = ed_json.toPlainText().strip()
            location = ed_location.text().strip() or "us-central1"

            if not name:
                QMessageBox.warning(self, "Validation Error", "Please enter account name")
                return

            if not json_str:
                QMessageBox.warning(self, "Validation Error", "Please enter service account JSON")
                return

            # Validate JSON
            from services.vertex_service_account_manager import (
                VertexServiceAccount,
                get_vertex_account_manager,
            )

            account_mgr = get_vertex_account_manager()
            is_valid, error_msg = account_mgr.validate_credentials_json(json_str)

            if not is_valid:
                QMessageBox.critical(self, "Invalid JSON", f"Service account JSON is invalid:\n\n{error_msg}")
                return

            # Extract project_id from JSON
            import json
            try:
                creds = json.loads(json_str)
                project_id = creds.get('project_id', '')
            except:
                QMessageBox.critical(self, "Error", "Could not parse JSON to extract project_id")
                return

            # Add account
            account = VertexServiceAccount(
                name=name,
                project_id=project_id,
                credentials_json=json_str,
                location=location,
                enabled=True
            )

            account_mgr.add_account(account)
            self._load_vertex_accounts_table()

            QMessageBox.information(
                self,
                "Success",
                f"✅ Added service account: {name}\n\nProject ID: {project_id}"
            )

    def _edit_vertex_account(self):
        """Edit selected Vertex AI service account"""
        row = self.vertex_accounts_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an account to edit")
            return

        from services.vertex_service_account_manager import get_vertex_account_manager

        account_mgr = get_vertex_account_manager()
        accounts = account_mgr.get_all_accounts()

        if row >= len(accounts):
            return

        account = accounts[row]

        # Similar dialog to add, but pre-populated
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Vertex AI Service Account")
        dialog.setMinimumWidth(600)

        layout = QVBoxLayout(dialog)

        # Name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Account Name:"))
        ed_name = _line()
        ed_name.setText(account.name)
        name_row.addWidget(ed_name, 1)
        layout.addLayout(name_row)

        # JSON
        layout.addWidget(QLabel("Service Account JSON:"))
        ed_json = QTextEdit()
        ed_json.setPlainText(account.credentials_json)
        ed_json.setMinimumHeight(200)
        ed_json.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New';
                font-size: 10px;
                background: #F5F5F5;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout.addWidget(ed_json)

        # Location
        loc_row = QHBoxLayout()
        loc_row.addWidget(QLabel("Region:"))
        ed_location = _line()
        ed_location.setText(account.location)
        loc_row.addWidget(ed_location, 1)
        layout.addLayout(loc_row)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            import json

            from services.vertex_service_account_manager import VertexServiceAccount

            name = ed_name.text().strip()
            json_str = ed_json.toPlainText().strip()
            location = ed_location.text().strip() or "us-central1"

            # Validate and extract project_id
            is_valid, error_msg = account_mgr.validate_credentials_json(json_str)
            if not is_valid:
                QMessageBox.critical(self, "Invalid JSON", f"Service account JSON is invalid:\n\n{error_msg}")
                return

            try:
                creds = json.loads(json_str)
                project_id = creds.get('project_id', '')
            except:
                QMessageBox.critical(self, "Error", "Could not parse JSON")
                return

            # Update account
            updated_account = VertexServiceAccount(
                name=name,
                project_id=project_id,
                credentials_json=json_str,
                location=location,
                enabled=account.enabled
            )

            account_mgr.update_account(row, updated_account)
            self._load_vertex_accounts_table()

    def _remove_vertex_account(self):
        """Remove selected Vertex AI service account"""
        row = self.vertex_accounts_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an account to remove")
            return

        from services.vertex_service_account_manager import get_vertex_account_manager

        account_mgr = get_vertex_account_manager()
        accounts = account_mgr.get_all_accounts()

        if row >= len(accounts):
            return

        account = accounts[row]

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove service account '{account.name}'?\n\nProject ID: {account.project_id}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            account_mgr.remove_account(row)
            self._load_vertex_accounts_table()

    def _check_vertex_credit(self, project_id: str, location: str):
        """Open GCP Console billing page to check credit usage"""
        from services.vertex_credit_checker import get_credit_checker

        credit_checker = get_credit_checker()

        # Show info dialog with links
        info_text = credit_checker.get_account_info_text(project_id, location)

        msg = QMessageBox(self)
        msg.setWindowTitle("Check Vertex AI Credit")
        msg.setText(f"Project: {project_id}")
        msg.setInformativeText(info_text)
        msg.setIcon(QMessageBox.Information)

        # Add custom buttons
        btn_billing = msg.addButton("🔗 Open Billing Console", QMessageBox.ActionRole)
        btn_vertex = msg.addButton("🔗 Open Vertex AI Console", QMessageBox.ActionRole)
        btn_quotas = msg.addButton("🔗 Open Quotas Console", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Close)

        msg.exec_()

        # Handle button clicks
        clicked = msg.clickedButton()
        if clicked == btn_billing:
            credit_checker.open_billing_console(project_id)
        elif clicked == btn_vertex:
            credit_checker.open_vertex_console(project_id, location)
        elif clicked == btn_quotas:
            credit_checker.open_quotas_console(project_id)

    def _show_pricing_info(self):
        """Show Vertex AI pricing information"""
        from services.vertex_credit_checker import get_credit_checker

        credit_checker = get_credit_checker()
        pricing_text = credit_checker.format_pricing_info()

        msg = QMessageBox(self)
        msg.setWindowTitle("Vertex AI Pricing Information")
        msg.setText("💰 Thông tin chi phí và credit Vertex AI")
        msg.setInformativeText(pricing_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def _save(self):
        storage = 'gdrive' if self.rb_drive.isChecked() else 'local'
        st = {
            **cfg.load(),
            'account_email': self.ed_email.text().strip(),
            'download_storage': storage,
            'download_root': self.ed_local.text().strip(),
            'gdrive_folder_id': self.ed_gdrive.text().strip(),
            'google_workspace_oauth_token': self.ed_oauth.text().strip(),
            'google_api_keys': self.w_google.get_keys(),
            'elevenlabs_api_keys': self.w_eleven.get_keys(),
            'openai_api_keys': self.w_openai.get_keys(),
            'default_voice_id': self.ed_voice.text().strip() or '3VnrjnYrskPMDsapTr8X',
            'flow_project_id': self.ed_project.text().strip() or DEFAULT_PROJECT_ID,
            'system_prompts_url': self.ed_sheets_url.text().strip(),  # Enhanced: Save prompts URL
            # Whisk Authentication
            'labs_session_token': self.ed_whisk_session.text().strip(),
            'whisk_bearer_token': self.ed_whisk_bearer.text().strip(),
            # Vertex AI Configuration
            'vertex_ai': {
                'enabled': self.chk_vertex_enabled.isChecked(),
                'use_vertex_first': self.chk_vertex_first.isChecked()
            }
        }

        # ISSUE #4 FIX: Save multi-account manager data
        from services.account_manager import get_account_manager
        account_mgr = get_account_manager()
        account_mgr.save_to_config(st)

        # Save Vertex AI service accounts
        from services.vertex_service_account_manager import get_vertex_account_manager
        vertex_account_mgr = get_vertex_account_manager()
        vertex_account_mgr.save_to_config(st)

        cfg.save(st)

        # FIX: Force refresh key_manager and config cache after saving
        # This ensures API keys are immediately available without waiting for cache timeout
        try:
            from services.core import config as core_config
            from services.core import key_manager
            core_config.clear_cache()  # Clear services/core/config cache
            key_manager.refresh(force=True)  # Force refresh key pools
        except Exception as e:
            logger.warning(f"Failed to refresh key manager cache: {e}")

        self.lb_saved.setText(f'✓ Saved at {_ts()}')

        # Update Vertex AI status after save
        self._update_vertex_status()

        QTimer.singleShot(5000, lambda: self.lb_saved.setText(''))

    def _update_vertex_status(self):
        """Update Vertex AI status indicator based on configuration"""
        if not hasattr(self, 'lb_vertex_status'):
            return

        enabled = (
            self.chk_vertex_enabled.isChecked()
            if hasattr(self, 'chk_vertex_enabled')
            else False
        )

        # Check service accounts
        from services.vertex_service_account_manager import get_vertex_account_manager
        account_mgr = get_vertex_account_manager()
        account_mgr.load_from_config(cfg.load())
        enabled_accounts = account_mgr.get_enabled_accounts()

        if enabled and len(enabled_accounts) > 0:
            status_text = (
                f'✅ Vertex AI enabled - {len(enabled_accounts)} '
                f'account(s) active - Giảm lỗi 503 đáng kể!'
            )
            self.lb_vertex_status.setText(status_text)
            self.lb_vertex_status.setStyleSheet(
                'color: #4CAF50; font-weight: bold; padding: 4px;'
            )
        elif enabled and len(enabled_accounts) == 0:
            self.lb_vertex_status.setText('⚠️ Cần thêm ít nhất 1 service account')
            self.lb_vertex_status.setStyleSheet('color: #FF9800; font-weight: bold; padding: 4px;')
        else:
            status_text = (
                'ℹ️ Vertex AI disabled - Sử dụng Google AI Studio '
                '(có thể bị lỗi 503)'
            )
            self.lb_vertex_status.setText(status_text)
            self.lb_vertex_status.setStyleSheet('color: #757575; padding: 4px;')

    def _update_system_prompts(self):
        self.lb_prompts_status.setText('⏳ Updating...')
        self.btn_update_prompts.setEnabled(False)
        QApplication.processEvents()

        try:
            import os

            from services.prompt_updater import update_prompts_file

            services_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services')
            prompts_file = os.path.join(services_dir, 'domain_prompts.py')

            success, message = update_prompts_file(prompts_file)

            if success:
                self.lb_prompts_status.setText(f'✅ {message}')
                QMessageBox.information(self, 'Success', message)
            else:
                self.lb_prompts_status.setText(f'❌ {message}')
                QMessageBox.critical(self, 'Error', message)

        except Exception as e:
            error_msg = f'❌ Error: {str(e)}'
            self.lb_prompts_status.setText(error_msg)
            QMessageBox.critical(self, 'Error', error_msg)

        finally:
            self.btn_update_prompts.setEnabled(True)
