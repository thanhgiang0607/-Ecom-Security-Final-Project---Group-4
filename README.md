# 🛡️ Hệ Thống Mô Phỏng Đòn Tấn Công Diện Rộng & Đánh Giá Chỉ Số Giảm Thiểu Rủi Ro

Dự án xây dựng một hệ thống mô phỏng kiểm thử áp lực bảo mật (Security Stress Testing) trên nền tảng thương mại điện tử OWASP Juice Shop thông qua Data Pipeline tự động bằng Python.

Hệ thống thực hiện:

- Mô phỏng nhiều dạng payload tấn công phổ biến
- Thu thập mã trạng thái HTTP và thời gian phản hồi vi mô ($T_{res}$)
- Định lượng hiệu quả cơ chế giảm thiểu rủi ro
- Sinh biểu đồ và bảng tổng hợp phục vụ nghiên cứu học thuật

---

# 📁 1. Cấu Trúc Thư Mục Dự Án

```text
Ecom_Security_Final_Project/
│
├── analytics/
│   ├── comparison.py
│   ├── remediation.py
│   ├── results_visualize.py
│   ├── risk_quantitative.py
│   └── summary_table.py
│
├── datasets/
│   ├── dataset_sqli.txt
│   ├── dataset_system.txt
│   └── dataset_xss.txt
│
├── experiments/
│   ├── remediation.py
│   └── simulation.py
│
├── results/
│   ├── bao_cao_dinh_luong_loi.csv
│   ├── bao_cao_dinh_luong_sau_va_loi.csv
│   ├── chuong4_kb01_sqli.png
│   ├── chuong4_kb02_xss.png
│   ├── chuong4_kb03_system.png
│   ├── chuong4_owasp_risk_matrix.png
│   ├── chuong4_tres_distribution.png
│   ├── chuong5_kb01_remediation.png
│   ├── chuong5_kb02_remediation.png
│   ├── chuong5_kb03_remediation.png
│   ├── chuong5_owasp_heatmap_shift.png
│   ├── chuong5_tres_comparison.png
│   ├── visualize_detailed_errors.png
│   └── visualize_security_mitigation.png
│
├── .gitignore
└── README.md
```

---

# 📌 2. Mô Tả Thành Phần

| Thành phần | Vai trò |
|------------|----------|
| `datasets/` | Bộ payload mô phỏng SQL Injection, XSS, Command Injection và SSRF |
| `experiments/simulation.py` | Phase 1 — Mô phỏng trạng thái hệ thống trước giảm thiểu |
| `experiments/remediation.py` | Phase 2 — Mô phỏng cơ chế vá lỗi và giảm thiểu |
| `analytics/results_visualize.py` | Trực quan hóa dữ liệu hiệu năng và lỗi |
| `analytics/comparison.py` | So sánh chỉ số trước và sau triển khai bảo mật |
| `analytics/risk_quantitative.py` | Định lượng rủi ro bảo mật theo chỉ số nghiên cứu |
| `analytics/summary_table.py` | Tổng hợp bảng số liệu nghiên cứu |
| `results/` | Lưu toàn bộ kết quả CSV và biểu đồ trực quan hóa |

---

# 🚀 3. Hướng Dẫn Cài Đặt & Vận Hành

## Bước 1. Khởi động môi trường OWASP Juice Shop

Đảm bảo hệ thống mục tiêu đang hoạt động:

```bash
http://localhost:3000
```

Có thể triển khai bằng Docker:

```bash
docker run -d -p 3000:3000 bkimminich/juice-shop
```

---

## Bước 2. Cài đặt thư viện phụ thuộc

Mở Terminal tại thư mục dự án:

```bash
pip install requests pandas matplotlib seaborn tabulate openpyxl
```

---

## Bước 3. Thực thi Phase 1 — Attack Simulation

Mô phỏng lưu lượng tấn công diện rộng:

```bash
python experiments/simulation.py
```

Đầu ra:

```text
results/bao_cao_dinh_luong_loi.csv
```

---

## Bước 4. Thực thi Phase 2 — Security Remediation

Mô phỏng cơ chế giảm thiểu:

- Parameterized Query
- Input Sanitization
- Domain Whitelist
- Request Filtering

Thực thi:

```bash
python experiments/remediation.py
```

