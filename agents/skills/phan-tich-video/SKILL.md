---
name: phan-tich-video
description: Phân tích một video bằng Gemini ở chế độ agentic (AI tự quay lại xem đúng đoạn cần, không nuốt cả video). Đầu vào là file video trong máy hoặc link YouTube công khai. Dùng khi người dùng muốn tóm tắt video/bài giảng kèm mốc thời gian, cắt highlight, bắt lỗi trong bản ghi màn hình, tìm lúc nào xuất hiện một thứ, đếm vật/hành động, hoặc hỏi bất kỳ câu gì về nội dung một video.
---

# Phân tích video (Gemini agentic)

Bạn (agent) **không tự xem video**. Việc xem do Gemini API làm, qua script `scripts/phan_tich.py`.
Phần của bạn: chọn đúng chế độ, chạy script, đọc kết quả, trả lời người dùng.

Luật quản lý dự án (`inputs/` · `outputs/`) ở `AGENTS.md` của workspace. Đọc nó trước.

## Bước 1. Chốt đầu vào và chế độ

- **Đầu vào:** link YouTube, đường dẫn file video, hoặc thư mục dự án `inputs/<dự án>` (khi hỏi lại về
  video đã có). Link YouTube phải để **Công khai** (Riêng tư hay Không công khai đều không đọc được).
  Chưa chắc video đã có dự án chưa thì chạy `--ds` xem trước.
- **Chế độ:** chọn theo việc người dùng muốn. Prompt từng chế độ ở `references/che-do.md`.

| Người dùng muốn | `--che-do` | Cần `--hoi`? |
|---|---|---|
| Tóm tắt, ý chính, mốc quan trọng (bài giảng, podcast, buổi họp) | `tom-tat` | không |
| Cắt clip ngắn, highlight thể thao, đoạn đáng xem | `highlight` | không |
| Bản ghi màn hình bị lỗi, tìm mã lỗi | `loi` | không |
| "Lúc nào thì…", tìm một cảnh, một câu nói | `tim` | **có** |
| "Có bao nhiêu lần…" | `dem` | **có** |
| Câu hỏi khác về nội dung | `hoi` | **có** |

Không rõ người dùng muốn gì thì hỏi lại một câu, đừng chạy bừa: mỗi lần chạy là tốn token thật.

## Bước 2. Chạy thử, rồi chạy thật

Đứng ở thư mục gốc workspace (có `inputs/` và `outputs/`). Đường dẫn script tính từ
thư mục chứa skill này; dưới đây là đường trong workspace `gvideo`, skill cài global thì thay bằng đường thật.

```bash
uv run --script .agents/skills/phan-tich-video/scripts/phan_tich.py "<link|file|inputs/<dự án>>" --che-do <chế độ> [--hoi "..."] --thu
uv run --script .agents/skills/phan-tich-video/scripts/phan_tich.py "<link|file|inputs/<dự án>>" --che-do <chế độ> [--hoi "..."]
```

- `--thu` chỉ in sẽ làm gì (dự án nào, mới hay cũ, kết quả ghi đâu, prompt), không gọi API, không tạo
  thư mục. Chạy nó trước lần chạy thật đầu tiên của một dự án.
- Script tạo dự án mới thì ghi yêu cầu của người dùng vào mục "Người dùng muốn gì" của `inputs/<dự án>/nguon.md`.
- **File trong máy sẽ được tải lên Google** (Files API, Google tự xoá sau 48 giờ). Video riêng tư,
  có thông tin nhạy cảm thì hỏi người dùng trước khi chạy.
- `--so-sanh` chạy thêm kiểu cũ (static) để so token. Tốn gấp đôi, chỉ dùng khi người dùng muốn so.
- `--model` mặc định `gemini-3.7-flash`. Model có agentic: 3.7 Flash, 3.6 Flash, 3.5 Flash-Lite.
- Lỗi thiếu key: bảo người dùng lấy key ở aistudio.google.com/apikey rồi tạo file `.env` ở gốc workspace, một dòng `GEMINI_API_KEY=<key>`.
  **Không đọc, không in nội dung `.env`.**

## Bước 3. Đọc kết quả và trả lời

Script in đường dẫn thư mục kết quả `outputs/<dự án>/<YYYYMMDD_HHMMSS>_<chế độ>/`:

- `bao-cao.md`: câu trả lời của Gemini
- `RUN.md`: video nào, model, token, số lần AI quay lại xem
- `so-do.json`: số đo dạng máy đọc

Trả lời người dùng bằng tiếng Việt: nội dung chính của `bao-cao.md` (giữ nguyên các mốc thời gian),
kèm một dòng số đo (token vào, số lần AI quay lại xem) và đường dẫn thư mục.

**Đừng thêm mốc thời gian, con số hay chi tiết mà `bao-cao.md` không có.** Bạn chưa xem video.
Người dùng hỏi tiếp về cùng video thì chạy lại trên `inputs/<dự án>` với `--che-do hoi --hoi "..."`,
đừng đoán từ báo cáo cũ và đừng tạo dự án mới.
