# Changelog

All notable changes to Video Super Ultra v3 are documented here.

## [7.2.6] - 2025-11-10

### Removed - Code Cleanup
- Removed unused duplicate logger implementation (`utils/logger_enhanced.py`)
- Removed unused duplicate API key managers:
  - `services/core/api_key_manager.py`
  - `services/core/key_rotation_manager.py`
  - `services/google/api_key_manager.py`
- Removed outdated UI components:
  - `ui/settings_panel.py` (replaced by v3_compact)
  - `ui/widgets/key_list.py` (replaced by v2)
- Archived historical documentation files to `docs/archive/`

### Optimized
- Consolidated key management to single implementation in `services/core/key_manager.py`
- Improved code organization and reduced redundancy

---

## Previous Releases

For detailed information about previous fixes and improvements, see:
- Multi-account video download fixes (v7.2.5)
- Bearer token storage improvements (v7.2.4)
- Text2Video language fixes
- Rate limit handling and Whisk integration
- Parallel video generation optimizations

See `docs/archive/` for detailed historical reports.