Đầu ra:

```text
results/bao_cao_dinh_luong_sau_va_loi.csv
```

---

## Bước 5. Phân tích & Trực quan hóa dữ liệu

Sinh biểu đồ phân tích:

```bash
python analytics/results_visualize.py

python analytics/comparison.py
```

Định lượng rủi ro:

```bash
python analytics/risk_quantitative.py
```

Xuất bảng tổng hợp:

```bash
python analytics/summary_table.py
```

---

# 📊 4. Chỉ Số Đầu Ra Nghiên Cứu

Sau khi hoàn thành pipeline, hệ thống tự động sinh:

## 1. Bảng số liệu nghiên cứu

```text
bao_cao_dinh_luong_loi.csv
bao_cao_dinh_luong_sau_va_loi.csv
```

---

## 2. Biểu đồ trực quan hóa

### Giai đoạn mô phỏng tấn công

```text
chuong4_kb01_sqli.png
chuong4_kb02_xss.png
chuong4_kb03_system.png
chuong4_owasp_risk_matrix.png
chuong4_tres_distribution.png
```

### Giai đoạn giảm thiểu bảo mật

```text
chuong5_kb01_remediation.png
chuong5_kb02_remediation.png
chuong5_kb03_remediation.png
chuong5_owasp_heatmap_shift.png
chuong5_tres_comparison.png
```

### Tổng hợp phân tích

```text
visualize_detailed_errors.png
visualize_security_mitigation.png
```

---

# ⚙️ 5. Quy Trình Xử Lý Dữ Liệu

```text
Dataset Payload
        ↓
Attack Simulation
        ↓
HTTP Metrics Collection
        ↓
Risk Quantification
        ↓
Security Mitigation
        ↓
Post-Mitigation Measurement
        ↓
Visualization & Analytics
        ↓
Research Output
```

---

# 📈 6. Chỉ Số Định Lượng Nghiên Cứu

Hệ thống tập trung đánh giá:

- HTTP Status Distribution
- Error Frequency
- Response Time ($T_{res}$)
- OWASP Risk Level
- Risk Reduction Score ($R_{mit}$)
- Security Heatmap Transition

---

# ⚖️ 7. Chính Sách Quản Lý Mã Nguồn (Git Policy)

## Theo dõi phiên bản

✅ Bao gồm:

- Source code Python (`*.py`)
- Dataset mô phỏng (`datasets/*.txt`)
- README và tài liệu hướng dẫn

## Không theo dõi

❌ Loại trừ:

- File cache
- File sinh tự động
- Dataset tạm thời

Ví dụ `.gitignore`:

```gitignore
__pycache__/
*.pyc
*.xlsx
.DS_Store
```

---

# 🎯 8. Mục Tiêu Nghiên Cứu

- Đánh giá khả năng chịu tải của hệ thống TMĐT trước tấn công diện rộng
- Định lượng hiệu quả cơ chế giảm thiểu thông qua chỉ số $R_{mit}$
- Phân tích biến động mức độ rủi ro OWASP trước và sau remediation
- Xây dựng mô hình nghiên cứu có khả năng tái lập trong môi trường học thuật

---

# 🧪 9. Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
|------------|------------|
| Ngôn ngữ | Python |
| Hệ thống mục tiêu | OWASP Juice Shop |
| Xử lý dữ liệu | Pandas |
| Visualization | Matplotlib, Seaborn |
| Xuất báo cáo | OpenPyXL |
| Kiểm thử | Security Stress Testing |

---

# 👥 10. Nhóm Thực Hiện 

**Đồ án cuối kỳ — Bảo mật Thương mại điện tử**

Nhóm thực hiện: **Nhóm 4**

| Họ và tên | MSSV |
|---|---|
| Nguyễn Vũ Thanh Giang| 31231026898 |
| Nguyễn Tùng Chi | 31231027333 |
| Lâm Bảo Nghi | 31231020352 |
| Đinh Thị Quỳnh Như | 31231025829 |
| Nguyễn Thị Trúc Quỳnh| 31231021679 |

Nền tảng nghiên cứu:

- OWASP Juice Shop
- Python Data Pipeline
- Security Stress Testing Framework

---

> Academic purpose only — phục vụ nghiên cứu và thực nghiệm bảo mật trong môi trường kiểm thử.