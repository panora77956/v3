# Content Policy Filter - Comprehensive Guide

## Overview

The Content Policy Filter is a comprehensive system for detecting and preventing content that may violate Google's content policies. This helps users avoid having their video generation requests blocked by Google's API.

**Version**: 2.0 (Enhanced with multiple violation categories)  
**Previous Version**: 1.0 (Minors-only detection)

## Problem Solved

When creating video scenarios, users often encounter Google policy violations without knowing which specific words or phrases are problematic. Users report:

> "Khi tạo kịch bản thì tôi hay bị google báo nhiều từ vi phạm => có thêm tính năng chặn các từ vi phạm này hay không? (Tôi không rõ các từ nào vi phạm)"

Translation: "When creating scenarios, I often get Google warnings about many violating words => is there a feature to block these violating words? (I don't know which words are violations)"

## Solution

This feature:

1. **Proactively detects** potentially violating content before API submission
2. **Warns users** with specific details about detected issues
3. **Provides choice** - users can proceed with warning or modify their content
4. **Supports bilingual** detection (Vietnamese and English)

## Features

### 1. Multi-Category Detection (NEW in v2.0)

The filter detects **5 categories** of policy violations:

#### 🧒 Minors/Children (Original + Enhanced)
- Detects references to children, teenagers, and minors under 18
- Keywords: "cô bé", "cậu bé", "child", "kid", "teenager", etc.
- Age detection: "10 tuổi", "12 years old", etc.
- **Action**: Automatically ages up characters to adults when possible

#### ⚔️ Violence and Weapons (NEW)
- Detects violence, weapons, fighting, and warfare
- Keywords: "súng", "dao", "gun", "knife", "fighting", "shooting", etc.
- **Action**: Warns user about potential violations

#### 🔞 Adult/Sexual Content (NEW)
- Detects explicit or sexual content
- Keywords: "khỏa thân", "nude", "sex", "khiêu dâm", "porn", etc.
- **Action**: Warns user about potential violations

#### 🚫 Hate Speech and Discrimination (NEW)
- Detects discriminatory or hateful content
- Keywords: "kỳ thị", "racist", "phân biệt chủng tộc", "hate", etc.
- **Action**: Warns user about potential violations

#### ⚠️ Dangerous Activities (NEW)
- Detects self-harm, drugs, and dangerous activities
- Keywords: "tự tử", "suicide", "ma túy", "drugs", etc.
- **Action**: Warns user about potential violations

### 2. Pre-Submission Validation (NEW in v2.0)

Users are warned **before** sending requests to Google's API, preventing:
- ❌ Wasted API calls
- ❌ Account flags or warnings
- ❌ Lost time and effort

When violations are detected, users see a dialog:

```
⚠️ Phát hiện các từ có thể vi phạm chính sách Google:

⚠️ Trẻ em/Minors: 'cô bé', 'bé', '10 tuổi'
⚠️ Bạo lực/Violence: 'súng', 'bắn'

Bạn có muốn tiếp tục? (Có thể bị Google chặn)
```

Users can then:
- ✅ **Cancel** and modify their content
- ✅ **Proceed** with full awareness of risks

## Usage

### For End Users

#### In Text2Video Panel (Tab "Text2Video V5"):

1. Enter your video idea in the "Ý tưởng" field
2. Click "🚀 Tạo Video Tự Động" button
3. **NEW**: If violations detected, you'll see a warning dialog
4. Choose to:
   - **No (Không)**: Cancel and edit your content
   - **Yes (Có)**: Proceed anyway (may be blocked by Google)

#### In Video Bán Hàng Panel (Tab "Video Bán Hàng V5"):

1. Enter your product idea and description
2. Click "🚀 Tạo Tất Cả Tự Động" or "📝 Tạo Kịch Bản"
3. **NEW**: Same warning flow as above

#### What You'll See:

**Before (without filter):**
- Submit prompt with violations → Google blocks it → Error message → Lost time

**After (with filter):**
- Enter prompt → **Warning appears before submission** → Choose to fix or proceed → No surprises!

### For Developers

#### Basic Usage

```python
from services.google.content_policy_filter import check_prompt_violations

# Check a prompt for violations
text = "Một cô bé 10 tuổi đang chơi"
is_safe, warnings = check_prompt_violations(text)

if not is_safe:
    print("Violations detected:")
    for warning in warnings:
        print(f"  - {warning}")
    # Output:
    # ⚠️ Trẻ em/Minors: 'cô bé', 'bé', '10 tuổi'
else:
    print("Content is safe!")
```

#### Advanced Usage

```python
from services.google.content_policy_filter import ContentPolicyFilter

# Create a filter instance
filter = ContentPolicyFilter(
    enable_age_up=True,   # Auto-age up minors
    min_age=18,           # Minimum age threshold
    strict_mode=False     # Don't raise exceptions
)

# Check all violations
text = "A man with a gun"
is_safe, violations = filter.check_prompt_safety(text)

print(f"Safe: {is_safe}")
print(f"Violations: {violations}")
# Output:
# Safe: False
# Violations: {'minors': [], 'violence': [('gun', 'violence_en')], ...}

# Check specific category
violence = filter.detect_violence(text)
print(f"Violence detected: {violence}")
# Output: [('gun', 'violence_en')]
```

