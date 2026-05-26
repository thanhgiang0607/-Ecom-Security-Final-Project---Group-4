import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# --- CẤU HÌNH PHONG CÁCH ĐỒ THỊ ĐỊNH LƯỢNG CHUẨN UEH ---
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
palette_phase = {'Trước khắc phục (Pha A)': '#D9534F', 'Sau khắc phục (Pha B)': '#4A90E2'}
palette_colors = {'Pha A: Trước khắc phục (Thực trạng)': '#D9534F', 'Pha B: Sau khắc phục (Remediated)': '#4A90E2'}

FILE_LOG_PHA_A = "../results/bao_cao_dinh_luong_loi.csv"
FILE_LOG_PHA_B = "../results/bao_cao_dinh_luong_sau_va_loi.csv"
OUTPUT_DIR = "../results"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

if not os.path.exists(FILE_LOG_PHA_A) or not os.path.exists(FILE_LOG_PHA_B):
    print("❌ Lỗi: Thiếu file log thực nghiệm Pha A hoặc Pha B để trích xuất số liệu động!")
    exit()

df_a = pd.read_csv(FILE_LOG_PHA_A)
df_b = pd.read_csv(FILE_LOG_PHA_B)

for df in [df_a, df_b]:
    df.columns = df.columns.str.strip()
    df['Mã KB'] = df['Mã KB'].astype(str).str.strip()
    df['HTTP Status'] = df['HTTP Status'].astype(str).str.strip()

col_time_a = 'Response Time' if 'Response Time' in df_a.columns else 'Thời Gian (s)'
col_time_b = 'Response Time' if 'Response Time' in df_b.columns else 'Thời Gian (s)'

df_a[col_time_a] = pd.to_numeric(df_a[col_time_a], errors='coerce')
df_b[col_time_b] = pd.to_numeric(df_b[col_time_b], errors='coerce')
df_a = df_a.dropna(subset=[col_time_a])
df_b = df_b.dropna(subset=[col_time_b])

# =========================================================================
# 📈 PHẦN 1: TỰ ĐỘNG TÍNH TOÁN ĐỘNG BẢNG THỐNG KÊ MÔ TẢ ĐỐI CHỨNG T_res
# =========================================================================
tres_pha_a = df_a[col_time_a].values
tres_pha_b = df_b[col_time_b].values

def calculate_stats(array):
    return {
        'Mean': np.mean(array),
        'Median': np.median(array),
        'St.Dev': np.std(array, ddof=1),
        'P95': np.percentile(array, 95),
        'Max': np.max(array)
    }

stats_a = calculate_stats(tres_pha_a)
stats_b = calculate_stats(tres_pha_b)

summary_data = []
metrics_mapping = {
    'Mean': 'Giá trị trung bình (Mean)',
    'Median': 'Trung vị (Median)',
    'St.Dev': 'Độ lệch chuẩn (Std Dev)',
    'P95': 'Bách phân vị 95 (P95)',
    'Max': 'Giá trị cực đại (Max)'
}

for key, label in metrics_mapping.items():
    val_a = stats_a[key]
    val_b = stats_b[key]
    pct_change = ((val_b - val_a) / val_a) * 100 if val_a != 0 else 0
    summary_data.append({
        'Tham số thống kê': label,
        'Giai đoạn thực trạng (Pha A)': f"{val_a:.4f} s",
        'Giai đoạn khắc phục (Pha B)': f"{val_b:.4f} s",
        'Biến động hình học (%)': f"{pct_change:+.2f}%"
    })

df_summary_table = pd.DataFrame(summary_data)

print("\n📊 BẢNG ĐỐI CHỨNG HIỆU NĂNG T_res")
print("=" * 95)
print(df_summary_table.to_string(index=False))
print("=" * 95)


def process_dynamic_scenario(ma_kb, mapping_labels):
    sub_a = df_a[df_a['Mã KB'] == ma_kb]
    sub_b = df_b[df_b['Mã KB'] == ma_kb]
    
    counts_a = sub_a['HTTP Status'].value_counts()
    counts_b = sub_b['HTTP Status'].value_counts()
    
    plot_data = []
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

