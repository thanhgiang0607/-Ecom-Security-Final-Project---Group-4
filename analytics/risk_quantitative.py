import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
import seaborn as sns
import pandas as pd
import numpy as np
import os

# --- CẤU HÌNH ĐƯỜNG DẪN ---
FILE_LOG_THO = "bao_cao_dinh_luong_loi.csv"
OUTPUT_ANH   = "chuong4_owasp_risk_matrix.png"

# ── FONT & STYLE (nền trắng) ─────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'figure.facecolor':  'white',
    'axes.facecolor':    'white',
    'text.color':        '#1A1A2E',
    'axes.labelcolor':   '#1A1A2E',
    'xtick.color':       '#444444',
    'ytick.color':       '#444444',
})

BG          = 'white'
TEXT_MAIN   = '#1A1A2E'
TEXT_MID    = '#444444'
TEXT_LIGHT  = '#777777'
BORDER      = '#CCCCCC'
HEADER_BG   = '#1F497D'
HEADER_FG   = 'white'
ROW_ODD     = '#F7F9FC'
ROW_EVEN    = 'white'

# ── DỮ LIỆU MẪU ──────────────────────────────────────────────────────────────
def get_sample_data():
    return pd.DataFrame([
        {'Mã KB': 'KB_01', 'Lỗ hổng': 'SQL Injection',
         'Likelihood': 8.5, 'Impact': 8.8, 'Risk Score': 74.8, 'Xếp hạng': 'Nghiêm trọng (Critical)'},
        {'Mã KB': 'KB_02', 'Lỗ hổng': 'Stored XSS',
         'Likelihood': 5.2, 'Impact': 6.1, 'Risk Score': 31.7, 'Xếp hạng': 'Trung bình (Medium)'},
        {'Mã KB': 'KB_03', 'Lỗ hổng': 'CMDi & SSRF',
         'Likelihood': 7.1, 'Impact': 8.6, 'Risk Score': 61.1, 'Xếp hạng': 'Nghiêm trọng (Critical)'},
    ])

# ── ĐỌC / TÍNH TOÁN DỮ LIỆU ──────────────────────────────────────────────────
mapping_loi = {'KB_01': 'SQL Injection', 'KB_02': 'Stored XSS', 'KB_03': 'CMDi & SSRF'}

if os.path.exists(FILE_LOG_THO):
    df = pd.read_csv(FILE_LOG_THO)
    df['Mã KB'] = df['Mã KB'].astype(str).str.strip()
    df['Response Time'] = pd.to_numeric(df['Thời Gian (s)'], errors='coerce')
    df = df.dropna(subset=['Thời Gian (s)'])
    dynamic_risk_data = []
    for ma_kb in ['KB_01', 'KB_02', 'KB_03']:
        df_sub = df[df['Mã KB'] == ma_kb]
        if df_sub.empty:
            continue
        total_reqs = len(df_sub)
        if ma_kb == 'KB_01':
            vulnerable_reqs = len(df_sub[df_sub['HTTP Status'].isin(['200', '500', 'TIMEOUT'])])
        elif ma_kb == 'KB_02':
            vulnerable_reqs = len(df_sub[df_sub['HTTP Status'] == '500'])
        else:
            vulnerable_reqs = len(df_sub[df_sub['HTTP Status'] == '201'])
        vulnerability_rate = vulnerable_reqs / total_reqs
        calculated_likelihood = 1.0 + (vulnerability_rate * 8.0)
        mean_tres = df_sub['Thời Gian (s)'].mean()
        if ma_kb in ['KB_01', 'KB_03']:
            calculated_impact = min(8.0 + (mean_tres * 10), 9.0)
        else:
            calculated_impact = min(5.0 + (mean_tres * 20), 9.0)
        risk_score = calculated_likelihood * calculated_impact
        if risk_score >= 50.0:   level = 'Nghiêm trọng (Critical)'
        elif risk_score >= 35.0: level = 'Cao (High)'
        elif risk_score >= 15.0: level = 'Trung bình (Medium)'
        else:                    level = 'Thấp (Low)'
        dynamic_risk_data.append({
            'Mã KB': ma_kb, 'Lỗ hổng': mapping_loi[ma_kb],
            'Likelihood': round(calculated_likelihood, 2),
            'Impact':     round(calculated_impact, 2),
            'Risk Score': round(risk_score, 2), 'Xếp hạng': level
        })
    df_risk = pd.DataFrame(dynamic_risk_data)
