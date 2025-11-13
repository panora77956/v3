# 🎤 Audio / Thoại - Quick Reference

## ❓ Câu Hỏi: "Tôi không thấy thư mục audio?"

### ✅ Trả Lời Ngắn Gọn

1. **Thư mục Audio ở đâu?**  
   👉 `~/Downloads/<Tên-Dự-Án>/Audio/`

2. **Audio có được tạo không?**  
   👉 **CÓ**, tự động khi click "Tạo Video"

3. **Làm sao xem audio files?**  
   👉 Mở thư mục dự án → vào folder `Audio/`

---

## 📁 Cấu Trúc Thư Mục

```
<Tên-Dự-Án>/
├── Video/
├── Prompt/
├── Ảnh xem trước/
└── Audio/              ⬅️ THƯ MỤC CHỨA THOẠI
    ├── scene_01_audio.mp3
    ├── scene_02_audio.mp3
    └── scene_03_audio.mp3
```

---

## 🎬 Quy Trình Tạo Audio

```
1. Tạo Dự Án
   ↓
2. Tạo Kịch Bản (AI sinh lời thoại)
   ↓
3. Click "Tạo Video"
   ↓
4. Audio tự động được tạo
   ↓
5. File lưu tại: Audio/scene_XX_audio.mp3
```

---

## 🎤 Giọng Tiếng Việt

- `vi-VN-Wavenet-A` - 🇻🇳 Nam Miền Bắc (chất lượng cao)
- `vi-VN-Wavenet-B` - 🇻🇳 Nữ Miền Bắc (chất lượng cao)
- `vi-VN-Wavenet-C` - 🇻🇳 Nữ Miền Nam (chất lượng cao)
- `vi-VN-Wavenet-D` - 🇻🇳 Nam Miền Nam (chất lượng cao)

---

## 🚀 Demo Nhanh

```bash
# Chạy demo script
python examples/audio_workflow_demo.py

# Xem file audio trong dự án
ls ~/Downloads/<Dự-Án>/Audio/

# Nghe audio (macOS)
afplay ~/Downloads/<Dự-Án>/Audio/scene_01_audio.mp3
```

---

## 📚 Tài Liệu Chi Tiết

Xem tài liệu đầy đủ tại:

1. **[Audio Processing Workflow](docs/AUDIO_PROCESSING_WORKFLOW.md)**  
   Hướng dẫn đầy đủ (English + Vietnamese)

2. **[Hướng Dẫn Audio VI](docs/HUONG_DAN_AUDIO_VI.md)**  
   Quick guide tiếng Việt

3. **[Audio Folder Explanation](docs/AUDIO_FOLDER_EXPLANATION.md)**  
   Giải thích chi tiết về thư mục Audio

4. **[TTS Service](docs/TTS_SERVICE.md)**  
   Chi tiết về TTS API

---

## ⚠️ Xử Lý Lỗi

### Không thấy thư mục Audio?

```python
from services.sales_video_service import ensure_project_dirs
dirs = ensure_project_dirs("Tên-Dự-Án")
print(f"Audio folder: {dirs['audio']}")
```

### Audio không được tạo?

1. Kiểm tra API key trong `config.json`
2. Kiểm tra lời thoại trong kịch bản
3. Xem log: `cat ~/Downloads/<Dự-Án>/nhat_ky_xu_ly.log`

---

## 💡 Tips

- ✅ Audio tự động tạo khi bạn tạo video
- ✅ File format: MP3, 128kbps, 24000Hz
- ✅ Tên file: `scene_XX_audio.mp3`
- ✅ Có thể tùy chỉnh tốc độ và cao độ giọng
- ✅ Backup audio files để tái sử dụng

---

**Cần trợ giúp?** Xem docs hoặc chạy `python examples/audio_workflow_demo.py`
