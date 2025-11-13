# Quy Trình Xử Lý Âm Thanh / Audio Processing Workflow

## 📋 Tổng Quan / Overview

Tài liệu này mô tả chi tiết quy trình xử lý và xuất file âm thanh (thoại) cho từng cảnh video trong dự án Video Super Ultra v7.

**English:** This document describes the detailed workflow for processing and exporting audio files (dialogue/voiceover) for each video scene in the Video Super Ultra v7 project.

---

## 📁 Cấu Trúc Thư Mục Âm Thanh / Audio Folder Structure

Mỗi dự án video tự động tạo cấu trúc thư mục sau:

```
<Tên Dự Án>/
├── Video/              # Video files
├── Prompt/             # Scene prompts
├── Ảnh xem trước/      # Preview images
└── Audio/              # 🎤 Audio files (voiceover/dialogue)
    ├── scene_01_audio.mp3
    ├── scene_02_audio.mp3
    ├── scene_03_audio.mp3
    └── ...
```

### Vị Trí Thư Mục Audio / Audio Folder Location

Thư mục `Audio/` được tự động tạo khi:
- Khởi tạo dự án mới trong Video Bán Hàng
- Tạo script/kịch bản cho video
- Bắt đầu quá trình tạo video

**Đường dẫn mặc định:**
```
~/Downloads/<Tên-Dự-Án>/Audio/
```

Hoặc theo cấu hình trong `config.json`:
```json
{
  "download_root": "/path/to/your/projects"
}
```

---

## 🎤 Quy Trình Tạo Audio / Audio Generation Workflow

### Bước 1: Tạo Kịch Bản Video

1. Mở tab **"Video Bán Hàng"** trong ứng dụng
2. Nhập thông tin sản phẩm
3. Click **"Tạo Kịch Bản"** để AI sinh script
4. Script sẽ bao gồm:
   - Mô tả từng cảnh (scene description)
   - Lời thoại/voiceover cho mỗi cảnh
   - Thời lượng mỗi cảnh

### Bước 2: Cấu Hình Voice/TTS Provider

Chọn voice và TTS provider trong cài đặt:

```json
{
  "tts_provider": "google",       // google | elevenlabs | openai
  "voice_id": "vi-VN-Wavenet-A",  // Voice ID/name
  "speech_lang": "vi"             // Language code
}
```

**Giọng tiếng Việt khả dụng (Google TTS):**
- `vi-VN-Wavenet-A` - 🇻🇳 Nam Miền Bắc (Male, Northern) - Chất lượng cao
- `vi-VN-Wavenet-B` - 🇻🇳 Nữ Miền Bắc (Female, Northern) - Chất lượng cao
- `vi-VN-Wavenet-C` - 🇻🇳 Nữ Miền Nam (Female, Southern) - Chất lượng cao
- `vi-VN-Wavenet-D` - 🇻🇳 Nam Miền Nam (Male, Southern) - Chất lượng cao

### Bước 3: Tạo Audio Tự Động

Khi click **"Tạo Video"** cho một cảnh, hệ thống tự động:

1. ✅ Đọc lời thoại từ script cảnh đó
2. ✅ Gọi TTS API (Google/ElevenLabs/OpenAI)
3. ✅ Tạo file audio MP3
4. ✅ Lưu vào thư mục `Audio/` với tên: `scene_XX_audio.mp3`
5. ✅ Ghi log vào console và file log

**Ví dụ log:**
```
🎤 Bắt đầu tạo audio cho cảnh 1...
✓ Đã tạo audio cho cảnh 1: /path/to/project/Audio/scene_01_audio.mp3
```

### Bước 4: Kiểm Tra Audio Files

Sau khi tạo xong, bạn có thể:
- Mở thư mục `Audio/` để nghe các file
- Mỗi file `scene_XX_audio.mp3` tương ứng với 1 cảnh
- File audio có thể được sử dụng để ghép với video

