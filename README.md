# Scan Transcript AI

Dự án quét bảng điểm và cung cấp API để trả về kết quả OCR và file Excel.

## Cấu trúc mới

- app.py: entrypoint Flask API
- pipeline.py: orchestrates table detection + OCR + export
- services/: module riêng cho OCR, table detection, title detection, export Excel
- config.py: cấu hình thư mục đầu vào/đầu ra
- legacy_compat.py: wrapper tương thích với import cũ

## Chạy ứng dụng

1. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```

2. Chạy server:
   ```bash
   python app.py
   ```

3. Gửi request:
   - POST /upload với field files
   - GET /health để kiểm tra trạng thái
   - GET /download/<filename> để tải file Excel
