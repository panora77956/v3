# Whisk API Authentication Fix / Sửa Lỗi Xác Thực Whisk API

## Problem / Vấn Đề

When using Whisk image generation, you may encounter 401 authentication errors:

Khi sử dụng tạo ảnh Whisk, bạn có thể gặp lỗi xác thực 401:

```
[ERROR] Caption failed with status 401
[ERROR] Whisk upload failed with status 401
```

## Root Cause / Nguyên Nhân

The Whisk API requires TWO types of authentication tokens that are different from regular API keys:

API Whisk yêu cầu HAI loại token xác thực khác với API key thông thường:

1. **Session Cookie** (`__Secure-next-auth.session-token`) - For caption and upload endpoints
2. **OAuth Bearer Token** - For runImageRecipe endpoint

These tokens CANNOT be the same as:
- Google API keys (for Gemini)
- Labs API tokens (for Veo video generation)

Các token này KHÔNG THỂ giống như:
- Google API keys (cho Gemini)
- Labs API tokens (cho tạo video Veo)

## Solution / Giải Pháp

You need to extract actual browser tokens from labs.google:

Bạn cần trích xuất token thực tế từ trình duyệt khi truy cập labs.google:

### Step 1: Get Session Cookie / Bước 1: Lấy Session Cookie

1. Open browser and login to https://labs.google
   
   Mở trình duyệt và đăng nhập vào https://labs.google

2. Navigate to Whisk tool: https://labs.google/fx/tools/whisk
   
   Truy cập công cụ Whisk: https://labs.google/fx/tools/whisk

3. Open Developer Tools (Press F12)
   
   Mở Developer Tools (Nhấn F12)

4. Go to **Application** tab → **Cookies** → `https://labs.google`
   
   Vào tab **Application** → **Cookies** → `https://labs.google`

5. Find cookie named: `__Secure-next-auth.session-token`
   
   Tìm cookie tên: `__Secure-next-auth.session-token`

6. Copy its **Value**
   
   Copy **Value** của nó

7. Add to `config.json`:

   Thêm vào `config.json`:

```json
{
  "labs_session_token": "YOUR_SESSION_TOKEN_HERE"
}
```

### Step 2: Get OAuth Bearer Token / Bước 2: Lấy OAuth Bearer Token

1. Still in Developer Tools, go to **Network** tab
   
   Vẫn trong Developer Tools, vào tab **Network**

2. In Whisk interface, click "Generate" to create an image
   
   Trong giao diện Whisk, nhấn "Generate" để tạo ảnh

3. Look for network requests to: `aisandbox-pa.googleapis.com`
   
   Tìm các request network tới: `aisandbox-pa.googleapis.com`

4. Click on one of these requests
   
   Nhấn vào một trong các request này

5. Go to **Headers** tab
   
   Vào tab **Headers**

6. Find **Authorization** header
   
   Tìm header **Authorization**

