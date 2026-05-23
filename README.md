# 🛡️ Hệ Thống Mô Phỏng Đòn Tấn Công Diện Rộng & Đánh Giá Chỉ Số Giảm Thiểu Rủi Ro ($R_{mit}$)

Dự án này xây dựng một đường ống dữ liệu (Data Pipeline) tự động bằng Python nhằm thực nghiệm xung kích dữ liệu lớn (Big Data Stress Testing) trên nền tảng Thương mại điện tử thử nghiệm OWASP Juice Shop.

Hệ thống thực hiện bóc tách, đánh giá định lượng mã trạng thái HTTP, thời gian phản hồi vi mô ($T_{res}$) trước và sau khi triển khai các cơ chế vá lỗi lớp sâu.

---

# 📁 1. Cấu Trúc Thư Mục Dự Án

```text
Ecom_Simulation/
├── datasets/
│   ├── dataset_sqli.txt
│   ├── dataset_xss.txt
│   └── dataset_system.txt
│
├── run_simulation_3k_final.py
├── run_mitigation_simulation.py
├── visualize_3k_metrics.py
├── visualize_mitigation_comparison.py
├── summary_table.py
├── .gitignore
└── README.md
```

### Mô tả thành phần

| Thành phần | Vai trò |
|------------|----------|
| `datasets/` | Bộ dữ liệu payload mô phỏng SQL Injection, XSS và Command Injection / SSRF |
| `run_simulation_3k_final.py` | Pha 1 - Mô phỏng trạng thái hệ thống trước giảm thiểu |
| `run_mitigation_simulation.py` | Pha 2 - Mô phỏng cơ chế giảm thiểu bảo mật |
| `visualize_3k_metrics.py` | Trực quan hóa chỉ số hiệu năng ban đầu |
| `visualize_mitigation_comparison.py` | So sánh trước và sau triển khai giảm thiểu |
| `summary_table.py` | Tổng hợp chỉ số nghiên cứu và tính toán $R_{mit}$ |

---

# 🚀 2. Hướng Dẫn Cài Đặt & Vận Hành

## Bước 1. Khởi động môi trường mục tiêu

Đảm bảo OWASP Juice Shop đang hoạt động:

```bash
http://localhost:3000
```

---

## Bước 2. Cài đặt thư viện phụ thuộc

Mở Terminal tại thư mục dự án:

```bash
pip install requests pandas statistics matplotlib seaborn tabulate openpyxl
```

---

## Bước 3. Thực thi Pha 1 — Thu thập số liệu thực trạng

Chạy mô phỏng tấn công dữ liệu lớn:

```bash
python run_simulation_3k_final.py
```

Đầu ra:

```text
bao_cao_dinh_luong_loi.csv
```

---

## Bước 4. Thực thi Pha 2 — Đánh giá hiệu quả giảm thiểu

Chạy cơ chế giả lập bảo vệ:

- Parameterized Query
- Input Sanitization
- Domain Whitelist

Thực thi:

```bash
python run_mitigation_simulation.py
```

Đầu ra:

```text
bao_cao_dinh_luong_sau_va_loi.csv
```

---

## Bước 5. Trực quan hóa và kết xuất báo cáo

Sinh biểu đồ phân tích:

```bash
python visualize_3k_metrics.py

python visualize_mitigation_comparison.py
```

Xuất bảng tổng hợp nghiên cứu:

```bash
python summary_table.py
```

---

# 📊 3. Chỉ Số Đầu Ra Nghiên Cứu

Sau khi hoàn thành toàn bộ pipeline, hệ thống sinh tự động:

### 1. Bảng tổng hợp số liệu

```text
bang_thong_ke_truoc_sau_v2.md
```

Phục vụ sao chép trực tiếp vào báo cáo nghiên cứu.

### 2. Tệp Excel chuẩn hóa

```text
bang_thong_ke_truoc_sau_v2.xlsx
```

Dùng cho phụ lục nghiên cứu và trình bày kết quả.

### 3. Biểu đồ trực quan hóa

```text
visualize_security_mitigation.png
```

Thể hiện xu hướng thay đổi chỉ số an ninh trước và sau triển khai cơ chế bảo vệ.

---

# ⚙️ 4. Quy Trình Xử Lý Dữ Liệu

```text
Dataset Payload
      ↓
Pha 1 - Attack Simulation
      ↓
Raw Metrics Collection
      ↓
Mitigation Layer
      ↓
Post-Mitigation Measurement
      ↓
Visualization
      ↓
Research Output
```

---

# ⚖️ 5. Chính Sách Quản Lý Mã Nguồn (Git Policy)

Nguyên tắc lưu trữ:

✅ Theo dõi phiên bản:

- Python source code (`*.py`)
- Tập dữ liệu mẫu (`datasets/*.txt`)
- README và tài liệu hướng dẫn

❌ Không theo dõi:

- File kết quả trung gian (`*.csv`)
- File Excel đầu ra (`*.xlsx`)
- File cache hoặc dữ liệu phát sinh cục bộ

Ví dụ `.gitignore`

```gitignore
*.csv
*.xlsx
__pycache__/
*.pyc
```

---

# 📌 Mục Tiêu Nghiên Cứu

- Đánh giá khả năng chịu tải của hệ thống TMĐT trước kịch bản tấn công diện rộng
- Định lượng hiệu quả cơ chế giảm thiểu thông qua chỉ số $R_{mit}$
- Xây dựng quy trình mô phỏng có khả năng tái lập phục vụ nghiên cứu học thuật

---

# 👥 Nhóm Thực Hiện

**E-Commerce Security Final Project — Group 4**

Môn học: **Bảo mật Thương mại điện tử**

Nền tảng thử nghiệm:

- OWASP Juice Shop
- Python Data Pipeline
- Security Stress Testing Framework

---

> Academic purpose only — phục vụ nghiên cứu và thực nghiệm bảo mật trong môi trường kiểm thử.
