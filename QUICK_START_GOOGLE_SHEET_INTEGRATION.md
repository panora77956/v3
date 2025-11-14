# 🚀 Quick Start: Google Sheet Integration

## TL;DR

Khi bạn cập nhật từ Google Sheet, file `domain_custom_prompts.py` sẽ **BỊ GHI ĐÈ**.

**Giải pháp**: Thêm enhanced prompt vào Google Sheet với `Type=custom`

---

## Bảng So Sánh

| Cách | Ưu điểm | Nhược điểm |
|------|---------|------------|
| **Hardcode trong repo** | ✅ Nhanh, không cần Google Sheet | ❌ Bị ghi đè khi update từ Sheet<br>❌ Không đồng bộ<br>❌ Phải commit code |
| **Thêm vào Google Sheet** ✅ | ✅ Single source of truth<br>✅ Tự động đồng bộ<br>✅ Không cần code | ⚠️ Cần thêm 1 dòng vào Sheet |

---

## 3 Bước Đơn Giản

### Bước 1: Tìm dòng PANORA trong Google Sheet

```
Domain: KHOA HỌC GIÁO DỤC
Topic: PANORA - Nhà Tường thuật Khoa học
```

### Bước 2: Thêm cột "Type"

```
Type: custom    ← QUAN TRỌNG: Phải là "custom" (chữ thường)
```

### Bước 3: Copy enhanced prompt

Mở file `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md` và copy toàn bộ prompt vào cột "System Prompt"

---

## Cách Hệ Thống Hoạt Động

```
┌─────────────────────────────────────────────────────┐
│           Google Sheet (Single Source)              │
│                                                      │
│  Domain  │  Topic  │  Type   │  System Prompt      │
│  ───────┼─────────┼─────────┼─────────────────     │
│  KHOA... │ PANORA  │ custom  │ ⚠️ Enhanced...      │
│  KHOA... │ Hóa học │         │ Regular prompt      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   prompt_updater.py           │
         │   (Fetch & Parse)             │
         └───────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────────┐      ┌─────────────────────┐
│ domain_prompts.py   │      │domain_custom_       │
│ (All merged)        │      │prompts.py           │
│                     │      │(Custom only)        │
│ - Regular prompts   │      │                     │
│ - Custom prompts    │      │ - PANORA enhanced   │
└─────────────────────┘      └─────────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
         ┌───────────────────────────────┐
         │   llm_story_service.py        │
         │   Checks custom first ↑       │
         │   Then fallback to regular    │
         └───────────────────────────────┘
```

---

## Matching Logic

```python
# Không dựa vào keyword "panora" hay "PANORA"
# Chỉ dựa vào cặp (Domain, Topic)

if (domain, topic) == ("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học"):
    # Sử dụng custom prompt với enhanced rules
    # ✅ NO CHARACTER rules được áp dụng
```

---

## Kiểm Tra Nhanh

Sau khi cập nhật từ Google Sheet:

```bash
# Check if custom prompt loaded
python3 -c "
from services.domain_custom_prompts import get_custom_prompt
p = get_custom_prompt('KHOA HỌC GIÁO DỤC', 'PANORA - Nhà Tường thuật Khoa học')
print('✅ OK' if p and 'CẤM TẠO NHÂN VẬT' in p else '❌ FAIL')
"
```

---

## FAQ

**Q: Tại sao không hardcode luôn trong repo?**
A: Vì khi bạn "Cập nhật từ Google Sheet", file `domain_custom_prompts.py` sẽ bị **GHI ĐÈ HOÀN TOÀN**. Mọi thay đổi hardcode sẽ **MẤT**.

**Q: Nếu tôi không update từ Google Sheet?**
A: Prompt hiện tại (hardcoded) vẫn hoạt động. Nhưng bạn sẽ không thể cập nhật các prompt khác.

**Q: Type column phải viết như thế nào?**
A: Phải là `custom` (chữ thường). Không phải `Custom`, `CUSTOM`, hoặc `Custom prompt`.

**Q: Nếu không có cột Type?**
A: Hệ thống xem như regular prompt và merge vào `domain_prompts.py`.

**Q: Có thể có nhiều custom prompts?**
A: Có! Mỗi dòng với `Type=custom` sẽ được xử lý riêng.

---

## Xem Thêm

- **Chi tiết**: `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md`
- **Code**: `services/prompt_updater.py` (lines 88-96)