else:
    print("⚠️  Không tìm thấy file CSV — dùng dữ liệu mẫu.")
    df_risk = get_sample_data()

# ── PALETTE ───────────────────────────────────────────────────────────────────
PALETTE   = ['#1F497D', '#E28743', '#C0392B']   # xanh navy / cam / đỏ
MARKERS   = ['o', 's', '^']
MARKER_SZ = 300
RISK_COLORS = {
    'Thấp (Low)':              '#2E7D32',
    'Trung bình (Medium)':     '#F9A825',
    'Cao (High)':              '#E65100',
    'Nghiêm trọng (Critical)': '#B71C1C',
}

cmap_risk = LinearSegmentedColormap.from_list(
    'owasp', ['#E8F5E9', '#A5D6A7', '#FFF9C4', '#FFCC80', '#EF9A9A', '#B71C1C'], N=256
)

# ── LAYOUT ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 10), dpi=150)
fig.patch.set_facecolor(BG)

gs = GridSpec(2, 2, figure=fig,
              left=0.08, right=0.97, top=0.90, bottom=0.10,
              wspace=0.35, hspace=0.48,
              width_ratios=[2.8, 1], height_ratios=[2.8, 1])

ax_main  = fig.add_subplot(gs[0, 0])
ax_bar   = fig.add_subplot(gs[0, 1])
ax_table = fig.add_subplot(gs[1, :])

# ── (A) HEATMAP ───────────────────────────────────────────────────────────────
matrix_grid = np.array([[(i+1)*(j+1) for j in range(9)] for i in range(9)], dtype=float)

sns.heatmap(
    matrix_grid, cmap=cmap_risk, alpha=0.45,
    cbar_kws={'label': 'Risk Score (L × I)', 'shrink': 0.8},
    xticklabels=range(1, 10), yticklabels=range(1, 10),
    linewidths=0.4, linecolor='#E0E0E0',
    ax=ax_main
)

# Viền vùng nguy hiểm
for r_min, i_min, color in [(6, 6, '#B71C1C'), (4, 4, '#E65100')]:
    ax_main.add_patch(mpatches.FancyBboxPatch(
        (i_min - 1, r_min - 1), 9 - (i_min - 1), 9 - (r_min - 1),
        boxstyle="square,pad=0", linewidth=1.8,
        edgecolor=color, facecolor='none', linestyle='--', alpha=0.7, zorder=3
    ))

# Chấm điểm
for idx, row in df_risk.iterrows():
    x = row['Impact']     - 1
    y = row['Likelihood'] - 1
    c = PALETTE[idx % len(PALETTE)]

    # Halo nhẹ
    ax_main.scatter(x, y, s=MARKER_SZ * 3, color=c, alpha=0.12, zorder=4)
    ax_main.scatter(x, y, s=MARKER_SZ * 1.6, color=c, alpha=0.25, zorder=4)

    # Điểm chính
    ax_main.scatter(x, y, s=MARKER_SZ, color=c,
                    marker=MARKERS[idx % len(MARKERS)],
                    edgecolors='white', linewidths=1.8, zorder=5,
                    label=f"{row['Mã KB']}: {row['Lỗ hổng']}")

    # Nhãn tooltip — nền trắng, viền màu
    ax_main.annotate(
        f" {row['Mã KB']}  {row['Risk Score']:.1f} ",
        xy=(x, y), xytext=(10, -20), textcoords='offset points',
        fontsize=8.5, fontweight='bold', color=c,
        bbox=dict(boxstyle='round,pad=0.35', fc='white', ec=c, lw=1.2, alpha=0.95),
        zorder=6
    )

ax_main.invert_yaxis()
ax_main.set_facecolor(BG)
ax_main.set_title('Ma trận rủi ro động theo chuẩn OWASP', fontsize=12,
                   fontweight='bold', color=TEXT_MAIN, pad=10)
ax_main.set_xlabel('Mức độ tác động (Impact) →', fontsize=10, color=TEXT_MID)
ax_main.set_ylabel('Khả năng xảy ra (Likelihood) →', fontsize=10, color=TEXT_MID)

