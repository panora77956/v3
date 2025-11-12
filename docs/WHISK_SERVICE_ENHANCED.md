# Enhanced Whisk Service Documentation

## Overview

The enhanced Whisk service provides complete integration with Google Labs' Whisk image generation platform, based on the [rohitaryal/whisk-api](https://github.com/rohitaryal/whisk-api) TypeScript implementation.

## Features

### 1. Text-to-Image Generation (Simplified)
Generate images from text prompts without requiring reference images.

### 2. Reference Image Generation
Generate images using reference model and product images (existing feature).

### 3. Image Refinement
Enhance and modify existing generated images with new prompts.

### 4. Project Management
Create, list, delete, and rename Whisk projects.

## Authentication

Whisk requires **two types of authentication**:

### 1. Session Cookie (`labs_session_token`)

**How to obtain:**
1. Open browser and login to labs.google
2. Navigate to https://labs.google/fx/tools/whisk
3. Open Developer Tools (F12) → Application → Cookies
4. Copy the value of `__Secure-next-auth.session-token`
5. Add to `config.json`:
   ```json
   {
     "labs_session_token": "your-session-token-here"
   }
   ```

### 2. Bearer Token (`whisk_bearer_token`)

**How to obtain:**
1. Open browser and login to labs.google
2. Navigate to https://labs.google/fx/tools/whisk
3. Open Developer Tools (F12) → Network tab
4. Make a generation request
5. Find request to `aisandbox-pa.googleapis.com`
6. Copy Authorization header value (starts with "Bearer ")
7. Add to `config.json` (without "Bearer " prefix):
   ```json
   {
     "whisk_bearer_token": "your-bearer-token-here"
   }
   ```

**Note:** Bearer tokens typically expire after some time and need to be refreshed.

## API Reference

### Text-to-Image Generation

#### `generate_image_text_only()`

Generate image from text prompt only (no reference images required).

```python
from services import whisk_service

img_bytes = whisk_service.generate_image_text_only(
    prompt="A serene mountain landscape at sunset",
    project_id=None,  # Auto-creates project if None
    image_model="IMAGEN_3_5",
    aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE",
    seed=0,
    log_callback=print
)

if img_bytes:
    with open("output.png", "wb") as f:
        f.write(img_bytes)
```

**Parameters:**
- `prompt` (str): Text prompt for image generation
- `project_id` (str, optional): Project ID. Creates new project if None
- `image_model` (str): Model to use (see Available Models below)
- `aspect_ratio` (str): Aspect ratio (see Aspect Ratios below)
- `seed` (int): Random seed for reproducibility (default: 0)
- `log_callback` (callable, optional): Logging callback function

**Returns:** `bytes` - Generated image data, or `None` if failed

### Reference Image Generation

#### `generate_image()`

Generate image using reference model/character and product images (existing feature).

```python
img_bytes = whisk_service.generate_image(
    prompt="Professional product photo",
    model_image="path/to/character.png",
    product_image="path/to/product.png",
    aspect_ratio="IMAGE_ASPECT_RATIO_PORTRAIT",
    debug_callback=print
)
```

**Parameters:**
- `prompt` (str): Text prompt
- `model_image` (str, optional): Path to model/character reference image
- `product_image` (str, optional): Path to product reference image
- `aspect_ratio` (str): Aspect ratio
- `debug_callback` (callable, optional): Debug logging callback

**Returns:** `bytes` - Generated image data, or `None` if failed

### Image Refinement

#### `refine_image()`

Refine an existing generated image with new prompts.

```python
refined_bytes = whisk_service.refine_image(
    base64_image=base64_encoded_image,
    existing_prompt="A mountain landscape",
    new_refinement="add dramatic sunset colors",
    project_id="project-uuid",
    image_id="image-uuid",
    image_model="IMAGEN_3_5",
    aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE",
    seed=0,
    count=1,
    log_callback=print
)
```

**Parameters:**
- `base64_image` (str): Base64 encoded image to refine
- `existing_prompt` (str): Original prompt used to generate the image
- `new_refinement` (str): New refinement instructions
- `project_id` (str): Project ID where image was generated
- `image_id` (str): ID of the image to refine
- `image_model` (str): Model to use
- `aspect_ratio` (str): Aspect ratio for refined image
- `seed` (int): Random seed (default: 0)
- `count` (int): Number of images to generate (default: 1)
- `log_callback` (callable, optional): Logging callback

