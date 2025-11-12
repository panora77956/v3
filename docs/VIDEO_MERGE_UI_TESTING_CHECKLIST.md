# Video Merge UI Testing Checklist

**Version:** 7.3.2  
**Date:** 2025-11-12  
**Feature:** 2-Row Layout Reorganization

## Pre-Testing Setup

- [ ] Ensure Python 3.8+ is installed
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify FFmpeg is installed: `ffmpeg -version`
- [ ] Have test video files ready (2-5 MP4 files)
- [ ] Have test audio file ready (MP3/WAV)

## Visual Layout Testing

### Row 1: Video và Audio
- [ ] Video Files section is on the left
- [ ] Audio section is on the right
- [ ] Video section is approximately 2x wider than Audio section
- [ ] Both sections are aligned horizontally at the same height
- [ ] Sections have consistent spacing (15px gap)

### Row 2: Cài đặt và Thư mục lưu
- [ ] Settings section is on the left
- [ ] Output section is on the right
- [ ] Both sections have equal width
- [ ] Both sections are aligned horizontally at the same height
- [ ] Sections have consistent spacing (15px gap)

## Functional Testing

### Video Files Section
- [ ] "➕ Thêm video" button works
- [ ] Can select multiple video files
- [ ] "📁 Thêm từ thư mục" button works
- [ ] Videos are listed in the list widget
- [ ] Video count updates correctly
- [ ] "🗑️ Xóa tất cả" button clears all videos

### Audio Section
- [ ] "➕ Chọn file audio" button works
- [ ] Can select audio file (MP3, WAV, etc.)
- [ ] Audio filename displays correctly
- [ ] Audio label shows green checkmark when file is selected
- [ ] "🗑️ Xóa audio" button clears audio

### Settings Section
- [ ] Transition effects dropdown displays all options
- [ ] Can select different transition effects
- [ ] ✨ sparkle icons are visible on transition options
- [ ] Resolution dropdown displays all options (720p - 8K)
- [ ] ⭐ star icons are visible on 4K and 8K options
- [ ] Helper notes are displayed and readable

### Output Section
- [ ] Output path text field is editable
- [ ] "📁 Chọn thư mục" button opens file dialog
- [ ] Selected path is displayed in text field
- [ ] Warning message "⚠️ BẮT BUỘC" is visible and prominent
- [ ] Path automatically gets .mp4 extension if not provided

## Integration Testing

### Video Merge Process
- [ ] Add at least 2 videos
- [ ] Optionally add audio
- [ ] Select transition effect
- [ ] Select resolution
- [ ] Choose output path
- [ ] Click "🎬 Ghép Video" button
- [ ] Progress bar appears
- [ ] Log messages appear in text area
- [ ] Cancel button appears during processing
- [ ] Process completes successfully
- [ ] Result section becomes visible

### Result Section
- [ ] "✅ Video ghép thành công!" message displays
- [ ] "▶️ Xem Video" button is enabled
- [ ] "📂 Mở Thư Mục" button is enabled
- [ ] Clicking "Xem Video" opens video in default player
- [ ] Clicking "Mở Thư Mục" opens folder in file explorer

## Error Handling Testing

### Missing Inputs
- [ ] Try to merge with 0 videos → Shows "Thiếu video" warning
- [ ] Try to merge with 1 video → Shows "Thiếu video" warning
- [ ] Try to merge without output path → Shows "Thiếu đường dẫn" warning

### Invalid Inputs
- [ ] Try to add non-video files → Should be filtered by file dialog
- [ ] Try to add non-audio files → Should be filtered by file dialog
- [ ] Try to merge with corrupted video files → Should show error

### System Issues
- [ ] Test without FFmpeg installed → Shows "Thiếu FFmpeg" error
- [ ] Test with invalid output path → Shows error

## Responsive Testing

### Window Sizes
- [ ] Test at 1024x600 (minimum) - sections should fit
- [ ] Test at 1280x720 (default) - optimal layout
- [ ] Test at 1440x900 (recommended) - spacious layout
- [ ] Test at 1920x1080 (full HD) - plenty of space

### Resizing
- [ ] Resize window smaller - sections should shrink proportionally
- [ ] Resize window larger - sections should expand proportionally
- [ ] Video section maintains 2:1 ratio with Audio in Row 1
- [ ] Settings and Output maintain 1:1 ratio in Row 2

## Performance Testing

### Small Videos
- [ ] Merge 2 videos (each < 10 seconds) - should be fast
- [ ] Merge 5 videos (each < 10 seconds) - should complete in < 1 min

### Large Videos
- [ ] Merge 2 videos (each > 1 minute) - should handle properly
- [ ] Test with 4K videos - should not crash
- [ ] Test with different resolutions - should handle properly

### With Audio
- [ ] Merge videos with audio overlay - audio should be audible
- [ ] Test with audio longer than video - should cut audio
- [ ] Test with audio shorter than video - should loop or end

### Transitions
- [ ] Test each transition effect - should apply correctly
- [ ] Test with "none" transition - should concatenate directly

## Compatibility Testing

### Operating Systems
- [ ] Windows 10/11 - all features work
- [ ] macOS - all features work
- [ ] Linux - all features work

### File Formats
- [ ] MP4 videos - supported
- [ ] AVI videos - supported
- [ ] MOV videos - supported
- [ ] MKV videos - supported
- [ ] WebM videos - supported

### Audio Formats
- [ ] MP3 audio - supported
- [ ] WAV audio - supported
- [ ] AAC audio - supported
- [ ] M4A audio - supported
- [ ] OGG audio - supported

## Accessibility Testing

### Keyboard Navigation
- [ ] Tab key navigates through all controls
- [ ] Enter key activates focused button
- [ ] Arrow keys work in dropdowns and lists

### Visual Elements
- [ ] All icons are visible (emojis render correctly)
- [ ] Colors have sufficient contrast
- [ ] Text is readable at default font size
- [ ] Buttons are large enough to click

## Documentation Testing

- [ ] README.md reflects new layout
- [ ] VIDEO_MERGE_UI_REORGANIZATION.md is accurate
- [ ] VIDEO_MERGE_UI_LAYOUT_DIAGRAM.md diagrams are correct
- [ ] Version number updated to 7.3.2

## Regression Testing

### Existing Features
- [ ] Progress tracking still works
- [ ] Log messages still display
- [ ] Cancel button still functions
- [ ] All previous features still accessible

### Other Panels
- [ ] Image2Video panel still works
- [ ] Text2Video panel still works
- [ ] Video Bán Hàng panel still works
- [ ] Clone Video panel still works
- [ ] Settings panel still works

## Security Testing

- [ ] No security alerts from CodeQL
- [ ] No SQL injection vulnerabilities
- [ ] No path traversal vulnerabilities
- [ ] No command injection vulnerabilities

## Sign-Off

### Developer
- [ ] All code changes reviewed
- [ ] Linting passed (ruff)
- [ ] No unused imports
- [ ] Documentation complete

### Tester
- [ ] All tests passed
- [ ] No critical bugs found
- [ ] UI looks professional
- [ ] Ready for production

### Stakeholder
- [ ] Meets requirements
- [ ] Improves user experience
- [ ] Approved for release

---

**Test Date:** _______________  
**Tester Name:** _______________  
**Result:** ☐ Pass  ☐ Fail  ☐ Needs Revision  
**Comments:**

_______________________________________________________________

_______________________________________________________________

_______________________________________________________________

---

**Author:** Video Super Ultra Team  
**Version:** 7.3.2
