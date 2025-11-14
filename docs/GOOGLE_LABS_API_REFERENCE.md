# Google Labs API Reference (Current)

**Last Updated**: 2025-11-14  
**Status**: Active - Field name verified as of this date  
**API Base**: `https://aisandbox-pa.googleapis.com/v1`

## ⚠️ API Stability Warning

The Google Labs API is an internal/sandbox API that changes frequently without notice. Field names and structures may change at any time. See `docs/API_FIELD_NAME_REVERSION_FIX.md` for change history.

## Authentication

```http
Authorization: Bearer <oauth_token>
Content-Type: application/json; charset=utf-8
Origin: https://labs.google
Referer: https://labs.google/
User-Agent: Mozilla/5.0
```

## Endpoints

### 1. Upload Image

**Endpoint**: `POST /v1:uploadUserImage`

**Request**:
```json
{
  "imageInput": {
    "rawImageBytes": "<base64_encoded_image>",
    "mimeType": "image/jpeg",
    "isUserUploaded": true,
    "aspectRatio": "IMAGE_ASPECT_RATIO_PORTRAIT"
  },
  "clientContext": {
    "sessionId": ";1700000000000",
    "tool": "ASSET_MANAGER"
  }
}
```

**Response**:
```json
{
  "mediaGenerationId": {
    "mediaGenerationId": "CAMaJD..."
  }
}
```

**Aspect Ratios** (Upload):
- `IMAGE_ASPECT_RATIO_PORTRAIT` - 9:16
- `IMAGE_ASPECT_RATIO_LANDSCAPE` - 16:9
- `IMAGE_ASPECT_RATIO_SQUARE` - 1:1

### 2. Generate Video from Image (I2V)

**Endpoint**: `POST /v1/video:batchAsyncGenerateVideoStartImage`

**Current Correct Format** (as of 2025-11-14):
```json
{
  "requests": [
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_PORTRAIT",
      "seed": 2210,
      "videoModelKey": "veo_3_1_i2v_s_fast_portrait_ultra",
      "metadata": {
        "sceneId": "e868f9cb-514e-4b65-b6ae-a52e9b2b86c4"
      },
      "imageInput": {
        "startImage": {
          "mediaId": "CAMaJD..."
        },
        "prompt": "A detailed description of the video"
      }
    }
  ],
  "clientContext": {
    "projectId": "87b19267-13d6-49cd-a7ed-db19a90c9339"
  }
}
```

**⚠️ Critical Field**: `imageInput` (NOT `startImageInput`)
- **History**: Changed multiple times (see API_FIELD_NAME_REVERSION_FIX.md)
- **Current**: `imageInput` as of 2025-11-14

**Video Models** (I2V):
- `veo_3_1_i2v_s_fast_portrait_ultra` - Fast, portrait, ultra quality
- `veo_3_1_i2v_s_fast_portrait` - Fast, portrait
- `veo_3_1_i2v_s_portrait` - Portrait
- `veo_3_1_i2v_s_fast_ultra` - Fast, landscape/square, ultra quality
- `veo_3_1_i2v_s_fast` - Fast, landscape/square
- `veo_3_1_i2v_s` - Standard, any aspect ratio

**Aspect Ratios** (Video):
- `VIDEO_ASPECT_RATIO_PORTRAIT` - 9:16
- `VIDEO_ASPECT_RATIO_LANDSCAPE` - 16:9
- `VIDEO_ASPECT_RATIO_SQUARE` - 1:1

### 3. Generate Video from Text (T2V)

**Endpoint**: `POST /v1/video:batchAsyncGenerateVideoText`

**Request**:
```json
{
  "requests": [
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
      "seed": 12345,
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "textInput": {
        "prompt": "A detailed description of the video"
      }
    }
  ],
  "clientContext": {
    "projectId": "87b19267-13d6-49cd-a7ed-db19a90c9339"
  }
}
```

**Video Models** (T2V):
- `veo_3_1_t2v_fast_ultra` - Fast, ultra quality
- `veo_3_1_t2v` - Standard quality

### 4. Check Video Generation Status

**Endpoint**: `POST /v1/video:batchCheckAsyncVideoGenerationStatus`

**Request**:
```json
{
  "operations": [
    {
      "operation": {
        "name": "bbf7250934f9f3d25e6182858da8bcb1"
      },
      "sceneId": "e83c6a7b-47a9-4a17-89e9-3d716c75a03f",
      "status": "MEDIA_GENERATION_STATUS_PENDING"
    }
  ],
  "clientContext": {
    "projectId": "87b19267-13d6-49cd-a7ed-db19a90c9339"
  }
}
```

**Response** (In Progress):
```json
{
  "operations": [
    {
      "operation": {
        "name": "bbf7250934f9f3d25e6182858da8bcb1"
      },
      "status": "MEDIA_GENERATION_STATUS_PENDING"
    }
  ]
}
```

**Response** (Completed):
```json
{
  "operations": [
    {
      "operation": {
        "name": "bbf7250934f9f3d25e6182858da8bcb1",
        "done": true
      },
      "status": "MEDIA_GENERATION_STATUS_SUCCEEDED",
      "response": {
        "videoUrl": "https://storage.googleapis.com/.../video.mp4",
        "downloadUrl": "https://storage.googleapis.com/.../video.mp4"
      }
    }
  ]
}
```

**Status Values**:
- `MEDIA_GENERATION_STATUS_PENDING` - In progress
- `MEDIA_GENERATION_STATUS_SUCCEEDED` - Completed successfully
- `MEDIA_GENERATION_STATUS_FAILED` - Failed

## Batch Generation

### Multiple Videos per Request
Both I2V and T2V endpoints support batch generation (up to 4 videos per request):

