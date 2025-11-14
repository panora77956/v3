# 📋 Tóm Tắt: Fix PANORA Custom Prompt Issue

## Vấn Đề Ban Đầu

Khi sử dụng custom prompt "PANORA - Nhà Tường thuật Khoa học", LLM vẫn tạo ra:
- ❌ Nhân vật hư cấu: Dr. Anya Sharma, Liam, Dr. Chen
- ❌ Cấu trúc ACT I/II/III
- ❌ Mô tả ngoại hình: áo blouse, tóc đen, kính gọng kim loại

**Lý do**: Prompt quá yếu, LLM không tuân thủ rules.

---

## Câu Hỏi Của Bạn (Comment #3531439735)

### Q1: Khi tôi cập nhật từ Google Sheet, các prompt được cập nhật vào đâu?

**Trả lời**: 
```
Google Sheet 
    ↓
prompt_updater.py (đọc cột "Type")
    ↓
├─ Type="custom" → domain_custom_prompts.py
└─ Type=""       → domain_prompts.py (merged với custom)
```

Cả 2 files đều được **GHI ĐÈ HOÀN TOÀN** khi bạn cập nhật.

### Q2: Có cập nhật riêng vào domain_prompts và domain_custom_prompts không?

**Trả lời**: Có, nhưng từ CÙNG 1 Google Sheet:
- Cột **Type="custom"** → `domain_custom_prompts.py` (chỉ custom)
- Cột **Type=""** hoặc không có → `domain_prompts.py` (merged tất cả)

### Q3: Bạn dùng keyword "panora"? Nếu không có keyword thì sao?

**Trả lời**: KHÔNG dùng keyword!

Matching dựa vào:
```python
(domain, topic) == ("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học")
```

Chỉ cần Domain + Topic khớp, không cần keyword "panora" trong prompt.

---

## Giải Pháp Đã Thực Hiện

### ✅ Commits

1. **f5d2cd0**: Strengthen PANORA custom prompt
   - Enhanced schema với rules mạnh hơn
   - Visual formatting (⚠️, ❌, ✅)
   - Ví dụ đúng/sai rõ ràng

2. **15b3a79**: Add validation function
   - `_validate_no_characters()` để detect violations
   - Scan forbidden patterns: names, titles, ACT structure
   - Warning với chi tiết violations

3. **d932394**: Add Google Sheet integration guide
   - `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md` (250+ lines)
   - Complete enhanced prompt ready to copy
   - Step-by-step instructions

4. **7c59d66**: Add quick start guide
   - `QUICK_START_GOOGLE_SHEET_INTEGRATION.md` (TL;DR)
   - Visual flow diagrams
   - FAQ section

### ✅ Files Changed

- `services/llm_story_service.py` (+333 lines)
  - Strengthened schema for custom prompts
  - Added validation function
  
- `services/domain_custom_prompts.py` (+10 lines)
  - Added auto-generation warning
  - Links to guide files

- `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md` (NEW)
  - Detailed migration guide
  - Complete enhanced prompt text
  
- `QUICK_START_GOOGLE_SHEET_INTEGRATION.md` (NEW)
  - Quick reference
  - Visual diagrams

---

## Trạng Thái Hiện Tại

### ✅ Đã Hoạt Động (Tạm Thời)

Enhanced PANORA prompt đã được hardcode trong `domain_custom_prompts.py`.

**Ưu điểm**: Hoạt động NGAY BÂY GIỜ
**Nhược điểm**: Sẽ **BỊ MẤT** khi bạn "Cập nhật từ Google Sheet"

### ⚠️ Hành Động Cần Thiết (Để Giữ Lâu Dài)

Để prompt không bị mất khi update:

1. Mở file: `QUICK_START_GOOGLE_SHEET_INTEGRATION.md`
2. Làm theo 3 bước đơn giản
3. ✅ Prompt sẽ được đồng bộ tự động mãi mãi

---

## Cách Chọn

| Nếu bạn... | Thì... |
|------------|--------|
| **Không bao giờ** cập nhật từ Google Sheet | ✅ Không cần làm gì, dùng prompt hiện tại |
| **Thỉnh thoảng** cập nhật từ Google Sheet | ⚠️ Cần migrate vào Google Sheet |
| **Thường xuyên** cập nhật từ Google Sheet | ❌ PHẢI migrate ngay, không prompt sẽ mất |

---

## Kiểm Tra Nhanh

### Test Custom Prompt Loaded

```bash
cd /home/runner/work/v3/v3
python3 << 'EOF'
from services.domain_custom_prompts import get_custom_prompt

prompt = get_custom_prompt("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học")

if prompt and "CẤM TẠO NHÂN VẬT" in prompt:
    print("✅ Enhanced PANORA prompt is active!")
    print(f"   Prompt length: {len(prompt)} characters")
else:
    print("❌ Custom prompt not found or incomplete")
EOF
```

### Test Validation Function

```bash
python3 << 'EOF'
from services.llm_story_service import _validate_no_characters

# Test with bad script (has characters)
bad_script = {
    "character_bible": [{"name": "Anya"}],
    "title_vi": "Story of Dr. Anya",
    "scenes": []
}

valid, warning = _validate_no_characters(
    bad_script, 
    "KHOA HỌC GIÁO DỤC", 
    "PANORA - Nhà Tường thuật Khoa học"
)

if not valid:
    print("✅ Validation working - detected violations!")
    print(f"   Found issues in validation")
else:
    print("❌ Validation should have failed")
EOF
```

---

## Tài Liệu Tham Khảo

1. **Quick Start** (đọc đầu tiên):
   - `QUICK_START_GOOGLE_SHEET_INTEGRATION.md`
   - 5 phút đọc
   - Visual diagrams

2. **Detailed Guide** (khi cần migrate):
   - `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md`
   - 15 phút đọc
   - Step-by-step với screenshots

3. **Code Reference**:
   - `services/prompt_updater.py` - Logic cập nhật
   - `services/llm_story_service.py` - Schema và validation
   - `services/domain_custom_prompts.py` - Custom prompts

---

## Liên Hệ

Nếu có vấn đề:
1. Check `QUICK_START_GOOGLE_SHEET_INTEGRATION.md` FAQ
2. Test validation như bên trên
3. Đảm bảo cột "Type" trong Google Sheet là `custom` (chữ thường)

---

## Kết Luận

✅ **Fixed**: PANORA custom prompt bây giờ có NO CHARACTER rules mạnh mẽ
✅ **Documented**: Complete migration guide cho Google Sheet
✅ **Validated**: Có validation function để detect violations
✅ **Tested**: All syntax checks và functional tests passed

⚠️ **Action Required**: Migrate enhanced prompt to Google Sheet để giữ lâu dài

**Commits**: f5d2cd0 → 15b3a79 → d932394 → 7c59d66
