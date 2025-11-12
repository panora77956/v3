# Hướng Dẫn Sử Dụng System Prompts / Domain Prompts

## Tổng Quan

Tính năng **Domain-Specific System Prompts** cho phép bạn tùy chỉnh cách AI tạo kịch bản video bằng cách chọn lĩnh vực (domain) và chủ đề (topic) phù hợp với nội dung video của bạn.

## Cách System Prompts Hoạt Động

### 1. Lưu Trữ Prompts

System prompts được lưu trữ trong file `services/domain_prompts.py`. File này chứa:
- Các lĩnh vực (domains) như: CÔNG NGHỆ/GIÁO DỤC, GIẢI TRÍ/CẢM XÚC, v.v.
- Các chủ đề (topics) trong mỗi lĩnh vực
- System prompt chi tiết cho mỗi cặp domain/topic

### 2. Cập Nhật Prompts Từ Google Sheets

Bạn có thể cập nhật system prompts từ Google Sheets bằng cách:
1. Mở tab **Settings** trong ứng dụng
2. Sử dụng tính năng "Update Prompts from Google Sheets"
3. File `domain_prompts.py` sẽ được tự động cập nhật với dữ liệu mới

### 3. Sử Dụng Trong Video Bán Hàng

Khi tạo video bán hàng, bạn có thể chọn domain và topic phù hợp:

#### Bước 1: Mở Phần Settings
- Trong tab "Video Bán Hàng", nhấp vào phần **⚙️ Cài Đặt**
- Phần này sẽ hiển thị các trường cấu hình

#### Bước 2: Chọn Lĩnh Vực (Domain)
- Tìm trường **"Lĩnh vực:"**
- Chọn lĩnh vực phù hợp với nội dung video của bạn
  - Ví dụ: "GIẢI TRÍ/CẢM XÚC" cho video kể chuyện
  - "CÔNG NGHỆ/GIÁO DỤC" cho video về lập trình
  - "GIÁO DỤC/HACKS" cho video mẹo vặt

#### Bước 3: Chọn Chủ Đề (Topic)
- Sau khi chọn lĩnh vực, trường **"Chủ đề:"** sẽ tự động cập nhật
- Chọn chủ đề cụ thể:
  - Ví dụ: "Kể chuyện Cá nhân (Storytelling)"
  - "Lập trình & Công nghệ Chuyên sâu"
  - "Mẹo Vặt (Life Hacks) Độc đáo"

#### Bước 4: Tạo Kịch Bản
- Điền các thông tin khác (ý tưởng, sản phẩm, v.v.)
- Nhấn **"📝 Viết kịch bản"**
- AI sẽ sử dụng system prompt tương ứng với domain/topic đã chọn

## Lợi Ích Của Việc Sử Dụng Domain Prompts

### 1. Character Bible Nhất Quán
Mỗi domain/topic có một "character bible" riêng:
- **Hình ảnh cố định (VISUAL LOCK)**: Mô tả chi tiết về nhân vật
- **Tâm lý cốt lõi**: Tính cách và đặc điểm tâm lý
- **Hành động nhất quán**: Cách nhân vật hành xử trong video

### 2. Phong Cách Phù Hợp
System prompt định nghĩa:
- Cấu trúc kịch bản (Hook → Problem → Solution → CTA)
- Tone giọng và cách kể chuyện
- Các yếu tố marketing (SEO, CTR, Retention)

### 3. Tối Ưu Hóa Cho Từng Loại Nội Dung
Mỗi domain/topic được tối ưu cho:
- Mục tiêu cụ thể (giáo dục, giải trí, bán hàng)
- Đối tượng khán giả mục tiêu
- Nền tảng phân phối (TikTok, YouTube, Facebook)

## Ví Dụ Sử Dụng

### Ví Dụ 1: Video Kể Chuyện Cá Nhân

**Cấu hình:**
- Lĩnh vực: `GIẢI TRÍ/CẢM XÚC`
- Chủ đề: `Kể chuyện Cá nhân (Storytelling - GRWM/Vlog)`

**Kết quả:**
- AI sẽ tạo kịch bản với giọng điệu chân thật, dễ bị tổn thương
- Nhân vật thể hiện cảm xúc một cách cởi mở
- Mục tiêu là tìm kiếm sự đồng cảm và chia sẻ bài học