```json
{
  "requests": [
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
      "seed": 1001,
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "textInput": {"prompt": "Video 1 description"}
    },
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_PORTRAIT",
      "seed": 1002,
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "textInput": {"prompt": "Video 2 description"}
    }
  ]
}
```

**Response**:
```json
{
  "operations": [
    {
      "operation": {"name": "operation_id_1"},
      "status": "MEDIA_GENERATION_STATUS_PENDING"
    },
    {
      "operation": {"name": "operation_id_2"},
      "status": "MEDIA_GENERATION_STATUS_PENDING"
    }
  ]
}
```

## Error Responses

### HTTP 400 - Invalid Request
```json
{
  "error": {
    "code": 400,
    "message": "Invalid JSON payload received. Unknown name \"startImageInput\" at 'requests[0]': Cannot find field.",
    "status": "INVALID_ARGUMENT"
  }
}
```

**Common Causes**:
- Incorrect field names (e.g., using `startImageInput` instead of `imageInput`)
- Missing required fields
- Invalid model keys
- Invalid aspect ratios
- Content policy violations

### HTTP 401 - Unauthorized
```json
{
  "error": {
    "code": 401,
    "message": "Request had invalid authentication credentials.",
    "status": "UNAUTHENTICATED"
  }
}
```

**Common Causes**:
- Expired OAuth token
- Invalid OAuth token
- Missing Authorization header

### HTTP 500 - Internal Server Error
```
{
  "error": {
    "code": 500,
    "message": "Internal error encountered.",
    "status": "INTERNAL"
  }
}
```

**Common Causes**:
- Server-side issues
- Temporary outages
- Overload

## Best Practices

### 1. Error Handling
- Always implement retry logic with exponential backoff
- Handle 401 errors by rotating to next OAuth token
- Handle 400 errors by checking field names against this reference
- Handle 500 errors with retry after delay

### 2. Token Management
- Use multiple OAuth tokens for load balancing
- Rotate tokens on 401 errors
- Mark invalid tokens and skip them in rotation
- Monitor token expiration

### 3. Batch Processing
- Use batch generation (up to 4 videos) for efficiency
- Generate unique sceneId for each request using UUID
- Track operation names for status checking
- Poll for status at reasonable intervals (not too frequent)

### 4. Prompt Engineering
- Keep prompts under 5000 characters
- Be specific and detailed
- Include visual style requirements
- Add negative prompts to avoid unwanted elements

### 5. API Monitoring
- Log all API requests and responses
- Monitor for HTTP 400 errors with "Unknown name" messages
- Track API response times
- Watch for pattern changes in error messages

## Troubleshooting

### "Unknown name 'imageInput'" Error
**Solution**: API changed field name to `startImageInput` (see version 7.3.0)

### "Unknown name 'startImageInput'" Error
**Solution**: API changed field name back to `imageInput` (see version 7.3.1)

### "Request contains an invalid argument" Error
**Possible Causes**:
1. Incorrect field name (check this reference)
2. Invalid model key
3. Invalid aspect ratio
4. Content policy violation
5. Prompt too long (> 5000 characters)

### Videos Not Generating
**Checklist**:
1. ✅ OAuth token is valid
2. ✅ Image upload succeeded (got mediaId)
3. ✅ Using correct field name (`imageInput`)
4. ✅ Model key is valid for aspect ratio
5. ✅ SceneId is included in metadata
6. ✅ Prompt is under 5000 characters
7. ✅ Content complies with Google's policies

## Rate Limits

**Note**: Rate limits are not officially documented but observed:
- ~60 requests per minute per token
- ~4 videos per request (batch limit)
- Consider using multiple tokens for higher throughput

## Migration Notes

### From Vertex AI API
The Google Labs API uses different field names and structure:
- Vertex AI: `image` → Labs API: `imageInput`
- Vertex AI: `instances` array → Labs API: `requests` array
- Vertex AI: Different authentication method

### API Versioning
The API currently has no version number in the URL (`/v1/`). Schema changes happen without version bumps, so:
- Monitor this reference document for updates
- Watch for API error messages indicating field name changes
- Implement fallback logic for field names

## Code Examples

### Python Example (Image-to-Video)
```python
import requests
import json
import uuid

# Configuration
bearer_token = "your_oauth_token"
media_id = "CAMaJD..."  # From upload step
prompt = "A detailed video description"

# Build request
request_body = {
    "requests": [{
        "aspectRatio": "VIDEO_ASPECT_RATIO_PORTRAIT",
        "seed": 1234,
        "videoModelKey": "veo_3_1_i2v_s_fast_portrait_ultra",
        "metadata": {"sceneId": str(uuid.uuid4())},
        "imageInput": {
            "startImage": {"mediaId": media_id},
            "prompt": prompt
        }
    }],
    "clientContext": {
        "projectId": "your_project_id"
    }
}

# Make request
response = requests.post(
    "https://aisandbox-pa.googleapis.com/v1/video:batchAsyncGenerateVideoStartImage",
    headers={
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json; charset=utf-8"
    },
    json=request_body,
    timeout=180
)

# Get operation ID
result = response.json()
operation_id = result["operations"][0]["operation"]["name"]
print(f"Operation ID: {operation_id}")
```

## Related Documentation
- `docs/API_FIELD_NAME_REVERSION_FIX.md` - Field name change history
- `docs/IMAGE2VIDEO_API_FIX.md` - Previous field name fix
- `docs/VIDEO_GENERATION_STATUS_FIX.md` - Metadata requirements
- `CHANGELOG.md` - Version history

---

**⚠️ Important**: This API is unofficial and subject to change without notice. Always refer to the latest documentation and error messages when integrating.
