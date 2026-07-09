# Ứng dụng phân tích nhân tố

Ứng dụng Python hỗ trợ khám phá cấu trúc nhân tố tiềm ẩn trong dữ liệu định
lượng. Dự án cung cấp giao diện desktop bằng Tkinter và giao diện dòng lệnh,
thực hiện phân tích nhân tố (Factor Analysis), thống kê mô tả, xác định số nhân
tố phù hợp và dùng mô hình chạy qua Ollama để gợi ý tên cho từng nhân tố.

## Chức năng chính

### 1. Phân tích nhân tố

- Đọc và chuẩn hóa dữ liệu từ file CSV.
- Trích xuất nhân tố bằng `factor-analyzer`.
- Hỗ trợ cấu hình số nhân tố, ngưỡng hệ số tải, phép xoay và phương pháp trích.
- Nếu không nhập số nhân tố, chương trình tự chọn theo quy tắc Kaiser
  (`eigenvalue > 1`).
- Nhóm các biến có hệ số tải vượt ngưỡng theo từng nhân tố.
- Gọi Ollama để gợi ý tên và giải thích ý nghĩa của các nhân tố.
- Xuất kết quả phân tích ra file JSON.

### 2. Thống kê mô tả

- Giá trị nhỏ nhất và lớn nhất.
- Trung bình.
- Phương sai mẫu.
- Ma trận hiệp phương sai mẫu.

### 3. Xác định số nhân tố

Ứng dụng so sánh ba phương pháp:

- **Quy tắc Kaiser:** giữ các nhân tố có trị riêng lớn hơn 1.
- **Scree Plot:** vẽ dãy trị riêng và ước lượng điểm khuỷu của đồ thị.
- **Parallel Analysis (Horn):** so sánh trị riêng quan sát với phân vị 95% của
  trị riêng sinh từ dữ liệu ngẫu nhiên, tương ứng mức ý nghĩa `α = 0,05`.

Mỗi phương pháp đều trả về số nhân tố đề xuất `m` và giải thích lý do lựa chọn.
Tab này cũng hiển thị trực tiếp biểu đồ Scree Plot.

## Cấu trúc thư mục

```text
.
├── data/                       # Dữ liệu CSV mẫu và kết quả mẫu
│   ├── OCEAN.csv
│   ├── OCEAN_preprocessed.csv
│   ├── sample.csv
│   └── sample_factor_analysis.csv
├── docs/                       # Đặc tả, kiến trúc và báo cáo dự án
├── scripts/
│   ├── run_gui.ps1             # Chạy giao diện desktop trên PowerShell
│   └── run_cli.ps1             # Chạy chương trình dòng lệnh
├── src/
│   ├── __main__.py             # Entry point cho `python -m src`
│   ├── main_gui.py             # Giao diện Tkinter
│   ├── main_cli.py             # Giao diện dòng lệnh
│   ├── data_processor.py       # Đọc, kiểm tra và chuẩn hóa dữ liệu
│   ├── factor_analysis.py      # Các thuật toán phân tích nhân tố
│   └── llm_namer.py            # Tích hợp Ollama để đặt tên nhân tố
├── tests/                      # Kiểm thử tự động
├── pyproject.toml              # Metadata và dependencies của dự án
├── requirements.txt            # Danh sách thư viện Python
└── uv.lock                     # Lockfile dùng với uv
```

## Yêu cầu

- Python 3.12 trở lên.
- Tkinter (thường được cài kèm Python trên Windows).
- Ollama nếu muốn ứng dụng tự động đặt tên và giải thích các nhân tố.

Dữ liệu đầu vào phải là file CSV:

- Có hàng tiêu đề chứa tên biến.
- Chỉ chứa các cột kiểu số.
- Không chứa ô trống hoặc giá trị `NaN`.
- Mỗi cột cần có phương sai khác 0.

## Cài đặt

Clone repo và chuyển vào thư mục dự án:

```powershell
git clone <repository-url>
cd MSA-Do-an
```

