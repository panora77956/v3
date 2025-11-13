# PANORA No-Character Fix - Documentation

## Problem Statement

After PR #47, the text2video scenario generation was creating fictional characters (Dr. An, KAI, The Architect) despite the PANORA Science Narrator system prompt explicitly forbidding this.

### Example of Incorrect Output (Before Fix):
```
- Dr. An [Nữ khoa học gia thần kinh hàng đầu, người bị ám ảnh bởi hiện tượng Deja Vu.]: 
  key_trait=Trí tuệ sắc bén, kiên định, dễ bị tổn thương bởi áp lực.
  motivation=Giải mã bí ẩn Deja Vu, chứng minh sự tồn tại của một thực tại khác.
  visual=Khuôn mặt thanh tú nhưng đôi mắt mệt mỏi, tóc đen dài buộc gọn gàng...
```

### PANORA System Prompt Requirements:
1. **CẤM TẠO NHÂN VẬT** (PROHIBIT CHARACTER CREATION) - Don't create fictional characters, don't use names
2. **CẤM MÔ TẢ HƯ CẤU** (PROHIBIT FICTIONAL DESCRIPTIONS) - Don't describe clothes, labs, hairstyles
3. **BẮT BUỘC DÙNG NGÔI THỨ HAI** (MUST USE SECOND PERSON) - All narration must address audience directly ("You", "Your body", "Your brain")

## Root Cause Analysis

The `_schema_prompt()` function in `services/llm_story_service.py` was **always** including character-related instructions and JSON schema fields, regardless of the domain-specific system prompt rules.

### Issues Found:
1. ❌ Character Bible section was **always** included in base_rules
2. ❌ JSON schema **always** required `character_bible` and `character_bible_tgt` fields  
3. ❌ Scene schema **always** required `characters` array with character names
4. ❌ Dialogue schema **always** included `speaker` field expecting character names

## Solution Implemented

### 1. Added Domain Detection
```python
# Check if domain requires no-character narration
no_character_domains = [
    ("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học"),
]
requires_no_characters = (domain, topic) in no_character_domains if domain and topic else False
```

### 2. Conditional Base Rules

**For PANORA (no characters):**
```python
**VOICEOVER NARRATION**: Use second-person narration addressing the audience
- NO character names or fictional personas
- NO dialogue between characters
- Scene descriptions focus on visual elements only
```

**For Other Domains (with characters):**
```python
**CHARACTER BIBLE** (2-4 characters):
- key_trait: Core personality
- motivation: Deep drive
- visual_identity: Detailed appearance
```

### 3. Conditional JSON Schema

**PANORA Schema (no character_bible):**
```json
{
  "title_vi": "...",
  "outline_vi": "...",
  "screenplay_vi": "Screenplay with VOICEOVER narration in second person...",
  "scenes": [
    {
      "voiceover_vi": "Lời thoại ngôi thứ hai",
      "voiceover_tgt": "Second-person narration",
      "visual_elements": ["hologram", "data overlay", "3D simulation"],
      // NO "characters" field
      // NO "dialogues" field with "speaker"
    }
  ]
  // NO "character_bible" field
}
```

**Standard Schema (with character_bible):**
```json
{
  "character_bible": [...],
  "scenes": [
    {
      "characters": ["Character names with visual_identity"],
      "dialogues": [{"speaker":"Name", "text_vi":"..."}]
    }
  ]
}
```

## How to Use

### For Content Creators

When creating a PANORA science video:

1. **Select Domain**: "KHOA HỌC GIÁO DỤC"
2. **Select Topic**: "PANORA - Nhà Tường thuật Khoa học"
3. **Enter Idea**: E.g., "Điều gì xảy ra khi bạn không ngủ trong 24 giờ?"
4. **Generate**: The script will now use:
   - ✅ Second-person narration ("Bạn", "Cơ thể của bạn")
   - ✅ Visual descriptions (holograms, medical simulations)
   - ✅ NO character names or personas
   - ✅ NO fictional scenarios with characters

### For Developers

To add more no-character domains:

```python
# In services/llm_story_service.py, function _schema_prompt()
no_character_domains = [
    ("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học"),
    ("YOUR_DOMAIN", "YOUR_TOPIC"),  # Add here
]
```

## Testing

Run validation tests:
```bash
python3 /tmp/test_panora_fix.py
```

Expected output:
```
✓ PASS: PANORA domain should require no characters
✓ PASS: Comedy domain should allow characters
✓ PASS: Coding domain should allow characters
✓ ALL TESTS PASSED!
```

## Verification Checklist

Before merging, verify:

- [ ] PANORA domain generates NO character names (Dr. An, KAI, etc.)
- [ ] PANORA domain uses second-person narration ("You", "Your body")
- [ ] PANORA domain has voiceover_vi/voiceover_tgt instead of dialogues
- [ ] PANORA domain has visual_elements array for scientific visualizations
- [ ] Other domains (Comedy, Coding, etc.) still generate characters normally
- [ ] character_bible is only present for character-based domains
- [ ] Debug logging shows correct domain/topic detection

## Impact

✅ **PANORA domain**: Now correctly generates voiceover-only content with no characters
✅ **Other domains**: Unaffected, continue to generate character-based stories
✅ **Backward compatible**: Existing functionality preserved for non-PANORA domains
✅ **Extensible**: Easy to add more no-character domains in the future

## Files Modified

- `services/llm_story_service.py`
  - Added `requires_no_characters` flag detection
  - Split `base_rules` into conditional versions
  - Split JSON `schema` into conditional versions
  - Added debug logging for domain/topic selection

## Related

- PR #47: Initial system prompt addition (didn't enforce schema changes)
- Issue: "tab text2video: Bạn xem lại việc áp dụng đúng chỉ thị từ system prompt nhé..."
