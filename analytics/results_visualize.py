import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

# Đọc file dữ liệu 3000 mẫu quy mô lớn mới
df = pd.read_csv('../results/bao_cao_dinh_luong_loi.csv')
df['HTTP Status'] = df['HTTP Status'].astype(str)

# BIỂU ĐỒ 1: PHÂN PHỐI MÃ TRẠNG THÁI HTTP (HTTP STATUS CODE DISTRIBUTION)
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, x='Loại Tấn Công', hue='HTTP Status', ax=ax, palette='viridis', edgecolor='black')
ax.set_title('Phân Phối Mã Trạng Thái HTTP Giữa Các Kịch Bản Tấn Công (3000 Samples)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Loại Tấn Công (Attack Type)', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Lượng Gói Tin (Request Count)', fontsize=12, fontweight='bold')
ax.legend(title='HTTP Status Code', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('visualize_http_status.png', dpi=300)
plt.close()
print("✔ Đã xuất biểu đồ: visualize_http_status.png")

# BIỂU ĐỒ 2: THỜI GIAN PHẢN HỒI TRUNG BÌNH (RESPONSE TIME BENCHMARK - Tres)
fig, ax = plt.subplots(figsize=(10, 6))
mean_times = df.groupby('Loại Tấn Công')['Thời Gian (s)'].mean().reset_index().sort_values(by='Thời Gian (s)', ascending=False)

sns.barplot(data=df, x='Loại Tấn Công', y='Thời Gian (s)', order=mean_times['Loại Tấn Công'], ax=ax, palette='magma', errorbar=None, edgecolor='black')
ax.set_title('Thời Gian Phản Hồi Trung Bình (Tres) Của Hệ Thống Dưới Áp Lực Tấn Công', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Loại Tấn Công (Attack Type)', fontsize=12, fontweight='bold')
ax.set_ylabel('Thời Gian Phản Hồi Trung Bình (giây)', fontsize=12, fontweight='bold')

for p in ax.patches:
    ax.annotate(f"{p.get_height():.4f} s", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('visualize_response_time.png', dpi=300)
plt.close()
print("✔ Đã xuất biểu đồ: visualize_response_time.png")

# BIỂU ĐỒ 3: THỐNG KÊ CHI TIẾT BẢN CHẤT LỖI CỤ THỂ (DETAILED ERROR ANALYTICS)
fig, ax = plt.subplots(figsize=(12, 7))

sns.countplot(data=df, y='Kết Quả Thực Nghiệm', hue='Loại Tấn Công', ax=ax, palette='Set2', edgecolor='black',
              order=df['Kết Quả Thực Nghiệm'].value_counts().index)

ax.set_title('Thống Kê Chi Tiết Bản Chất Lỗi Hệ Thống Theo Từng Phân Hệ', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Số Lượng Request Ghi Nhận (Count)', fontsize=12, fontweight='bold')
ax.set_ylabel('Bản Chất Kỹ Thuật Lỗi / Kết Quả', fontsize=12, fontweight='bold')
ax.legend(title='Phân Hệ Kịch Bản', loc='lower right')

for p in ax.patches:
    if p.get_width() > 0:  # Loại bỏ các nhãn trống của các phân hệ khác
        ax.annotate(f" {int(p.get_width())} reqs", (p.get_width(), p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('visualize_detailed_errors.png', dpi=300)
plt.close()
print("✔ Đã xuất biểu đồ nâng cấp chi tiết lỗi: visualize_detailed_errors.png")