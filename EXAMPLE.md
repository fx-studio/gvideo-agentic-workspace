# Phân Tích Video với Agentic AI - Thực Hành & Bài Học

Tài liệu này ghi lại quá trình thực hiện 2 demo thực tế khi sử dụng workspace `gvideo` để phân tích video thông qua sức mạnh của **Gemini Agentic Video**, cùng với những bài học và điểm cần lưu ý (Best Practices).

## 1. Demo phân tích video từ link YouTube
**Mục tiêu:** Tóm tắt và tìm highlight từ một video trên YouTube (chủ đề "Hiệu ứng chuột" - Goodhart's Law & AI Reward Hacking).
**Đầu vào:** Link YouTube `https://youtu.be/KVSQCE74t7o`

**Quá trình thực hiện:**
- **Bước 1 (Chạy thử & Tóm tắt):** Dùng script để tóm tắt (`--che-do tom-tat`).
- **Bước 2 (Xử lý sự cố mạng):** Trong quá trình chạy thật, các model mặc định (`gemini-3.7-flash` và `3.6`) gặp lỗi 503 (quá tải do lượng truy cập cao từ phía server Google). Trợ lý AI (Agent) đã chủ động xử lý bằng cách chuyển sang sử dụng cờ `--model gemini-3.5-flash-lite`.
- **Bước 3 (Đánh giá Token):** Chạy thành công rực rỡ. Kết quả trả về báo cáo chi tiết chỉ tốn **152 token** (cực kỳ tiết kiệm so với việc phải nạp cả file video) và AI chỉ cần quay lại xem/rà soát đúng 1 lần.
- **Bước 4 (Highlight & Tự động cắt):** Chạy lệnh `--che-do highlight`. Nhờ việc tái sử dụng dữ liệu dự án đã có, tốc độ ra kết quả rất nhanh. Sau đó, Agent tận dụng khả năng tự động hóa để gọi công cụ dòng lệnh `yt-dlp` và `ffmpeg` tải và cắt trực tiếp đoạn highlight trên YouTube thành file `.mp4.mkv` (và remux sang `.mp4` chuẩn H.264) một cách hoàn hảo.

## 2. Demo phân tích file video Local (trong máy)
**Mục tiêu:** Tóm tắt và trích xuất highlight của một video quay dọc (9x16) được lưu sẵn trong máy.
**Đầu vào:** File local `inputs/agentic-video-9x16.mp4` (~90MB)

**Quá trình thực hiện:**
- **Bước 1 (Tải lên an toàn):** Gọi phân tích tóm tắt với `--model gemini-3.5-flash-lite`. Quá trình chạy ngầm sẽ tải file này lên **Google Files API**. Dữ liệu được bảo mật và tự động xóa sau 48h.
- **Bước 2 (Kết quả & Token):** Báo cáo tóm tắt trả về cực kỳ chuẩn xác cho một video có chủ đề công nghệ. Tương tự như YouTube, AI cũng chỉ dùng khoảng **152 token** và tua lại 2 lần để rà soát.
- **Bước 3 (Cắt Local siêu tốc):** Khi đã có mốc thời gian từ chế độ `highlight`, do file video đã có sẵn ở local, Agent trực tiếp dùng lệnh `ffmpeg -ss ... -to ...` để trích xuất đoạn cắt chỉ trong vài giây.

---

## Các bài học và Điểm cần lưu ý (Best Practices)

1. **Chuẩn bị Model dự phòng (Fallback):** Các mô hình mới nhất đôi khi có lượng truy cập đột biến dẫn đến quá tải (503 Service Unavailable). Việc thêm cờ `--model gemini-3.5-flash-lite` giúp hệ thống hoạt động ổn định và mượt mà hơn khi model chính tạm thời bị nghẽn.
2. **Lợi thế vượt trội về Token của Agentic Video:** Khác với cách "nuốt" toàn bộ video truyền thống, chế độ **agentic** thực sự hoạt động như một đạo diễn ảo. LLM tự ra quyết định tìm và xem đúng các mốc thời gian cần thiết. Hệ quả là nó chỉ tốn khoảng 150 - 200 token cho một video kéo dài nhiều phút, tối ưu chi phí cực lớn.
3. **Quyền riêng tư với file Local:** Với file trong máy, video sẽ buộc phải được đẩy lên máy chủ Google (Files API, lưu tạm 48h). Do đó, hãy luôn nhắc nhở hoặc kiểm tra lại về vấn đề bảo mật đối với các video nội bộ/nhạy cảm trước khi thực thi. Với link YouTube thì an toàn tuyệt đối về bảo mật local vì Google đọc thẳng từ URL.
4. **Sự kết hợp hoàn hảo (AI + Hệ thống CLI):** Điểm sáng lớn nhất của demo là sự kết hợp nhuần nhuyễn giữa **Gemini API** (dùng AI để tìm, định vị mốc thời gian, tạo tiêu đề) với **các công cụ Terminal/CLI như `ffmpeg` và `yt-dlp`**. Agent (Antigravity) đóng vai trò nhạc trưởng, nối 2 bước này thành một chuỗi tự động hoàn toàn: Từ lúc người dùng chỉ định video cho đến khi xuất ra file `.mp4` nhỏ gọn thành phẩm mà không cần người dùng tự click chuột mở phần mềm dựng.
