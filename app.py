"""
🛡️ OWASP Security Stress-Testing Dashboard — Streamlit (dark / SOC vibe).

Đọc trực tiếp 2 file kết quả trong results/ (không cần Juice Shop):
  - results/bao_cao_dinh_luong_loi.csv        (Pha A: trước khi vá)
  - results/bao_cao_dinh_luong_sau_va_loi.csv (Pha B: sau khi vá)

Công thức Likelihood/Impact/Risk Score đồng bộ với
analytics/risk_quantitative.py & analytics/reme_results.py.

Chạy:  streamlit run app.py
"""
import os
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================================================
# Cấu hình
# ==========================================================================
AUTHOR = "Nguyen Vu Thanh Giang"

st.set_page_config(
    page_title="OWASP Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_A = os.path.join(BASE_DIR, "results", "bao_cao_dinh_luong_loi.csv")
FILE_B = os.path.join(BASE_DIR, "results", "bao_cao_dinh_luong_sau_va_loi.csv")

KB_NAME = {"KB_01": "SQL Injection", "KB_02": "Stored XSS", "KB_03": "CMDi & SSRF"}
KB_ICON = {"KB_01": "💉", "KB_02": "🧬", "KB_03": "⚙️"}
KB_COLOR = {"KB_01": "#22D3EE", "KB_02": "#A78BFA", "KB_03": "#FB923C"}
TIME_COL = "Thời Gian (s)"

# Bảng màu "security" trên nền tối
BG = "#0A0F1C"
PANEL = "#111A2E"
BORDER = "#1E2B45"
INK = "#E2E8F0"
MUTED = "#8B9BB4"
C_A = "#F43F5E"      # Pha A (threat) — đỏ
C_B = "#22D3EE"      # Pha B (secured) — cyan
C_OK = "#34D399"     # an toàn — xanh lá

RISK_COLORS = {
    "Nghiêm trọng (Critical)": "#F43F5E",
    "Cao (High)": "#FB923C",
    "Trung bình (Medium)": "#FBBF24",
    "Thấp (Low)": "#34D399",
}
PLOT_FONT = dict(family="ui-monospace, SFMono-Regular, Menlo, monospace", color=INK, size=13)


def style_fig(fig, height=360, legend_top=True):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=PLOT_FONT, margin=dict(t=40 if legend_top else 14, b=18, l=10, r=10),
        legend=(dict(orientation="h", y=1.14, x=0, bgcolor="rgba(0,0,0,0)",
                     font=dict(color=MUTED)) if legend_top else {}),
        hoverlabel=dict(font_size=12, bgcolor=PANEL),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=MUTED)
    fig.update_yaxes(gridcolor=BORDER, zeroline=False, color=MUTED)
    return fig


