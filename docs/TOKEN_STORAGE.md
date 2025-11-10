# Token and API Key Storage Documentation

## Overview
All API keys and authentication tokens used by Video Super Ultra are stored in **JSON configuration files** on your local machine. No credentials are sent to external servers except when making API calls to the respective services (Google Labs, Whisk, ElevenLabs, etc.).

## Storage Locations

### Primary Configuration File
**Location:** `~/.veo_image2video_cfg.json`
- **Full Path (Windows):** `C:\Users\<YourUsername>\.veo_image2video_cfg.json`
- **Full Path (macOS/Linux):** `/home/<username>/.veo_image2video_cfg.json`

This is the main configuration file where all settings and credentials are stored.

### Secondary Configuration File
**Location:** `config.json` (in the application root directory)

This file may also be used for initial configuration or deployment-specific settings.

## Stored Credentials

The configuration files contain the following sensitive information:

### 1. Google API Keys
- **Config Key:** `google_api_keys`
- **Type:** Array of strings
- **Used For:** Gemini AI, Google Cloud services
- **Example:**
  ```json
  "google_api_keys": [
    "AIzaSy...",
    "AIzaSy..."
  ]
  ```

### 2. ElevenLabs API Keys
- **Config Key:** `elevenlabs_api_keys`
- **Type:** Array of strings
- **Used For:** Text-to-speech voice generation
- **Example:**
  ```json
  "elevenlabs_api_keys": [
    "sk_...",
    "sk_..."
  ]
  ```

### 3. OpenAI API Keys
- **Config Key:** `openai_api_keys`
- **Type:** Array of strings
- **Used For:** ChatGPT, GPT-4 services
- **Example:**
  ```json
  "openai_api_keys": [
    "sk-...",
    "sk-..."
  ]
  ```

### 4. Google Labs Flow Tokens (Video Generation)
- **Config Key:** `labs_accounts`
- **Type:** Array of account objects
- **Used For:** Multi-account video generation with Google Labs Flow
- **Example:**
  ```json
  "labs_accounts": [
    {
      "name": "Account 1",
      "tokens": ["token1", "token2"],
      "project_id": "87b19267-13d6-49cd-a7ed-db19a90c9339",
      "enabled": true
    }
  ]
  ```

### 5. Whisk Authentication (NEW)
Whisk requires **two types of authentication** from labs.google.com:

#### Session Token
- **Config Key:** `labs_session_token`
- **Type:** String
- **Used For:** Browser session authentication for Whisk image generation
- **How to Obtain:**
  1. Open browser and login to labs.google.com
  2. Navigate to https://labs.google/fx/tools/whisk
  3. Open Developer Tools (F12) → Application → Cookies
  4. Copy value of `__Secure-next-auth.session-token`
- **Example:**
  ```json
  "labs_session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..."
  ```

#### Bearer Token
- **Config Key:** `whisk_bearer_token`
- **Type:** String  
- **Used For:** OAuth authentication for Whisk API requests
- **How to Obtain:**
  1. Open browser and login to labs.google.com
  2. Navigate to https://labs.google/fx/tools/whisk
  3. Open Developer Tools (F12) → Network tab
  4. Make a generation request
  5. Find request to `aisandbox-pa.googleapis.com`
  6. Copy Authorization header value (without "Bearer " prefix)
- **Example:**
  ```json
  "whisk_bearer_token": "ya29.a0AfH6SMB..."
  ```
- **Note:** Bearer tokens typically expire after some time and need to be refreshed.

### 6. Google Drive OAuth Token
- **Config Key:** `google_workspace_oauth_token`
- **Type:** String
- **Used For:** Uploading videos to Google Drive
- **Example:**
  ```json
  "google_workspace_oauth_token": "ya29.a0AfH6SMB..."
  ```

## Security Considerations

### ⚠️ Important Security Notes

1. **Never commit config files to version control**
   - Add `.veo_image2video_cfg.json` and `config.json` to `.gitignore`

2. **File Permissions**
   - Ensure config files are only readable by your user account
   - On Unix/Linux: `chmod 600 ~/.veo_image2video_cfg.json`

3. **Sharing Configurations**
   - Never share your config files as they contain sensitive credentials
   - Create template files without actual keys for sharing

4. **Backup Strategy**
   - Back up config files securely (encrypted)
   - Don't store backups in cloud services unless encrypted

5. **Token Expiration**
   - OAuth tokens (bearer tokens) expire and need periodic renewal
   - Session tokens from browsers also expire
   - Monitor error logs for authentication failures

6. **Access Control**
   - Only authorized users should have access to the config files
   - Use OS-level encryption if possible (FileVault, BitLocker, etc.)

## Managing Credentials via UI

All credentials can be managed through the application's **Settings Panel**:

### Settings → API Credentials

1. **Google API Keys** - Accordion section with key management
2. **ElevenLabs API Keys** - Accordion section with key management  
3. **OpenAI API Keys** - Accordion section with key management
4. **Google Labs Flow Tokens** - Multi-account management table
5. **Whisk Authentication** (NEW) - Session and Bearer token inputs

The UI provides:
- ✅ Visual validation
- ✅ Password masking for sensitive values
- ✅ Helpful tooltips and instructions
- ✅ Automatic save/load functionality

## Example Configuration File

```json
{
  "google_api_keys": ["AIzaSy..."],
  "elevenlabs_api_keys": ["sk_..."],
  "openai_api_keys": ["sk-..."],
  "labs_accounts": [
    {
      "name": "Production Account",
      "tokens": ["token1"],
      "project_id": "87b19267-13d6-49cd-a7ed-db19a90c9339",
      "enabled": true
    }
  ],
  "labs_session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0...",
  "whisk_bearer_token": "ya29.a0AfH6SMB...",
  "default_voice_id": "3VnrjnYrskPMDsapTr8X",
  "flow_project_id": "87b19267-13d6-49cd-a7ed-db19a90c9339",
  "download_root": "/path/to/projects",
  "download_storage": "local",
  "gdrive_folder_id": "",
  "google_workspace_oauth_token": ""
}
```

## Troubleshooting

### Configuration Not Loading
- Check file exists: `ls -la ~/.veo_image2video_cfg.json`
- Verify JSON syntax: `python -m json.tool ~/.veo_image2video_cfg.json`
- Check file permissions: Should be readable by current user

### Authentication Errors
- **401 Unauthorized**: Token expired or invalid - refresh from browser
- **Missing config**: Add required keys to config file
- **Invalid format**: Ensure JSON is properly formatted

### Where to Get Help
- Check error logs in the application console
- Review tooltips in Settings panel for credential instructions
- Ensure all required credentials are configured before use

## Related Files

- **Config Loader:** `utils/config.py`
- **Core Config:** `services/core/config.py`
- **Settings UI:** `ui/settings_panel_v3_compact.py`
- **Whisk Service:** `services/whisk_service.py`
- **Labs Service:** `services/labs_flow_service.py`