---

## 🔧 Tạo Audio Thủ Công / Manual Audio Generation

### Sử Dụng Script Example

```bash
cd /home/runner/work/v3/v3
python examples/generate_scene_audio.py
```

### Sử Dụng Audio Generator Service

```python
from services.audio_generator import generate_scene_audio, generate_batch_audio

# Tạo audio cho 1 cảnh
scene_data = {
    "scene_index": 1,
    "audio": {
        "voiceover": {
            "tts_provider": "google",
            "voice_id": "vi-VN-Wavenet-A",
            "language": "vi",
            "text": "Xin chào, đây là cảnh đầu tiên của video."
        }
    }
}

audio_path = generate_scene_audio(
    scene_data=scene_data,
    output_dir="./Audio",
    scene_index=1
)

print(f"Audio saved to: {audio_path}")
# Output: Audio saved to: ./Audio/scene_01_audio.mp3
```

### Tạo Audio Cho Nhiều Cảnh (Batch)

```python
from services.audio_generator import generate_batch_audio

scenes = [
    {
        "scene_index": 1,
        "voiceover": "Lời thoại cảnh 1",
        "voice_id": "vi-VN-Wavenet-A"
    },
    {
        "scene_index": 2,
        "voiceover": "Lời thoại cảnh 2",
        "voice_id": "vi-VN-Wavenet-A"
    }
]

results = generate_batch_audio(scenes, output_dir="./Audio")
# Returns: {1: "./Audio/scene_01_audio.mp3", 2: "./Audio/scene_02_audio.mp3"}

print(f"Generated {len(results)} audio files")
```

---

## 🎛️ Tùy Chỉnh Audio / Audio Customization

### Điều Chỉnh Tốc Độ và Cao Độ / Rate & Pitch Adjustment

```python
voiceover_config = {
    "tts_provider": "google",
    "voice_id": "vi-VN-Wavenet-A",
    "language": "vi",
    "text": "Nội dung lời thoại",
    "prosody": {
        "rate": 1.2,      # Tốc độ nói (0.25 - 4.0, mặc định 1.0)
        "pitch": +2       # Cao độ giọng (-20 đến +20, mặc định 0)
    }
}
```

### Sử Dụng SSML Markup

SSML cho phép điều khiển chi tiết hơn:

```python
voiceover_config = {
    "tts_provider": "google",
    "voice_id": "vi-VN-Wavenet-A",
    "language": "vi",
    "ssml_markup": """
        <speak>
            <prosody rate="110%" pitch="+2st">
                Xin chào! 
            </prosody>
            <break time="500ms"/>
            <prosody rate="90%">
                Đây là sản phẩm tuyệt vời nhất năm 2025.
            </prosody>
        </speak>
    """
}
```

---

## 📤 Xuất File Audio / Exporting Audio Files

### Định Dạng File / File Format

- **Format:** MP3
- **Bitrate:** 128 kbps (mặc định từ TTS API)
- **Sample Rate:** 24000 Hz (Google TTS), 44100 Hz (ElevenLabs)
- **Channels:** Mono (1 channel)

### Đặt Tên File / File Naming

Mặc định: `scene_XX_audio.mp3` (XX là số thứ tự cảnh, có leading zero)

Ví dụ:
- `scene_01_audio.mp3`
- `scene_02_audio.mp3`
- `scene_15_audio.mp3`

### Tìm File Audio / Finding Audio Files

**Cách 1: Mở Thư Mục Từ UI**
1. Trong tab Video Bán Hàng
2. Click nút **"📂 Mở Thư Mục"**
3. Vào thư mục `Audio/`

**Cách 2: Đường Dẫn Trực Tiếp**
```bash
# Mặc định
cd ~/Downloads/<Tên-Dự-Án>/Audio/

# Hoặc theo config
cd /your/download/root/<Tên-Dự-Án>/Audio/
```

---

