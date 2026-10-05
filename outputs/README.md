# outputs

Kết quả. Thư mục `outputs/<dự án>/` cùng tên với `inputs/<dự án>/`. Mỗi lần phân tích là một thư mục con
`<YYYYMMDD_HHMMSS>_<chế độ>/`:

- `bao-cao.md`: câu trả lời của Gemini
- `bao-cao-static.md`: chỉ có khi chạy `--so-sanh`
- `RUN.md`: video, model, chế độ, token, số lần AI quay lại xem
- `so-do.json`: số đo dạng máy đọc

Không ghi đè, không đổi tên. Mốc thời gian là của AI: đem đi dùng thì mở video kiểm lại.
