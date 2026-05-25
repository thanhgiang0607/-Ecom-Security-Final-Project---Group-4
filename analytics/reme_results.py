import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# Cấu hình phong cách đồ thị học thuật chuẩn UEH
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
palette_phase = {'Trước khắc phục (Pha A)': '#D9534F', 'Sau khắc phục (Pha B)': '#4A90E2'}

# 1. ĐỊNH NGHĨA ĐƯỜNG DẪN LOG THÔ ĐẦU VÀO
FILE_LOG_PHA_A = "../results/bao_cao_dinh_luong_loi.csv"
FILE_LOG_PHA_B = "../results/bao_cao_dinh_luong_sau_va_loi.csv"
OUTPUT_DIR = "../results"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Kiểm tra sự tồn tại của các file log thực nghiệm
if not os.path.exists(FILE_LOG_PHA_A) or not os.path.exists(FILE_LOG_PHA_B):
    print("❌ Lỗi: Thiếu file log thực nghiệm Pha A hoặc Pha B để trích xuất số liệu động!")
    exit()

# 2. ĐỌC VÀ TIỀN XỬ LÝ DỮ LIỆU ĐỘNG TỪ LOG THÔ
df_a = pd.read_csv(FILE_LOG_PHA_A)
df_b = pd.read_csv(FILE_LOG_PHA_B)

# Chuẩn hóa tên cột và dữ liệu chữ
for df in [df_a, df_b]:
    df.columns = df.columns.str.strip()
    df['Mã KB'] = df['Mã KB'].astype(str).str.strip()
    df['HTTP Status'] = df['HTTP Status'].astype(str).str.strip()

# Hàm xử lý bóc tách dữ liệu động cho từng kịch bản
def process_dynamic_scenario(ma_kb, mapping_labels):
    sub_a = df_a[df_a['Mã KB'] == ma_kb]
    sub_b = df_b[df_b['Mã KB'] == ma_kb]
    
    # Tính toán tần suất động dựa trên mã HTTP phản hồi thực tế
    counts_a = sub_a['HTTP Status'].value_counts()
    counts_b = sub_b['HTTP Status'].value_counts()
    
    plot_data = []
    # Tổng hợp tất cả các mã HTTP xuất hiện ở cả 2 pha
    all_statuses = sorted(list(set(counts_a.index) | set(counts_b.index)))
    
    for status in all_statuses:
        label = mapping_labels.get(status, f"Mã HTTP {status}")
        plot_data.append({
            'Phân loại phản hồi': label,
            'Trước khắc phục (Pha A)': counts_a.get(status, 0),
            'Sau khắc phục (Pha B)': counts_b.get(status, 0)
        })
        
    df_plot = pd.DataFrame(plot_data)
    return df_plot.melt(id_vars='Phân loại phản hồi', var_name='Giai đoạn', value_name='Số lượng Reqs')

# =========================================================================
# 📊 XỬ LÝ ĐỘNG & VẼ ĐỒ THỊ KỊCH BẢN KB_01 (SQL INJECTION)
# =========================================================================
kb01_labels = {
    '200': '200\n(Lọt lưới độc hại)',
    '401': '401\n(Từ chối xác thực)',
    '500': '500\n(Sập luồng hệ thống)',
    'TIMEOUT': 'TIMEOUT\n(Nghẽn mạch)'
}
kb01_melted = process_dynamic_scenario('KB_01', kb01_labels)
n_kb01 = len(df_a[df_a['Mã KB'] == 'KB_01']) + len(df_b[df_b['Mã KB'] == 'KB_01'])

fig, ax = plt.subplots(figsize=(9, 5.5))
sns.barplot(data=kb01_melted, x='Phân loại phản hồi', y='Số lượng Reqs', hue='Giai đoạn', palette=palette_phase, ax=ax)
ax.set_title(f'PHÂN PHỐI MÃ PHẢN HỒI HTTP ĐỘNG - KỊCH BẢN KB_01 (SQL INJECTION)', fontsize=11, fontweight='bold', color='#1F497D', pad=15)
ax.set_xlabel('Trạng thái phân tách và phản hồi thực tế từ Backend', fontsize=10, fontweight='bold', labelpad=10)
ax.set_ylabel('Số lượng Gói tin (Requests)', fontsize=10, fontweight='bold')
ax.legend(loc='upper right', frameon=True, shadow=True)