leg = ax_main.legend(loc='lower left', frameon=True, framealpha=0.95,
                      facecolor='white', edgecolor=BORDER,
                      fontsize=8.5, title='Lỗ hổng', title_fontsize=9)
leg.get_title().set_color(TEXT_MID)
for t in leg.get_texts():
    t.set_color(TEXT_MAIN)

# Colorbar
cbar = ax_main.collections[0].colorbar
cbar.ax.yaxis.label.set_color(TEXT_MID)
cbar.ax.tick_params(colors=TEXT_MID)
cbar.outline.set_edgecolor(BORDER)

# ── (B) BAR CHART ─────────────────────────────────────────────────────────────
bar_colors = [RISK_COLORS.get(r['Xếp hạng'], '#888') for _, r in df_risk.iterrows()]
bars = ax_bar.barh(df_risk['Mã KB'], df_risk['Risk Score'],
                   color=bar_colors, edgecolor='none', height=0.5)

for bar, (_, row) in zip(bars, df_risk.iterrows()):
    ax_bar.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                f"{row['Risk Score']:.1f}", va='center', ha='left',
                fontsize=9, fontweight='bold', color=TEXT_MAIN)

ax_bar.set_facecolor(BG)
ax_bar.set_xlim(0, df_risk['Risk Score'].max() * 1.28)
ax_bar.set_title('Risk Score', fontsize=10, fontweight='bold', color=TEXT_MAIN, pad=8)
ax_bar.tick_params(axis='x', colors=TEXT_MID, labelsize=8)
ax_bar.tick_params(axis='y', colors=TEXT_MAIN, labelsize=9)
ax_bar.spines['bottom'].set_color(BORDER)
ax_bar.spines['left'].set_color(BORDER)

for thresh, col, lbl in [(50, '#B71C1C', 'Critical'), (35, '#E65100', 'High')]:
    if thresh < df_risk['Risk Score'].max() * 1.2:
        ax_bar.axvline(thresh, color=col, lw=1, ls='--', alpha=0.7)
        ax_bar.text(thresh + 0.5, len(df_risk) - 0.08, lbl,
                    fontsize=7, color=col, va='top')

# ── (C) BẢNG TÓM TẮT ─────────────────────────────────────────────────────────
ax_table.set_facecolor(BG)
ax_table.axis('off')

col_labels = ['Mã KB', 'Lỗ hổng', 'Likelihood', 'Impact', 'Risk Score', 'Xếp hạng']
table_data = [[
    row['Mã KB'], row['Lỗ hổng'],
    f"{row['Likelihood']:.2f}", f"{row['Impact']:.2f}",
    f"{row['Risk Score']:.2f}", row['Xếp hạng']
] for _, row in df_risk.iterrows()]

tbl = ax_table.table(
    cellText=table_data, colLabels=col_labels,
    cellLoc='center', loc='center', bbox=[0, 0, 1, 1]
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)

# Header
for j in range(len(col_labels)):
    cell = tbl[0, j]
    cell.set_facecolor(HEADER_BG)
    cell.set_text_props(color=HEADER_FG, fontweight='bold')
    cell.set_edgecolor(HEADER_BG)

# Rows
for i, (_, row) in enumerate(df_risk.iterrows(), start=1):
    rc = RISK_COLORS.get(row['Xếp hạng'], '#888')
    for j in range(len(col_labels)):
        cell = tbl[i, j]
        cell.set_facecolor(ROW_ODD if i % 2 == 1 else ROW_EVEN)
        cell.set_edgecolor('#E8E8E8')
        if j == 5:
            cell.set_text_props(color=rc, fontweight='bold')
        elif j == 4:
            cell.set_text_props(color=PALETTE[i - 1], fontweight='bold')
        else:
            cell.set_text_props(color=TEXT_MAIN)

# ── TIÊU ĐỀ TOÀN TRANG ───────────────────────────────────────────────────────
fig.text(0.5, 0.955, 'MA TRẬN XẾP HẠNG RỦI RO THEO CHUẨN OWASP',
         ha='center', va='top', fontsize=14, fontweight='bold', color='#1F497D')


plt.savefig(OUTPUT_ANH, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()

print("\n📊 KẾT QUẢ TÍNH TOÁN:")
print("-" * 85)
print(df_risk.to_string(index=False))
print("-" * 85)
print(f"✔ Đã xuất: {OUTPUT_ANH}\n")