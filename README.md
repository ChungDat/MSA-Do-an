# Ứng dụng phân tích nhân tố

Ứng dụng đọc dữ liệu CSV, thực hiện Factor Analysis và dùng Ollama để gợi ý tên
cho các nhân tố tiềm ẩn. Giao diện cũng cung cấp tab thống kê mô tả để tính min,
max, mean, phương sai mẫu và ma trận hiệp phương sai.

Khi ô **Số nhân tố** để trống, chương trình áp dụng tiêu chuẩn Kaiser và chọn tất
cả nhân tố có trị riêng lớn hơn 1. Các trị riêng và số nhân tố được chọn được
hiển thị ở đầu kết quả.

## Cấu trúc

```text
.
├── docs/             # Đặc tả và tài liệu dự án
├── scripts/          # Script khởi chạy trên PowerShell
├── src/              # Package Python của ứng dụng
├── thirdparty/bot/   # Điểm tích hợp bot/Ollama
├── requirements.txt
└── pyproject.toml
```

## Cài đặt và chạy

```powershell
pip install -r requirements.txt

# GUI
python -m src

# CLI
python -m src.main_cli sample.csv -o results.json
```

Có thể dùng `scripts/run_gui.ps1` và `scripts/run_cli.ps1` để chạy nhanh trên
PowerShell.
