# Whisk API Fix - Before vs After Comparison

## Quick Reference

This document provides a side-by-side comparison of the Whisk API payload structure before and after the 400 error fix.

---

## The Problem: 400 "INVALID_ARGUMENT" Error

```
[ERROR] Whisk recipe failed with status 400
[DEBUG] Response: {
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
```

---

## The Fix: Payload Structure Correction

### BEFORE (Incorrect - Causes 400 Error)

```python
recipe_media_inputs = [{
    "caption": "Reference image",
    "mediaInput": {
        "mediaCategory": "MEDIA_CATEGORY_SUBJECT",  # ❌ WRONG - This causes 400 error
        "mediaGenerationId": "CAMaJDEwNDhiMGVjLWQ2YjYtNGEyYy..."
    }
}]
```

**Why it fails:**
- `mediaCategory` was already set during the upload phase
- Repeating it in the recipe phase causes API validation error
- Google API rejects payload with redundant/unexpected field

### AFTER (Correct - Works Successfully)

```python
recipe_media_inputs = [{
    "caption": "Reference image",
    "mediaInput": {
        "mediaGenerationId": "CAMaJDEwNDhiMGVjLWQ2YjYtNGEyYy..."  # ✅ CORRECT
    }
}]
```

**Why it works:**
- `mediaInput` contains only the generation ID
- Category is already known from upload phase
- Clean, minimal structure that API expects

---

## Complete API Flow

### 1. Upload Phase (Sets Category)

```python
# POST https://labs.google/fx/api/trpc/backbone.uploadImage
{
    "json": {
        "uploadMediaInput": {
            "mediaCategory": "MEDIA_CATEGORY_SUBJECT",  # ✅ Set here during upload
            "rawBytes": "data:image/png;base64,..."
        }
    }
}

# Response:
{
    "result": {
        "data": {
            "json": {
                "result": {
                    "uploadMediaGenerationId": "CAMaJD..."  # ← Use this ID later
                }
            }
        }
    }
}
```

### 2. Recipe Phase (Reference by ID Only)

```python
# POST https://aisandbox-pa.googleapis.com/v1/whisk:runImageRecipe
{
    "clientContext": {...},
    "seed": 123456,
    "imageModelSettings": {...},
    "userInstruction": "Create an image...",
    "recipeMediaInputs": [{
        "caption": "Reference image",
        "mediaInput": {
            "mediaGenerationId": "CAMaJD..."  # ✅ Reference by ID only
            # NO mediaCategory here!
        }
    }]
}

# Response (Success):
{
    "imageRecipeResult": {
        "generatedImage": {
            "rawBytes": "data:image/png;base64,..."
        }
    }
}
```

---

## Code Change Summary

**File:** `services/whisk_service.py`  
**Lines:** 507-517  
**Change:** 1 line removed

```diff
  if media_id:
+     # FIXED: Remove mediaCategory from recipeMediaInputs
+     # The API expects mediaInput with only mediaGenerationId (category was set during upload)
+     # Correct structure: {"caption": "...", "mediaInput": {"mediaGenerationId": "..."}}
      recipe_media_inputs.append({
          "caption": caption,
          "mediaInput": {
-             "mediaCategory": "MEDIA_CATEGORY_SUBJECT",
              "mediaGenerationId": media_id
          }
      })
```

---

## Key Takeaways

1. **Upload Phase**: Specify `mediaCategory` ✅
2. **Recipe Phase**: Use only `mediaGenerationId` ✅
3. **Don't**: Repeat `mediaCategory` in recipe ❌

---

## Related Errors & Fixes

| Error Code | Issue | Fix Document |
|------------|-------|--------------|
| **400** | Invalid argument (redundant field) | This document |
| **401** | Authentication issues | [WHISK_AUTH_FIX.md](WHISK_AUTH_FIX.md) |
| **500** | Wrong content-type header | [WHISK_500_ERROR_FIX.md](WHISK_500_ERROR_FIX.md) |

---

## Testing Your Fix

After applying this fix, you should see:

✅ **Success Logs:**
```
[INFO] Whisk: Starting generation...
[INFO] Whisk: Processing 2 reference images...
[INFO] Whisk: Uploading image 1/2...
[INFO] Whisk: Upload response status 200
[INFO] Whisk: Uploading image 2/2...
[INFO] Whisk: Upload response status 200
[INFO] Whisk: Uploaded 2 images successfully
[INFO] Whisk: Running image recipe...
[INFO] Whisk: Image generation complete!  ← ✅ Success!
```

❌ **Before Fix (Error):**
```
[ERROR] Whisk recipe failed with status 400
[ERROR] Error message: Request contains an invalid argument.
```

---

**Version:** 7.2.8  
**Date:** 2025-11-10  
**Status:** ✅ Fixed and Tested
