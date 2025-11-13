# Vertex AI Setup Guide

## Tại sao nên dùng Vertex AI thay vì Google AI Studio?

### Vấn đề với Google AI Studio API
- **Rate limit thấp**: Chỉ 60 requests/minute (RPM), dễ bị vượt quota
- **Lỗi 503 thường xuyên**: Service unavailable khi server quá tải
- **Không phù hợp production**: Thiết kế cho prototyping và demo

### Ưu điểm của Vertex AI
- ✅ **Rate limit cao hơn**: Quota có thể tăng theo nhu cầu
- ✅ **Ổn định hơn**: Infrastructure cấp enterprise, ít bị 503 errors
- ✅ **Tính năng nâng cao**: Model tuning, monitoring, deployment
- ✅ **Bảo mật tốt hơn**: IAM roles, service accounts, audit logs

---

## Cách setup Vertex AI

### Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Lưu lại **Project ID** (ví dụ: `my-ai-project-123`)

### Bước 2: Enable Vertex AI API

1. Trong Google Cloud Console, vào [Vertex AI](https://console.cloud.google.com/vertex-ai)
2. Click "Enable Vertex AI API"
3. Đợi vài giây để API được kích hoạt

### Bước 3: Enable Billing

1. Vào [Billing](https://console.cloud.google.com/billing)
2. Link project với billing account
3. **Lưu ý**: Vertex AI có free tier và pay-as-you-go pricing

### Bước 4: Setup Authentication

Có 3 cách để authenticate với Vertex AI:

#### Option A: Sử dụng gcloud CLI (Recommended for local development)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login và set up application default credentials
gcloud auth application-default login

# Set project ID
gcloud config set project YOUR_PROJECT_ID
```

#### Option B: Sử dụng Service Account (Recommended for production)

1. Vào [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Name: `vertex-ai-service-account`
4. Grant role: **Vertex AI User** (`roles/aiplatform.user`)
5. Create and download JSON key file
6. Set environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

#### Option C: Sử dụng API Key (Fallback)

- Vẫn có thể dùng API key từ [Google AI Studio](https://aistudio.google.com/app/apikey)
- Hệ thống sẽ tự động fallback về AI Studio nếu Vertex AI không khả dụng

### Bước 5: Cấu hình trong ứng dụng

Mở file `config.json` và cập nhật:

```json
{
  "tokens": [],
  "google_keys": ["your-api-key-here"],
  "elevenlabs_keys": [],
  "default_project_id": "",
  "download_root": "",
  "vertex_ai": {
    "enabled": true,
    "project_id": "your-gcp-project-id",
    "location": "us-central1",
    "use_vertex_first": true
  }
}
```

**Các trường quan trọng:**
- `enabled`: Set `true` để bật Vertex AI
- `project_id`: Project ID từ bước 1
- `location`: Region của GCP (mặc định: `us-central1`)
  - Options: `us-central1`, `us-west1`, `europe-west1`, `asia-southeast1`
- `use_vertex_first`: `true` = ưu tiên Vertex AI, fallback về AI Studio nếu lỗi

---

## Testing Setup

### Kiểm tra authentication

```bash
# Test gcloud auth
gcloud auth application-default print-access-token

# Test Vertex AI API
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H "Content-Type: application/json" \
  https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/publishers/google/models/gemini-2.0-flash-exp:generateContent \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

### Chạy test trong Python

```python
from services.vertex_ai_client import VertexAIClient

# Test Vertex AI connection
client = VertexAIClient(
    model="gemini-2.0-flash-exp",
    project_id="your-project-id",
    location="us-central1"
)

result = client.generate_content(
    prompt="Say hello in Vietnamese",
    temperature=0.7
)

print(result)
```

---

## Pricing

### Vertex AI Pricing (Pay-as-you-go)

**Gemini 2.0 Flash:**
- Input: $0.075 per 1M characters
- Output: $0.30 per 1M characters

**Example cost:**
- 1000 video scripts (mỗi script ~10k characters input, ~5k output)
- Cost = (1000 × 10k × $0.075/1M) + (1000 × 5k × $0.30/1M)
- Cost ≈ $0.75 + $1.50 = **$2.25 cho 1000 scripts**

**So sánh với Google AI Studio:**
- AI Studio: Free nhưng rate limit rất thấp, hay bị 503
- Vertex AI: Trả phí nhưng ổn định, rate limit cao hơn nhiều

### Free tier

Vertex AI có [free tier](https://cloud.google.com/vertex-ai/pricing):
- $300 credit cho new customers (valid 90 days)
- Đủ để test và chạy hàng nghìn requests

---

## Troubleshooting

### Lỗi "Permission denied"

**Nguyên nhân:** Service account không có quyền

**Giải pháp:**
```bash
# Add Vertex AI User role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/aiplatform.user"
```

### Lỗi "Project not found"

**Nguyên nhân:** Project ID sai hoặc chưa enable Vertex AI API

**Giải pháp:**
1. Kiểm tra project ID trong config.json
2. Enable Vertex AI API: https://console.cloud.google.com/vertex-ai

### Lỗi "Quota exceeded"

**Nguyên nhân:** Vượt quota limit

**Giải pháp:**
1. Vào [Quotas page](https://console.cloud.google.com/iam-admin/quotas)
2. Search for "Vertex AI API"
3. Request quota increase

### Vẫn bị lỗi 503

**Nguyên nhân:** Network issue hoặc region outage

**Giải pháp:**
1. Thử đổi region khác: `us-west1`, `europe-west1`
2. Check [Google Cloud Status](https://status.cloud.google.com/)
3. System sẽ tự động fallback về AI Studio

---

## Fallback Mechanism

Hệ thống có cơ chế fallback thông minh:

1. **Try Vertex AI first** (nếu configured)
   - Better rate limits
   - More stable
   - Less 503 errors

2. **Fallback to AI Studio** (automatic)
   - If Vertex AI not configured
   - If Vertex AI fails
   - If authentication error

3. **Retry with exponential backoff**
   - 10s → 20s → 30s → 60s
   - Try multiple API keys
   - Try fallback models

**Kết quả:** Hệ thống robust và ít bị lỗi hơn rất nhiều!

---

## Monitoring Credit Usage

### Kiểm tra Credit qua UI

Ứng dụng có tích hợp tính năng kiểm tra credit usage trực tiếp trong Settings Panel:

1. **Mở Settings Panel** → **Vertex AI Configuration**
2. **Trong bảng Service Accounts**, click nút **💰 Check** bên cạnh account muốn kiểm tra
3. **Chọn một trong các options:**
   - **🔗 Open Billing Console**: Xem chi tiết billing và credits còn lại
   - **🔗 Open Vertex AI Console**: Xem dashboard và usage statistics
   - **🔗 Open Quotas Console**: Xem quota limits và current usage

### Kiểm tra Credit manually trên GCP Console

1. Truy cập [Billing Overview](https://console.cloud.google.com/billing)
2. Chọn project cần kiểm tra
3. Xem phần **"Credits"** hoặc **"Promotional credits"**:
   - **Current balance**: Credit còn lại
   - **Usage to date**: Đã sử dụng bao nhiêu
   - **Expiration date**: Ngày hết hạn

### Xem Pricing Information

Click nút **💰 View Pricing Info** trong Settings Panel để xem:
- Chi phí cho từng model (Gemini 2.5 Flash, Gemini 1.5 Pro)
- Thông tin free tier ($300 credit)
- Ước tính chi phí cho workload của bạn

### Tips để tối ưu credit usage

1. **Sử dụng nhiều service accounts**: Mỗi GCP project mới = $300 credit mới
2. **Chọn model phù hợp**: Gemini 2.5 Flash rẻ hơn nhiều so với Gemini 1.5 Pro
3. **Monitor usage thường xuyên**: Click nút 💰 Check để xem credit còn lại
4. **Setup billing alerts**: 
   - Vào [Billing Budgets](https://console.cloud.google.com/billing/budgets)
   - Tạo budget alert để nhận email khi sắp hết credit
5. **Fallback to AI Studio**: Khi hết credit, hệ thống tự động fallback về AI Studio (free)

### Example Cost Calculation

**Scenario**: Generate 1000 video scripts

- Input: ~10,000 characters/script
- Output: ~5,000 characters/script

**Using Gemini 2.5 Flash:**
```
Input cost:  1000 × 10,000 × $0.075/1M = $0.75
Output cost: 1000 × 5,000 × $0.30/1M  = $1.50
Total cost:                             = $2.25
```

**With $300 credit:**
- Can generate ~133,000 scripts before running out!
- Với nhiều accounts: 3 accounts × $300 = $900 → 400,000+ scripts

---

## FAQ

### Q: Tôi có cần xóa API keys cũ không?

**A:** KHÔNG! Giữ nguyên API keys trong `config.json`. Hệ thống sẽ dùng chúng khi Vertex AI không khả dụng.

### Q: Tôi không muốn trả tiền, chỉ dùng free tier?

**A:** Có thể! Vertex AI có $300 free credit. Sau khi hết, set `"enabled": false` trong config để dùng lại AI Studio.

### Q: Có thể dùng cả Vertex AI và AI Studio cùng lúc?

**A:** CÓ! Đó chính là thiết kế của hệ thống. Vertex AI được ưu tiên, AI Studio làm backup.

### Q: Region nào tốt nhất?

**A:** `us-central1` (default) thường nhanh và ổn định nhất. Nếu bị lỗi, thử `us-west1` hoặc `europe-west1`.

### Q: Làm sao biết đang dùng Vertex AI hay AI Studio?

**A:** Check console logs:
```
[VertexAI] Initialized Vertex AI client for project my-project in us-central1
```
hoặc
```
[GeminiClient] Falling back to AI Studio API
```

---

## Liên hệ

- GitHub Issues: [panora77956/v3/issues](https://github.com/panora77956/v3/issues)
- Google Cloud Support: https://cloud.google.com/support
- Vertex AI Documentation: https://cloud.google.com/vertex-ai/docs