# ==========================================================================
# CSS — dark SOC
# ==========================================================================
st.markdown(f"""
<style>
  .stApp {{ background:
      radial-gradient(1100px 500px at 15% -5%, #16213E 0%, rgba(10,15,28,0) 55%),
      radial-gradient(900px 500px at 100% 0%, #10243A 0%, rgba(10,15,28,0) 50%),
      {BG}; }}
  .block-container {{ padding-top: 1.3rem; padding-bottom: 2.5rem; max-width: 1300px; }}
  #MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
  h1,h2,h3,h4 {{ color:{INK}; }}

  /* Hero */
  .hero {{
    position: relative; overflow: hidden; border-radius: 18px; padding: 24px 28px;
    background: linear-gradient(120deg, #0F1D3A 0%, #0B2538 55%, #0A1F2E 100%);
    border: 1px solid {BORDER}; margin-bottom: 20px;
    box-shadow: 0 0 0 1px rgba(34,211,238,.08), 0 18px 48px rgba(0,0,0,.45);
  }}
  .hero:before {{
    content:""; position:absolute; inset:0;
    background: linear-gradient(90deg, transparent, rgba(34,211,238,.10), transparent);
    animation: sweep 6s linear infinite;
  }}
  @keyframes sweep {{ 0%{{transform:translateX(-100%)}}100%{{transform:translateX(100%)}} }}
  .hero h1 {{ font-size: 1.55rem; font-weight: 800; margin: 0 0 6px; letter-spacing:.4px; }}
  .hero p  {{ margin: 0; color:#A9C7D8; font-size:.95rem; }}
  .hero .pill {{ display:inline-block; margin-top:10px; padding:3px 12px; border-radius:999px;
    background: rgba(52,211,153,.12); color:{C_OK}; border:1px solid rgba(52,211,153,.35);
    font-size:.78rem; font-weight:700; letter-spacing:.3px; }}

  /* KPI */
  .kpi {{ background:{PANEL}; border:1px solid {BORDER}; border-radius:14px; padding:16px 18px;
    border-top:3px solid var(--accent,#22D3EE); height:100%;
    box-shadow: 0 0 22px -12px var(--accent,#22D3EE); }}
  .kpi .lbl {{ color:{MUTED}; font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.8px; }}
  .kpi .val {{ color:{INK}; font-size:1.95rem; font-weight:800; line-height:1.1; margin-top:4px; }}
  .kpi .sub {{ font-size:.78rem; margin-top:5px; font-weight:600; color:{MUTED}; }}
  .up {{ color:{C_OK}; }} .down {{ color:{C_A}; }}

  /* Card */
  .card {{ background:{PANEL}; border:1px solid {BORDER}; border-radius:14px;
    padding:16px 18px 6px; margin-bottom:8px; box-shadow:0 10px 30px rgba(0,0,0,.30); }}
  .sec-title {{ font-size:1.0rem; font-weight:700; color:{INK}; margin:4px 0 10px;
    display:flex; align-items:center; gap:8px; }}
  .badge {{ padding:3px 11px; border-radius:999px; font-size:.78rem; font-weight:800; }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{ gap:6px; border-bottom:1px solid {BORDER}; }}
  .stTabs [data-baseweb="tab"] {{ background:{PANEL}; border:1px solid {BORDER};
    border-radius:10px 10px 0 0; padding:8px 16px; color:{MUTED}; font-weight:700; }}
  .stTabs [aria-selected="true"] {{ color:{INK}!important;
    border-color:{C_B}; box-shadow:0 -2px 14px -6px {C_B}; background:#12263B; }}

  section[data-testid="stSidebar"] {{ background:{PANEL}; border-right:1px solid {BORDER}; }}
  div[data-testid="stDataFrame"] {{ border:1px solid {BORDER}; border-radius:10px; overflow:hidden; }}
  .stDownloadButton button {{ width:100%; background:linear-gradient(90deg,#0E7490,#22D3EE);
    color:#04121A; font-weight:800; border:0; border-radius:10px; }}
  .foot {{ color:{MUTED}; font-size:.8rem; text-align:center; margin-top:18px;
    padding-top:14px; border-top:1px solid {BORDER}; }}
</style>
""", unsafe_allow_html=True)


# ==========================================================================
# Dữ liệu & rủi ro
# ==========================================================================
@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["Mã KB"] = df["Mã KB"].astype(str).str.strip()
    df["HTTP Status"] = df["HTTP Status"].astype(str).str.strip()
    df[TIME_COL] = pd.to_numeric(df[TIME_COL], errors="coerce")
    return df.dropna(subset=[TIME_COL])


def risk_level(s):
    if s >= 50: return "Nghiêm trọng (Critical)"
    if s >= 35: return "Cao (High)"
    if s >= 15: return "Trung bình (Medium)"
    return "Thấp (Low)"


def compute_risk(df):
    rows = []
    for kb in ["KB_01", "KB_02", "KB_03"]:
        sub = df[df["Mã KB"] == kb]
        if sub.empty:
            continue
        total = len(sub)
        if kb == "KB_01":
            vuln = len(sub[sub["HTTP Status"].isin(["200", "500", "TIMEOUT"])])
        else:
            vuln = len(sub[sub["HTTP Status"] == "201"])
        pvul = vuln / total
        lk = round(1 + pvul * 8, 2)
        mt = sub[TIME_COL].mean()
        im = round(min(8 + mt * 10, 9), 2) if kb in ["KB_01", "KB_03"] else round(min(5 + mt * 20, 9), 2)
        sc = round(lk * im, 2)
        rows.append({"Mã KB": kb, "Lỗ hổng": KB_NAME[kb], "Pvul": round(pvul, 4),
                     "Likelihood": lk, "Impact": im, "Risk Score": sc, "Xếp hạng": risk_level(sc)})
    return pd.DataFrame(rows)


try:
    df_a, df_b = load_csv(FILE_A), load_csv(FILE_B)