## 🔍 Kiểm Tra và Debug / Testing & Debugging

### Kiểm Tra Audio Đã Tạo

```bash
# List all audio files in project
ls -lh ~/Downloads/<Tên-Dự-Án>/Audio/

# Count audio files
ls ~/Downloads/<Tên-Dự-Án>/Audio/*.mp3 | wc -l

# Play audio file (macOS)
afplay ~/Downloads/<Tên-Dự-Án>/Audio/scene_01_audio.mp3

# Play audio file (Linux)
mpg123 ~/Downloads/<Tên-Dự-Án>/Audio/scene_01_audio.mp3
```

### Xem Log Chi Tiết

```bash
# Xem log file của dự án
cat ~/Downloads/<Tên-Dự-Án>/nhat_ky_xu_ly.log

# Filter audio-related logs
grep "audio\|Audio\|🎤" ~/Downloads/<Tên-Dự-Án>/nhat_ky_xu_ly.log
```

### Debug Audio Generation Issues

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from services.audio_generator import generate_scene_audio

# Enable debug logging
logger = logging.getLogger("services.tts_service")
logger.setLevel(logging.DEBUG)

# Try generating audio
audio_path = generate_scene_audio(scene_data, output_dir)
```

---

## ⚠️ Xử Lý Lỗi / Troubleshooting

### Lỗi 1: Không Tìm Thấy Thư Mục Audio

**Nguyên nhân:** Dự án chưa được khởi tạo hoặc thư mục bị xóa

**Giải pháp:**
```python
from services.sales_video_service import ensure_project_dirs

# Tạo lại thư mục
dirs = ensure_project_dirs("Tên-Dự-Án")
print(f"Audio folder: {dirs['audio']}")
```

### Lỗi 2: Audio Files Không Được Tạo

**Nguyên nhân:** 
- Thiếu API key
- Lời thoại rỗng (no speech text)
- Lỗi TTS API

**Giải pháp:**

1. Kiểm tra API key:
```json
{
  "google_api_keys": ["YOUR_GOOGLE_API_KEY"]
}
```

2. Kiểm tra lời thoại trong script:
```python
# Trong scene data phải có:
scene_data["speech"]  # hoặc
scene_data["dialogues"][0]["text_vi"]
```

3. Xem log để biết lỗi cụ thể

### Lỗi 3: Audio Quality Thấp

**Giải pháp:**
- Sử dụng Wavenet voices thay vì Standard
- Tăng sample rate trong TTS config
- Sử dụng ElevenLabs cho chất lượng tốt nhất

### Lỗi 4: Voice Không Phù Hợp với Language

**Giải pháp:**
```python
from services.audio_generator import validate_voiceover_config

config = {
    "tts_provider": "google",
    "voice_id": "vi-VN-Wavenet-A",  # ✅ Đúng cho tiếng Việt
    "language": "vi",
    "text": "Test"
}

is_valid, error = validate_voiceover_config(config)
if not is_valid:
    print(f"Invalid config: {error}")
```

---

## 🔗 Tích Hợp với Video / Integration with Video

### Ghép Audio với Video Clip

Sau khi có audio files, bạn có thể:

1. **Sử dụng Video Merge Panel:**
   - Chọn video clip
   - Thêm audio overlay từ thư mục `Audio/`
   - Xuất video với audio

2. **Sử dụng FFmpeg:**
```bash
# Ghép audio với video
ffmpeg -i scene_01.mp4 -i Audio/scene_01_audio.mp3 \
  -c:v copy -c:a aac -shortest \
  scene_01_with_audio.mp4
```

3. **Ghép nhiều cảnh:**
```bash
# Concatenate multiple scenes with audio
for i in {1..10}; do
  printf "file 'scene_%02d_with_audio.mp4'\n" $i >> concat_list.txt
