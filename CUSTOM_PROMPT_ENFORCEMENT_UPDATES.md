# Custom Prompt Enforcement Updates

## Problem Statement (Vietnamese)

Trong các video được tạo ra bằng custom prompt thì vẫn thấy bị lẫn các nhân vật vào, và đặc biệt là còn lẫn các phần mô tả cảnh vào trong lời thoại.

**Translation**: In videos created with custom prompts, character names are still appearing, and especially scene descriptions are mixing into dialogue/voiceover.

## Root Cause Analysis

The issue occurred because:

1. **Insufficient Separation**: The LLM was not clearly distinguishing between:
   - `voiceover` fields (what the narrator SAYS)
   - `prompt` fields (what viewers SEE on screen)

2. **Weak Enforcement**: The custom prompt enforcement was not strong enough to prevent the LLM from:
   - Creating fictional characters (Anya, Kai, Dr. Sharma)
   - Mixing visual descriptions into voiceover text
   - Using ACT I/II/III structure instead of the required 5-stage structure

3. **Validation Gaps**: The validation function wasn't recognizing Vietnamese prohibition phrases like "CẤM TẠO NHÂN VẬT"

## Solution Implemented

### 1. Enhanced Custom Prompt (`services/domain_custom_prompts.py`)

**Added Critical Separation Section**:
```
VOICEOVER = CHỈ LỜI THOẠI (Dialogue Only)
- Only write what the narrator SAYS
- Use second-person: "Bạn", "Cơ thể của bạn"
- Do NOT describe visuals
- Example WRONG: "Bạn thấy hologram 3D của não bộ với màu cyan"
- Example RIGHT: "Giờ thứ 24. Não của bạn bắt đầu tạo ra ảo giác."

PROMPT = CHỈ MÔ TẢ HÌNH ẢNH (Visual Description Only)
- Only describe what APPEARS on screen
- Do NOT write dialogue
- Example WRONG: "Bạn cảm thấy mệt mỏi"
- Example RIGHT: "3D hologram của não bộ màu cyan, data overlay hiển thị 'Cortisol +200%'"
```

**Added Few-Shot Examples**:
- VÍ DỤ SAI (Wrong Example): Boring list-based narration
- VÍ DỤ ĐÚNG (Right Example): Dramatic narrative in PANORA style

### 2. Strengthened Schema Prompt (`services/llm_story_service.py`)

**Enhanced Enforcement Header**:
```
⚠️⚠️⚠️ CRITICAL ENFORCEMENT RULES - MUST OBEY ⚠️⚠️⚠️
MANDATORY REQUIREMENTS:
- Separate voiceover (SPOKEN) from visual prompts (SEEN)
- IF CUSTOM PROMPT SAYS "NO CHARACTERS" → character_bible MUST be []
- IF CUSTOM PROMPT SAYS "SECOND-PERSON" → Use "Bạn", "You" ONLY
- VOICEOVER = What narrator SAYS (dialogue only)
- PROMPT = What viewer SEES (visuals only)
```

**Updated Field Descriptions**:
```json
{
  "prompt_vi": "CHỈ MÔ TẢ HÌNH ẢNH - Mô tả những gì xuất hiện trên màn hình...",
  "voiceover_vi": "CHỈ LỜI THOẠI - Những gì người tường thuật NÓI..."
}
```

**Added Critical Reminders** (8 key points at end of schema)

### 3. Enhanced Validation (`services/llm_story_service.py`)

**Expanded Forbidden Patterns**:
- Vietnamese names: Anya, Liam, Kai, Mai, Minh, Hoa, Lan, Linh, etc.
- English names: Sharma, Chen, Smith, Johnson, Williams, Brown, Emma, Oliver, etc.
- Titles and roles: Dr., Tiến sĩ, Bác sĩ, Y tá, Nhà khoa học, Chuyên gia
- Character descriptors: nhà khoa học, bệnh nhân, người phụ nữ, người đàn ông
- Appearance descriptions: áo blouse, tóc đen, kính gọng, quần áo
- Lab/office with people: phòng thí nghiệm với, phòng lab có, người đứng
- ACT structure: ACT I, ACT II, ACT III, Scene \d+:

**Fixed Vietnamese Detection**:
```python
prohibits_characters = any([
    "no character" in custom_lower,
    "cấm tạo nhân vật" in custom_lower,  # Now detects Vietnamese
    "không tạo nhân vật" in custom_lower,
    "character_bible = []" in custom_prompt,
])
```

## Testing

### Test 1: Custom Prompt Loading
```bash
python3 examples/example_custom_prompt_usage.py
```
✅ All required sections present in custom prompt

### Test 2: Validation Function
```python
from services.llm_story_service import _validate_no_characters

# Valid script (no characters)
valid_script = {
    "character_bible": [],
    "voiceover_vi": "Sau 24 giờ, não của bạn bắt đầu tạo ra ảo giác."
}
✅ Passes validation

# Invalid script (has character 'Anya')
invalid_script = {
    "character_bible": [{"name": "Anya"}],
    "voiceover_vi": "Anya cảm thấy mệt mỏi"
}
❌ Fails validation (as expected)
```

## Expected Results

With these enhancements, videos generated with PANORA custom prompt should:

✅ **NOT** contain fictional characters (Anya, Kai, Dr. Sharma, etc.)
✅ **NOT** mix scene descriptions into voiceover text
✅ **USE** second-person narration only (Bạn, Cơ thể của bạn, Não của bạn)
✅ **FOLLOW** 5-stage structure (VẤN ĐỀ → PHẢN ỨNG → LEO THANG → GIỚI HẠN → TOÀN CẢNH)
✅ **SEPARATE** voiceover (dialogue) from visual descriptions

## How to Update Google Sheets

If you manage prompts through Google Sheets:

1. Add/update the PANORA prompt with Type="custom"
2. Include the enhanced prompt with CRITICAL SEPARATION section
3. Click "Update Prompts" in the app
4. The system will automatically:
   - Update `domain_prompts.py` (regular prompts)
   - Update `domain_custom_prompts.py` (custom prompts)
   - Apply new enforcement rules

## Troubleshooting

If violations still occur after updating:

1. **Check the custom prompt loaded**:
   ```python
   from services.domain_custom_prompts import get_custom_prompt
   prompt = get_custom_prompt("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học")
   assert "CRITICAL SEPARATION" in prompt
   ```

2. **Check logs for custom prompt usage**:
   ```
   [INFO] Using CUSTOM system prompt for KHOA HỌC GIÁO DỤC/PANORA - Nhà Tường thuật Khoa học
   ```

3. **Run validation manually**:
   ```python
   from services.llm_story_service import _validate_no_characters
   is_valid, warning = _validate_no_characters(script_data, domain, topic)
   if not is_valid:
       print(warning)
   ```

4. **Regenerate the video** with the updated prompt

## Files Changed

1. `services/domain_custom_prompts.py` - Enhanced PANORA custom prompt
2. `services/llm_story_service.py` - Strengthened enforcement and validation
3. `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md` - Updated documentation
4. `CUSTOM_PROMPT_ENFORCEMENT_UPDATES.md` - This file (developer reference)

## References

- Original Problem: Videos with PANORA custom prompt still have characters and mixed descriptions
- Solution: Stronger enforcement, clearer separation, enhanced validation
- Documentation: See `PANORA_CUSTOM_PROMPT_FOR_GOOGLE_SHEET.md` for user guide
