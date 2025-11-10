# Character Consistency & Scene Continuity Enhancement

## Overview

This document describes the comprehensive enhancements made to the video generation system to address three critical issues:

1. **Scene Continuity** - Scenes now have better narrative continuity and are easier to assemble into complete videos
2. **Style Consistency** - Video styles are maintained consistently across all scenes
3. **Character Consistency** - Character appearance, clothing, accessories, and weapons remain consistent across scenes

## Problem Statement (Vietnamese Translation)

The original problem statement identified:

1. **Các cảnh trong video không có sự nối tiếp nhau về mặt nội dung** - Video scenes don't have continuity in content, making them very messy and difficult to assemble into a complete video.

2. **Phong cách video ở các cảnh thi thoảng vẫn bị lẫn các phong cách khác** - Video style in scenes sometimes still gets mixed with other styles.

3. **Sự nhất quán về nhân vật, ngoại hình, trang phục, phụ kiện, vũ khí vẫn đang chưa khớp nhau qua các cảnh** - Character consistency regarding appearance, clothing, accessories, and weapons are not matching across scenes.

## Enhanced Features

### 1. Character Bible Enhancements

#### New Fields Added

**Costume/Clothing Details:**
```python
"costume": {
    "default_style": "black leather jacket, blue jeans",
    "color_palette": "black, blue", 
    "condition": "worn"
}
```

**Accessories:**
```python
"accessories": ["silver watch", "glasses", "necklace"]
```

**Weapons:**
```python
"weapons": ["pistol", "sword"]
```

#### Enhanced Character Bible Structure

The character bible now includes:

- **Visual & Physical Elements:**
  - Physical Blueprint (age, ethnicity, height, build, skin tone)
  - Hair DNA (color, length, style, texture)
  - Eye Signature (color, shape, expression)
  - Facial Map (nose, lips, jawline, distinguishing marks)
  - **NEW:** Costume details (clothing style, color palette, condition)
  - **NEW:** Accessories list
  - **NEW:** Weapons list

- **Internal & Behavioral Elements:**
  - Key trait, motivation, default behavior
  - Archetype, fatal flaw
  - Goals (external and internal)

### 2. Character Consistency Injection

The `inject_character_consistency()` function has been enhanced to include:

```python
inject_character_consistency(
    scene_prompt,
    bible,
    character_names=None,
    include_costume=True,      # NEW
    include_accessories=True   # NEW
)
```

**Features:**
- Automatically extracts clothing from visual_identity if not explicitly defined
- Extracts accessories from visual_identity if not explicitly defined
- Extracts weapons from visual_identity if not explicitly defined
- Includes facial map details (nose, lips, jawline, marks)
- Provides granular control over what to include

**Example Output:**
```
[John Smith - CONSISTENT APPEARANCE]
Physical: 30-35 Caucasian, tall (180cm), athletic build, fair skin
Hair: black short neat straight
Eyes: brown almond with focused expression
Face: average nose, medium lips, strong jawline
Marks: scar on left cheek
Costume: black leather jacket, blue jeans, colors: black, blue
Accessories: silver watch
Weapons: pistol
Key identifiers: Black leather jacket always worn, Silver watch on left wrist, Scar on left cheek
```

### 3. Style Consistency Enforcement

**New Function:** `inject_style_consistency()`

Ensures visual style remains consistent across all scenes by adding style markers to prompts.

```python
inject_style_consistency(scene_prompt, style)
```

**Supported Styles:**
- Cinematic - "film-like lighting, depth of field, professional camera work"
- Anime - "vibrant colors, expressive features, dynamic poses"
- Documentary - "realistic, natural lighting, observational camera"
- 3D/CGI - "rendered graphics, consistent 3D models"
- Cartoon, Realistic, Stop-motion, etc.

**Example Output:**
```
[STYLE: Maintain cinematic quality: film-like lighting, depth of field, professional camera work]

A hero walks through a dark alley...
```

### 4. Scene Transition Support