except FileNotFoundError:
    st.error("❌ Không tìm thấy kết quả trong `results/`. Hãy chạy `simulation.py` & `remediation.py` trước.")
    st.stop()

risk_a, risk_b = compute_risk(df_a), compute_risk(df_b)
compare = risk_a.merge(risk_b, on=["Mã KB", "Lỗ hổng"], suffixes=(" A", " B"))
compare["R_mit (%)"] = ((compare["Risk Score A"] - compare["Risk Score B"])
                        / compare["Risk Score A"] * 100).round(2)
overall_a = round(risk_a["Risk Score"].mean(), 2)
overall_b = round(risk_b["Risk Score"].mean(), 2)
overall_rmit = round((overall_a - overall_b) / overall_a * 100, 2)


def build_report() -> str:
    lines = [
        "# BÁO CÁO ĐÁNH GIÁ GIẢM THIỂU RỦI RO BẢO MẬT (OWASP)",
        f"_Tác giả: {AUTHOR} · Xuất ngày {datetime.now():%d/%m/%Y %H:%M}_\n",
        "## Tổng quan",
        f"- Tổng request mô phỏng: **{len(df_a)+len(df_b):,}** (Pha A: {len(df_a):,} · Pha B: {len(df_b):,})",
        f"- Risk Score trung bình — Pha A: **{overall_a}** → Pha B: **{overall_b}**",
        f"- **Tỷ lệ giảm thiểu rủi ro tổng (R_mit): {overall_rmit:.2f}%**\n",
        "## Chi tiết theo kịch bản",
        "| Mã KB | Lỗ hổng | Risk A | Risk B | Xếp hạng B | R_mit (%) |",
        "|-------|---------|-------:|-------:|-----------|----------:|",
    ]
    for _, r in compare.iterrows():
        lines.append(f"| {r['Mã KB']} | {r['Lỗ hổng']} | {r['Risk Score A']:.2f} | "
                     f"{r['Risk Score B']:.2f} | {r['Xếp hạng B']} | {r['R_mit (%)']:.2f} |")
    return "\n".join(lines) + "\n"


# ==========================================================================
# Sidebar
# ==========================================================================
with st.sidebar:
    st.markdown(f"### 🛡️ Security Console")
    st.markdown(
        f"<span style='color:{MUTED}'>Mục tiêu:</span> <code>OWASP Juice Shop</code><br>"
        f"<span style='color:{MUTED}'>Pha A (trước vá):</span> <b>{len(df_a):,}</b> req<br>"
        f"<span style='color:{MUTED}'>Pha B (sau vá):</span> <b>{len(df_b):,}</b> req",
        unsafe_allow_html=True)
    st.markdown("---")
    st.download_button("⬇️ Tải báo cáo (.md)", data=build_report(),
                       file_name="security_risk_report.md", mime="text/markdown")
    st.caption("Dashboard đọc tĩnh từ `results/*.csv`.")


# ==========================================================================
# Hero
# ==========================================================================
verdict = "✅ RỦI RO ĐÃ GIẢM ĐÁNG KỂ" if overall_rmit >= 40 else "⚠️ CẦN TIẾP TỤC KHẮC PHỤC"
st.markdown(f"""
<div class="hero">
  <h1>🛡️ OWASP Security Stress-Testing Dashboard</h1>
  <p>Mô phỏng tấn công diện rộng &amp; định lượng rủi ro — SQL Injection · Stored XSS · Command Injection / SSRF.</p>
  <span class="pill">{verdict} · R_mit {overall_rmit:.1f}%</span>
</div>
""", unsafe_allow_html=True)


def kpi(col, label, value, accent, sub):
    col.markdown(f'<div class="kpi" style="--accent:{accent}"><div class="lbl">{label}</div>'
                 f'<div class="val">{value}</div><div class="sub">{sub}</div></div>',
                 unsafe_allow_html=True)


# ==========================================================================
# Helper: biểu đồ dùng chung
# ==========================================================================
def status_chart(dfa, dfb, h=360):
    sa = dfa["HTTP Status"].value_counts().rename("Pha A")
    sb = dfb["HTTP Status"].value_counts().rename("Pha B")
    d = pd.concat([sa, sb], axis=1).fillna(0).reset_index(names="HTTP Status")
    f = go.Figure()
    f.add_bar(name="Pha A", x=d["HTTP Status"], y=d["Pha A"], marker_color=C_A)
    f.add_bar(name="Pha B", x=d["HTTP Status"], y=d["Pha B"], marker_color=C_B)
    f.update_layout(barmode="group", yaxis_title="Số request")
    return style_fig(f, h)


