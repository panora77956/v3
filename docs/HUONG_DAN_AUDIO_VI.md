# 🎤 Hướng Dẫn Xử Lý Audio - Quick Guide

## ❓ Câu Hỏi Thường Gặp

### 1. Thư mục Audio ở đâu?

**Trả lời:** Thư mục `Audio/` được tự động tạo trong **mỗi dự án video**:

```
~/Downloads/<Tên-Dự-Án>/Audio/
```

**Ví dụ:**
- Nếu dự án của bạn tên là "2025-11-13-1"
- Thư mục audio sẽ ở: `~/Downloads/2025-11-13-1/Audio/`

### 2. Thoại (audio) có được tạo tự động không?

**Trả lời:** **CÓ**, audio được tạo tự động khi bạn:

1. Tạo kịch bản trong tab **"Video Bán Hàng"**
2. Click nút **"Tạo Video"** cho một cảnh
3. Hệ thống sẽ:
   - ✅ Đọc lời thoại từ kịch bản
   - ✅ Gọi API Text-to-Speech (Google TTS)
   - ✅ Tạo file MP3
   - ✅ Lưu vào thư mục `Audio/`

**File được tạo:** `scene_01_audio.mp3`, `scene_02_audio.mp3`, v.v.

### 3. Làm sao để xem các file audio đã tạo?

**Cách 1: Mở từ ứng dụng**
1. Trong tab "Video Bán Hàng"
2. Click nút **"📂 Mở Thư Mục"**
3. Vào thư mục `Audio/`

**Cách 2: Mở trực tiếp**
```bash
# Mở thư mục dự án
cd ~/Downloads/<Tên-Dự-Án>/Audio/

# Xem danh sách file audio
ls -lh *.mp3

# Nghe file audio (macOS)
afplay scene_01_audio.mp3
```

---

## 📋 Quy Trình Tạo Audio Đầy Đủ

### Bước 1: Tạo Dự Án Mới

1. Mở ứng dụng: `python main_image2video.py`
2. Chọn tab **"Video Bán Hàng"**
3. Nhập tên dự án và thông tin sản phẩm

➜ Thư mục `Audio/` sẽ được tạo tự động

### Bước 2: Tạo Kịch Bản

1. Điền thông tin sản phẩm
2. Click **"Tạo Kịch Bản"**
3. AI sẽ sinh kịch bản với lời thoại cho mỗi cảnh

### Bước 3: Cấu Hình Voice (Tùy Chọn)

**Giọng tiếng Việt khả dụng:**
- `vi-VN-Wavenet-A` - 🇻🇳 **Nam Miền Bắc** (Chất lượng cao)
- `vi-VN-Wavenet-B` - 🇻🇳 **Nữ Miền Bắc** (Chất lượng cao)
- `vi-VN-Wavenet-C` - 🇻🇳 **Nữ Miền Nam** (Chất lượng cao)
- `vi-VN-Wavenet-D` - 🇻🇳 **Nam Miền Nam** (Chất lượng cao)

### Bước 4: Tạo Audio

1. Click **"Tạo Video"** cho một cảnh
2. Xem log trong ứng dụng:
   ```
   🎤 Bắt đầu tạo audio cho cảnh 1...
   ✓ Đã tạo audio cho cảnh 1: /path/to/Audio/scene_01_audio.mp3
   ```
3. File audio đã được lưu!

---

## 🔧 Tạo Audio Thủ Công

Nếu muốn tạo audio riêng, sử dụng script demo:

```bash
cd /home/runner/work/v3/v3
python examples/audio_workflow_demo.py
```

Hoặc viết code Python:

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
            "text": "Nội dung lời thoại của bạn"
        }
    }
}

# Tạo audio
audio_path = generate_scene_audio(
    scene_data=scene_data,
    output_dir="./Audio",
    scene_index=1
)

