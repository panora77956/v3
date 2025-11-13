# 🎤 Giải Thích Về Thư Mục Audio / Audio Folder Explanation

## Tóm Tắt / Summary

Tài liệu này giải đáp câu hỏi: **"Tôi vẫn chưa thấy thư mục audio (chứa thoại của từng cảnh). Bạn chưa tạo ra thoại này?"**

**Trả lời ngắn gọn:**
✅ **Thư mục Audio ĐÃ TỒN TẠI** và được tạo tự động
✅ **Audio/thoại ĐƯỢC TẠO TỰ ĐỘNG** khi bạn tạo video
✅ **Xem hướng dẫn đầy đủ** trong tài liệu này

---

## 1️⃣ Thư Mục Audio Ở Đâu? / Where is the Audio Folder?

### Vị Trí / Location

Thư mục `Audio/` được tự động tạo trong **mỗi dự án video**:

```
📁 ~/Downloads/<Tên-Dự-Án>/Audio/
```

### Ví Dụ / Example

Nếu bạn tạo dự án tên **"Sản-Phẩm-iPhone-2025"**, thư mục audio sẽ ở:

```
📁 ~/Downloads/Sản-Phẩm-iPhone-2025/
   ├── Video/
   ├── Prompt/
   ├── Ảnh xem trước/
   └── Audio/              ⬅️ THƯ MỤC NÀY
       ├── scene_01_audio.mp3
       ├── scene_02_audio.mp3
       └── scene_03_audio.mp3
```

### Cách Mở / How to Open

**Cách 1: Từ Ứng Dụng**
1. Mở tab "Video Bán Hàng"
2. Click nút **"📂 Mở Thư Mục"**
3. Vào folder **"Audio"**

**Cách 2: Từ Terminal/Finder**
```bash
# macOS/Linux
cd ~/Downloads/<Tên-Dự-Án>/Audio/
ls -la

# Xem file audio
open .   # macOS
```

---

## 2️⃣ Audio/Thoại Có Được Tạo Không? / Is Audio/Dialogue Generated?

### ✅ Có, Audio Được Tạo Tự Động / Yes, Auto-Generated

Audio (thoại) **ĐƯỢC TẠO TỰ ĐỘNG** khi bạn:

1. ✅ Tạo kịch bản trong tab **"Video Bán Hàng"**
2. ✅ Click nút **"Tạo Video"** cho một cảnh
3. ✅ Hệ thống tự động:
   - Đọc lời thoại từ kịch bản
   - Gọi Google Text-to-Speech API
   - Tạo file MP3
   - Lưu vào `Audio/scene_XX_audio.mp3`

### Log Khi Tạo Audio / Audio Generation Log

Khi audio được tạo, bạn sẽ thấy trong log:

```
🎤 Bắt đầu tạo audio cho cảnh 1...
✓ Đã tạo audio cho cảnh 1: /path/to/Audio/scene_01_audio.mp3

🎤 Bắt đầu tạo audio cho cảnh 2...
✓ Đã tạo audio cho cảnh 2: /path/to/Audio/scene_02_audio.mp3
```

### File Audio Được Tạo / Generated Audio Files

- **Format:** MP3
- **Naming:** `scene_01_audio.mp3`, `scene_02_audio.mp3`, ...
- **Quality:** 128 kbps, 24000 Hz, Mono
- **Location:** `<Dự-Án>/Audio/`

---

## 3️⃣ Quy Trình Xử Lý Âm Thanh / Audio Processing Workflow

### Sơ Đồ Quy Trình / Workflow Diagram

```
1. TẠO DỰ ÁN / CREATE PROJECT
   ↓
   📁 Thư mục Audio/ được tạo tự động
   
2. TẠO KỊCH BẢN / GENERATE SCRIPT
   ↓
   📝 AI sinh kịch bản với lời thoại cho mỗi cảnh
   
3. CLICK "TẠO VIDEO" / CLICK "GENERATE VIDEO"
   ↓
   🎤 Hệ thống tự động:
   - Đọc lời thoại từ kịch bản
   - Gọi TTS API (Google/ElevenLabs/OpenAI)
   - Tạo file MP3
   - Lưu vào Audio/scene_XX_audio.mp3
   
4. KIỂM TRA / VERIFY
   ↓
   ✅ Mở thư mục Audio/ để xem và nghe các file
```

### Chi Tiết Từng Bước / Step-by-Step Details

#### Bước 1: Khởi Tạo Dự Án

```python
from services.sales_video_service import ensure_project_dirs

# Tạo cấu trúc thư mục
dirs = ensure_project_dirs("Tên-Dự-Án")

# Thư mục Audio được tạo
print(dirs["audio"])  # ~/Downloads/Tên-Dự-Án/Audio
```

