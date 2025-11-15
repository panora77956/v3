# PANORA Custom Prompt - Hướng Dẫn Cập Nhật (Update Instructions)

## 🎯 Vấn Đề Đã Được Giải Quyết

✅ Video không còn bị lẫn tên nhân vật (Anya, Kai, Dr. Sharma)
✅ Mô tả cảnh không còn bị trộn vào lời thoại
✅ Tuân thủ chặt chẽ ngôi thứ hai và cấu trúc 5 giai đoạn

## 🚀 Cách Áp Dụng Ngay (Quick Start)

### Bước 1: Cập Nhật Code (Nếu cần)

Nếu bạn đang dùng phiên bản cũ, pull code mới nhất:

```bash
cd /home/runner/work/v3/v3
git pull origin main
```

### Bước 2: Không Cần Làm Gì Thêm!

✨ **Custom prompt đã được tự động cập nhật** trong code!

File `services/domain_custom_prompts.py` đã có prompt mới với:
- ✅ Phân tách rõ ràng voiceover và visual
- ✅ Ví dụ cụ thể về đúng/sai
- ✅ Enforcement mạnh mẽ hơn

### Bước 3: Tạo Video Mới

Khi tạo video với domain/topic PANORA, hệ thống sẽ:
1. Tự động load custom prompt đã cải tiến
2. Áp dụng enforcement rules nghiêm ngặt
3. Validate output để phát hiện vi phạm

## 📝 Nếu Quản Lý Prompt Qua Google Sheet

Nếu bạn đang cập nhật prompt qua Google Sheet:

### Bước 1: Mở Google Sheet

Mở sheet của bạn (ví dụ: https://docs.google.com/spreadsheets/d/...)

### Bước 2: Cập Nhật PANORA Prompt

Tìm dòng:
- Domain: `KHOA HỌC GIÁO DỤC`
- Topic: `PANORA - Nhà Tường thuật Khoa học`
- Type: `custom`

### Bước 3: Copy Prompt Mới

Copy toàn bộ nội dung từ `services/domain_custom_prompts.py` (dòng 21-108) vào cột "System Prompt" trong Google Sheet.

**Hoặc** copy từ file `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md` (dòng 34-166).

### Bước 4: Cập Nhật Trong App

1. Mở Settings panel trong app
2. Tìm phần "🔄 Prompts"
3. Click "⬇ Update" button
4. Đợi thông báo thành công

## 🔍 Kiểm Tra Đã Cập Nhật Thành Công

Chạy test script:

```bash
python3 examples/example_custom_prompt_usage.py
```

Bạn sẽ thấy:
```
✅ Custom prompt FOUND!
First 200 characters:
------------------------------------------------------------
═══════════════════════════════════════════════════════════════
⚠️ PANORA SCIENCE NARRATOR - CRITICAL RULES ⚠️
═══════════════════════════════════════════════════════════════
```

## ✅ Kết Quả Mong Đợi

Sau khi cập nhật, video PANORA sẽ:

### ✅ KHÔNG CÒN (Fixed):
- ❌ Tên nhân vật: Anya, Kai, Liam, Dr. Sharma
- ❌ Mô tả người: "nhà khoa học", "bệnh nhân", "áo blouse trắng"
- ❌ Cấu trúc ACT I/II/III
- ❌ Mô tả cảnh trong lời thoại: "Bạn thấy hologram 3D màu cyan hiển thị..."

### ✅ SẼ CÓ (Correct):
- ✅ Ngôi thứ hai: "Bạn", "Cơ thể của bạn", "Não của bạn"
- ✅ Cấu trúc 5 giai đoạn: VẤN ĐỀ → PHẢN ỨNG → LEO THANG → GIỚI HẠN → TOÀN CẢNH
- ✅ Voiceover riêng: "Sau 24 giờ, não của bạn bắt đầu tạo ra ảo giác"
- ✅ Visual riêng: "3D hologram của não bộ màu cyan, data overlay 'Cortisol +200%'"

## 🆘 Nếu Vẫn Còn Vấn Đề

### Vấn đề 1: Vẫn thấy tên nhân vật

**Nguyên nhân**: Video được tạo trước khi cập nhật

**Giải pháp**: 
- Xóa video cũ
- Tạo lại video mới với prompt đã cập nhật

### Vấn đề 2: Mô tả cảnh vẫn lẫn vào lời thoại

**Nguyên nhân**: Custom prompt chưa load đúng

**Giải pháp**:
1. Kiểm tra log xem có dòng: `[INFO] Using CUSTOM system prompt for KHOA HỌC GIÁO DỤC/PANORA`
2. Nếu không có, kiểm tra domain/topic có đúng không
3. Chạy lại test script để verify

### Vấn đề 3: Validation báo lỗi nhưng không thấy vấn đề

**Nguyên nhân**: Validation quá nghiêm ngặt (false positive)

**Giải pháp**:
- Đọc warning message để xem field nào bị phát hiện
- Kiểm tra xem có phải từ hợp lệ bị nhầm không (ví dụ: "Hoa học" vs tên "Hoa")
- Nếu là false positive, có thể bỏ qua warning

## 📚 Tài Liệu Tham Khảo

- **User Guide**: `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md`
- **Developer Reference**: `CUSTOM_PROMPT_ENFORCEMENT_UPDATES.md`
- **Example Code**: `examples/example_custom_prompt_usage.py`
- **Quick Start**: `CUSTOM_PROMPTS_QUICKSTART.md`

## 📞 Liên Hệ

Nếu có vấn đề khác, vui lòng:
1. Kiểm tra log output khi tạo video
2. Chạy test script để verify custom prompt
3. Xem documentation chi tiết trong các file trên
4. Mở issue trên GitHub với log và example output

---

**Version**: v7.4.0  
**Update Date**: 2025-11-15  
**Status**: ✅ Production Ready
