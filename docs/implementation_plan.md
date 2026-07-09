# Kế hoạch Triển khai Ứng dụng Phân Tích Nhân Tố kết hợp LLM

Dựa trên đặc tả `SPEC.md` đã được chốt, đây là kế hoạch chi tiết để xây dựng ứng dụng phân tích dữ liệu, tự động gom nhóm và đặt tên nhân tố thông qua mô hình ngôn ngữ lớn (Ollama).

## User Review Required

> [!IMPORTANT]
> Vui lòng xem qua cấu trúc các tệp dự kiến dưới đây. Nếu mọi thứ đúng với thiết kế của bạn, hãy bấm "Approve" (Phê duyệt) để tôi tiến hành tạo danh sách công việc (`task.md`) và bắt đầu viết mã.

## Proposed Changes

### 1. Cấu hình & Môi trường

#### [NEW] [requirements.txt](file:///home/chungdat/HCMUS/2025-2026_HK2/Multivariate%20Statistical%20Analysis/Do%20an/Src/requirements.txt)
Danh sách các thư viện Python:
- `pandas`: Đọc, xử lý DataFrame.
- `numpy`: Tính toán ma trận.
- `factor_analyzer`: Chạy thuật toán Factor Analysis.
- `scikit-learn`: Chuẩn hóa dữ liệu (StandardScaler).
- `python-dotenv`: Đọc biến môi trường.
- `requests`: Giao tiếp HTTP với Ollama.

#### [NEW] `.env`
File mẫu chứa cấu hình:
- `OLLAMA_ENDPOINT=http://localhost:11434/api/generate`
- `OLLAMA_MODEL=llama3`

---

### 2. Các Module Cốt lõi (Core Logic)

#### [NEW] [data_processor.py](file:///home/chungdat/HCMUS/2025-2026_HK2/Multivariate%20Statistical%20Analysis/Do%20an/Src/data_processor.py)
- Đọc dữ liệu từ file `.csv`.
- Kiểm tra tính hợp lệ: Báo lỗi nếu có dữ liệu bị thiếu (Missing values).
- Chuẩn hóa (standardize) tập dữ liệu đầu vào.

#### [NEW] [factor_analysis.py](file:///home/chungdat/HCMUS/2025-2026_HK2/Multivariate%20Statistical%20Analysis/Do%20an/Src/factor_analysis.py)
- Phân tích nhân tố với tuỳ chọn phương pháp xoay (mặc định Varimax) và phương pháp trích xuất (mặc định minres).
- Tự động tính số lượng nhân tố dựa trên giá trị Eigenvalue > 1 (nếu người dùng không cung cấp số lượng).
- Lọc các thuộc tính theo ngưỡng hệ số tải (`factor loading threshold`) do người dùng cài đặt. Trả về cấu trúc dữ liệu gồm các nhóm biến theo nhân tố và hệ số tải tương ứng.

#### [NEW] [llm_namer.py](file:///home/chungdat/HCMUS/2025-2026_HK2/Multivariate%20Statistical%20Analysis/Do%20an/Src/llm_namer.py)
- Đọc biến môi trường từ `.env` để lấy thiết lập model.
- Thiết kế Prompt yêu cầu mô hình tổng hợp tên đại diện cho các nhóm biến.
- Gửi HTTP POST request tới Ollama, yêu cầu trả về chuẩn định dạng JSON chứa hai trường: Tên nhân tố (khái quát) và Lời giải thích ngắn.

---

### 3. Giao diện Người dùng

#### [NEW] [main_cli.py](file:///home/chungdat/HCMUS/2025-2026_HK2/Multivariate%20Statistical%20Analysis/Do%20an/Src/main_cli.py)
- File chạy cho chế độ dòng lệnh (CLI), sử dụng thư viện `argparse`.
- Cho phép người dùng truyền đầu vào như: file csv, số lượng nhân tố, ngưỡng tải, đường dẫn xuất kết quả `.json`.
- In kết quả thẳng ra terminal và tự động lưu JSON.

#### [NEW] [main_gui.py](file:///home/chungdat/HCMUS/2025-2026_HK2/Multivariate%20Statistical%20Analysis/Do%20an/Src/main_gui.py)
- Sử dụng thư viện `tkinter` để thiết kế giao diện dạng cửa sổ.
- Có các thành phần: Chọn tệp CSV, nhập số lượng nhân tố, ngưỡng hệ số tải, chọn phương pháp FA, và nút bấm "Chạy phân tích".
- Cửa sổ văn bản (hoặc bảng) hiển thị kết quả (Tên nhân tố, thuộc tính, hệ số tải).
- Nút bấm lưu báo cáo dạng tệp JSON.

## Verification Plan

### Automated Tests
- Do tính chất tích hợp ứng dụng giao diện và tương tác mô hình, dự án không thiết lập automated test.

### Manual Verification
1. Dùng bộ dữ liệu `.csv` mẫu (tạo ra hoặc tải trên mạng) để chạy `main_cli.py`.
2. Kiểm tra xem file `.json` đầu ra có đúng cấu trúc hay không.
3. Chạy lệnh `python main_gui.py`, chọn tham số và kiểm tra hành vi báo lỗi (nếu dữ liệu thiếu) và tính năng kết xuất file.