#### Bước 2: Tạo Kịch Bản

- AI sinh kịch bản với lời thoại
- Mỗi cảnh có phần `speech` hoặc `voiceover`

```json
{
  "scene": 1,
  "speech": "Xin chào! Chào mừng bạn đến với sản phẩm của chúng tôi.",
  "duration": 5
}
```

#### Bước 3: Tạo Audio

```python
from services.audio_generator import generate_scene_audio

# Cấu hình cảnh
scene_data = {
    "scene_index": 1,
    "audio": {
        "voiceover": {
            "tts_provider": "google",
            "voice_id": "vi-VN-Wavenet-A",
            "language": "vi",
            "text": "Lời thoại của cảnh"
        }
    }
}

# Tạo audio
audio_path = generate_scene_audio(scene_data, audio_dir, 1)
# Kết quả: Audio/scene_01_audio.mp3
```

#### Bước 4: Xuất File

- File MP3 được lưu tại: `Audio/scene_XX_audio.mp3`
- Có thể sử dụng để ghép với video
- Backup files để tái sử dụng

---

## 4️⃣ Kiểm Tra Audio Files / Verify Audio Files

### Lệnh Kiểm Tra / Verification Commands

```bash
# 1. Kiểm tra thư mục Audio có tồn tại
ls -ld ~/Downloads/<Dự-Án>/Audio/

# 2. Xem danh sách file audio
ls -lh ~/Downloads/<Dự-Án>/Audio/*.mp3

# 3. Đếm số file audio
ls ~/Downloads/<Dự-Án>/Audio/*.mp3 | wc -l

# 4. Nghe file audio (macOS)
afplay ~/Downloads/<Dự-Án>/Audio/scene_01_audio.mp3

# 5. Xem thông tin file
file ~/Downloads/<Dự-Án>/Audio/scene_01_audio.mp3
```

### Kết Quả Mong Đợi / Expected Output

```bash
$ ls -lh ~/Downloads/Sản-Phẩm-iPhone-2025/Audio/
total 256K
-rw-r--r-- 1 user user  24K Nov 13 10:30 scene_01_audio.mp3
-rw-r--r-- 1 user user  28K Nov 13 10:31 scene_02_audio.mp3
-rw-r--r-- 1 user user  32K Nov 13 10:32 scene_03_audio.mp3
```

---

## 5️⃣ Xử Lý Khi Không Thấy Audio / Troubleshooting Missing Audio

### Tình Huống 1: Thư Mục Audio Không Tồn Tại

**Nguyên nhân:** Dự án chưa được khởi tạo đúng cách

**Giải pháp:**
```python
from services.sales_video_service import ensure_project_dirs

# Tạo lại thư mục
dirs = ensure_project_dirs("Tên-Dự-Án-Của-Bạn")
print(f"Audio folder created: {dirs['audio']}")
```

### Tình Huống 2: Thư Mục Audio Rỗng (Không Có File)

**Nguyên nhân có thể:**
1. ❌ Chưa click "Tạo Video" cho bất kỳ cảnh nào
2. ❌ Thiếu Google API key trong config.json
3. ❌ Kịch bản không có lời thoại (speech field rỗng)
4. ❌ Lỗi kết nối API

**Giải pháp:**

**A. Kiểm tra API Key**
```json
// config.json
{
  "google_api_keys": ["YOUR_GOOGLE_API_KEY"]
}
```

**B. Kiểm tra Kịch Bản**
```python
# Script phải có phần speech/voiceover
scene = {
    "scene": 1,
    "speech": "Nội dung lời thoại",  # ⬅️ PHẢI CÓ
    "prompt": "..."
}
```

**C. Xem Log Chi Tiết**
```bash
# Xem log file
cat ~/Downloads/<Dự-Án>/nhat_ky_xu_ly.log | grep -i audio

# Tìm lỗi
grep -i "error\|failed" ~/Downloads/<Dự-Án>/nhat_ky_xu_ly.log
```

### Tình Huống 3: Audio Không Có Âm Thanh

**Nguyên nhân:** File bị lỗi hoặc tham số TTS không đúng

**Giải pháp:**
```bash
# Kiểm tra file có hợp lệ
file scene_01_audio.mp3
# Kết quả phải là: "MPEG ADTS, layer III"

# Kiểm tra kích thước file
ls -lh scene_01_audio.mp3
# Phải > 10KB
```

---

## 6️⃣ Demo Scripts / Example Scripts

### Script 1: Demo Đầy Đủ

```bash
python examples/audio_workflow_demo.py
```

Hiển thị:
- ✅ Cách tạo thư mục Audio
- ✅ Cách tạo audio cho 1 cảnh
- ✅ Cách tạo audio hàng loạt
- ✅ Tùy chỉnh giọng nói
- ✅ Xử lý lỗi