def gauge(score_a, score_b):
    f = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=score_b,
        domain={"x": [0, 1], "y": [0, 0.82]},   # chừa chỗ cho số/delta, tránh chồng lấn
        number={"font": {"color": INK, "size": 30}, "valueformat": ".2f"},
        delta={"reference": score_a, "valueformat": ".2f",
               "font": {"size": 15},
               "decreasing": {"color": C_OK}, "increasing": {"color": C_A}},
        gauge={"axis": {"range": [0, 81], "tickcolor": MUTED, "nticks": 5},
               "bar": {"color": C_B, "thickness": 0.28},
               "steps": [{"range": [0, 15], "color": "#13351F"},
                         {"range": [15, 35], "color": "#3A3416"},
                         {"range": [35, 50], "color": "#3E2A16"},
                         {"range": [50, 81], "color": "#3A1620"}],
               "threshold": {"line": {"color": C_A, "width": 3}, "value": score_a}},
    ))
    f.update_layout(margin=dict(t=18, b=10, l=24, r=24))
    return style_fig(f, 300, legend_top=False)


# ==========================================================================
# TABS
# ==========================================================================
tab_titles = ["🛰️ Tổng quan"] + [f"{KB_ICON[k]} {KB_NAME[k]}" for k in ["KB_01", "KB_02", "KB_03"]]
tabs = st.tabs(tab_titles)

