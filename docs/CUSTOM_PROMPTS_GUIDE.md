# Custom Prompts Guide

## Overview

The system now supports two types of prompts that can be managed through Google Sheets:

1. **Regular Prompts** - Standard prompts for domain/topic combinations
2. **Custom Prompts** - Special prompts with advanced formatting and specific requirements

Both types can be updated from a single Google Sheets document, making it easy to maintain all your prompts in one place.

## Google Sheets Format

### Required Columns

Your Google Sheets must have these columns:

| Column Name | Description | Required |
|-------------|-------------|----------|
| `Domain` | The domain name (e.g., "KHOA HỌC GIÁO DỤC") | ✅ Yes |
| `Topic` | The topic name (e.g., "PANORA - Nhà Tường thuật Khoa học") | ✅ Yes |
| `System Prompt` | The full system prompt text | ✅ Yes |
| `Type` | Set to "custom" for custom prompts, leave empty or "regular" for regular prompts | ⚠️ Optional but recommended |

### Example Sheet Structure

```
Domain              | Topic                    | System Prompt                    | Type
--------------------|--------------------------|----------------------------------|--------
GIÁO DỤC/HACKS     | Mẹo Vặt                 | Bạn là chuyên gia về mẹo vặt...| regular
KHOA HỌC GIÁO DỤC  | PANORA - Nhà Tường thuật| Bạn là Nhà Tường thuật...       | custom
```

## How It Works

### 1. Regular Prompts
- Stored in `services/domain_prompts.py`
- Used for standard video generation
- Single-line format in the generated code
- Accessed via `get_system_prompt(domain, topic)`

### 2. Custom Prompts
- Stored in `services/domain_custom_prompts.py`
- Override regular prompts when present
- Multi-line format with triple quotes
- Support complex formatting with newlines
- Accessed via `get_custom_prompt(domain, topic)`

### Priority System

When generating content, the system checks:
1. First, look for a custom prompt for the domain/topic combination
2. If found, use the custom prompt
3. If not found, fall back to regular prompt or default system prompt

## Updating Prompts from Google Sheets

### Method 1: Using the UI (Recommended)

1. Open the application
2. Go to **Settings** panel
3. Find the **"🔄 Prompts"** section
4. Ensure the Google Sheets URL is correct
5. Click **"⬇ Update"** button
6. Wait for confirmation message

The system will automatically:
- Download data from Google Sheets
- Generate `domain_prompts.py` with regular prompts
- Generate `domain_custom_prompts.py` with custom prompts (if any)
- Display success message with counts

### Method 2: Using Python Script

```python
from services.prompt_updater import update_prompts_file
import os

# Path to the domain_prompts.py file
services_dir = 'services'
prompts_file = os.path.join(services_dir, 'domain_prompts.py')

# Update from default Google Sheets URL
success, message = update_prompts_file(prompts_file)

if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

### Method 3: Using Custom Google Sheets URL

```python
from services.prompt_updater import update_prompts_file

# Path to the domain_prompts.py file
prompts_file = 'services/domain_prompts.py'

# Custom Google Sheets URL
custom_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit?gid=YOUR_GID"

# Update from custom URL
success, message = update_prompts_file(prompts_file, sheet_url=custom_url)

print(message)
```

## Benefits of Custom Prompts

### 1. Advanced Formatting
Custom prompts support:
- Multiple paragraphs
- Bullet points and lists
- Special characters and emojis
- Structured sections (I. II. III.)
- Code-like formatting

### 2. Specialized Requirements
Perfect for domains that need:
- Strict rules and constraints
- Character bibles
- Style guides
- Technical specifications
- Multi-stage instructions

### 3. Easy Management
- Edit in Google Sheets (familiar interface)
- Update both regular and custom prompts together
- Version control through Sheets history
- Team collaboration

## Example: Custom Prompt

Here's an example of a custom prompt in Google Sheets:

**Domain:** KHOA HỌC GIÁO DỤC  
**Topic:** PANORA - Nhà Tường thuật Khoa học  
**Type:** custom  
**System Prompt:**
```
Bạn là Nhà Tường thuật Khoa học (Science Narrator) của kênh PANORA.