for p in ax.patches:
    h = p.get_height()
    if h > 0:
        ax.annotate(f'{int(h):,}', (p.get_x() + p.get_width() / 2., h),
                    ha='center', va='baseline', fontsize=9, fontweight='bold', color='#333333', xytext=(0, 4), textcoords='offset points')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/chuong5_kb01_remediation.png', dpi=300)
plt.close()

# =========================================================================
# 📊 XỬ LÝ ĐỘNG & VẼ ĐỒ THỊ KỊCH BẢN KB_02 (STORED XSS)
# =========================================================================
kb02_labels = {
    '500': '500\n(Sập luồng lỗi thô)',
    '401': '401\n(Màng lọc bảo vệ)',
    '400': '400\n(Bad Request Schema)'
}
kb02_melted = process_dynamic_scenario('KB_02', kb02_labels)

fig, ax = plt.subplots(figsize=(7, 5.5))
sns.barplot(data=kb02_melted, x='Phân loại phản hồi', y='Số lượng Reqs', hue='Giai đoạn', palette=palette_phase, ax=ax)
ax.set_title(f'PHÂN PHỐI MÃ PHẢN HỒI HTTP ĐỘNG - KỊCH BẢN KB_02 (STORED XSS)', fontsize=11, fontweight='bold', color='#1F497D', pad=15)
ax.set_xlabel('Trạng thái phân tách và phản hồi thực tế từ Backend', fontsize=10, fontweight='bold', labelpad=10)
ax.set_ylabel('Số lượng Gói tin (Requests)', fontsize=10, fontweight='bold')
ax.legend(loc='upper right', frameon=True, shadow=True)

for p in ax.patches:
    h = p.get_height()
    if h > 0:
        ax.annotate(f'{int(h):,}', (p.get_x() + p.get_width() / 2., h),
                    ha='center', va='baseline', fontsize=9, fontweight='bold', color='#333333', xytext=(0, 4), textcoords='offset points')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/chuong5_kb02_remediation.png', dpi=300)
plt.close()

# =========================================================================
# 📊 XỬ LÝ ĐỘNG & VẼ ĐỒ THỊ KỊCH BẢN KB_03 (CMDi & SSRF)
# =========================================================================
kb03_labels = {
    '201': '201\n(Phản hồi nghiệp vụ)',
    '400': '400\n(Chặn độc hại / Regex)'
}
kb03_melted = process_dynamic_scenario('KB_03', kb03_labels)

fig, ax = plt.subplots(figsize=(8.5, 5.5))
sns.barplot(data=kb03_melted, x='Phân loại phản hồi', y='Số lượng Reqs', hue='Giai đoạn', palette=palette_phase, ax=ax)
ax.set_title(f'PHÂN PHỐI MÃ PHẢN HỒI HTTP ĐỘNG - KỊCH BẢN KB_03 (CMDi & SSRF)', fontsize=11, fontweight='bold', color='#1F497D', pad=15)
ax.set_xlabel('Trạng thái phân tách và phản hồi thực tế từ Backend', fontsize=10, fontweight='bold', labelpad=10)
ax.set_ylabel('Số lượng Gói tin (Requests)', fontsize=10, fontweight='bold')
ax.legend(loc='upper right', frameon=True, shadow=True)

for p in ax.patches:
    h = p.get_height()
    if h > 0:
        ax.annotate(f'{int(h):,}', (p.get_x() + p.get_width() / 2., h),
                    ha='center', va='baseline', fontsize=9, fontweight='bold', color='#333333', xytext=(0, 4), textcoords='offset points')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/chuong5_kb03_remediation.png', dpi=300)
plt.close()

print(f"✔ Hoàn thành! Toàn bộ số liệu phân phối đã được tính toán động và xuất ra thư mục: {OUTPUT_DIR}/")