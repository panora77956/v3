# 🎞️ Video Merge Feature Documentation

## Overview

The **Video Merge** (Ghép video) feature allows users to combine multiple video files into a single video with professional transitions, audio overlay, and resolution scaling up to 8K.

**Version:** 1.0.0  
**Added:** 2025-11-12  
**Author:** Video Super Ultra Team

---

## 🌟 Features

### 1. Video Selection
- **Add Individual Videos**: Select multiple video files one by one
- **Add from Folder**: Automatically add all videos from a folder
- **Supported Formats**: MP4, AVI, MOV, MKV, WebM
- **Batch Management**: Clear all videos with one click

### 2. Video Preview (NEW in v1.1.0)
After merging completes successfully:
- **Instant Playback**: Click "▶️ Xem Video" to open video in default player
- **Quick Access**: Click "📂 Mở Thư Mục" to open containing folder
- **Visual Feedback**: Success message displays output filename
- **One-Click Access**: No need to manually navigate to output location

### 3. Transition Effects
Choose from 10 professional transition effects between video scenes (marked with ✨ icons for better visibility):

| Transition | Description | Use Case |
|------------|-------------|----------|
| **None** | Simple concatenation | Fast merging, no visual effect |
| **Fade** | Gradual fade between scenes | Smooth, professional look |
| **Wipe Left** | Scene wipes from right to left | Dynamic, directional |
| **Wipe Right** | Scene wipes from left to right | Dynamic, directional |
| **Wipe Up** | Scene wipes from bottom to top | Upward motion |
| **Wipe Down** | Scene wipes from top to bottom | Downward motion |
| **Slide Left** | Scene slides from right | Smooth movement |
| **Slide Right** | Scene slides from left | Smooth movement |
| **Circle Crop** | Circular reveal effect | Creative, attention-grabbing |
| **Dissolve** | Cross-dissolve between scenes | Classic, elegant |

### 4. Audio Overlay
- Add background music or voiceover to the merged video
- **Supported Formats**: MP3, WAV, AAC, M4A, OGG
- Audio automatically syncs to video length
- Uses shortest duration (video or audio) as final length

### 5. Resolution Scaling
Export merged videos in various resolutions (4K/8K marked with ⭐ icons for prominence):

| Resolution | Dimensions | Quality | Use Case |
|------------|------------|---------|----------|
| **Original** | Keep source | Fast | No quality change |
| **720p (HD)** | 1280×720 | Standard | Web, mobile |
| **1080p (Full HD)** | 1920×1080 | High | YouTube, streaming |
| **2K** | 2560×1440 | Very High | Professional work |
| **4K (Ultra HD)** | 3840×2160 | Ultra High | Cinema, high-end displays |
| **8K** | 7680×4320 | Extreme | Future-proof, professional |

---

## 📋 Usage Guide

### Step 1: Select Videos

1. Click **"➕ Thêm video"** to add individual video files
2. Or click **"📁 Thêm từ thư mục"** to add all videos from a folder
3. Videos are listed in the order they will be merged
4. Use **"🗑️ Xóa tất cả"** to clear the list

**Tip:** Videos from a folder are sorted alphabetically. Name your files like `01_intro.mp4`, `02_main.mp4` to control order.

### Step 2: Add Audio (Optional)

1. Click **"➕ Chọn file audio"** to select an audio file
2. The audio will be overlaid on the merged video
3. Click **"🗑️ Xóa audio"** to remove it

### Step 3: Configure Settings

1. **Hiệu ứng chuyển cảnh** (Transition Effect)
   - Select desired transition from dropdown
   - Transition duration is 0.5 seconds
   
2. **Độ phân giải** (Resolution)
   - Select output resolution
   - Higher resolutions take longer to process

### Step 4: Choose Output Location

1. Click **"📁 Chọn"** next to the output path field
2. Choose where to save the merged video
3. Default format is MP4

### Step 5: Start Merging

1. Click **"🎬 Ghép Video"** to start
2. Watch progress in the log viewer
3. Click **"⏹️ Hủy"** to cancel at any time
4. Wait for completion notification

### Step 6: View Merged Video (NEW in v1.1.0)

After successful merge, the **"🎥 Xem Video"** section appears with two action buttons:

1. **▶️ Xem Video** - Opens the merged video in your system's default video player
2. **📂 Mở Thư Mục** - Opens the folder containing the merged video in file explorer

