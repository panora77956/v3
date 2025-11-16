# PANORA Custom Prompt - Hướng Dẫn Cập Nhật (Update Instructions)

## 🎯 Vấn Đề Đã Được Giải Quyết

✅ Video không còn bị lẫn tên nhân vật (Anya, Kai, Dr. Sharma)
✅ Mô tả cảnh không còn bị trộn vào lời thoại
✅ Tuân thủ chặt chẽ ngôi thứ hai và cấu trúc 5 giai đoạn

## 🆕 Cập Nhật Mới Nhất (v7.4.1)

### ✨ Giải Quyết Vấn Đề Cập Nhật Từ Google Sheet

**Vấn đề trước đây**: Khi cập nhật custom prompt từ Google Sheet, các cải tiến từ PR #95 (CRITICAL SEPARATION, few-shot examples) bị mất vì `domain_custom_prompts.py` bị ghi đè.

**Giải pháp mới**: 
- ✅ Hệ thống TỰ ĐỘNG thêm các cải tiến PR #95 vào PANORA custom prompt
- ✅ Bạn có thể thoải mái cập nhật base prompt từ Google Sheet
- ✅ Các enhancement (CRITICAL SEPARATION, few-shot examples) vẫn được giữ lại
- ✅ Logic enhancement nằm trong code, không bị ghi đè

**Cách hoạt động**:
- Khi load PANORA custom prompt, hệ thống gọi `_enhance_panora_custom_prompt()`
- Function này tự động thêm CRITICAL SEPARATION và few-shot examples
- Enhancements được inject vào runtime, không lưu trong file

**Lợi ích**:
- Bạn chỉ cần maintain base prompt trong Google Sheet
- Enhancements được quản lý trong code (dễ maintain, version control)
- Update từ Google Sheet không làm mất các fix từ PR #95

## 🚀 Cách Áp Dụng Ngay (Quick Start)

### Bước 1: Cập Nhật Code (Nếu cần)

Nếu bạn đang dùng phiên bản cũ, pull code mới nhất:

```bash
cd /home/runner/work/v3/v3
git pull origin main
```

### Bước 2: Không Cần Làm Gì Thêm!

✨ **Enhancements được tự động áp dụng** trong runtime!

Khi tạo video với PANORA, hệ thống sẽ:
- ✅ Load base custom prompt từ `domain_custom_prompts.py` (có thể từ Google Sheet)
- ✅ TỰ ĐỘNG thêm CRITICAL SEPARATION guidelines
- ✅ TỰ ĐỘNG thêm few-shot examples (VÍ DỤ SAI vs ĐÚNG)
- ✅ TỰ ĐỘNG thêm final warnings và prohibitions

### Bước 3: Tạo Video Mới

Khi tạo video với domain/topic PANORA, hệ thống sẽ:
1. Tự động load custom prompt từ file hoặc Google Sheet
2. Tự động enhance với CRITICAL SEPARATION và examples
3. Áp dụng enforcement rules nghiêm ngặt
4. Validate output để phát hiện vi phạm

## 📝 Nếu Quản Lý Prompt Qua Google Sheet

**✨ THAY ĐỔI QUAN TRỌNG**: Giờ đây bạn chỉ cần maintain BASE PROMPT trong Google Sheet!

### Bước 1: Mở Google Sheet

Mở sheet của bạn (ví dụ: https://docs.google.com/spreadsheets/d/...)

### Bước 2: Cập Nhật BASE PANORA Prompt

Tìm dòng:
- Domain: `KHOA HỌC GIÁO DỤC`
- Topic: `PANORA - Nhà Tường thuật Khoa học`
- Type: `custom`

### Bước 3: Chỉ Cần Viết Base Prompt

**KHÔNG CẦN** copy toàn bộ prompt dài từ file code nữa!

Chỉ cần viết base prompt, ví dụ:

```
Bạn là Nhà Tường thuật Khoa học (Science Narrator) của kênh PANORA.

I. QUY TẮC TỐI THƯỢNG (BẮT BUỘC):
- CẤM TẠO NHÂN VẬT: Không dùng tên riêng (Anya, Kai)
- BẮT BUỘC NGÔI THỨ HAI: Toàn bộ lời thoại dùng "Bạn", "Cơ thể của bạn"
- CẤM DÙNG DÀN Ý BÊN NGOÀI: Tuân thủ CẤU TRÚC 5 GIAI ĐOẠN

II. VISUAL IDENTITY:
- Phong cách: Mô phỏng 3D/2D Y tế (Hologram)
- Màu sắc: Nền Đen/Navy, Hologram Cyan, Điểm nhấn Cam

III. CẤU TRÚC 5 GIAI ĐOẠN:
1. VẤN ĐỀ - Hook 3 giây
2. PHẢN ỨNG - Cơ thể "chiến đấu"
3. LEO THANG - Triệu chứng xuất hiện
4. GIỚI HẠN - Cao trào kịch tính
5. TOÀN CẢNH - Giải thích khoa học
```

**Hệ thống sẽ TỰ ĐỘNG thêm:**
- ✅ CRITICAL SEPARATION (Voiceover vs Visual)
- ✅ Few-shot examples (VÍ DỤ SAI vs ĐÚNG)
- ✅ Character prohibitions chi tiết
- ✅ Final warnings

### Bước 4: Cập Nhật Trong App

1. Mở Settings panel trong app
2. Tìm phần "🔄 Prompts"
3. Click "⬇ Update" button
4. Đợi thông báo thành công

**Lưu ý**: Các enhancements sẽ được thêm tự động khi chạy, không cần viết trong Google Sheet!

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
