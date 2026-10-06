# gvideo

Workspace nhỏ cho **Google Antigravity**: đưa vào một video (file trong máy hoặc link YouTube), nhận về bản
phân tích có mốc thời gian. Gemini xem video ở chế độ **agentic**: AI tự quay lại xem đúng đoạn cần thay vì
nuốt cả video, nên tốn ít token hơn hẳn (Google công bố tới 88%).

Dựng 2026-10-05, từ câu hỏi của khán giả về reel `video-lab/projects/20260930_142024_agentic-video`.

**Tác giả & Bản quyền:** Dự án này thuộc về [Fx Studio](https://fxstudio.dev/). Mọi mục đích sử dụng phải tuân thủ theo giấy phép đính kèm.

## Cài một lần

1. Lấy key ở https://aistudio.google.com/apikey
2. Tạo file `gvideo/.env` có đúng một dòng: `GEMINI_API_KEY=<key vừa lấy>`. File này không vào git.
3. Máy cần có `uv` (https://docs.astral.sh/uv/). Thư viện `google-genai` tự cài khi chạy lần đầu.
4. Mở thư mục `gvideo/` bằng Antigravity (File → Open Folder).

## Dùng trong Antigravity

Nói với agent bằng tiếng Việt, kèm file hoặc link:

```
/phan-tich-video tóm tắt https://youtu.be/xxxxxxxxxxx
Video ~/Desktop/tran-dau.mp4: cắt giúp mấy pha highlight
Bản ghi màn hình ~/Desktop/loi-build.mov bị lỗi gì?
Trong video này lúc nào người nói nhắc tới "context window"?
```

Agent tự chọn chế độ, chạy script, rồi trả lời. Luật cho agent ở [AGENTS.md](AGENTS.md).

## Quản lý theo dự án

Mỗi video là một dự án, cùng tên ở hai nơi:

```
inputs/20261005_143000_yt-7Z5Vy9JBANs/
└── nguon.md                       link / đường dẫn video + muốn gì
outputs/20261005_143000_yt-7Z5Vy9JBANs/
├── 20261005_143012_tom-tat/       mỗi lần phân tích một thư mục
│   ├── bao-cao.md · RUN.md · so-do.json
└── 20261005_150200_tim/
```

- Đưa link hoặc file lần đầu: script tự tạo dự án. Đưa lại đúng link/file đó: dùng lại dự án cũ.
- Muốn giữ video trong workspace: bỏ file vào `inputs/<dự án>/` (không vào git).
- Hỏi lại về video cũ: truyền `inputs/<dự án>` thay cho link.
- Xem danh sách: `uv run --script .agents/skills/phan-tich-video/scripts/phan_tich.py --ds`

## Sáu chế độ

| Chế độ | Làm gì |
|---|---|
| `tom-tat` | Tóm tắt + bảng mốc quan trọng + 3 ý đáng nhớ |
| `highlight` | Đoạn đáng cắt thành clip ngắn, có bắt đầu–kết thúc |
| `loi` | Bắt lỗi trong bản ghi màn hình, chép nguyên văn chữ lỗi |
| `tim` | Tìm mọi lần một thứ xuất hiện |
| `dem` | Đếm vật hoặc hành động, kèm từng mốc |
| `hoi` | Câu hỏi tự do, mỗi ý kèm mốc làm bằng chứng |

Thêm chế độ: thêm một mục vào `.agents/skills/phan-tich-video/references/che-do.md`, không phải sửa script.

## Chạy tay, không cần Antigravity

```bash
S=.agents/skills/phan-tich-video/scripts/phan_tich.py
uv run --script $S https://youtu.be/xxxxxxxxxxx --che-do tom-tat --thu      # xem sẽ làm gì
uv run --script $S https://youtu.be/xxxxxxxxxxx --che-do tom-tat            # chạy thật
uv run --script $S inputs/<dự án> --che-do tim --hoi "lúc nào có logo"   # hỏi lại video cũ
uv run --script $S video.mp4 --che-do tom-tat --so-sanh                     # so token với kiểu cũ
```

## Dùng skill ở mọi workspace Antigravity

Chép thư mục `.agents/skills/phan-tich-video/` sang `~/.gemini/config/skills/` (Antigravity IDE) hoặc
`~/.gemini/antigravity-cli/skills/` (CLI). Script luôn dùng `inputs/` · `outputs/` · `.env` của **thư mục
đang mở**, nên workspace khác cũng có dự án riêng. Nhớ chép kèm phần "Quản lý dự án" của `AGENTS.md`.

## Giới hạn (theo docs Google, tra 2026-10-05)

- YouTube: chỉ video **Công khai**. Gói miễn phí tối đa 8 giờ video YouTube mỗi ngày.
- File: tối đa 2 GB (miễn phí) / 20 GB (trả phí). Google tự xoá file đã tải lên sau 48 giờ.
- Model có agentic: Gemini 3.7 Flash, 3.6 Flash, 3.5 Flash-Lite.
- Giá: tính theo token thường, không thu thêm phí cho agentic.

## Trạng thái

- ✅ Script chạy `--thu` được, thư viện `google-genai` 2.28 có sẵn `processing: "agentic"` (kiểm mã nguồn).
- ✅ Đã chạy thật thành công với cả link YouTube và file video local. Chi tiết xem tại [EXAMPLE.md](EXAMPLE.md).
- ✅ Đã mở trong Antigravity, skill tự kích hoạt và phối hợp mượt mà với các công cụ CLI (`ffmpeg`, `yt-dlp`).

Nguồn: [Google Blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/) ·
[Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding) ·
[Antigravity: Skills](https://antigravity.google/docs/skills?app=antigravity-ide)

## Swap gương mặt ảnh/video (FaceFusion local)

Skill mới: `.agents/skills/swap-guong-mat/`. Ví dụ trong Antigravity:

```text
/swap-guong-mat dùng ảnh Linh làm source, thay mặt người bên trái trong video này
```

Cần cài riêng FaceFusion 3.9.0 và FFmpeg theo hướng dẫn trong [SKILL.md](.agents/skills/swap-guong-mat/SKILL.md).
Script hỗ trợ chạy thử `--thu`, chọn mặt target, đổi model, tắt enhancer và ghi log từng lượt.
Mặc định HyperSwap 1A + GFPGAN blend 30; không bảo đảm giữ identity tuyệt đối.
Đã cài runtime FaceFusion 3.9.0 + FFmpeg, tải và xác minh hash các model của preset,\nvà chạy thành công pipeline ảnh với source/target mẫu chính thức trên CPU (2026-10-06).\nChưa đánh giá độ giống mặt Linh/Đạt hoặc render video thực tế. Mỗi máy chạy vẫn cần cài runtime riêng.
