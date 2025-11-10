# Vietnamese Text Overlay Fix

## Problem Statement

**Issue**: Generated videos had text overlays appearing with Vietnamese text displaying incorrectly (encoding errors with diacritical marks).

Vietnamese: "Trong các video tạo ra vẫn bị lẫn chữ chèn lên. Các chữ này lại bị lỗi tiếng Việt :(("

## Root Causes

1. **Font Selection Issue**: 
   - Previous font priority: DejaVuSans → Helvetica → Arial → Default
   - These fonts have limited or no support for Vietnamese diacritical marks
   - Vietnamese has many tone marks: á, à, ả, ã, ạ, ă, ắ, ằ, ẳ, ẵ, ặ, â, ấ, ầ, ẩ, ẫ, ậ, etc.

2. **Weak Negative Prompts**:
   - Original prompt: "text, words, letters, subtitles, captions..." (166 chars)
   - Not explicit enough to prevent text overlays in generated videos
   - No specific Vietnamese text avoidance

## Solution Implemented

### 1. Font Priority Update (`services/sales_script_service.py`)

**Before**:
```python
font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Limited Vietnamese support
    "/System/Library/Fonts/Helvetica.ttc",
    "C:\\Windows\\Fonts\\arialbd.ttf"
]
```

**After**:
```python
font_paths = [
    # Bundled Roboto fonts with FULL Vietnamese support (highest priority)
    str(project_root / "ui" / "styles" / "fonts" / "Roboto-Bold.ttf"),
    str(project_root / "ui" / "styles" / "fonts" / "Roboto-Medium.ttf"),
    str(project_root / "ui" / "styles" / "fonts" / "Roboto-Regular.ttf"),
    # System fonts (fallback)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:\\Windows\\Fonts\\arialbd.ttf"
]
```

**Why Roboto?**
- Already bundled in `ui/styles/fonts/`
- Designed by Google with full Unicode support
- Excellent Vietnamese diacritical mark rendering
- Professional appearance suitable for thumbnails

### 2. Enhanced Negative Prompts

Updated in both:
- `services/labs_flow_service.py`
- `services/google/labs_flow_client.py`

**Before** (166 characters):
```python
"text, words, letters, subtitles, captions, titles, credits, on-screen text, 
watermarks, logos, brands, camera shake, fisheye, photorealistic, live action, 
3D CGI, Disney 3D, Pixar style"
```

**After** (379 characters):
```python
"text overlays, on-screen text, burned-in text, hardcoded text, embedded text, 
text, words, letters, characters, typography, writing, script, 
subtitles, captions, titles, credits, labels, annotations, 
watermarks, logos, brands, signatures, stamps, 
Vietnamese text, English text, any language text, 
camera shake, fisheye, photorealistic, live action, 3D CGI, Disney 3D, Pixar style"
```

**Key additions**:
- "text overlays" - more explicit than just "text"
- "burned-in text", "hardcoded text", "embedded text" - various forms of text in video
- "Vietnamese text", "English text", "any language text" - language-specific avoidance

## Testing

### Test 1: Vietnamese Character Rendering

All Vietnamese diacritical marks tested:
- ✓ á à ả ã ạ (a with tones)
- ✓ ă ắ ằ ẳ ẵ ặ (ă with tones)
- ✓ â ấ ầ ẩ ẫ ậ (â with tones)
- ✓ é è ẻ ẽ ẹ (e with tones)
- ✓ ê ế ề ể ễ ệ (ê with tones)
- ✓ í ì ỉ ĩ ị (i with tones)
- ✓ ó ò ỏ õ ọ (o with tones)
- ✓ ô ố ồ ổ ỗ ộ (ô with tones)
- ✓ ơ ớ ờ ở ỡ ợ (ơ with tones)
- ✓ ú ù ủ ũ ụ (u with tones)
- ✓ ư ứ ừ ử ữ ự (ư with tones)
- ✓ ý ỳ ỷ ỹ ỵ (y with tones)
- ✓ đ Đ (special d)

### Test 2: Negative Prompt Verification

Required terms confirmed present:
- ✓ "text overlays"
- ✓ "on-screen text"
- ✓ "burned-in text"
- ✓ "Vietnamese text"
- ✓ "English text"
- ✓ "any language text"
- ✓ "subtitles"
- ✓ "captions"
- ✓ "watermarks"

### Test 3: Thumbnail Generation

Successfully generated thumbnails with Vietnamese text:
- ✓ "XEM NGAY!" (See now!)
- ✓ "TIẾNG VIỆT" (Vietnamese)
- ✓ "ĐẶC BIỆT" (Special)

## Files Modified

1. **services/sales_script_service.py**
   - Function: `generate_thumbnail_with_text()`
   - Change: Updated font priority to use Roboto fonts first

2. **services/labs_flow_service.py**
   - Function: `_extract_negative_prompt()`
   - Change: Enhanced default negative prompt with explicit text avoidance

3. **services/google/labs_flow_client.py**
   - Function: `_extract_negative_prompt()`
   - Change: Same enhancement for consistency across codebase

## Impact

### For Users:
- ✅ Vietnamese text in thumbnails displays correctly
- ✅ All diacritical marks render properly
- ✅ Reduced likelihood of text overlays in generated videos

### For Developers:
- ✅ Consistent font handling across the application
- ✅ Better video generation prompts
- ✅ Maintains backward compatibility (fonts are bundled)

## Future Improvements

Consider:
1. Add user preference for font selection in settings
2. Support for other languages with special characters (Thai, Arabic, Chinese, etc.)
3. Optional text overlay feature with proper Vietnamese font rendering
4. Enhanced prompt engineering for even better text avoidance

## Related Issues

- Vietnamese text encoding in generated videos
- Text overlay prevention in video generation
- Font selection for international characters

## Version

- **Fixed in**: v7.2.4
- **Date**: 2025-11-10
- **Tested**: ✅ All tests passed
- **Security**: ✅ No vulnerabilities (CodeQL verified)
