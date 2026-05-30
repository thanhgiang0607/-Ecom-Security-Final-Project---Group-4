import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

FILE_PRE = '../results/bao_cao_dinh_luong_loi.csv'
FILE_POST = '../results/bao_cao_dinh_luong_sau_va_loi.csv'
OUTPUT_IMAGE = 'visualize_security_mitigation.png'

if not os.path.exists(FILE_PRE) or not os.path.exists(FILE_POST):
    print("❌ Thiếu file dữ liệu thực nghiệm! Vui lòng chạy cả 2 kịch bản mô phỏng trước.")
    exit()

# 1. Đọc dữ liệu và dán nhãn trạng thái Thực nghiệm
df_pre = pd.read_csv(FILE_PRE)
df_pre['Giai Đoạn'] = 'Trước khi vá'

df_post = pd.read_csv(FILE_POST)
df_post['Giai Đoạn'] = 'Sau khi vá'

# 2. Gom nhóm các kết quả nguy hiểm cần theo dõi trực quan
def categorize_result(row):
    res = row['Kết Quả Thực Nghiệm']
    status = str(row['HTTP Status'])
    
    if 'Chiếm quyền' in res or 'vào luồng xử lý OS' in res:
        return 'Lọt lưới nguy hiểm (200/201)'
    elif 'Rò rỉ cấu trúc SQLite' in res or 'HTTP 500' in status or 'Crash hệ thống' in res:
        return 'Lỗi hệ thống thô (HTTP 500)'
    elif 'TIMEOUT' in status or 'Mất kết nối' in res:
        return 'Nghẽn mạch vật lý (TIMEOUT)'
    else:
        return 'Chặn an toàn (HTTP 400/401)'

df_pre['Phân Loại Bảo Mật'] = df_pre.apply(categorize_result, axis=1)
df_post['Phân Loại Bảo Mật'] = df_post.apply(categorize_result, axis=1)

# Gộp 2 bảng dữ liệu lớn lại làm một để phân tích đối chứng
df_combined = pd.concat([df_pre, df_post], ignore_index=True)

# 3. Tiến hành vẽ đồ thị so sánh diện rộng
fig, ax = plt.subplots(figsize=(13, 7))

# Sắp xếp thứ tự hiển thị để nhấn mạnh các ca nguy hiểm lên đầu
plot_order = [
    'Lọt lưới nguy hiểm (200/201)', 
    'Lỗi hệ thống thô (HTTP 500)', 
    'Nghẽn mạch vật lý (TIMEOUT)', 
    'Chặn an toàn (HTTP 400/401)'
]

sns.countplot(
    data=df_combined, 
    y='Phân Loại Bảo Mật', 
    hue='Giai Đoạn', 
    order=plot_order, 
    ax=ax, 
    palette='vlag', 
    edgecolor='black'
)

# Cấu trúc tiêu đề và dán nhãn đồ thị khoa học
ax.set_title('Đánh giá trước và sau khi vá lỗi', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Số Lượng Request Ghi Nhận Diện Rộng (Count)', fontsize=12, fontweight='bold')
ax.set_ylabel('Trạng Thái Thực Nghiệm Bảo Mật', fontsize=12, fontweight='bold')
ax.legend(title='Kịch Bản Thực Nghiệm', loc='lower right', fontsize=11)

for p in ax.patches:
    width = p.get_width()
    if width > 0: # Bỏ qua các thanh có giá trị bằng 0
        ax.annotate(
            f" {int(width):,} reqs", 
            (width, p.get_y() + p.get_height() / 2.),
            ha='left', 
            va='center', 
            xytext=(5, 0), 
            textcoords='offset points', 
            fontsize=10, 
            fontweight='bold'
        )

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300)
plt.close()