# -------------------------- TAB 0: Tổng quan ------------------------------
with tabs[0]:
    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Tổng request", f"{len(df_a)+len(df_b):,}", "#22D3EE", "Pha A + Pha B")
    kpi(k2, "Risk Score · Pha A", f"{overall_a:.2f}", C_A, "trung bình 3 kịch bản")
    kpi(k3, "Risk Score · Pha B", f"{overall_b:.2f}", C_B, f"<span class='up'>▼ {overall_a-overall_b:.2f}</span>")
    kpi(k4, "Giảm thiểu R_mit", f"{overall_rmit:.1f}%", C_OK, "<span class='up'>▲ an toàn hơn</span>")
    st.write("")

    cL, cR = st.columns([1.12, 1])
    with cL:
        st.markdown('<div class="card"><div class="sec-title">📋 Ma trận đối chứng rủi ro (A → B)</div>',
                    unsafe_allow_html=True)
        show = compare[["Mã KB", "Lỗ hổng", "Risk Score A", "Risk Score B", "Xếp hạng B", "R_mit (%)"]].copy()
        sty = (show.style
               .format({"Risk Score A": "{:.2f}", "Risk Score B": "{:.2f}", "R_mit (%)": "{:.2f}"})
               .map(lambda v: f"color:{RISK_COLORS.get(v,'#ccc')};font-weight:800", subset=["Xếp hạng B"])
               .bar(subset=["R_mit (%)"], color="#155E52", vmin=0, vmax=100))
        st.dataframe(sty, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with cR:
        st.markdown('<div class="card"><div class="sec-title">📊 Risk Score: trước vs sau</div>',
                    unsafe_allow_html=True)
        f = go.Figure()
        f.add_bar(name="Pha A", x=compare["Lỗ hổng"], y=compare["Risk Score A"],
                  marker_color=C_A, text=compare["Risk Score A"], textposition="outside")
        f.add_bar(name="Pha B", x=compare["Lỗ hổng"], y=compare["Risk Score B"],
                  marker_color=C_B, text=compare["Risk Score B"], textposition="outside")
        f.update_layout(barmode="group", yaxis_title="Risk Score (L × I)")
        st.plotly_chart(style_fig(f, 360), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="sec-title">🎯 OWASP Risk Matrix — dịch chuyển L × I (A → B)</div>',
                unsafe_allow_html=True)
    grid = np.array([[(i+1)*(j+1) for j in range(9)] for i in range(9)], dtype=float)
    fm = go.Figure(go.Heatmap(
        z=grid, x=list(range(1, 10)), y=list(range(1, 10)),
        colorscale=[[0, "#0E2A1E"], [0.35, "#2E3A14"], [0.65, "#5A3418"], [1, "#5E1726"]],
        opacity=0.9, showscale=True, colorbar=dict(title="L×I", thickness=14, tickcolor=MUTED),
        hovertemplate="Impact %{x} · Likelihood %{y}<br>Risk %{z}<extra></extra>"))
    for _, r in compare.iterrows():
        kb = r["Mã KB"]
        fm.add_trace(go.Scatter(
            x=[r["Impact A"], r["Impact B"]], y=[r["Likelihood A"], r["Likelihood B"]],
            mode="markers+lines+text", text=[f"{kb} A", f"{kb} B"], textposition="top center",
            textfont=dict(size=11, color=KB_COLOR[kb]),
            line=dict(color=KB_COLOR[kb], width=2, dash="dot"),
            marker=dict(size=[14, 19], color=KB_COLOR[kb], symbol=["circle", "star"],
                        line=dict(color=BG, width=2)),
            name=r["Lỗ hổng"],
            hovertemplate=f"<b>{r['Lỗ hổng']}</b><br>L=%{{y}}, I=%{{x}}<extra></extra>"))
    fm.update_layout(xaxis_title="Impact →", yaxis_title="Likelihood →",
                     xaxis=dict(range=[0.5, 9.5], dtick=1), yaxis=dict(range=[0.5, 9.5], dtick=1))
    st.plotly_chart(style_fig(fm, 500), use_container_width=True)
    st.caption("● Pha A (trước vá) · ★ Pha B (sau vá). Điểm dịch về góc dưới-trái = rủi ro giảm.")
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------- TAB per-KB ------------------------------------
def render_kb(tab, kb):
    row = compare[compare["Mã KB"] == kb].iloc[0]
    da, db = df_a[df_a["Mã KB"] == kb], df_b[df_b["Mã KB"] == kb]
    with tab:
        lvl = row["Xếp hạng B"]
        st.markdown(
            f'<div class="card"><div class="sec-title">{KB_ICON[kb]} {KB_NAME[kb]} '
            f'<span class="badge" style="background:{RISK_COLORS[lvl]}22;color:{RISK_COLORS[lvl]};'
            f'border:1px solid {RISK_COLORS[lvl]}55">Sau vá: {lvl}</span></div></div>',
            unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        kpi(k1, "Risk · Pha A", f"{row['Risk Score A']:.2f}", C_A, f"L={row['Likelihood A']} · I={row['Impact A']}")
        kpi(k2, "Risk · Pha B", f"{row['Risk Score B']:.2f}", C_B, f"L={row['Likelihood B']} · I={row['Impact B']}")
        kpi(k3, "R_mit", f"{row['R_mit (%)']:.1f}%", C_OK, "mức giảm rủi ro")
        kpi(k4, "Request", f"{len(da):,}", "#A78BFA", "mỗi pha")
        st.write("")

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="card"><div class="sec-title">🎚️ Chỉ số rủi ro (gauge)</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(gauge(row["Risk Score A"], row["Risk Score B"]), use_container_width=True)
            st.caption("Vạch đỏ = Pha A · kim = Pha B. Càng thấp càng an toàn.")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card"><div class="sec-title">🌐 HTTP Status (trước vs sau)</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(status_chart(da, db, 300), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="sec-title">🧾 Mẫu payload &amp; kết quả</div>',
                    unsafe_allow_html=True)
        ph = st.radio(f"Giai đoạn ({kb})", ["Pha A (trước vá)", "Pha B (sau vá)"],
                      horizontal=True, label_visibility="collapsed", key=f"ph_{kb}")
        src = da if ph.startswith("Pha A") else db
        cols = ["Payload", "HTTP Status", TIME_COL, "Kết Quả Thực Nghiệm"]
        st.dataframe(src[cols].head(400), use_container_width=True, hide_index=True, height=300)
        st.caption(f"Hiển thị tối đa 400/{len(src):,} request · {ph}.")
        st.markdown('</div>', unsafe_allow_html=True)


render_kb(tabs[1], "KB_01")
render_kb(tabs[2], "KB_02")
render_kb(tabs[3], "KB_03")

st.markdown(f'<div class="foot">© {datetime.now():%Y} {AUTHOR} · OWASP Security Stress-Testing Dashboard '
            f'· built with Streamlit + Plotly</div>', unsafe_allow_html=True)