**Returns:** `bytes` - Refined image data, or `None` if failed

### Project Management

#### `create_project()`

Create a new Whisk project.

```python
project_id = whisk_service.create_project(
    title="My New Project",
    log_callback=print
)
```

**Parameters:**
- `title` (str): Project title/name
- `log_callback` (callable, optional): Logging callback

**Returns:** `str` - Project ID (workflow ID), or `None` if failed

#### `get_project_history()`

Get list of user's projects.

```python
projects = whisk_service.get_project_history(
    limit=20,
    log_callback=print
)

for project in projects:
    print(f"Project: {project['workflowId']} - {project['workflowMetadata']['workflowName']}")
```

**Parameters:**
- `limit` (int): Maximum number of projects to retrieve (default: 20)
- `log_callback` (callable, optional): Logging callback

**Returns:** `list` - List of project dictionaries, or `None` if failed

#### `delete_projects()`

Delete one or more projects.

```python
success = whisk_service.delete_projects(
    project_ids=["project-uuid-1", "project-uuid-2"],
    log_callback=print
)
```

**Parameters:**
- `project_ids` (list): List of project IDs to delete
- `log_callback` (callable, optional): Logging callback

**Returns:** `bool` - True if successful, False otherwise

#### `rename_project()`

Rename a project.

```python
project_id = whisk_service.rename_project(
    project_id="project-uuid",
    new_name="Updated Project Name",
    log_callback=print
)
```

**Parameters:**
- `project_id` (str): Project ID to rename
- `new_name` (str): New name for the project
- `log_callback` (callable, optional): Logging callback

**Returns:** `str` - Project ID if successful, `None` otherwise

## Available Models

| Model | Description | Recommended For |
|-------|-------------|-----------------|
| `IMAGEN_2` | Second generation | Standard quality |
| `IMAGEN_3` | Third generation | Improved quality |
| `IMAGEN_3_5` | Enhanced Imagen 3 (actually Imagen 4) | **Default - Best quality** |
| `IMAGEN_4` | Latest generation | Highest quality |
| `IMAGEN_3_PORTRAIT` | Portrait-optimized | Portrait photos |
| `IMAGEN_3_LANDSCAPE` | Landscape-optimized | Landscape scenes |

## Aspect Ratios

| Constant | Description | Use Case |
|----------|-------------|----------|
| `IMAGE_ASPECT_RATIO_PORTRAIT` | Vertical (9:16) | Instagram Stories, TikTok |
| `IMAGE_ASPECT_RATIO_LANDSCAPE` | Horizontal (16:9) | YouTube thumbnails |
| `IMAGE_ASPECT_RATIO_SQUARE` | Square (1:1) | Instagram posts |

## Integration with Video Ban Hang Panel

The enhanced Whisk service is automatically integrated with the Video Ban Hang panel:

### Automatic Method Selection

When Whisk is selected as the image model:

1. **With Reference Images:** Uses `generate_image()` method
   - Requires both model and product images
   - Provides better character/product consistency

2. **Without Reference Images:** Uses `generate_image_text_only()` method
   - Simpler, faster generation
   - No reference images required

### Usage in Video Ban Hang

1. Select "Whisk" as the image generation model
2. (Optional) Upload model and product reference images
3. Generate script and images as normal
4. The panel automatically chooses the appropriate generation method

## Error Handling

All functions return `None` on failure and provide detailed error messages through the log callback:

```python
def my_log(msg):
    print(f"[LOG] {msg}")

result = whisk_service.generate_image_text_only(
    prompt="test",
    log_callback=my_log
)

if result is None:
    print("Generation failed - check logs above")
else:
    print("Success!")
```

### Common Errors

#### Missing Credentials

```
[ERROR] Whisk configuration missing: No Whisk session token configured
```

**Solution:** Add `labs_session_token` to `config.json` (see Authentication section)

#### Expired Bearer Token

```
[ERROR] Whisk generation failed with status 401
```

**Solution:** Refresh `whisk_bearer_token` in `config.json` (bearer tokens expire)

## Examples

### Example 1: Simple Text Generation

```python
from services import whisk_service

# Generate a simple image
img = whisk_service.generate_image_text_only(
    prompt="A cute cat wearing sunglasses",
    aspect_ratio="IMAGE_ASPECT_RATIO_SQUARE",
    log_callback=print
)

if img:
    with open("cat.png", "wb") as f:
        f.write(img)
    print("Image saved as cat.png")
```