# --- KB_01 (SQL INJECTION) ---
kb01_labels = {'200': '200\n(Lọt lưới độc hại)', '401': '401\n(Từ chối xác thực)', '500': '500\n(Sập luồng hệ thống)', 'TIMEOUT': 'TIMEOUT\n(Nghẽn mạch)'}
kb01_melted = process_dynamic_scenario('KB_01', kb01_labels)
fig, ax = plt.subplots(figsize=(9, 5.5))
sns.barplot(data=kb01_melted, x='Phân loại phản hồi', y='Số lượng Reqs', hue='Giai đoạn', palette=palette_phase, ax=ax)
ax.set_title('PHÂN PHỐI MÃ PHẢN HỒI HTTP ĐỘNG - KỊCH BẢN KB_01 (SQL INJECTION)', fontsize=11, fontweight='bold', color='#1F497D', pad=15)
ax.set_xlabel('Trạng thái phân tách và phản hồi thực tế từ Backend', fontsize=10, fontweight='bold', labelpad=10)
ax.set_ylabel('Số lượng Gói tin (Requests)', fontsize=10, fontweight='bold')
ax.legend(loc='upper right', frameon=True, shadow=True)
for p in ax.patches:
    h = p.get_height()
    if h > 0: ax.annotate(f'{int(h):,}', (p.get_x() + p.get_width() / 2., h), ha='center', va='baseline', fontsize=9, fontweight='bold', color='#333333', xytext=(0, 4), textcoords='offset points')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/chuong5_kb01_remediation.png', dpi=300)
plt.close()

# --- KB_02 (STORED XSS) ---
kb02_labels = {'500': '500\n(Sập luồng lỗi thô)', '401': '401\n(Màng lọc bảo vệ)', '400': '400\n(Bad Request Schema)'}
kb02_melted = process_dynamic_scenario('KB_02', kb02_labels)
fig, ax = plt.subplots(figsize=(7, 5.5))
sns.barplot(data=kb02_melted, x='Phân loại phản hồi', y='Số lượng Reqs', hue='Giai đoạn', palette=palette_phase, ax=ax)
ax.set_title('PHÂN PHỐI MÃ PHẢN HỒI HTTP ĐỘNG - KỊCH BẢN KB_02 (STORED XSS)', fontsize=11, fontweight='bold', color='#1F497D', pad=15)
ax.set_xlabel('Trạng thái phân tách và phản hồi thực tế từ Backend', fontsize=10, fontweight='bold', labelpad=10)
ax.set_ylabel('Số lượng Gói tin (Requests)', fontsize=10, fontweight='bold')
ax.legend(loc='upper right', frameon=True, shadow=True)
for p in ax.patches:
    h = p.get_height()
    if h > 0: ax.annotate(f'{int(h):,}', (p.get_x() + p.get_width() / 2., h), ha='center', va='baseline', fontsize=9, fontweight='bold', color='#333333', xytext=(0, 4), textcoords='offset points')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/chuong5_kb02_remediation.png', dpi=300)
plt.close()

# --- KB_03 (CMDi & SSRF) ---
kb03_labels = {'201': '201\n(Phản hồi nghiệp vụ)', '400': '400\n(Chặn độc hại / Regex)'}
kb03_melted = process_dynamic_scenario('KB_03', kb03_labels)
fig, ax = plt.subplots(figsize=(8.5, 5.5))
sns.barplot(data=kb03_melted, x='Phân loại phản hồi', y='Số lượng Reqs', hue='Giai đoạn', palette=palette_phase, ax=ax)
ax.set_title('PHÂN PHỐI MÃ PHẢN HỒI HTTP ĐỘNG - KỊCH BẢN KB_03 (CMDi & SSRF)', fontsize=11, fontweight='bold', color='#1F497D', pad=15)
ax.set_xlabel('Trạng thái phân tách và phản hồi thực tế từ Backend', fontsize=10, fontweight='bold', labelpad=10)
ax.set_ylabel('Số lượng Gói tin (Requests)', fontsize=10, fontweight='bold')
ax.legend(loc='upper right', frameon=True, shadow=True)
for p in ax.patches:
    h = p.get_height()
    if h > 0: ax.annotate(f'{int(h):,}', (p.get_x() + p.get_width() / 2., h), ha='center', va='baseline', fontsize=9, fontweight='bold', color='#333333', xytext=(0, 4), textcoords='offset points')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/chuong5_kb03_remediation.png', dpi=300)
