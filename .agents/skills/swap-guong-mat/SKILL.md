---
name: swap-guong-mat
description: Thay gương mặt từ ảnh tham chiếu vào ảnh hoặc video bằng FaceFusion local. Dùng khi người dùng yêu cầu face swap, swap gương mặt, phục hồi identity Linh/Đạt hoặc thay mặt trong ảnh cưới/video đã có.
---

# Swap gương mặt

Đọc AGENTS.md ở gốc workspace. Chạy script ở gốc bằng `uv run --script`.
Dùng FaceFusion **3.9.0** cài riêng, không tải media lên Google/Gemini.
Không tuyên bố giống 100% hay chất lượng cao nhất nếu chưa so mẫu thực tế.

## Chuẩn bị runtime

Cài FaceFusion theo hướng dẫn chính thức https://docs.facefusion.io/installation.
Checkout tag `3.9.0` từ https://github.com/facefusion/facefusion trong thư mục ngoài workspace.
Cài FFmpeg (bao gồm ffprobe) và môi trường FaceFusion theo nền tảng; không pip install vào workspace gvideo.
Truyền `--facefusion-dir /duong/dan/facefusion` và `--python /duong/dan/python-cua-facefusion`.
Có thể dùng biến môi trường `FACEFUSION_DIR` và `FACEFUSION_PYTHON`; không đọc hoặc in .env.
FaceFusion tự tải model lần đầu; cần mạng và dung lượng, CPU chạy được nhưng chậm với video.

## Chọn đầu vào

- Dùng một hoặc nhiều ảnh rõ của **cùng một người** cho `--source`. Mỗi ảnh nguồn chỉ có một mặt.
- Dùng ảnh/video cần thay mặt cho `--target`; không chép hoặc di chuyển media.
- Chọn đường dẫn mới trong `outputs/<dự án>/` cho `--output`; không ghi đè kết quả cũ.
- Chọn người cần thay trong target bằng `--face-position` (0 là người bên trái theo `--face-order left-right`).
  Với video, chọn `--reference-frame` có mặt người đó rõ và `--reference-distance 0.3` để bám identity target.
  Nếu có nhiều người và chưa rõ cần thay ai, hỏi trước khi chạy render.
- Không gom ảnh Linh và Đạt thành một source. Thay từng người qua hai lượt, lấy kết quả lượt trước làm target lượt sau;
  kiểm tra lại thứ tự mặt và frame tham chiếu ở mỗi lượt.

## Chạy thử rồi chạy thật

```bash
uv run --script .agents/skills/swap-guong-mat/scripts/face_swap.py --source inputs/linh.jpg --target inputs/canh-cuoi.mp4 --output outputs/canh-cuoi/linh-swap.mp4 --facefusion-dir /opt/facefusion --python /opt/facefusion-python/bin/python --face-position 0 --thu
```

Bỏ `--thu` sau khi kiểm tra đúng đường dẫn và người cần thay. Dry-run không tạo thư mục hoặc tải model.
Thêm `--provider cuda` cho NVIDIA hoặc `--provider coreml` cho Apple khi runtime có provider đó.
Mặc định dùng CPU, HyperSwap 1A 256 + GFPGAN 1.4 blend 30, ảnh quality 100, video H.264 quality 95,
scale 1.0. Giữ FPS theo FaceFusion mặc định của nguồn; không tăng thành 60 fps.
Dùng `--enhancer-blend 0` để bỏ enhancer nếu mặt bị đẹp hóa hoặc lệch nét.
Đổi model bằng `--model`; để FaceFusion kiểm tra model hợp lệ cho tag đã cài.

## Đọc kết quả

Chỉ báo hoàn tất khi script exit 0 và đầu ra có dữ liệu. Đọc RUN.json và facefusion.log trong thư mục run
nằm cạnh đầu ra. Nếu thất bại, báo lỗi thực tế từ log; không giới thiệu file dở dang là thành phẩm.
Kiểm tra mặt có đúng người, cằm và mắt có lệch không, viền mặt có lỗi không; đối với video dùng workflow
phân tích của workspace khi cần xem nội dung, không tự mô tả cảnh chưa được phân tích.
Đề nghị render ảnh/đoạn ngắn để người dùng kiểm tra identity trước video dài; không hứa khóa góc mặt tuyệt đối.

## Giấy phép

Mã FaceFusion 3.9.0 ghi OpenRAIL-AS; metadata HyperSwap 1A ghi ResearchRAIL, GFPGAN 1.4 ghi Apache-2.0.
Kiểm tra điều khoản đầy đủ của model và các model phụ thuộc trước khi dùng thương mại; khả năng đổi model
không tự đảm bảo toàn bộ pipeline có quyền thương mại.
Nguồn CLI đã đối chiếu: https://github.com/facefusion/facefusion/tree/3.9.0/facefusion.