This allows you to immediately preview your merged video without manually navigating to the output location.

---

## ⚙️ Technical Details

### FFmpeg Commands

The feature uses FFmpeg for video processing:

#### Simple Concatenation (No Transition)
```bash
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

#### With Transitions (xfade filter)
```bash
ffmpeg -i video1.mp4 -i video2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=2.5[v]" \
  -map "[v]" -c:v libx264 -preset medium -crf 23 output.mp4
```

#### Audio Overlay
```bash
ffmpeg -i video.mp4 -i audio.mp3 \
  -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest output.mp4
```

#### Resolution Scaling
```bash
ffmpeg -i input.mp4 -vf scale=3840:2160 \
  -c:v libx264 -preset slow -crf 18 -c:a copy output.mp4
```

### Performance Considerations

| Resolution | Processing Time* | Disk Space** |
|------------|-----------------|--------------|
| Original | 1x (baseline) | 1x |
| 1080p | 2-3x | 1.2x |
| 4K | 5-8x | 2-3x |
| 8K | 15-25x | 4-6x |

*Relative to simple concatenation  
**Relative to original file size

### Quality Settings

- **No Transition**: `-c copy` (lossless, fast)
- **With Transition**: `-c:v libx264 -preset medium -crf 23` (high quality)
- **4K/8K Scaling**: `-c:v libx264 -preset slow -crf 18` (highest quality)

---

## 🎯 Use Cases

### 1. Social Media Content
- Merge multiple clips into one video
- Add background music
- Export in 1080p for optimal quality/size

### 2. Professional Presentations
- Combine slides and demo videos
- Use fade transitions for smooth flow
- Export in 4K for presentations

### 3. Video Compilations
- Merge highlights from multiple videos
- Add transition effects for professional look
- Scale to consistent resolution

### 4. Archive and Backup
- Combine related videos into single files
- Maintain original quality with no transition
- Reduce file management overhead

---

## ⚠️ Important Notes

### Requirements
- **FFmpeg**: Must be installed on the system
- **Disk Space**: Ensure sufficient space for output (especially 4K/8K)
- **Processing Time**: Large videos and high resolutions require more time

### Limitations
- Transition effects work best with videos of the same resolution
- Mixed aspect ratios may result in black bars
- Very long videos (>30 minutes) may take significant time to process

### Tips for Best Results
1. Use videos with the same resolution and aspect ratio
2. Start with "Original" resolution, scale up if needed
3. Test with 2-3 videos before processing large batches
4. Use "No transition" for fastest processing
5. For 4K/8K, ensure videos are already high resolution

---

## 🐛 Troubleshooting

### Error: FFmpeg not found
**Solution:** Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
Download from https://ffmpeg.org/download.html
```

### Error: Processing takes too long
**Solution:**
- Use "No transition" for faster processing
- Keep resolution at "Original" or 1080p
- Process fewer videos at once

### Error: Out of disk space
**Solution:**
- Free up disk space before processing
- Use lower resolution output
- Process videos in smaller batches

### Error: Audio not syncing
**Solution:**
- Ensure audio file is not corrupted
- Try converting audio to MP3 format
- Check audio file duration vs. video duration

---

## 📊 Performance Benchmarks

Test configuration: 3 videos × 10 seconds, 1080p source

| Configuration | Time | Output Size |
|--------------|------|-------------|
| No transition, Original | 5s | 30MB |
| Fade transition, Original | 45s | 32MB |
| No transition, 4K | 180s | 120MB |
| Fade transition, 4K | 240s | 125MB |

*Results may vary based on hardware and video codec*

---

## 🔮 Future Enhancements

Completed in v1.1.0:
- [x] Preview merged video ✅
- [x] Open merged video in default player ✅
- [x] Open folder containing merged video ✅

Potential features for future versions:
- [ ] Custom transition duration control
- [ ] Audio fade in/out
- [ ] Multiple audio tracks
- [ ] Video trimming before merge
- [ ] Batch processing multiple merge jobs
- [ ] GPU acceleration support
- [ ] More transition effects
- [ ] Custom watermark overlay
- [ ] Subtitle/caption support

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify FFmpeg is properly installed
3. Check application logs in the "📊 Tiến trình" section
4. Report issues on GitHub

---

**Happy Video Merging! 🎬**