plt.close()

# =========================================================================
# 🎨 PHẦN 3: ĐỒ THỊ PHỨC HỢP ĐA TẦNG ĐỐI CHỨNG ĐỘ TRỄ VI MÔ T_res
# =========================================================================
data_a = pd.DataFrame({'Thời gian phản hồi $T_{res}$ (Giây)': tres_pha_a, 'Giai đoạn': 'Pha A: Trước khắc phục (Thực trạng)'})
data_b = pd.DataFrame({'Thời gian phản hồi $T_{res}$ (Giây)': tres_pha_b, 'Giai đoạn': 'Pha B: Sau khắc phục (Remediated)'})
df_total = pd.concat([data_a, data_b], ignore_index=True)

fig, (ax_box, ax_kde) = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True, gridspec_kw={"height_ratios": (.35, .65)})
fig.suptitle('PHÂN TÍCH BIẾN ĐỘNG CHUYỂN DỊCH HIỆU NĂNG VÀ ĐỘ TRỄ VI MÔ $T_{res}$ QUY MÔ TOÀN MẠNG\n(Đối chứng thực chứng giữa Pha thực trạng và Pha khắc phục)', fontsize=12, fontweight='bold', color='#1F497D', y=0.96)

sns.boxplot(data=df_total, x='Thời gian phản hồi $T_{res}$ (Giây)', y='Giai đoạn', hue='Giai đoạn', palette=palette_colors, ax=ax_box, linewidth=1.5, fliersize=4, flierprops={"marker": "x", "markeredgecolor": "#333333", "alpha": 0.4}, legend=False)
ax_box.set_title('Biểu đồ hộp (Boxplot) định vị các phân vị hình học và giá trị cực đoan (Outliers)', fontsize=10, fontweight='bold', loc='left', pad=8)
ax_box.set_ylabel('')
ax_box.set_xlabel('')

sns.kdeplot(data=df_total, x='Thời gian phản hồi $T_{res}$ (Giây)', hue='Giai đoạn', palette=palette_colors, fill=True, alpha=0.4, linewidth=2.5, common_norm=False, ax=ax_kde)
ax_kde.set_title('Biểu đồ phân phối mật độ xác suất (Kernel Density Estimate - KDE)', fontsize=10, fontweight='bold', loc='left', pad=8)
ax_kde.set_xlabel('Thời gian phản hồi $T_{res}$ (Đơn vị: Giây)', fontsize=11, fontweight='bold', labelpad=10)
ax_kde.set_ylabel('Mật độ phân bổ (Density)', fontsize=11, fontweight='bold')

max_x = max(np.max(tres_pha_a), np.max(tres_pha_b))
ax_kde.set_xlim(-0.1, min(max_x + 0.2, 4.0)) 
ax_kde.legend(title='Chu kỳ phân tích thực nghiệm', labels=['Pha B: Sau khắc phục (Remediated)', 'Pha A: Trước khắc phục (Thực trạng)'], loc='upper right', frameon=True, shadow=True)

plt.tight_layout()
plt.subplots_adjust(top=0.88, hspace=0.15)

OUTPUT_IMAGE = f"{OUTPUT_DIR}/chuong5_tres_comparison.png"
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# PHẦN 4: THUẬT TOÁN TÍNH ĐỘNG VÀ VẼ LƯỢNG HÓA HEATMAP RỦI RO OWASP
# =========================================================================
print("ĐANG KHỞI CHẠY MA TRẬN NHIỆT LƯỢNG HÓA RỦI RO OWASP DI ĐỘNG...")

mapping_loi = {
    'KB_01': 'SQL Injection',
    'KB_02': 'Stored XSS',
    'KB_03': 'CMDi & SSRF'
}

owasp_coordinates = {}