### Cách 1: dùng uv

```powershell
uv sync
```

### Cách 2: dùng pip

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Cấu hình Ollama

Mặc định ứng dụng gọi model `llama3` tại
`http://localhost:11434/api/generate`.

```powershell
ollama pull llama3
ollama serve
```

Có thể thay đổi endpoint và model qua biến môi trường:

```powershell
$env:OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
$env:OLLAMA_MODEL = "llama3"
```

Nếu Ollama không hoạt động, phần tính toán nhân tố vẫn được thực hiện nhưng tên
nhân tố sẽ được ghi là `LLM_Error_Factor` cùng thông báo lỗi kết nối.

## Chạy ứng dụng

### Giao diện desktop

Khi dùng uv:

```powershell
uv run python -m src
```

Khi đã kích hoạt virtual environment:

```powershell
python -m src
```

Trên PowerShell cũng có thể dùng:

```powershell
.\scripts\run_gui.ps1
```

### Giao diện dòng lệnh

Ví dụ cơ bản:

```powershell
python -m src.main_cli data\sample_factor_analysis.csv
```

Ví dụ chỉ định đầy đủ tham số:

```powershell
python -m src.main_cli data\OCEAN_preprocessed.csv `
  --factors 5 `
  --threshold 0.4 `
  --rotation varimax `
  --method minres `
  --output results.json
```

Các tham số CLI:

| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `input_file` | Đường dẫn file CSV đầu vào | Bắt buộc |
| `-f`, `--factors` | Số nhân tố; `0` để dùng Kaiser | `0` |
| `-t`, `--threshold` | Ngưỡng trị tuyệt đối của hệ số tải | `0.4` |
| `-r`, `--rotation` | Phép xoay nhân tố | `varimax` |
| `-m`, `--method` | Phương pháp trích nhân tố | `minres` |
| `-o`, `--output` | File JSON đầu ra | `results.json` |

Script PowerShell tương đương:

```powershell
.\scripts\run_cli.ps1 data\sample_factor_analysis.csv `
  --factors 3 --output results.json
```

## Hướng dẫn sử dụng GUI

### Tab “Phân tích nhân tố”

1. Nhấn **Chọn file CSV** và chọn dữ liệu cần phân tích.
2. Nhập **Số nhân tố**, hoặc để trống để chương trình dùng quy tắc Kaiser.
3. Nhập **Ngưỡng tải**; giá trị thường dùng là `0.4`.
4. Nhấn **Chạy phân tích**.
5. Xem các biến thuộc từng nhân tố, hệ số tải, tên và phần giải thích.
6. Nhấn **Lưu JSON** để lưu kết quả.

### Tab “Thống kê mô tả”

1. Chọn file CSV.
2. Nhấn **Tính các đại lượng**.
3. Xem bảng thống kê và ma trận hiệp phương sai.

### Tab “Xác định số nhân tố”

1. Chọn file CSV.
2. Nhấn **Xác định số nhân tố**.
3. So sánh kết quả từ Kaiser, Scree Plot và Parallel Analysis.
4. Quan sát điểm khuỷu, đường `Kaiser = 1` và ngưỡng Parallel Analysis trên
   biểu đồ trước khi quyết định giá trị `m`.

Parallel Analysis là khuyến nghị chính vì có đối chứng bằng dữ liệu ngẫu nhiên;
Kaiser và Scree Plot nên được dùng để kiểm tra chéo cùng kiến thức chuyên môn.

## Chạy kiểm thử

```powershell
python -m unittest discover -s tests
```

## Kết quả JSON

Kết quả phân tích có cấu trúc theo từng nhân tố:

```json
{
  "Factor_1": {
    "llm_name": "Tên nhân tố được đề xuất",
    "explanation": "Giải thích ngắn về ý nghĩa nhân tố.",
    "features": [
      {
        "feature": "Tên biến",
        "loading": 0.75
      }
    ]
  }
}
```