### Script 2: TTS Examples

```bash
python examples/generate_scene_audio.py
```

### Script 3: Tạo Audio Thủ Công

```python
from services.audio_generator import generate_batch_audio

scenes = [
    {"scene_index": 1, "voiceover": "Cảnh 1", "voice_id": "vi-VN-Wavenet-A"},
    {"scene_index": 2, "voiceover": "Cảnh 2", "voice_id": "vi-VN-Wavenet-A"},
]

results = generate_batch_audio(scenes, "./Audio")
print(f"Generated {len(results)} audio files")
```

---

## 7️⃣ Tài Liệu Liên Quan / Related Documentation

### Tài Liệu Chính / Main Docs

1. **[AUDIO_PROCESSING_WORKFLOW.md](./AUDIO_PROCESSING_WORKFLOW.md)**  
   📖 Hướng dẫn đầy đủ về quy trình xử lý audio (Vietnamese + English)

2. **[HUONG_DAN_AUDIO_VI.md](./HUONG_DAN_AUDIO_VI.md)**  
   📖 Quick guide bằng tiếng Việt

3. **[TTS_SERVICE.md](./TTS_SERVICE.md)**  
   📖 Chi tiết về TTS API và cấu hình

### Code Examples

- `examples/audio_workflow_demo.py` - Demo script
- `examples/generate_scene_audio.py` - TTS examples
- `services/audio_generator.py` - Audio generation service
- `services/tts_service.py` - TTS service implementation

---

## 8️⃣ Câu Hỏi Thường Gặp / FAQ

### Q1: Tại sao tôi không thấy thư mục Audio?

**A:** Thư mục chỉ được tạo khi bạn khởi tạo dự án mới. Kiểm tra:
```bash
ls ~/Downloads/<Tên-Dự-Án>/
```

Nếu không thấy, chạy:
```python
from services.sales_video_service import ensure_project_dirs
ensure_project_dirs("Tên-Dự-Án")
```

### Q2: File audio được lưu ở đâu?

**A:** Trong thư mục `Audio/` của dự án:
```
~/Downloads/<Dự-Án>/Audio/scene_XX_audio.mp3
```

### Q3: Audio có chất lượng tốt không?

**A:** Có, sử dụng:
- Google TTS Wavenet: Chất lượng cao nhất
- Bitrate: 128 kbps
- Sample rate: 24000 Hz

### Q4: Có thể tùy chỉnh giọng nói không?

**A:** Có, tùy chỉnh:
- Voice (nam/nữ, miền Bắc/miền Nam)
- Speaking rate (0.5 - 2.0)
- Pitch (-20 đến +20)

### Q5: Audio có tốn phí không?

**A:** Có, sử dụng Google TTS API (tính phí theo ký tự).
- Wavenet: ~$16 per 1M chars
- Standard: ~$4 per 1M chars

### Q6: Làm sao biết audio đã được tạo thành công?

**A:** Xem log trong ứng dụng hoặc file log:
```bash
cat ~/Downloads/<Dự-Án>/nhat_ky_xu_ly.log | grep "✓ Đã tạo audio"
```

---

## 9️⃣ Tóm Tắt / Summary

### ✅ Những Gì ĐÃ CÓ

- ✅ Thư mục `Audio/` được tạo tự động cho mỗi dự án
- ✅ Audio/thoại được tạo tự động khi click "Tạo Video"
- ✅ Hỗ trợ đa ngôn ngữ, đặc biệt tiếng Việt
- ✅ Nhiều giọng nói chất lượng cao (Wavenet)
- ✅ Tùy chỉnh tốc độ, cao độ giọng
- ✅ Tự động đặt tên file: `scene_XX_audio.mp3`
- ✅ Log chi tiết quá trình tạo audio
- ✅ Tài liệu và demo scripts đầy đủ

### 📋 Quy Trình Nhanh

1. Tạo dự án → Thư mục `Audio/` được tạo
2. Tạo kịch bản → AI sinh lời thoại
3. Click "Tạo Video" → Audio tự động được tạo
4. Kiểm tra `Audio/scene_XX_audio.mp3`

### 🔗 Links Hữu Ích

- Demo: `python examples/audio_workflow_demo.py`
- Docs: `docs/AUDIO_PROCESSING_WORKFLOW.md`
- Quick Guide: `docs/HUONG_DAN_AUDIO_VI.md`

---

**Hy vọng tài liệu này đã giải đáp thắc mắc của bạn về thư mục Audio và quy trình tạo thoại!**

---

**Phiên bản:** 1.0  
**Cập nhật:** 2025-11-13  
**Tác giả:** Video Super Ultra v7 Team
