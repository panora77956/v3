# services/history_service.py
"""
History Service - Track video creation history for Text2Video and VideoBanHang
Author: chamnv-dev
Date: 2025-01-09
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class HistoryEntry:
    """Represents a single history entry for video creation"""
    
    def __init__(
        self,
        timestamp: str,
        idea: str,
        style: str,
        genre: Optional[str] = None,
        video_count: int = 0,
        folder_path: str = "",
        panel_type: str = "text2video"  # or "videobanhang"
    ):
        self.timestamp = timestamp
        self.idea = idea
        self.style = style
        self.genre = genre
        self.video_count = video_count
        self.folder_path = folder_path
        self.panel_type = panel_type
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "idea": self.idea,
            "style": self.style,
            "genre": self.genre,
            "video_count": self.video_count,
            "folder_path": self.folder_path,
            "panel_type": self.panel_type
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'HistoryEntry':
        """Create from dictionary"""
        return HistoryEntry(
            timestamp=data.get("timestamp", ""),
            idea=data.get("idea", ""),
            style=data.get("style", ""),
            genre=data.get("genre"),
            video_count=data.get("video_count", 0),
            folder_path=data.get("folder_path", ""),
            panel_type=data.get("panel_type", "text2video")
        )


class HistoryService:
    """Service for managing video creation history"""
    
    def __init__(self, history_file: Optional[str] = None):
        """
        Initialize history service
        
        Args:
            history_file: Path to history file. If None, uses default location.
        """
        if history_file is None:
            history_file = os.path.join(
                os.path.expanduser("~"),
                ".veo_video_history.json"
            )
        self.history_file = history_file
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Ensure history file exists"""
        if not os.path.exists(self.history_file):
            self._save_history([])
    
    def _load_history(self) -> List[HistoryEntry]:
        """Load history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [HistoryEntry.from_dict(item) for item in data]
        except Exception as e:
            print(f"⚠️ Error loading history: {e}")
        return []
    
    def _save_history(self, entries: List[HistoryEntry]):
        """Save history to file"""
        try:
            data = [entry.to_dict() for entry in entries]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving history: {e}")
    
    def add_entry(
        self,
        idea: str,
        style: str,
        genre: Optional[str] = None,
        video_count: int = 0,
        folder_path: str = "",
        panel_type: str = "text2video"
    ) -> HistoryEntry:
        """
        Add a new history entry
        
        Args:
            idea: Video idea/concept
            style: Video style
            genre: Video genre (optional)
            video_count: Number of videos created
            folder_path: Path to folder containing videos
            panel_type: Type of panel ("text2video" or "videobanhang")
        
        Returns:
            The created history entry
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = HistoryEntry(
            timestamp=timestamp,
            idea=idea,
            style=style,
            genre=genre,
            video_count=video_count,
            folder_path=folder_path,
            panel_type=panel_type
        )
        
        entries = self._load_history()
        entries.insert(0, entry)  # Add to beginning for newest-first order
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(entries) > 1000:
            entries = entries[:1000]
        
        self._save_history(entries)
        return entry
    
    def get_history(
        self,
        panel_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[HistoryEntry]:
        """
        Get history entries
        
        Args:
            panel_type: Filter by panel type (None for all)
            limit: Maximum number of entries to return (None for all)
        
        Returns:
            List of history entries
        """
        entries = self._load_history()
        
        if panel_type:
            entries = [e for e in entries if e.panel_type == panel_type]
        
        if limit:
            entries = entries[:limit]
        
        return entries
    
    def clear_history(self, panel_type: Optional[str] = None):
        """
        Clear history
        
        Args:
            panel_type: Clear only for specific panel type (None for all)
        """
        if panel_type is None:
            self._save_history([])
        else:
            entries = self._load_history()
            entries = [e for e in entries if e.panel_type != panel_type]
            self._save_history(entries)
    
    def delete_entry(self, timestamp: str) -> bool:
        """
        Delete a specific entry by timestamp
        
        Args:
            timestamp: Timestamp of entry to delete
        
        Returns:
            True if entry was deleted, False otherwise
        """
        entries = self._load_history()
        original_len = len(entries)
        entries = [e for e in entries if e.timestamp != timestamp]
        
        if len(entries) < original_len:
            self._save_history(entries)
            return True
        return False


# Singleton instance
_history_service_instance = None


def get_history_service() -> HistoryService:
    """Get singleton history service instance"""
    global _history_service_instance
    if _history_service_instance is None:
        _history_service_instance = HistoryService()
    return _history_service_instance
