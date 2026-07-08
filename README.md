# Ứng dụng phân tích nhân tố

Ứng dụng đọc dữ liệu CSV, thực hiện Factor Analysis và dùng Ollama để gợi ý tên
cho các nhân tố tiềm ẩn.

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