for ma_kb in ['KB_01','KB_02','KB_03']:

    phase_data = {}

    for phase_name, df, time_col in [
        ('Pha A', df_a, col_time_a),
        ('Pha B', df_b, col_time_b)
    ]:

        df_sub = df[df['Mã KB']==ma_kb]

        total_reqs = len(df_sub)

        if total_reqs == 0:
            continue

        # Pvul (THEO LOGIC CHƯƠNG 4)
        # 
        if ma_kb == 'KB_01':

            vulnerable = len(
                df_sub[
                    df_sub['HTTP Status']
                    .isin(['200','500','TIMEOUT'])
                ]
            )

        elif ma_kb == 'KB_02':

            vulnerable = len(
                df_sub[
                    df_sub['HTTP Status']=='500'
                ]
            )

        else:

            vulnerable = len(
                df_sub[
                    df_sub['HTTP Status']=='201'
                ]
            )

        Pvul = vulnerable / total_reqs

        # LIKELIHOOD
        likelihood = 1 + (Pvul * 8)

        # IMPACT
        mean_tres = df_sub[time_col].mean()

        if ma_kb in ['KB_01','KB_03']:

            impact = min(
                8 + (mean_tres*10),
                9
            )

        else:

            impact = min(
                5 + (mean_tres*20),
                9
            )

        phase_data[phase_name] = [
            round(likelihood,2),
            round(impact,2)
        ]

    owasp_coordinates[ma_kb] = phase_data
    # =========================================================================
# 📊 PHẦN 4.1: BẢNG LƯỢNG HÓA RỦI RO OWASP ĐỘNG ĐỐI CHỨNG 2 PHA
# =========================================================================

risk_compare = []

for ma_kb in ['KB_01','KB_02','KB_03']:

    if 'Pha A' not in owasp_coordinates[ma_kb]:
        continue

    if 'Pha B' not in owasp_coordinates[ma_kb]:
        continue

    L_a, I_a = owasp_coordinates[ma_kb]['Pha A']
    L_b, I_b = owasp_coordinates[ma_kb]['Pha B']

    risk_a = round(L_a * I_a,2)
    risk_b = round(L_b * I_b,2)

    rmit = (
        ((risk_a-risk_b)/risk_a)*100
        if risk_a!=0 else 0
    )

    if risk_b >= 50:
        level='Critical'

    elif risk_b >=35:
        level='High'

    elif risk_b >=15:
        level='Medium'

    else:
        level='Low'

    risk_compare.append({

        'Mã KB':ma_kb,

        'Nhóm lỗ hổng':
        mapping_loi[ma_kb],

        'Likelihood A':
        L_a,

        'Impact A':
        I_a,

        'Risk Score A':
        risk_a,

        'Likelihood B':
        L_b,

        'Impact B':
        I_b,

        'Risk Score B':
        risk_b,

        'Risk Level B':
        level,

        'Rmit (%)':
        round(rmit,2)

    })

df_risk_compare = pd.DataFrame(
    risk_compare
)

overall_phase_a = round(
    df_risk_compare[
        'Risk Score A'
    ].mean(),
    2
)

overall_phase_b = round(
    df_risk_compare[
        'Risk Score B'
    ].mean(),
    2
)

overall_rmit = round(

    (
        (
            overall_phase_a
            -
            overall_phase_b
        )
        /
        overall_phase_a
    )*100,

    2

)

print("\n")
print("="*130)
print("MA TRẬN ĐỐI CHỨNG RỦI RO OWASP GIỮA PHA A VÀ PHA B")
print("="*130)

print(
    df_risk_compare.to_string(
        index=False
    )
)

print("="*130)

print(
f"""
TỔNG THỂ HỆ THỐNG BACKEND

Risk Score Giai đoạn A : {overall_phase_a}

Risk Score Giai đoạn B : {overall_phase_b}

Tỷ lệ giảm thiểu rủi ro Rmit :

{overall_rmit} %

"""
)

highest_before = df_risk_compare.loc[
    df_risk_compare[
        'Risk Score A'
    ].idxmax()
]

highest_after = df_risk_compare.loc[
    df_risk_compare[
        'Risk Score B'
    ].idxmax()
]

