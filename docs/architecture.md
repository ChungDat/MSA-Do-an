# Kiến trúc Ứng dụng Phân tích Nhân Tố & LLM

Tài liệu này mô tả chi tiết luồng dữ liệu (Data Flow) và kiến trúc tương tác giữa các thành phần trong ứng dụng, được tổng hợp sau toàn bộ quá trình xây dựng.

## Sơ đồ Luồng công việc (Workflow)

````mermaid
graph TD
    A[Người dùng] -->|Nhập File CSV, Cấu hình Tham số| B(Giao diện: CLI hoặc GUI)
    B -->|File Path| C{data_processor.py}
    C -->|Lỗi Thiếu Dữ Liệu| B
    C -->|Data DataFrame Chuẩn hóa| D{factor_analysis.py}
    D -->|Dict: Các nhóm thuộc tính| E{llm_namer.py}
    E -->|Gửi HTTP POST Prompt| F[Ollama API Local]
    F -->|Trả về Tên & Giải thích JSON| E
    E -->|Tổng hợp Kết quả| B
    B -->|Lưu Kết quả| G[(File JSON Đầu ra)]
````

## Chi tiết Các Lớp (Layers)

### 1. Giao diện (UI Layer)
- **`main_gui.py`**: Giao diện người dùng đồ họa bằng `tkinter`. Đặc điểm nổi bật là thiết kế sử dụng `threading` cho quá trình phân tích. Điều này giúp giao diện không bị "treo" (Not Responding) trong thời gian chờ mô hình LLM sinh văn bản, giúp tăng trải nghiệm người dùng.
- **`main_cli.py`**: Giao diện dòng lệnh giúp tự động hóa dễ dàng. Tích hợp `argparse` cho phép truy xuất mọi cấu hình trực tiếp từ terminal.

### 2. Tiền xử lý Dữ liệu (Data Layer)
- **`data_processor.py`**: Đóng vai trò là chốt chặn an toàn (Guardrail). 
  - Yêu cầu chặt chẽ về dữ liệu (không null, toàn bộ là dạng số).
  - Sử dụng `StandardScaler` (z-score normalization) để đưa mọi thuộc tính về cùng một không gian scale (trung bình 0, phương sai 1) - điều kiện bắt buộc để Factor Analysis hoạt động hiệu quả trên dữ liệu đa chiều khác biệt đơn vị.

### 3. Phân tích Thống kê (Statistical Layer)
- **`factor_analysis.py`**:
  - Hỗ trợ fallback: Tự động trích xuất các giá trị riêng (Eigenvalues) từ ma trận tương quan để tìm số lượng nhân tố tự nhiên của dữ liệu (Tiêu chuẩn Kaiser) nếu người dùng không biết trước cần chọn bao nhiêu.
  - Sử dụng phép xoay Varimax để tối đa hóa phương sai của các hệ số tải (loadings), giúp mỗi thuộc tính chỉ gắn chặt (loading cao) vào 1 nhân tố duy nhất, giảm độ nhiễu.

### 4. Khai thác Trí tuệ Nhân tạo (AI Layer)
- **`llm_namer.py`**: 
  - Xây dựng prompt tĩnh chuyên gia (Expert persona).
  - Tích hợp bắt lỗi parse JSON thủ công. LLM đôi khi trả về đoạn văn bản (markdown ` ```json `) bọc ngoài nội dung cần thiết. Mặc dù cấu hình payload là `format: "json"`, mã vẫn bọc khối lượng `try...catch` cẩn thận để đảm bảo không sụp đổ ứng dụng nếu AI bị "ảo giác" định dạng.
