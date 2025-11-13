# API Key Storage and Persistence

## Overview
All API keys and tokens are now automatically saved to a user-specific configuration file and are immediately available across all tabs without restarting the application.

## Storage Location
All API keys, tokens, and configuration data are stored in:
```
~/.veo_image2video_cfg.json
```

This file is automatically created on first run and is updated whenever settings are changed.

## Supported API Keys and Tokens

### 1. Google API Keys (Gemini)
- **Storage Key**: `google_api_keys`
- **Type**: Array of API keys
- **Usage**: Used by GeminiClient for text generation
- **Auto-save**: ✅ Yes

### 2. ElevenLabs API Keys
- **Storage Key**: `elevenlabs_api_keys`
- **Type**: Array of API keys
- **Usage**: Text-to-speech generation
- **Auto-save**: ✅ Yes

### 3. OpenAI API Keys
- **Storage Key**: `openai_api_keys`
- **Type**: Array of API keys
- **Usage**: Alternative LLM provider
- **Auto-save**: ✅ Yes

### 4. Google Labs Flow Tokens
- **Storage Key**: `labs_accounts`
- **Type**: Array of account objects
- **Fields**:
  - `name`: Account display name
  - `project_id`: Google Labs project ID
  - `tokens`: Array of OAuth Flow tokens
  - `enabled`: Boolean flag
- **Usage**: Video generation with labs.google.com
- **Auto-save**: ✅ Yes
- **Multi-account**: ✅ Supported with round-robin load balancing

### 5. Vertex AI Service Accounts
- **Storage Key**: `vertex_ai.service_accounts`
- **Type**: Array of service account objects
- **Fields**:
  - `name`: Account display name
  - `project_id`: GCP project ID
  - `credentials_json`: Full service account JSON (as string)
  - `location`: GCP region (default: us-central1)
  - `enabled`: Boolean flag
- **Usage**: Vertex AI Gemini API (higher rate limits, fewer 503 errors)
- **Auto-save**: ✅ Yes
- **Multi-account**: ✅ Supported with round-robin load balancing

### 6. Vertex AI Configuration
- **Storage Key**: `vertex_ai`
- **Fields**:
  - `enabled`: Boolean - whether to use Vertex AI
  - `use_vertex_first`: Boolean - try Vertex AI before AI Studio
  - `service_accounts`: Array of service accounts
- **Auto-save**: ✅ Yes

### 7. Whisk Authentication
- **Storage Keys**:
  - `labs_session_token`: Labs session token
  - `whisk_bearer_token`: Whisk bearer token
- **Usage**: Whisk AI image generation
- **Auto-save**: ✅ Yes

### 8. Google Workspace OAuth
- **Storage Key**: `google_workspace_oauth_token`
- **Usage**: Google Drive integration
- **Auto-save**: ✅ Yes

## Auto-Save Behavior

### Settings Panel
All changes in the Settings panel are **automatically saved** when:
- ✅ Adding a new Labs account
- ✅ Editing an existing Labs account
- ✅ Removing a Labs account
- ✅ Toggling Labs account enabled/disabled
- ✅ Adding a new Vertex AI service account
- ✅ Editing an existing Vertex AI service account
- ✅ Removing a Vertex AI service account
- ✅ Toggling Vertex AI service account enabled/disabled
- ✅ Manually clicking "Save Settings" button

User feedback is provided with messages like:
- "✓ Added account: [name] (auto-saved)"
- "✓ Updated account: [name] (Settings auto-saved)"
- "✓ Removed account: [name] (Settings auto-saved)"

### Cache Invalidation
After each save, the system automatically:
1. Clears the configuration cache (`services.core.config`)
2. Refreshes the key manager (`services.core.key_manager`)
3. Updates UI status indicators

This ensures that all services get the latest configuration immediately.

## Cross-Tab Availability

### How It Works
1. **Settings Tab**: Auto-saves configuration to `~/.veo_image2video_cfg.json`
2. **Other Tabs**: Load fresh configuration when starting work
   - Text2Video panel: ✅ Uses fresh config via GeminiClient
   - Video Ban Hang panel: ✅ Forces reload with `force_reload=True`
   - Image2Video panel: ✅ Uses fresh config via services
   - Clone Video panel: ✅ Uses fresh config via services