### Example 2: High-Quality Landscape

```python
# Generate with best model
img = whisk_service.generate_image_text_only(
    prompt="Majestic mountain range during golden hour",
    image_model="IMAGEN_4",
    aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE",
    seed=12345,  # For reproducibility
    log_callback=print
)
```

### Example 3: Project Management Workflow

```python
# Create a project
project_id = whisk_service.create_project("My Image Collection")

# Generate images in the project
img1 = whisk_service.generate_image_text_only(
    prompt="Forest scene",
    project_id=project_id,
    log_callback=print
)

# Rename the project
whisk_service.rename_project(project_id, "Forest Collection")

# List all projects
projects = whisk_service.get_project_history(limit=10)
for p in projects:
    print(p['workflowMetadata']['workflowName'])

# Delete old projects
old_ids = [p['workflowId'] for p in projects if 'Old' in p['workflowMetadata']['workflowName']]
whisk_service.delete_projects(old_ids)
```

### Example 4: Batch Generation with Seeds

```python
base_prompt = "A serene lake at"
times_of_day = ["dawn", "noon", "sunset", "night"]

for i, time in enumerate(times_of_day):
    img = whisk_service.generate_image_text_only(
        prompt=f"{base_prompt} {time}",
        seed=1000 + i,  # Different seed for variety
        log_callback=print
    )
    
    if img:
        with open(f"lake_{time}.png", "wb") as f:
            f.write(img)
```

## Limitations

1. **Authentication:** Requires valid Google Labs session cookie and bearer token
2. **Token Expiration:** Bearer tokens expire and need periodic refresh
3. **Rate Limits:** Subject to Google Labs API rate limits
4. **Regional Availability:** May not be available in all regions
5. **Async Generation:** Polling for long-running generations not yet implemented

## Troubleshooting

### Issue: 401 Unauthorized

**Cause:** Expired or invalid bearer token

**Solution:**
1. Open https://labs.google/fx/tools/whisk in browser
2. Open DevTools → Network tab
3. Make a generation request
4. Copy new bearer token from Authorization header
5. Update `whisk_bearer_token` in `config.json`

### Issue: No image generated (returns None)

**Cause:** Various (check log messages)

**Solutions:**
- Verify both session token and bearer token are configured
- Check that tokens haven't expired
- Ensure prompt is not empty
- Try with default parameters first
- Check internet connectivity

### Issue: Import error

```python
from services import whisk_service
# ModuleNotFoundError: No module named 'services'
```

**Solution:** Run from project root directory or add to Python path:
```python
import sys
sys.path.insert(0, '/path/to/v3')
from services import whisk_service
```

## Migration from Old API

If you were using the old `generate_image()` method with reference images only:

### Before (Reference images only)
```python
img = whisk_service.generate_image(
    prompt="Product photo",
    model_image="model.png",
    product_image="product.png",
    aspect_ratio="IMAGE_ASPECT_RATIO_PORTRAIT"
)
```

### Now (Automatic method selection)
```python
# With reference images (same as before)
img = whisk_service.generate_image(
    prompt="Product photo",
    model_image="model.png",
    product_image="product.png",
    aspect_ratio="IMAGE_ASPECT_RATIO_PORTRAIT"
)

# OR without reference images (new simplified method)
img = whisk_service.generate_image_text_only(
    prompt="Product photo",
    aspect_ratio="IMAGE_ASPECT_RATIO_PORTRAIT"
)
```

The Video Ban Hang panel now automatically chooses the right method based on whether reference images are provided.

## Contributing

To add new Whisk features:

1. Follow the structure in `services/whisk_service.py`
2. Use consistent error handling with `WhiskError`
3. Add comprehensive docstrings
4. Test with and without credentials
5. Update this documentation

## References

- [rohitaryal/whisk-api](https://github.com/rohitaryal/whisk-api) - TypeScript implementation
- [Google Labs Whisk](https://labs.google/fx/tools/whisk) - Official Whisk tool
- [Main README](../README.md) - Project overview

## Version History

- **v7.3.3** (2025-11-12): Added text-only generation, project management, and image refinement
- **v7.2.2** (2025-11-07): Initial Whisk integration with reference images

---

**Last Updated:** 2025-11-12  
**Author:** Based on rohitaryal/whisk-api implementation