7. Copy the value AFTER "Bearer " (don't include "Bearer " itself)
   
   Copy giá trị SAU "Bearer " (không copy chữ "Bearer ")

8. Add to `config.json`:

   Thêm vào `config.json`:

```json
{
  "whisk_bearer_token": "YOUR_BEARER_TOKEN_HERE"
}
```

### Complete Config Example / Ví Dụ Config Đầy Đủ

```json
{
  "google_keys": ["your-gemini-api-key"],
  "tokens": ["your-labs-api-token-for-veo"],
  "labs_session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0...",
  "whisk_bearer_token": "ya29.a0AfB_byD...",
  "elevenlabs_keys": [],
  "default_project_id": "",
  "download_root": ""
}
```

## Important Notes / Lưu Ý Quan Trọng

### Token Expiration / Hết Hạn Token

Both tokens expire after some time:

Cả hai token đều hết hạn sau một thời gian:

- **Session cookie**: Usually valid for days/weeks
  
  **Session cookie**: Thường hợp lệ trong nhiều ngày/tuần

- **Bearer token**: Usually valid for hours
  
  **Bearer token**: Thường hợp lệ trong vài giờ

When you see 401 errors, you need to refresh the tokens by repeating the steps above.

Khi gặp lỗi 401, bạn cần làm mới token bằng cách lặp lại các bước trên.

### Alternative: Disable Whisk / Thay Thế: Tắt Whisk

If you cannot get valid tokens, you can disable Whisk and use other image generation methods:

Nếu không thể lấy token hợp lệ, bạn có thể tắt Whisk và dùng phương pháp tạo ảnh khác:

1. Don't select "Whisk" as image generation model
   
   Không chọn "Whisk" làm model tạo ảnh

2. Use Imagen or other available models instead
   
   Dùng Imagen hoặc các model khác

## Technical Details / Chi Tiết Kỹ Thuật

### Why Regular API Keys Don't Work / Tại Sao API Key Thông Thường Không Hoạt Động

The Whisk API endpoints use different authentication mechanisms:

Các endpoint API Whisk sử dụng cơ chế xác thực khác:

1. **Caption/Upload endpoints** (`backbone.captionImage`, `backbone.uploadImage`):
   - Use session-based authentication
   - Require browser session cookies
   - Not compatible with API keys
   
2. **Generation endpoint** (`whisk:runImageRecipe`):
   - Use OAuth 2.0 authentication
   - Require OAuth bearer tokens
   - Not compatible with API keys

Regular API keys are designed for server-to-server communication, while Whisk requires browser-based OAuth tokens.

API key thông thường được thiết kế cho giao tiếp server-to-server, trong khi Whisk yêu cầu OAuth token từ trình duyệt.

### Security Considerations / Cân Nhắc Bảo Mật

- Never share your session cookies or bearer tokens publicly
  
  Không bao giờ chia sẻ session cookie hoặc bearer token công khai

- These tokens have the same access level as your Google account
  
  Các token này có quyền truy cập tương đương tài khoản Google của bạn

- Store them securely in `config.json` (which should be in `.gitignore`)
  
  Lưu trữ chúng an toàn trong `config.json` (phải có trong `.gitignore`)

- Refresh tokens regularly for security
  
  Làm mới token định kỳ để bảo mật

## Troubleshooting / Xử Lý Sự Cố

### Still Getting 401 After Adding Tokens / Vẫn Gặp 401 Sau Khi Thêm Token

1. Verify tokens are correctly copied (no extra spaces)
   
   Kiểm tra token được copy đúng (không có khoảng trắng thừa)

2. Check if tokens have expired - get fresh ones
   
   Kiểm tra token có hết hạn không - lấy token mới

3. Make sure you're logged into labs.google in the same browser
   
   Đảm bảo bạn đã đăng nhập labs.google trong cùng trình duyệt

4. Try clearing browser cache and getting new tokens
   
   Thử xóa cache trình duyệt và lấy token mới

### Can't Find Tokens in Browser / Không Tìm Thấy Token Trong Trình Duyệt

1. Make sure you're logged into labs.google
   
   Đảm bảo bạn đã đăng nhập labs.google

2. Navigate to Whisk tool specifically (not just labs.google homepage)
   
   Truy cập công cụ Whisk cụ thể (không chỉ trang chủ labs.google)

3. Try making a test generation first
   
   Thử tạo một ảnh test trước

4. Refresh Developer Tools
   
   Làm mới Developer Tools

---

## Code Changes / Thay Đổi Code

The following changes have been made to improve error messages:

Các thay đổi sau đã được thực hiện để cải thiện thông báo lỗi:

1. **services/whisk_service.py**:
   - Added detailed documentation for token requirements
   - Improved error messages with instructions
   - Added support for `labs_session_token` and `whisk_bearer_token` config keys
   
2. Enhanced fallback behavior while maintaining backward compatibility

---

*Last updated: 2025-11-09*
*Cập nhật lần cuối: 2025-11-09*
