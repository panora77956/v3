# Google Flow Image Generation

This feature allows you to generate images using Google Labs Flow API with reference images and text prompts.

## Features

- Generate images from text prompts
- Use up to 3 reference images for consistent style and objects
- Support for multiple aspect ratios (Portrait 9:16, Landscape 16:9, Square 1:1)
- Integrated into Video Sales tab alongside Gemini and Whisk options

## Configuration

To use Flow image generation, you need to configure the following in `config.json`:

### 1. Flow Bearer Token (Required)

The Flow API requires an OAuth bearer token from Google Labs.

**How to obtain the bearer token:**

1. Open your browser and login to https://labs.google
2. Navigate to https://labs.google/fx/tools/flow
3. Open Developer Tools (F12) → Network tab
4. Make an image generation request in the Flow tool
5. Find the request to `aisandbox-pa.googleapis.com` (look for `batchGenerateImages`)
6. Copy the `Authorization` header value (it starts with "Bearer ")
7. Add to config.json (without the "Bearer " prefix):

```json
{
  "flow_bearer_token": "ya29.a0ATi6K2swm1rfTOQmOl..."
}
```

Alternative key name: `labs_bearer_token`

**Note:** Bearer tokens typically expire after some time (hours/days) and will need to be refreshed.

### 2. Flow Project ID (Optional)

The Flow API requires a project ID. If not configured, a default will be used.

**How to obtain the project ID:**

1. Open Developer Tools on https://labs.google/fx/tools/flow
2. Look at the URL when you create a project: `https://labs.google/fx/tools/flow/project/{PROJECT_ID}`
3. Or check the Network tab for requests containing the project ID

Add to config.json:

```json
{
  "flow_project_id": "88f510eb-f32a-40c2-adce-8f492f37a144"
}
```

Alternative key name: `labs_project_id`

### Example config.json

```json
{
  "tokens": [],
  "google_keys": ["your-gemini-api-key"],
  "elevenlabs_keys": [],
  "flow_bearer_token": "ya29.a0ATi6K2swm1rfTOQmOl...",
  "flow_project_id": "88f510eb-f32a-40c2-adce-8f492f37a144",
  "default_project_id": "",
  "download_root": "",
  "vertex_ai": {
    "enabled": false,
    "project_id": "",
    "location": "us-central1",
    "use_vertex_first": true
  }
}
```

## Usage

1. Open the Video Sales tab in the application
2. In the Settings section, find the "Tạo ảnh:" (Image Generation) dropdown
3. Select "Flow" from the options (Gemini, Whisk, Flow)
4. (Optional) Upload reference images using the model/product image selectors
5. Click "🎨 Tạo ảnh" to generate images

## How It Works

### With Reference Images

When you provide reference images (model photos, product photos), Flow will:
- Use up to 3 reference images to maintain visual consistency
- Generate images that match the style and objects from your references
- Apply your text prompt to create variations

### Without Reference Images (Text-Only)

When no reference images are provided, Flow will:
- Generate images purely from your text prompt
- Use the GEM_PIX model for high-quality results
- Create 4 variants for each scene

## API Details

The Flow API endpoint is:
```
POST https://aisandbox-pa.googleapis.com/v1/projects/{project_id}/flowMedia:batchGenerateImages
```

Request structure:
```json
{
  "requests": [
    {
      "clientContext": {
        "sessionId": ";1763184933603"
      },
      "seed": 317639,
      "imageModelName": "GEM_PIX",
      "imageAspectRatio": "IMAGE_ASPECT_RATIO_PORTRAIT",
      "prompt": "your text prompt here",
      "imageInputs": [
        {
          "name": "CAMaJD...",
          "imageInputType": "IMAGE_INPUT_TYPE_REFERENCE"
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Error: "No Bearer token configured for Flow API"

This means you need to configure `flow_bearer_token` in config.json. Follow the configuration steps above.

### Error: "Flow API returned status 401"

Your bearer token has expired. Follow the configuration steps to obtain a new token.

### Error: "Flow API returned status 403"

You may not have access to the Flow API, or your project ID is incorrect. Make sure you can access https://labs.google/fx/tools/flow in your browser.

### Images not generating

1. Check that your bearer token is valid
2. Verify your project ID is correct
3. Check the log output for detailed error messages
4. Try generating an image manually in the Flow web interface first to confirm access

## Comparison with Other Options

| Feature | Gemini | Whisk | Flow |
|---------|--------|-------|------|
| API Key Required | Yes (Google API) | Yes (Session + Bearer) | Yes (Bearer token) |
| Reference Images | Yes (Vertex AI) | Yes (3 images) | Yes (3 images) |
| Variants per Request | 1 | 1 | 4 |
| Speed | Fast | Medium | Medium |
| Quality | High | High | High |
| Consistency | Good | Excellent | Excellent |

## Links

- Google Labs Flow: https://labs.google/fx/tools/flow
- Google Labs: https://labs.google
- Documentation: This file

---

For questions or issues, please check the application logs for detailed error messages.