**New Function:** `inject_scene_transition()`

Improves scene-to-scene continuity by adding transition context.

```python
inject_scene_transition(
    current_scene_prompt,
    previous_scene_prompt=None,
    transition_type="cut"
)
```

**Transition Types:**
- `cut` - Direct cut from previous scene
- `fade` - Fade in from previous scene
- `dissolve` - Dissolve transition
- `match_cut` - Match cut with similar composition/action

**Example Output:**
```
[SCENE TRANSITION: Fade in from previous scene]

John walks outside into the rain...
```

### 5. Scene Continuity Validation

**New Function:** `_validate_scene_continuity()`

Validates that scenes can be properly assembled by checking:

1. **Location Continuity:** Detects sudden location changes without transition explanations
2. **Time Continuity:** Detects illogical time jumps (e.g., day → night in same location)
3. **Character Continuity:** Detects characters disappearing without explanation

**Example Warnings:**
```
Scene 1 -> 2: Location jump from 'office' to 'forest' without clear transition explanation
Scene 2 -> 3: Time jump from morning to night in same location without explanation
Scene 3 -> 4: Characters {'Mary'} disappeared without explanation
```

### 6. Enhanced LLM Prompts

The prompts sent to the LLM have been enhanced with:

#### Character Consistency Section
```
🔒 NHẤT QUÁN NHÂN VẬT QUA CÁC CẢNH (CHARACTER CONSISTENCY)

**TUYỆT ĐỐI CẤM thay đổi:**
- ❌ Màu sắc quần áo, kiểu dáng trang phục
- ❌ Phụ kiện (kính, đồng hồ, trang sức...)
- ❌ Vũ khí (nếu có - phải giữ nguyên qua các cảnh)
```

#### Scene Continuity Section
```
🎞️ TÍNH LIÊN TỤC GIỮA CÁC CẢNH (SCENE CONTINUITY)

1. **Liên kết nội dung:** Mỗi cảnh phải TIẾP NỐI logic với cảnh trước
2. **Chuyển cảnh:** Kế thừa context từ cảnh trước
3. **Visual Notes:** Lighting, location, action continuity
```

#### Style Consistency Section
```
🎨 NHẤT QUÁN PHONG CÁCH (STYLE CONSISTENCY)

- Visual Style: TẤT CẢ các cảnh phải cùng phong cách
- KHÔNG được lẫn lộn: Cinematic ↔ Anime ↔ Documentary
```

#### Enhanced Scene Schema
```json
{
  "scenes": [
    {
      "prompt_vi": "Visual prompt with FULL character details",
      "characters": ["Character with FULL visual_identity"],
      "time_of_day": "MUST be consistent with previous scene",
      "lighting_mood": "MUST match time_of_day",
      "transition_from_previous": "How this scene connects to previous",
      "style_notes": "Specific style elements in this scene",
      "visual_notes": "Continuity elements from previous scene"
    }
  ]
}
```

## Usage Examples

### Example 1: Creating Character Bible with Enhancements

```python
from services.google.character_bible import create_character_bible

video_concept = "Epic fantasy adventure"
script = """
Scene 1: A warrior in black leather armor, wielding a silver sword,
wearing a golden necklace and a red cape.
"""

# Create character bible (automatically extracts costume, accessories, weapons)
bible = create_character_bible(video_concept, script)

# Access enhanced character data
for char in bible.characters:
    print(f"Character: {char['name']}")
    print(f"Costume: {char['costume']}")
    print(f"Accessories: {char['accessories']}")
    print(f"Weapons: {char['weapons']}")
```

### Example 2: Injecting Character Consistency

```python
from services.google.character_bible import inject_character_consistency

scene_prompt = "John runs through the city streets"

# Inject full character consistency (costume, accessories, weapons)
enhanced_prompt = inject_character_consistency(
    scene_prompt,
    character_bible,
    include_costume=True,
    include_accessories=True
)

# Result includes all character details for consistency
```