I. QUY TẮC TỐI THƯỢNG (TUYỆT ĐỐI CẤM):
CẤM TẠO NHÂN VẬT: Tuyệt đối không được tạo ra nhân vật hư cấu.
BẮT BUỘC DÙNG NGÔI THỨ HAI: Toàn bộ lời thoại (VO) phải nói chuyện trực tiếp với khán giả.

II. CHARACTER BIBLE (KHÓA CỨNG ĐỊNH DANH):
HÌNH ẢNH CỐ ĐỊNH (VISUAL LOCK): Mô phỏng 3D/2D Y tế (FUI/Hologram/Blueprint).

III. CẤU TRÚC & MỤC TIÊU:
MỞ ĐẦU HOOK (0:00 - 0:03): BẮT BUỘC. 3 giây đầu tiên phải là CÂU HỎI SỐC.
```

## Troubleshooting

### Issue: Prompts not updating

**Solutions:**
1. Check internet connection
2. Verify Google Sheets URL is correct
3. Ensure sheet has proper permissions (Anyone with link can view)
4. Check that columns are named exactly: `Domain`, `Topic`, `System Prompt`, `Type`

### Issue: Custom prompts not being used

**Solutions:**
1. Verify `Type` column is set to "custom" (case-insensitive)
2. Check that domain and topic names match exactly
3. Reload the module or restart the application
4. Check logs for custom prompt loading messages

### Issue: JSON parsing errors

**Problem:** "Unterminated string" errors from VertexAI
**Solution:** This has been fixed! The system now automatically:
- Detects unterminated strings in JSON responses
- Escapes literal newlines, tabs, and special characters
- Retries parsing with proper escaping

## Best Practices

1. **Use Regular Prompts for:**
   - Simple instructions
   - General-purpose prompts
   - Short, single-paragraph prompts

2. **Use Custom Prompts for:**
   - Complex multi-section prompts
   - Domain-specific requirements
   - Prompts with special formatting
   - Character bibles and style guides

3. **Organization:**
   - Keep all prompts in one Google Sheet
   - Use clear domain and topic names
   - Document prompt purpose in sheet
   - Use comments in sheet for team notes

4. **Testing:**
   - Test prompts after updating
   - Verify both regular and custom prompts work
   - Check that custom prompts override correctly

## Technical Details

### Files Affected
- `services/domain_prompts.py` - Auto-generated regular prompts
- `services/domain_custom_prompts.py` - Auto-generated custom prompts
- `services/prompt_updater.py` - Update logic and code generation
- `services/llm_story_service.py` - Prompt selection and usage

### Code Generation
- Regular prompts: Single-line strings with escaped quotes
- Custom prompts: Triple-quoted strings preserving formatting
- Both: UTF-8 encoding for Vietnamese and special characters

### Error Handling
- Network timeouts (30 seconds)
- Invalid sheet URLs
- Missing or malformed data
- CSV parsing errors
- File write permissions

## FAQ

**Q: Can I have both regular and custom prompts for the same domain?**  
A: Yes! Different topics in the same domain can be regular or custom.

**Q: What happens if I don't specify the Type column?**  
A: All prompts are treated as regular prompts by default.

**Q: Can I update the Google Sheets URL in the UI?**  
A: Yes! Edit the URL in the Settings panel before clicking Update.

**Q: Do I need to restart the application after updating prompts?**  
A: For the UI, changes take effect after the update. For Python scripts, you may need to reload modules or restart.

**Q: Can custom prompts contain special characters?**  
A: Yes! Custom prompts fully support UTF-8, emojis, and special characters.

## Support

If you encounter issues:
1. Check this guide first
2. Look at the test file: `test_prompt_system.py`
3. Review error messages in console/logs
4. Check Google Sheets format matches requirements