print(
f"""
PHÂN HỆ RỦI RO CAO NHẤT

Trước khắc phục :

{highest_before['Mã KB']}
|
{highest_before['Nhóm lỗ hổng']}
|
Risk={highest_before['Risk Score A']}

Sau khắc phục :

{highest_after['Mã KB']}
|
{highest_after['Nhóm lỗ hổng']}
|
Risk={highest_after['Risk Score B']}

"""
)

print("="*130)
grid_size = 5
heatmap_grid = np.zeros((grid_size, grid_size))
x_ticks = np.linspace(1, 9, grid_size)
y_ticks = np.linspace(1, 9, grid_size)

for i in range(grid_size):
    for j in range(grid_size):
        heatmap_grid[i, j] = x_ticks[j] * y_ticks[grid_size - 1 - i]

fig, ax = plt.subplots(figsize=(8.5, 7.5))

sns.heatmap(
    heatmap_grid, 
    annot=True, 
    fmt=".1f", 
    cmap="YlOrRd", 
    cbar_kws={'label': 'Điểm số rủi ro tích hợp (Risk Score = L × I)'},
    xticklabels=[f"{val:.1f}" for val in x_ticks],
    yticklabels=[f"{val:.1f}" for val in reversed(y_ticks)],
    ax=ax,
    alpha=0.65
)

ax.set_title('MA TRẬN NHIỆT DỊCH CHUYỂN TỌA ĐỘ RỦI RO THEO CHUẨN OWASP\n(Quỹ đạo từ Pha A thực trạng sang Pha B khắc phục)', fontsize=11, fontweight='bold', color='#1F497D', pad=15)
ax.set_xlabel('Mức độ ảnh hưởng tổn thất (Impact Score)', fontsize=10, fontweight='bold', labelpad=10)
ax.set_ylabel('Khả năng xảy ra biến cố (Likelihood Score)', fontsize=10, fontweight='bold', labelpad=10)

def get_grid_coords(l_val, i_val):
    x_coord = (i_val - 1) / 8 * 4
    y_coord = 4 - ((l_val - 1) / 8 * 4)
    return x_coord, y_coord

label_offsets = {
    'KB_01': {'x': 0.08, 'y': 0.08},
    'KB_02': {'x': 0.08, 'y': -0.08},
    'KB_03': {'x': 0.08, 'y': 0.22}  
}
colors_scenarios = {'KB_01': '#2C3E50', 'KB_02': '#8E44AD', 'KB_03': '#D35400'}

for scenario, phases in owasp_coordinates.items():
    l_a, i_a = phases['Pha A']
    l_b, i_b = phases['Pha B']
    
    x_a, y_a = get_grid_coords(l_a, i_a)
    x_b, y_b = get_grid_coords(l_b, i_b)
    
    ax.plot(x_a, y_a, marker='o', color=colors_scenarios[scenario], markersize=10, label=f'{scenario} (Pha A)')
    ax.plot(x_b, y_b, marker='*', color=colors_scenarios[scenario], markersize=14)
    rad_val = -0.15 if scenario == 'KB_03' else -0.05
    ax.annotate(
        '', 
        xy=(x_b, y_b), 
        xytext=(x_a, y_a),
        arrowprops=dict(
            facecolor=colors_scenarios[scenario], 
            edgecolor=colors_scenarios[scenario],
            arrowstyle="->", 
            lw=2.5, 
            connectionstyle="arc3,rad=-0.1" 
        )
    )
    off_x = label_offsets[scenario]['x']
    off_y = label_offsets[scenario]['y']
    ax.text(
        x_b + off_x, 
        y_b + off_y, 
        f"{scenario} (Pha B)", 
        color='#333333', 
        fontsize=9, 
        fontweight='bold',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1) 
    )

plt.tight_layout()
OUTPUT_HEATMAP = f"{OUTPUT_DIR}/chuong5_owasp_heatmap_shift.png"
plt.savefig(OUTPUT_HEATMAP, dpi=300, bbox_inches='tight')
plt.close()

print(f"✔ Đã kết xuất đồ thị hộp phối hợp mật độ tại: {OUTPUT_IMAGE}")