### Example 3: Ensuring Style Consistency

```python
from services.google.character_bible import inject_style_consistency

scene_prompt = "A hero walks through a dark alley"
style = "Cinematic"

# Add style consistency marker
enhanced_prompt = inject_style_consistency(scene_prompt, style)

# All scenes will maintain cinematic style
```

### Example 4: Adding Scene Transitions

```python
from services.google.character_bible import inject_scene_transition

scenes = [
    "John stands in a coffee shop, ordering a drink",
    "John walks outside into the rain",
    "John drives through the city streets"
]

enhanced_scenes = []
for i, scene in enumerate(scenes):
    prev_scene = scenes[i-1] if i > 0 else None
    enhanced = inject_scene_transition(scene, prev_scene, "fade")
    enhanced_scenes.append(enhanced)
```

### Example 5: Validating Scene Continuity

```python
from services.llm_story_service import _validate_scene_continuity

scenes = [
    {
        "location": "office",
        "time_of_day": "morning",
        "characters": ["John", "Mary"],
        "transition_from_previous": ""
    },
    {
        "location": "coffee shop",
        "time_of_day": "afternoon",
        "characters": ["John"],
        "transition_from_previous": "John leaves office for lunch"
    }
]

# Check for continuity issues
issues = _validate_scene_continuity(scenes)
if issues:
    for issue in issues:
        print(f"Warning: {issue}")
```

## Integration Points

### 1. Sales Video Service
The enhanced character bible is automatically integrated into `services/sales_script_service.py`:

```python
from services.google.character_bible import create_character_bible

# Character bible is created from LLM-generated character data
bible = create_character_bible(video_concept, screenplay, existing_bible)
```

### 2. Video Generation
Character consistency is injected during image generation in `ui/video_ban_hang_v5_complete.py`:

```python
from services.google.character_bible import inject_character_consistency

# Inject character consistency into image prompts
if self.character_bible:
    prompt = inject_character_consistency(prompt, self.character_bible)
```

### 3. Story Generation
Scene continuity is validated during script generation in `services/llm_story_service.py`:

```python
# Validate scene continuity
continuity_issues = _validate_scene_continuity(scenes)
if continuity_issues:
    res["scene_continuity_warnings"] = continuity_issues
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_character_consistency.py
```

**Test Coverage:**
- ✓ Character bible creation with enhanced features
- ✓ Character consistency injection (costume, accessories, weapons)
- ✓ Style consistency injection for all styles
- ✓ Scene transition injection for all types
- ✓ Scene continuity validation

## Benefits

### For Users:
1. **Better Video Quality:** Scenes flow naturally from one to another
2. **Consistent Characters:** No jarring changes in appearance, clothing, or accessories
3. **Unified Style:** All scenes maintain the same visual style
4. **Professional Results:** Videos look polished and well-planned

### For Developers:
1. **Modular Design:** Each enhancement is a separate function
2. **Easy Integration:** Functions can be used independently or together
3. **Comprehensive Validation:** Automatic detection of continuity issues
4. **Extensible:** Easy to add new validation rules or style types

## Future Enhancements

Potential areas for further improvement:

1. **Advanced Lighting Continuity:** Track lighting conditions across scenes
2. **Props Tracking:** Maintain consistency of objects/props across scenes
3. **Background Consistency:** Ensure background elements remain consistent
4. **Camera Angle Continuity:** Validate logical camera angle transitions
5. **Action Continuity:** Ensure actions flow logically from scene to scene

## Conclusion

These enhancements significantly improve the quality and consistency of generated videos by:

1. ✅ Ensuring character appearance, clothing, accessories, and weapons remain consistent
2. ✅ Maintaining visual style consistency across all scenes
3. ✅ Validating and improving scene-to-scene continuity
4. ✅ Providing clear transition context between scenes
5. ✅ Giving developers powerful tools to enforce consistency

The system now produces videos that are much easier to assemble into complete, professional-looking content.
