# AGENTS.md — gvideo

Đọc file này trước khi làm bất cứ việc gì trong workspace.

## Đây là gì

Workspace phân tích video bằng **Gemini ở chế độ agentic**: đưa vào một video (file trong máy hoặc link
YouTube công khai), nhận về bản phân tích có mốc thời gian. Gemini tự quay lại xem đúng đoạn cần thay vì
nuốt cả video, nên tốn ít token hơn.

Ngôn ngữ làm việc: **tiếng Việt**.

**Bạn (agent) không tự xem video.** Việc xem do Gemini API làm, qua skill `phan-tich-video`
(`.agents/skills/phan-tich-video/`). Chưa chạy skill thì không mô tả nội dung một video.

## Bố cục

```
gvideo/
├── AGENTS.md            file này
├── README.md            hướng dẫn cho người
├── .env                 GEMINI_API_KEY (không đọc, không in, không commit)
├── .agents/skills/phan-tich-video/
│   ├── SKILL.md         cách chọn chế độ, chạy, trả lời
│   ├── scripts/phan_tich.py
│   └── references/che-do.md   prompt của 6 chế độ
├── inputs/              ĐẦU VÀO: mỗi video là một dự án
│   └── <YYYYMMDD_HHMMSS>_<slug>/
│       ├── nguon.md     link / đường dẫn video + người dùng muốn gì
│       └── <video>.mp4  (tuỳ chọn) video bỏ thẳng vào đây
└── outputs/             KẾT QUẢ: cùng tên dự án với inputs/
    └── <YYYYMMDD_HHMMSS>_<slug>/
        └── <YYYYMMDD_HHMMSS>_<chế độ>/   một lần phân tích
            ├── bao-cao.md      câu trả lời của Gemini
            ├── RUN.md          video, model, token, số lần AI quay lại xem
            └── so-do.json
```

## Quản lý dự án

- **Một video = một dự án.** Tên thư mục `<YYYYMMDD_HHMMSS>_<slug>`, giống nhau ở `inputs/` và `outputs/`.
  Slug: `yt-<id>` với link YouTube, tên file (chữ thường, gạch nối) với file máy.
- **Script tự tạo dự án.** Đưa link YouTube hoặc file nằm ngoài `inputs/` thì script tìm dự án đã ghi
  đúng nguồn đó trong `nguon.md`; chưa có thì tạo mới. Đừng tự `mkdir` dự án bằng tay.
- **Hỏi lại về một video đã có** thì truyền thư mục dự án (`inputs/<dự án>`), không tạo dự án mới.
- Người dùng muốn để video trong workspace thì **họ** bỏ file vào `inputs/<dự án>/`. Agent không chép,
  không dời video của người dùng.
- Sau khi script tạo dự án mới, ghi yêu cầu của người dùng vào mục "Người dùng muốn gì" của `nguon.md`.
- **Không đổi tên, không xoá, không gom** thư mục dự án hay thư mục kết quả. `RUN.md` tham chiếu tới chúng.
- Một dự án có nhiều lần phân tích: mỗi lần một thư mục con trong `outputs/<dự án>/`, không ghi đè lần cũ.
- Xem có những dự án nào: `uv run --script .agents/skills/phan-tich-video/scripts/phan_tich.py --ds`

## Luật bắt buộc

- **Không đọc, không in, không commit `.env`.** Key chỉ để script tự đọc. Thiếu key thì bảo người dùng
  lấy ở aistudio.google.com/apikey rồi tạo `.env` có một dòng `GEMINI_API_KEY=<key>`.
- **File video trong máy sẽ được tải lên Google** khi chạy thật (Files API, Google tự xoá sau 48 giờ).
  Video riêng tư, có thông tin nhạy cảm thì hỏi người dùng trước.
- Chạy `--thu` trước lần chạy thật đầu tiên của một dự án. Mỗi lần chạy thật là tốn token thật.
- **Không bịa** mốc thời gian, con số, chi tiết mà `bao-cao.md` không có.
- Chạy ở **gốc workspace** bằng `uv run --script`. Không tạo `.venv`, không `pip install`.