print(f"Audio đã lưu tại: {audio_path}")
```

---

## 📊 Cấu Trúc Thư Mục Dự Án

```
<Tên-Dự-Án>/
├── Audio/                      ⬅️ THƯ MỤC CHỨA THOẠI
│   ├── scene_01_audio.mp3     (Cảnh 1)
│   ├── scene_02_audio.mp3     (Cảnh 2)
│   ├── scene_03_audio.mp3     (Cảnh 3)
│   └── ...
├── Video/                      (Video clips)
│   ├── scene_01.mp4
│   └── ...
├── Prompt/                     (Kịch bản cảnh)
│   ├── scene_01_prompt.txt
│   └── ...
├── Ảnh xem trước/             (Ảnh preview)
└── nhat_ky_xu_ly.log          (Log file)
```

---

## 🎛️ Tùy Chỉnh Giọng Nói

### Tốc Độ Nói (Speaking Rate)

```python
"prosody": {
    "rate": 1.2   # 1.0 = bình thường, 1.2 = nhanh hơn 20%
}
```

- **0.5** = Rất chậm
- **0.8** = Chậm
- **1.0** = Bình thường (mặc định)
- **1.3** = Nhanh
- **2.0** = Rất nhanh

### Cao Độ Giọng (Pitch)

```python
"prosody": {
    "pitch": +2   # 0 = bình thường, +2 = cao hơn 2 bậc
}
```

- **-10** = Rất trầm
- **-5** = Trầm
- **0** = Bình thường (mặc định)
- **+5** = Cao
- **+10** = Rất cao

---

## ⚠️ Xử Lý Lỗi

### Lỗi 1: Không Tìm Thấy Thư Mục Audio

**Giải pháp:**
```python
from services.sales_video_service import ensure_project_dirs

# Tạo lại thư mục
dirs = ensure_project_dirs("Tên-Dự-Án-Của-Bạn")
print(f"Thư mục Audio: {dirs['audio']}")
```

### Lỗi 2: Audio Không Được Tạo

**Nguyên nhân phổ biến:**
1. ❌ Thiếu Google API key
2. ❌ Kịch bản không có lời thoại
3. ❌ Lỗi kết nối API

**Giải pháp:**

**1. Kiểm tra API key:**
Mở file `config.json` và thêm:
```json
{
  "google_api_keys": ["YOUR_GOOGLE_API_KEY_HERE"]
}
```

**2. Kiểm tra lời thoại:**
Đảm bảo kịch bản có phần `speech` hoặc `voiceover`:
```json
{
  "scene": 1,
  "speech": "Lời thoại cần có ở đây"
}
```

**3. Xem log chi tiết:**
```bash
cat ~/Downloads/<Tên-Dự-Án>/nhat_ky_xu_ly.log | grep -i audio
```

### Lỗi 3: Audio Quality Thấp

**Giải pháp:**
- ✅ Sử dụng **Wavenet voices** thay vì Standard
- ✅ Ví dụ: `vi-VN-Wavenet-A` (Wavenet) thay vì `vi-VN-Standard-A` (Standard)
- ✅ Wavenet cho chất lượng tốt hơn nhưng tốn nhiều quota hơn

---

## 📚 Tài Liệu Chi Tiết

Để biết thêm chi tiết, xem:

1. **[Audio Processing Workflow](./AUDIO_PROCESSING_WORKFLOW.md)** - Hướng dẫn đầy đủ (Vietnamese + English)
2. **[TTS Service](./TTS_SERVICE.md)** - Chi tiết về TTS API
3. **Demo Script:** `python examples/audio_workflow_demo.py`

---

## 💡 Tips Hữu Ích

### 1. Kiểm Tra Audio Đã Tạo

```bash
# Đếm số file audio
ls ~/Downloads/<Dự-Án>/Audio/*.mp3 | wc -l

# Xem kích thước file
ls -lh ~/Downloads/<Dự-Án>/Audio/

# Nghe tất cả audio (macOS)
for file in ~/Downloads/<Dự-Án>/Audio/*.mp3; do
    echo "Playing: $file"
    afplay "$file"
done
```

### 2. Sao Lưu Audio

Audio files tốn chi phí API để tạo, nên backup:

```bash
# Backup thư mục Audio
cp -r ~/Downloads/<Dự-Án>/Audio ~/Backups/Audio-$(date +%Y%m%d)
```

### 3. Ghép Audio với Video

Sử dụng **Video Merge Panel** trong ứng dụng:
1. Tab **"Video Merge / Ghép Video"**
2. Chọn video clip
3. Thêm audio từ thư mục `Audio/`
4. Xuất video hoàn chỉnh

---

## 🆘 Cần Trợ Giúp?

**Nếu gặp vấn đề:**
1. Chạy demo script để test: `python examples/audio_workflow_demo.py`
2. Xem log file: `cat ~/Downloads/<Dự-Án>/nhat_ky_xu_ly.log`
3. Đọc tài liệu TTS: [TTS_SERVICE.md](./TTS_SERVICE.md)
4. Mở issue trên GitHub với log chi tiết

---

## 📞 Liên Hệ

- 📧 Email: chamnv-dev@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/panora77956/v3/issues)

---

**Phiên bản:** 1.0  
**Cập nhật:** 2025-11-13  
**Ngôn ngữ:** Tiếng Việt  
**Tác giả:** Video Super Ultra v7 Team