#### Age-Up Functionality (Original Feature)

The filter can automatically convert child references to adult equivalents:

```python
from services.google.content_policy_filter import ContentPolicyFilter

filter = ContentPolicyFilter(enable_age_up=True)

text = "Một cô bé 10 tuổi"
sanitized = filter.age_up_text(text)
print(sanitized)  
# Output: "Một cô gái trẻ 20 tuổi"
```

## Implementation Details

### Files Added/Modified

#### New Files:
- `tests/test_content_policy_filter.py` - Comprehensive unit tests (17 tests)

#### Modified Files:
1. **`services/google/content_policy_filter.py`** (ENHANCED)
   - Added 4 new violation categories
   - New detection methods: `detect_violence()`, `detect_adult_content()`, `detect_hate_speech()`, `detect_dangerous_activities()`
   - New convenience function: `check_prompt_violations()`
   - New formatting function: `format_violation_warnings()`

2. **`ui/text2video_panel_v5_complete.py`** (ENHANCED)
   - Added pre-submission check in `_on_auto_generate()` method
   - Shows warning dialog when violations detected
   - Logs user decisions

3. **`ui/video_ban_hang_v5_complete.py`** (ENHANCED)
   - Added pre-submission check in `_on_write_script()` method
   - Shows warning dialog when violations detected
   - Checks both idea and product description

4. **`services/google/labs_flow_client.py`** (UNCHANGED)
   - Already had age-up integration from v1.0

### Detection Method

- **Case-insensitive** keyword matching
- **Bilingual** support (Vietnamese + English)
- **Age pattern** recognition (regex-based)
- **Multi-category** parallel detection

### Performance

- ⚡ **Fast**: ~0.001 seconds per check
- 📦 **Lightweight**: No external dependencies
- 🔄 **Non-blocking**: Failures don't stop workflow

## Testing

### Run Tests

```bash
cd /home/runner/work/v3/v3
python3 tests/test_content_policy_filter.py
```

### Test Results

```
Ran 17 tests in 0.003s
OK
```

### Test Coverage

- ✅ Clean content validation
- ✅ Minor detection (Vietnamese + English)
- ✅ Violence detection (Vietnamese + English)
- ✅ Adult content detection
- ✅ Hate speech detection
- ✅ Dangerous activities detection
- ✅ Multiple violation detection
- ✅ Warning message formatting
- ✅ Age-up functionality
- ✅ Case-insensitive matching
- ✅ Edge cases (empty strings, special chars, etc.)

## Examples

### Example 1: Clean Content ✅

```python
text = "A beautiful landscape with mountains"
is_safe, warnings = check_prompt_violations(text)
# is_safe = True
# warnings = []
```

### Example 2: Minor Violation ⚠️

```python
text = "Một cô bé 10 tuổi"
is_safe, warnings = check_prompt_violations(text)
# is_safe = False
# warnings = ["⚠️ Trẻ em/Minors: 'cô bé', 'bé', '10 tuổi'"]
```

### Example 3: Multiple Violations ⚠️⚠️

```python
text = "Một cô bé với súng đang bắn"
is_safe, warnings = check_prompt_violations(text)
# is_safe = False
# warnings = [
#     "⚠️ Trẻ em/Minors: 'cô bé', 'bé'",
#     "⚠️ Bạo lực/Violence: 'súng', 'bắn'"
# ]
```

### Example 4: Real User Scenario

**User Input**: "Một thanh niên 25 tuổi đi dạo trong công viên với phong cảnh đẹp"

**Filter Result**: ✅ Safe - No violations

**User Input**: "Một học sinh tiểu học với dao nhỏ"

**Filter Result**: ⚠️ Violations detected:
- ⚠️ Trẻ em/Minors: 'học sinh', 'tiểu học'
- ⚠️ Bạo lực/Violence: 'dao'

## Configuration

### Keyword Lists

Keywords are defined in `services/google/content_policy_filter.py`:

```python
# Minors
MINOR_KEYWORDS_VI = ["cô bé", "cậu bé", "em bé", ...]
MINOR_KEYWORDS_EN = ["little girl", "little boy", "child", ...]

# Violence
VIOLENCE_KEYWORDS_VI = ["súng", "dao", "kiếm", "bom", ...]
VIOLENCE_KEYWORDS_EN = ["gun", "knife", "sword", "bomb", ...]

# Adult Content
ADULT_KEYWORDS_VI = ["khỏa thân", "nude", "sex", ...]
ADULT_KEYWORDS_EN = ["naked", "nude", "sex", ...]

# Hate Speech
HATE_KEYWORDS_VI = ["kỳ thị", "phân biệt chủng tộc", ...]
HATE_KEYWORDS_EN = ["racist", "discrimination", ...]

# Dangerous Activities
DANGEROUS_KEYWORDS_VI = ["tự tử", "ma túy", ...]
DANGEROUS_KEYWORDS_EN = ["suicide", "drugs", ...]
```

