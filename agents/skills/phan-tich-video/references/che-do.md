# Các chế độ phân tích

Mỗi mục `## <tên>` là một chế độ, script đọc đúng khối `text` ngay dưới nó làm prompt. Thêm chế độ thì
thêm một mục theo đúng khuôn này, không phải sửa script. `{hoi}` là chỗ điền câu hỏi của người dùng (`--hoi`).

Sáu chế độ rút từ những gì video *Agentic Video Understanding* nêu (tóm tắt bài giảng, cắt highlight,
bắt lỗi trong bản ghi màn hình) cộng bốn việc Google liệt kê trong docs (tìm đúng khoảnh khắc, mò kim
đáy bể trong video dài, phát hiện bất thường, đếm vật/hành động).

Luật chung cho mọi prompt: mốc thời gian dạng `MM:SS` (hoặc `H:MM:SS`), trả lời tiếng Việt, không thấy
thì nói không thấy, không đoán cho đủ.

## tom-tat — tóm tắt bài giảng, podcast, buổi họp

```text
Xem video này và tóm tắt bằng tiếng Việt.

1. Một đoạn 3–4 câu: video nói về gì, cho ai, kết luận chính là gì.
2. Bảng các mốc quan trọng: | Mốc | Nội dung | Vì sao đáng chú ý |. Mốc dạng MM:SS (hoặc H:MM:SS).
   Chỉ ghi mốc đã tự xem lại đoạn đó, không ước lượng.
3. Ba ý đáng nhớ nhất, mỗi ý kèm mốc thời gian.
4. Ngữ cảnh: thứ người xem cần biết trước mới hiểu được video (thuật ngữ, bối cảnh), nếu có.

Không thấy thì ghi "không thấy", không đoán.
```

## highlight — khoảnh khắc đáng cắt thành clip ngắn

```text
Tìm các khoảnh khắc đáng cắt thành clip ngắn (thể thao: bàn thắng, pha cứu thua, tình huống gây tranh cãi;
nội dung khác: câu nói đắt, cao trào, đoạn bất ngờ).

Trả về bảng: | # | Bắt đầu | Kết thúc | Chuyện gì xảy ra | Vì sao đáng cắt | Gợi ý tiêu đề clip |.
Bắt đầu–kết thúc dạng MM:SS, mỗi clip 5–60 giây, lùi bắt đầu vài giây để người xem kịp hiểu bối cảnh.
Xếp theo độ đáng xem giảm dần. Tối đa 10 clip. Chỉ ghi mốc đã tự xem lại, không ước lượng.
Trả lời tiếng Việt.
```

## loi — bắt lỗi trong bản ghi màn hình

```text
Đây là bản ghi màn hình. Tìm mọi chỗ có lỗi: thông báo lỗi, mã lỗi, stack trace, cảnh báo đỏ/vàng,
thao tác bị từ chối, màn hình treo, kết quả khác với điều người dùng đang cố làm.

Với mỗi lỗi trả về:
- Mốc MM:SS lúc lỗi hiện ra
- Chép NGUYÊN VĂN chữ lỗi đọc được trên màn hình (không dịch, không sửa). Đọc không rõ thì ghi "[mờ]".
- Người dùng đang làm gì ngay trước đó (mốc + thao tác)
- Nguyên nhân có thể, ghi rõ là phỏng đoán
- Cách sửa gợi ý, nếu có

Cuối cùng: lỗi nào là gốc, lỗi nào kéo theo. Không thấy lỗi thì nói rõ là không thấy. Trả lời tiếng Việt.
```

## tim — tìm đúng khoảnh khắc

```text
Tìm trong video: {hoi}

Trả về mọi lần nó xuất hiện: | Mốc | Đã thấy gì (mô tả cụ thể) | Chắc chắn đến đâu (chắc / khá chắc / không chắc) |.
Mốc dạng MM:SS, chính xác tới giây. Chỉ ghi mốc đã tự xem lại đoạn đó.
Không tìm thấy thì nói thẳng "không thấy", và kể đã xem những đoạn nào. Trả lời tiếng Việt.
```

## dem — đếm vật hoặc hành động

```text
Đếm trong video: {hoi}

1. Con số cuối cùng.
2. Bảng từng lần: | # | Mốc MM:SS | Mô tả ngắn |.
3. Trường hợp không chắc có tính hay không: liệt kê riêng, nói vì sao.
Không đoán cho tròn số. Trả lời tiếng Việt.
```

## hoi — câu hỏi tự do

```text
{hoi}

Trả lời dựa trên chính video, mỗi ý kèm mốc thời gian MM:SS làm bằng chứng.
Phần nào video không nói tới thì ghi rõ là video không nói, không lấy kiến thức ngoài lấp vào.
Trả lời tiếng Việt.
```