done
ffmpeg -f concat -i concat_list.txt -c copy final_video.mp4
```

---

## 📚 Tài Liệu Liên Quan / Related Documentation

- [TTS Service Documentation](./TTS_SERVICE.md) - Chi tiết về TTS API
- [Voice Options](../services/voice_options.py) - Danh sách voices
- [Audio Generator Examples](../examples/generate_scene_audio.py) - Ví dụ code

---

## 📊 Workflow Diagram / Sơ Đồ Quy Trình

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUDIO PROCESSING WORKFLOW                    │
└─────────────────────────────────────────────────────────────────┘

1. TẠO KỊCH BẢN / SCRIPT GENERATION
   ├─> Nhập thông tin sản phẩm
   ├─> AI sinh script với lời thoại
   └─> Lưu script vào Prompt/

2. CẤU HÌNH TTS / TTS CONFIGURATION
   ├─> Chọn TTS provider (Google/ElevenLabs/OpenAI)
   ├─> Chọn voice (vi-VN-Wavenet-A, etc.)
   └─> Cấu hình prosody (rate, pitch)

3. TẠO AUDIO TỰ ĐỘNG / AUTO AUDIO GENERATION
   ├─> Click "Tạo Video" cho cảnh
   ├─> Đọc lời thoại từ script
   ├─> Gọi TTS API
   ├─> Nhận audio bytes (MP3)
   └─> Lưu vào Audio/scene_XX_audio.mp3

4. KIỂM TRA & XUẤT / VERIFY & EXPORT
   ├─> Mở thư mục Audio/
   ├─> Kiểm tra các file .mp3
   └─> Sử dụng audio cho video editing

┌─────────────────────────────────────────────────────────────────┐
│                       FILE STRUCTURE                             │
└─────────────────────────────────────────────────────────────────┘

Dự Án/
├── Audio/                    ⬅️ THƯ MỤC AUDIO CHÍNH
│   ├── scene_01_audio.mp3   (Cảnh 1 - Giới thiệu)
│   ├── scene_02_audio.mp3   (Cảnh 2 - Tính năng)
│   ├── scene_03_audio.mp3   (Cảnh 3 - Lợi ích)
│   └── ...
├── Video/
│   ├── scene_01.mp4
│   └── ...
├── Prompt/
│   ├── scene_01_prompt.txt
│   └── ...
└── nhat_ky_xu_ly.log        ⬅️ LOG FILE

```

---

## 🎯 Best Practices / Thực Hành Tốt Nhất

### 1. Chọn Voice Phù Hợp
- **Video chuyên nghiệp:** Sử dụng Wavenet voices (chất lượng cao)
- **Video nhanh/demo:** Sử dụng Standard voices (nhanh hơn, rẻ hơn)
- **Video cảm xúc:** Sử dụng ElevenLabs (tự nhiên nhất)

### 2. Tối Ưu Lời Thoại
- Viết câu ngắn, rõ ràng
- Tránh từ khó đọc hoặc viết tắt
- Thêm dấu câu để TTS ngắt nghỉ tự nhiên

### 3. Quản Lý API Keys
- Sử dụng multiple API keys để tránh rate limit
- Rotate keys trong config.json
- Monitor usage để tránh vượt quota

### 4. Backup Audio Files
- Audio files được tạo có thể tốn chi phí API
- Backup thư mục Audio/ định kỳ
- Không xóa audio files nếu muốn tái sử dụng

---

## 🆘 Hỗ Trợ / Support

**Nếu bạn gặp vấn đề với audio generation:**

1. Kiểm tra log file: `<Dự-Án>/nhat_ky_xu_ly.log`
2. Xem TTS Service docs: [TTS_SERVICE.md](./TTS_SERVICE.md)
3. Chạy example script: `python examples/generate_scene_audio.py`
4. Mở issue trên GitHub với log chi tiết

---

**Phiên bản:** 1.0  
**Cập nhật:** 2025-11-13  
**Tác giả:** Video Super Ultra v7 Team
