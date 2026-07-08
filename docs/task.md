# Danh sách công việc (Task Tracking)

Tiến độ thực hiện các tính năng của ứng dụng Phân Tích Nhân Tố kết hợp LLM.

- `[x]` **Setup môi trường**
  - `[x]` Tạo file `requirements.txt`.
  - `[x]` Tạo file cấu hình `.env`.
- `[x]` **Xây dựng Logic Cốt lõi (Core Logic)**
  - `[x]` Code `data_processor.py` (Đọc dữ liệu, kiểm tra lỗi missing, chuẩn hóa).
  - `[x]` Code `factor_analysis.py` (Chạy FA, xoay trục, lọc hệ số tải, phân cụm đặc trưng).
  - `[x]` Code `llm_namer.py` (Gọi API Ollama, trả về JSON, prompt cấu trúc).
- `[x]` **Giao diện người dùng**
  - `[x]` Code `main_cli.py` (Nhận tham số, in kết quả, lưu json).
  - `[x]` Code `main_gui.py` (Tkinter GUI, hiển thị kết quả, lưu file).
- `[x]` **Xác minh & Hoàn thiện**
  - `[x]` Xác minh chức năng chạy thử trên dữ liệu mẫu.