### Customization

To add new keywords:

```python
# In services/google/content_policy_filter.py

VIOLENCE_KEYWORDS_VI = [
    "súng", "dao", "kiếm",
    # Add your keywords here
    "your_new_keyword"
]
```

## Best Practices

### For Users

1. ✅ **Review warnings carefully** - they indicate real policy risks
2. ✅ **Modify content** when possible instead of proceeding with warnings
3. ✅ **Use adult characters** - replace children with young adults (20+)
4. ✅ **Avoid violence** - focus on peaceful, positive scenarios
5. ✅ **Be respectful** - avoid discriminatory or hateful content
6. ✅ **Keep it safe** - avoid explicit adult content or dangerous activities

### For Developers

1. ✅ **Call filter early** - check content before expensive operations
2. ✅ **Handle exceptions** - filter failures shouldn't block workflow
3. ✅ **Log decisions** - track when users proceed despite warnings
4. ✅ **Update keywords** - expand lists based on real violations
5. ✅ **Test thoroughly** - add tests for new keyword categories

## Limitations

### Current Limitations

1. **Keyword-based**: Uses simple keyword matching, not AI-based semantic analysis
2. **False positives**: May flag safe content containing trigger words in different contexts
   - Example: "begun" contains "gun" but is safe
3. **False negatives**: May miss violations using uncommon words or phrases
4. **Language support**: Currently only Vietnamese and English
5. **Context-blind**: Doesn't understand context or intent

### Future Improvements

Potential enhancements:

- 🤖 AI-based semantic analysis using LLMs
- 🌍 Additional language support (Japanese, Korean, Chinese, etc.)
- 📊 Context-aware detection
- 🔄 Learning from blocked requests
- ⚙️ User-configurable sensitivity levels
- 📈 Violation statistics and analytics
- 🎯 Keyword refinement based on false positives

## Troubleshooting

### Filter Not Triggering

**Problem**: Violations not detected

**Solutions**:
1. Check if keywords are in the lists
2. Verify case-insensitive matching is working
3. Add missing keywords to appropriate list
4. Check import is successful: `from services.google.content_policy_filter import check_prompt_violations`

### False Positives

**Problem**: Safe content flagged as violation

**Solutions**:
1. Review keyword lists for overly broad terms
2. Report false positives for keyword list refinement
3. Use more specific wording in prompts

### Import Errors

**Problem**: `ImportError: cannot import ContentPolicyFilter`

**Solutions**:
1. Verify file path: `services/google/content_policy_filter.py`
2. Check Python path configuration
3. Ensure no circular imports
4. Try: `python3 -c "from services.google.content_policy_filter import check_prompt_violations; print('OK')"`

### Still Getting Blocked by Google?

If you still get blocked despite passing the filter:

1. **Review Google's policies** - filter may not catch everything
2. **Check logs** - see what was actually sent to API
3. **Report new violations** - help improve keyword lists
4. **Try simpler prompts** - complex prompts may have edge cases

## Changelog

### v2.0.0 (2025-11-13) - MAJOR UPDATE
- ✨ **NEW**: 4 additional violation categories (violence, adult content, hate speech, dangerous activities)
- ✨ **NEW**: Pre-submission validation with warning dialogs
- ✨ **NEW**: User choice to proceed or cancel
- ✨ **NEW**: Bilingual warning messages
- ✨ **NEW**: 17 comprehensive unit tests
- ✨ **NEW**: UI integration in Text2Video and Video Bán Hàng panels
- ✅ Enhanced documentation
- ✅ 100% backward compatible

### v1.0.0 (2025-11-08) - INITIAL RELEASE
- ✅ Minors/children detection
- ✅ Age-up functionality
- ✅ Bilingual support (Vietnamese + English)
- ✅ Automatic sanitization in labs_flow_client

## Migration from v1.0 to v2.0

**Good news**: No code changes required! v2.0 is 100% backward compatible.

**What's new**:
- Users now see warnings before submission (instead of only after Google blocks)
- 4 new violation categories automatically checked
- All existing code continues to work

**Benefits**:
- Fewer blocked requests
- Better user experience
- More comprehensive protection

## Related Files

- **Implementation**: `services/google/content_policy_filter.py`
- **UI Integration**: `ui/text2video_panel_v5_complete.py`
- **UI Integration**: `ui/video_ban_hang_v5_complete.py`
- **Tests**: `tests/test_content_policy_filter.py`
- **Documentation**: `docs/CONTENT_POLICY_FILTER.md` (this file)
- **Old Documentation**: `docs/CONTENT_POLICY_FILTER_OLD.md` (v1.0 version)

## Support

For questions or issues:

1. 📖 Check this documentation
2. 🧪 Review test examples in `tests/test_content_policy_filter.py`
3. 🐛 Open an issue on GitHub
4. 📧 Contact: VideoUltra Team

---

**Version**: 2.0.0  
**Last Updated**: 2025-11-13  
**Author**: VideoUltra Team  
**Status**: ✅ Production Ready
