# History Tab Feature - Documentation

## Overview
The History Tab feature tracks all video creation activities in the Text2Video and VideoBanHang panels, providing users with a complete history of their work including ideas, styles, video counts, and quick access to output folders.

## Features

### History Tracking
- **Automatic tracking**: Videos are automatically logged when generation completes
- **Comprehensive data**: Records date/time, idea, style, genre (if applicable), video count, and folder path
- **Panel-specific**: Separate history for Text2Video and VideoBanHang panels

### History Widget
- **Table view**: Clear display of all history entries
- **Search/Filter**: Real-time search across all fields
- **Quick actions**:
  - 📂 Open folder button - Quick access to video output folder
  - 🗑️ Delete button - Remove individual entries
  - 🔄 Refresh button - Reload history
  - 🗑️ Clear history button - Remove all entries for the panel

### Data Columns
1. **Ngày giờ** (Date/Time) - When the video was created
2. **Ý tưởng** (Idea) - The video idea/concept
3. **Phong cách** (Style) - Video style used
4. **Thể loại** (Genre) - Category/topic (if applicable)
5. **Số video** (Video Count) - Number of videos generated
6. **Thư mục** (Folder) - Output folder path
7. **Hành động** (Actions) - Quick action buttons

## Implementation Details

### Files Created

#### 1. `services/history_service.py`
History management service with the following components:

**HistoryEntry class**:
- Represents a single history record
- Fields: timestamp, idea, style, genre, video_count, folder_path, panel_type
- Methods: to_dict(), from_dict()

**HistoryService class**:
- Manages history persistence
- Storage: `~/.veo_video_history.json`
- Methods:
  - `add_entry()` - Add new history entry
  - `get_history()` - Retrieve history with optional filtering
  - `delete_entry()` - Remove specific entry
  - `clear_history()` - Clear all or panel-specific history
- Automatic limit: Keeps last 1000 entries

**get_history_service()**:
- Singleton instance getter

#### 2. `ui/widgets/history_widget.py`
Reusable Qt widget for displaying history:

**Features**:
- PyQt5 QTableWidget-based display
- Search box with real-time filtering
- Refresh and clear all buttons
- Per-entry delete buttons
- Quick folder access buttons
- Alternating row colors
- Column resizing (flexible for idea and folder)
- Tooltips for truncated text

**Constructor**:
```python
HistoryWidget(panel_type: str = "text2video", parent=None)
```

**Public Methods**:
- `refresh()` - Reload and display history

### Integration Points

#### Text2Video Panel (`ui/text2video_panel_v5_complete.py`)

**Import**:
```python
from ui.widgets.history_widget import HistoryWidget
```

**Tab Addition** (line ~1000):
```python
# Tab 6: History
if HistoryWidget:
    self.history_widget = HistoryWidget(panel_type="text2video", parent=self)
    self.result_tabs.addTab(self.history_widget, "📜 Lịch sử")
```

**History Saving** (line ~1693):
```python
def _on_video_all_complete(self, video_paths):
    # ... existing code ...
    self._save_to_history(len(video_paths))
```

**Save Method** (line ~2763):
```python
def _save_to_history(self, video_count: int = 0):
    """Save current video creation to history"""
    # Extracts: idea, style, genre (domain/topic), folder path
    # Calls history service to add entry
    # Refreshes history widget
```

#### VideoBanHang Panel (`ui/video_ban_hang_v5_complete.py`)

**Import**:
```python
from ui.widgets.history_widget import HistoryWidget
```

**Tab Addition** (line ~885):
```python
# Tab 5: History
if HistoryWidget:
    self.history_widget = HistoryWidget(panel_type="videobanhang", parent=self)
    self.results_tabs.addTab(self.history_widget, "📜 Lịch sử")
```

**History Saving** (line ~1788):
```python
def _on_single_scene_video_completed(self, scene_idx, video_path):
    # ... existing code ...
    self._save_to_history(video_count=1)
```

**Save Method** (line ~1867):
```python
def _save_to_history(self, video_count: int = 0):
    """Save current video creation to history"""
    # Extracts: idea, style (fixed as "Video bán hàng"), folder path
    # Calls history service to add entry
    # Refreshes history widget
```

## Usage

### For Users

1. **Navigate to History Tab**:
   - Open Text2Video or VideoBanHang panel
   - Click on "📜 Lịch sử" tab

2. **View History**:
   - All past video creations are listed in the table
   - Newest entries appear first

3. **Search History**:
   - Type in the search box to filter entries
   - Searches across idea, style, genre, and folder path

4. **Quick Folder Access**:
   - Click "📂 Mở" button to open the video folder
   - Button is disabled if folder doesn't exist

5. **Delete Entry**:
   - Click "🗑️" button to delete specific entry
   - Confirmation dialog will appear

6. **Clear History**:
   - Click "🗑️ Xóa lịch sử" button to clear all entries
   - Confirmation dialog will appear
   - This only clears history for the current panel (text2video or videobanhang)

### For Developers

#### Adding History to a New Panel

1. **Import the widget**:
```python
from ui.widgets.history_widget import HistoryWidget
```

2. **Add the tab**:
```python
self.history_widget = HistoryWidget(panel_type="your_panel_type", parent=self)
self.your_tabs.addTab(self.history_widget, "📜 Lịch sử")
```

3. **Save to history when videos complete**:
```python
from services.history_service import get_history_service

def _on_videos_complete(self, video_count):
    hs = get_history_service()
    hs.add_entry(
        idea="Your idea text",
        style="Your style",
        genre="Optional genre",
        video_count=video_count,
        folder_path="Path to videos",
        panel_type="your_panel_type"
    )
    
    # Refresh widget if available
    if hasattr(self, 'history_widget') and self.history_widget:
        self.history_widget.refresh()
```

## Data Storage

**Location**: `~/.veo_video_history.json`

**Format**:
```json
[
  {
    "timestamp": "2025-11-09 06:17:43",
    "idea": "Video về AI và Machine Learning",
    "style": "Anime Cinematic",
    "genre": "Công nghệ - AI",
    "video_count": 3,
    "folder_path": "/home/user/videos/ai_ml",
    "panel_type": "text2video"
  },
  ...
]
```

**Retention**: Automatically keeps only the last 1000 entries to prevent file bloat.

## Error Handling

- **Missing HistoryWidget**: Falls back to placeholder tab with warning message
- **Import Errors**: Gracefully handles missing dependencies
- **File Errors**: Logs warnings if history file cannot be read/written
- **Invalid Folder Paths**: Disables "Open" button if folder doesn't exist

## Testing

See `/tmp/test_history.py` for comprehensive test suite covering:
- Entry creation
- Retrieval and filtering
- Deletion
- Panel-specific operations

Run tests:
```bash
python3 /tmp/test_history.py
```

## Future Enhancements

Potential improvements:
1. Export history to CSV/Excel
2. History statistics dashboard
3. Filter by date range
4. Sort by any column
5. Restore previous project settings from history
6. History analytics (most used styles, genres, etc.)
7. Cloud sync for history across devices