### No Restart Required
API keys and tokens added in the Settings tab are **immediately available** in other tabs without restarting the application because:
- Configuration is always loaded fresh from disk when needed
- Worker threads force reload configuration
- GeminiClient loads config on each instantiation
- Cache is cleared after every save

## Configuration File Format

Example structure of `~/.veo_image2video_cfg.json`:

```json
{
  "google_api_keys": [
    "AIzaSyABC123...",
    "AIzaSyDEF456..."
  ],
  "elevenlabs_api_keys": [
    "sk_abc123..."
  ],
  "openai_api_keys": [
    "sk-xyz789..."
  ],
  "labs_accounts": [
    {
      "name": "Account 1",
      "project_id": "87b19267-13d6-49cd-a7ed-db19a90c9339",
      "tokens": [
        "token1...",
        "token2..."
      ],
      "enabled": true
    }
  ],
  "vertex_ai": {
    "enabled": true,
    "use_vertex_first": true,
    "service_accounts": [
      {
        "name": "Production Account",
        "project_id": "my-gcp-project",
        "credentials_json": "{\"type\":\"service_account\",...}",
        "location": "us-central1",
        "enabled": true
      }
    ]
  },
  "labs_session_token": "session_token...",
  "whisk_bearer_token": "bearer_token...",
  "google_workspace_oauth_token": "oauth_token...",
  "default_voice_id": "3VnrjnYrskPMDsapTr8X",
  "flow_project_id": "87b19267-13d6-49cd-a7ed-db19a90c9339",
  "download_storage": "local",
  "download_root": "/home/user/VeoProjects",
  "gdrive_folder_id": "",
  "account_email": "user@example.com",
  "system_prompts_url": "https://docs.google.com/spreadsheets/d/..."
}
```

## Security Considerations

### Current Implementation
- Configuration file is stored in user's home directory with standard file permissions
- File is only accessible by the current user (Unix file permissions)
- Credentials are stored in plain text in the configuration file

### Future Enhancements (Optional)
If additional security is required, the following can be implemented:

1. **File Encryption**
   - Encrypt configuration file with a master password
   - Use AES-256 encryption
   - Prompt for password on application startup

2. **Credential Obfuscation**
   - Base64 encode sensitive fields (basic obfuscation)
   - Store encryption key in OS keyring

3. **Separate Credential Store**
   - Store API keys in OS-specific secure storage
   - Windows: Credential Manager
   - macOS: Keychain
   - Linux: Secret Service API / gnome-keyring

For most use cases, the current implementation (file permissions only) is sufficient as the configuration file is in the user's home directory.

## Troubleshooting

### Issue: API keys not appearing after adding
**Solution**: Check that auto-save completed successfully. Look for confirmation message: "✓ Added account: [name] (auto-saved)"

### Issue: Old API keys still being used
**Solution**: 
1. Check that Vertex AI is enabled in Settings
2. Verify that service accounts have `enabled: true`
3. Try manually clicking "Save Settings" button

### Issue: Configuration file not found
**Solution**: Configuration file is auto-created on first run at `~/.veo_image2video_cfg.json`

### Issue: Settings lost after tab switch
**Fixed**: This was the original issue. Now fixed with:
- Auto-save on all account operations
- Prevention of config reload on tab switch
- Proper cache management

## Testing

Run the test script to verify configuration persistence:
```bash
python3 test_config_persistence.py
```

This validates:
- Configuration file location
- Load and save operations
- Vertex AI configuration structure
- Service account manager integration
- Config loading in GeminiClient

## Summary of Changes

1. **Auto-save**: All account operations now trigger automatic save
2. **Cache management**: Configuration cache is cleared after every save
3. **Force reload**: Worker threads force reload configuration to ensure freshness
4. **GeminiClient**: Now loads from user config file (not project config.json)
5. **Settings panel**: Prevents unnecessary config reloads on tab switches

These changes ensure that API keys and tokens are:
- ✅ Persistently stored to file
- ✅ Immediately available across all tabs
- ✅ No application restart required
- ✅ Properly cached and invalidated
