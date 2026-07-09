# Specification: Ứng dụng Phân Tích Nhân Tố (Factor Analysis) và Rút Trích Đặc Trưng Ẩn

## 1. Tổng quan
Dự án nhằm xây dựng một ứng dụng phân tích dữ liệu hỗ trợ Phân tích Nhân tố (Factor Analysis). Điểm nổi bật của ứng dụng là khả năng tự động phân tích ngữ nghĩa các thuộc tính thành phần và đặt tên cho các nhân tố ẩn (latent features) bằng cách sử dụng Mô hình Ngôn ngữ Lớn (LLM).

## 2. Các tác vụ và luồng công việc (Workflow)
1. **Nhập dữ liệu đầu vào**:
   - Ứng dụng cho phép đọc dữ liệu từ tệp định dạng `.csv`.
   - Cấu trúc tệp: Dòng đầu tiên (row 1) bắt buộc là header (tên các thuộc tính/biến quan sát), các dòng tiếp theo chứa dữ liệu dạng số.
   - **Xử lý dữ liệu lỗi**: Nếu dữ liệu chứa giá trị thiếu (missing values/NaN), chương trình sẽ báo lỗi và yêu cầu người dùng tự làm sạch dữ liệu trước khi chạy tiếp (không tự động xử lý).
2. **Cấu hình tham số**:
   - Người dùng có thể tùy chọn số lượng nhân tố (number of factors) mong muốn trích xuất. Nếu không thiết lập, chương trình sẽ tự động xác định số lượng nhân tố dựa trên tiêu chuẩn Eigenvalue > 1.
   - Người dùng có thể thiết lập ngưỡng hệ số tải (factor loading threshold) làm tham số đầu vào để xác định thuộc tính nào sẽ được gắn với nhân tố nào.
3. **Phân tích nhân tố (Factor Analysis)**:
   - Thực hiện các tiền xử lý cơ bản (chuẩn hóa dữ liệu nếu cần).
   - Chạy thuật toán Factor Analysis để gom nhóm các thuộc tính. Cấu hình mặc định sử dụng phép xoay **Varimax** và phương pháp trích xuất **minres**. Người dùng có thể thay đổi sang các phương pháp khác được hỗ trợ bởi thư viện `factor_analyzer`.
4. **Rút trích tên đặc trưng ẩn (Latent Feature Naming)**:
   - Nhóm tên các thuộc tính thuộc về cùng một nhân tố.
   - Tạo prompt và gửi tới LLM để phân tích sự tương đồng ngữ nghĩa.
   - Yêu cầu LLM trả về kết quả dưới định dạng **JSON**, bao gồm: tên nhân tố (ngắn gọn, khái quát) và lời giải thích ngắn gọn lý do chọn tên đó.
5. **Đầu ra (Output)**:
   - Hiển thị danh sách các nhân tố ẩn (kèm tên mới và giải thích), các thuộc tính thành phần được đại diện và **hệ số tải** (factor loading) tương ứng của chúng.
   - Kết quả này sẽ được lưu vào một tệp tin `.json` do người dùng đặt tên.

## 3. Tech Stack (Công nghệ sử dụng)
- **Ngôn ngữ**: Python
- **Xử lý dữ liệu & Thống kê**: 
  - `pandas`: Đọc và thao tác với tệp `.csv`.
  - `numpy`: Xử lý mảng và tính toán.
  - `factor_analyzer` hoặc `scikit-learn`: Thực thi thuật toán Factor Analysis và xoay trục (vd: Varimax) để xác định rõ ràng sự gắn kết của các thuộc tính với các nhân tố.
- **Giao diện người dùng**:
  - Hỗ trợ cả 2 chế độ: Giao diện dòng lệnh (CLI) và Giao diện đồ họa (GUI) sử dụng `tkinter`.
- **Tích hợp LLM**: 
  - `Ollama`: Nền tảng chạy các mô hình LLM cục bộ (local). Đảm bảo tính riêng tư cho dữ liệu (không cần gọi API ra ngoài internet) và tốc độ suy luận nhanh.
  - Cấu hình thông qua file `.env`: Người dùng cần nhập endpoint của LLM (vd: URL của Ollama) và các cấu hình liên quan vào file `.env` (sử dụng thư viện `python-dotenv`).
  - Các thư viện gọi HTTP Request (như `requests`) hoặc `langchain` để giao tiếp với API của Ollama.

## 4. Cấu trúc chương trình dự kiến
- `main_cli.py`: File thực thi dành cho giao diện dòng lệnh (CLI).
- `main_gui.py`: File thực thi dành cho giao diện đồ họa (GUI) bằng `tkinter`.
- `.env`: File cấu hình cục bộ chứa endpoint của LLM và các biến môi trường khác.
- `data_processor.py`: Chứa các hàm đọc file `.csv`, kiểm tra và tiền xử lý dữ liệu.
- `factor_analysis.py`: Chứa logic phân tích nhân tố, tìm ra ma trận factor loadings và phân cụm thuộc tính.
- `llm_namer.py`: Chứa logic tạo prompt, kết nối với Ollama và lấy kết quả trả về.
- `requirements.txt` ở thư mục gốc: Danh sách các thư viện Python cần cài đặt.

## 5. Yêu cầu môi trường (Environment Requirements)
- Python 3.12+
- Cài đặt Ollama trên máy tính (`https://ollama.com/`).
- Tải sẵn một mô hình ngôn ngữ (ví dụ: `llama3` hoặc `mistral`) thông qua lệnh: `ollama pull llama3`.
