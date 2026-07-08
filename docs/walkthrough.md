# Tổng kết: Ứng dụng Phân Tích Nhân Tố (Factor Analysis) kết hợp LLM

Quá trình xây dựng ứng dụng theo đặc tả `docs/SPEC.md` đã hoàn tất. Dưới đây là các thành phần chính đã được triển khai:

## 1. Các tệp đã được tạo

- **Môi trường**: 
  - `requirements.txt` ở thư mục gốc: Chứa danh sách các thư viện cần thiết (`pandas`, `scikit-learn`, `factor_analyzer`, `requests`, v.v.).
  - `.env`: File cấu hình cục bộ chứa thiết lập kết nối đến Ollama API.
- **Logic Cốt lõi**:
  - `data_processor.py`: Đọc dữ liệu CSV, xử lý ngoại lệ khi thiếu dữ liệu (missing values) và chuẩn hóa dữ liệu.
  - `factor_analysis.py`: Áp dụng thuật toán Factor Analysis. Tự động tính toán số lượng nhân tố (nếu cần) bằng Eigenvalue > 1. Lọc các thuộc tính theo ngưỡng tải.
  - `llm_namer.py`: Sinh prompt với định dạng chặt chẽ yêu cầu mô hình LLM trả về chuỗi JSON chứa tên nhân tố (khái quát) và giải thích.
- **Giao diện Người dùng**:
  - `main_cli.py`: Giao diện terminal sử dụng `argparse` cho phép truyền các tham số một cách linh hoạt và xuất file `.json` tự động.
  - `main_gui.py`: Giao diện Desktop trực quan xây dựng bằng Tkinter. Hỗ trợ chọn tệp dễ dàng, cấu hình ngưỡng tải, chạy phân tích trên thread riêng (không gây đơ màn hình), và lưu kết quả JSON.

## 2. Hướng dẫn sử dụng nhanh

### 2.1 Cài đặt
1. Cài đặt các thư viện: `pip install -r requirements.txt`
2. Cấu hình `OLLAMA_ENDPOINT` / `OLLAMA_MODEL` trong `.env` nếu cần thiết (mặc định là llama3).

### 2.2 Chạy ứng dụng qua CLI
Bạn có thể chạy thử lệnh sau để hiểu cách hoạt động:
```bash
python -m src.main_cli path/to/your/data.csv -f 0 -t 0.4 -r varimax -o my_results.json
```
Trong đó:
- `-f 0`: Tự động tìm số nhân tố.
- `-t 0.4`: Ngưỡng hệ số tải.
- `-o my_results.json`: Nơi xuất kết quả.

### 2.3 Chạy ứng dụng qua GUI
Chỉ cần gọi lệnh:
```bash
python -m src.main_gui
```
Cửa sổ sẽ hiện lên. Bạn chọn tệp CSV, chỉnh sửa các tham số và bấm "Chạy phân tích". Kết quả phân tích sẽ được in trực tiếp lên cửa sổ dưới dạng văn bản và có thể lưu lại thông qua nút bấm "Lưu Kết Quả (JSON)".

## 3. Tương lai
- Nếu cần, bạn có thể kiểm thử mã nguồn này trên dữ liệu thực tế.
- Trong trường hợp mô hình LLM bị lỗi trả về không phải JSON chuẩn (nếu dùng các model nhỏ), hàm xử lý trong `llm_namer.py` đã có phần fallback để không làm hỏng toàn bộ quá trình. Tuy nhiên, khuyến nghị sử dụng mô hình có khả năng xuất JSON tốt như `llama3` hoặc `mistral`.
