# Custom Prompts Quick Start

## 🎯 Problem Solved

This PR solves two issues:

1. ✅ **JSON Parsing Error**: "Unterminated string" errors from VertexAI
2. ✅ **Custom Prompts Management**: Update custom prompts via Google Sheets

## 🚀 Quick Start (3 Steps)

### Step 1: Update Your Google Sheets

Add a **"Type"** column to your existing Google Sheets:

```
Domain              | Topic           | System Prompt      | Type
────────────────────────────────────────────────────────────────────
GIÁO DỤC/HACKS     | Mẹo Vặt        | (prompt text)      | regular
KHOA HỌC GIÁO DỤC  | PANORA...      | (custom prompt)    | custom
```

- Set `Type = "custom"` for custom prompts
- Set `Type = "regular"` or leave empty for regular prompts

### Step 2: Update in App

1. Open Settings panel
2. Find "🔄 Prompts" section
3. Click "⬇ Update" button
4. Wait for success message

### Step 3: Done! 🎉

Both files are automatically updated:
- `services/domain_prompts.py` (regular prompts)
- `services/domain_custom_prompts.py` (custom prompts)

## 📝 Example: Vietnamese Custom Prompt

**Domain:** KHOA HỌC GIÁO DỤC  
**Topic:** PANORA - Nhà Tường thuật Khoa học  
**Type:** custom  
**System Prompt:**
```
Bạn là Nhà Tường thuật Khoa học (Science Narrator) của kênh PANORA.

I. QUY TẮC TỐI THƯỢNG (TUYỆT ĐỐI CẤM):
CẤM TẠO NHÂN VẬT: Tuyệt đối không được tạo ra nhân vật hư cấu.
...
```

## 🧪 Test Your Changes

```bash
# Run comprehensive tests
python examples/test_prompt_system.py

# See usage examples
python examples/example_custom_prompt_usage.py
```

Expected output: 🎉 All tests passed!

## 📚 Full Documentation

For complete details, see:
- [Custom Prompts Guide](docs/CUSTOM_PROMPTS_GUIDE.md) - Complete documentation
- [Example Usage](examples/example_custom_prompt_usage.py) - Code examples

## 🎁 Benefits

1. ✨ **Centralized** - All prompts in one Google Sheet
2. 🔄 **Automatic** - Both files update with one click
3. 👥 **Collaborative** - Team can edit together
4. 📝 **Tracked** - Google Sheets version history
5. 🛡️ **Reliable** - Better error handling

## ❓ FAQ

**Q: Do I need to change my existing Google Sheets?**  
A: Just add the "Type" column. Existing prompts work as "regular" by default.

**Q: Can I mix regular and custom prompts?**  
A: Yes! Different topics can be regular or custom.

**Q: What happens to my current custom prompts?**  
A: They remain in `domain_custom_prompts.py`. You can now update them via sheets.

**Q: Does this break existing functionality?**  
A: No! Everything is backward compatible. Regular prompts work exactly as before.

## 🐛 Troubleshooting

**Issue:** Prompts not updating  
**Fix:** Check internet connection and Google Sheets URL

**Issue:** Custom prompts not being used  
**Fix:** Verify Type column is set to "custom" (case-insensitive)

**Issue:** JSON parsing errors  
**Fix:** Already fixed! System now handles unterminated strings automatically.

---

**Need help?** See the full guide: [docs/CUSTOM_PROMPTS_GUIDE.md](docs/CUSTOM_PROMPTS_GUIDE.md)