### Ví Dụ 2: Video Hướng Dẫn Lập Trình

**Cấu hình:**
- Lĩnh vực: `CÔNG NGHỆ/GIÁO DỤC`
- Chủ đề: `Lập trình & Công nghệ Chuyên sâu (Coding & Dev)`

**Kết quả:**
- AI sẽ tạo kịch bản với giọng điệu logic và tỉ mỉ
- Nhân vật giải thích vấn đề bằng thuật toán
- Mục tiêu là đơn giản hóa kiến thức lập trình phức tạp

### Ví Dụ 3: Video Mẹo Vặt

**Cấu hình:**
- Lĩnh vực: `GIÁO DỤC/HACKS`
- Chủ đề: `Mẹo Vặt (Life Hacks) Độc đáo`

**Kết quả:**
- AI sẽ tạo kịch bản với giọng điệu hiệu quả và nhanh nhẹn
- Nhân vật luôn tìm giải pháp tối ưu
- Mục tiêu là giúp cuộc sống dễ dàng hơn

## Khi Nào Không Chọn Domain/Topic?

Nếu bạn **không chọn** domain/topic (để mặc định "(Không chọn)"):
- AI sẽ sử dụng prompt mặc định cho video bán hàng
- Vẫn tạo được kịch bản tốt, nhưng không có character bible và phong cách đặc trưng

**Khuyến nghị:** Luôn chọn domain/topic phù hợp để có kết quả tốt nhất!

## Câu Hỏi Thường Gặp

### Q: Làm thế nào để thêm domain/topic mới?

**A:** Có 2 cách:
1. Cập nhật trực tiếp file `services/domain_prompts.py`
2. Cập nhật Google Sheets và sync lại từ Settings tab

### Q: Domain/topic nào phù hợp với video của tôi?

**A:** Xem danh sách domains:
- **CÔNG NGHỆ**: Coding, AI Content
- **GIẢI TRÍ**: Comedy, Horror, Storytelling
- **GIÁO DỤC**: Career, Life Hacks, Reviews
- **KHOA HỌC**: Physics, Biology, Astronomy
- **SÁNG TẠO**: DIY, Art, Cooking, Fashion
- **TÀI CHÍNH**: Real Estate, Marketing, Investment

### Q: Tôi có thể sử dụng nhiều domain/topic cho một video?

**A:** Không, mỗi video chỉ có thể chọn 1 domain và 1 topic. Chọn cái phù hợp nhất với nội dung chính.

### Q: System prompt có ảnh hưởng đến hình ảnh không?

**A:** Có! System prompt chứa VISUAL_IDENTITY được sử dụng trong prompt tạo hình ảnh, đảm bảo nhất quán về nhân vật và phong cách visual.

## Technical Details (Cho Developers)

### Flow Hoạt Động

```
User chọn Domain/Topic
    ↓
UI lưu domain/topic vào config
    ↓
Script service nhận config với domain/topic
    ↓
Gọi domain_prompts.get_system_prompt(domain, topic)
    ↓
Inject domain prompt vào system prompt chính
    ↓
Gửi prompt đến Gemini AI
    ↓
Nhận kịch bản theo character bible và style
```

### Files Liên Quan

- `services/domain_prompts.py`: Lưu trữ system prompts
- `services/prompt_updater.py`: Service cập nhật prompts từ Google Sheets
- `services/sales_script_service.py`: Service tạo kịch bản (sử dụng domain prompts)
- `ui/video_ban_hang_v5_complete.py`: UI để chọn domain/topic
- `ui/settings_panel_v3_compact.py`: UI để cập nhật prompts từ Google Sheets

## Kết Luận

Tính năng Domain-Specific System Prompts giúp bạn:
✅ Tạo kịch bản phù hợp với từng loại nội dung
✅ Đảm bảo tính nhất quán về character và phong cách
✅ Tối ưu hóa cho mục tiêu cụ thể (giáo dục, giải trí, bán hàng)
✅ Dễ dàng cập nhật và quản lý từ Google Sheets

Hãy thử nghiệm với các domain/topic khác nhau để tìm ra công thức phù hợp nhất cho nội dung của bạn!
