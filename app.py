import os
import io
import math
import base64
import html as html_lib
import urllib.request

import streamlit as st
from PIL import Image, ImageChops
from html2image import Html2Image

st.set_page_config(
    page_title="羽球隊賽程圖片產生器 (雙表同步)",
    page_icon="🏸",
    layout="wide"
)

POSTER_WIDTH = 1080      # 海報固定寬度 (px)
BOTTOM_PAD = 120         # 海報底部留白 (px)
FEMALE_COLOR = "#be1e4a" # 女子組別文字色
ACCENT_YELLOW = "#f0c030"  # 黃色標籤與圖示

# 色系設定（含原有深色系與新增亮色系）
THEMES = {
    # --- 原有深色系 ---
    "藍色體系": dict(
        bg="#13214b", header="#23407c", male="#1d4f9f", sub="#c3cdf2",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1f2937", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fef7e6", notice_border="#f0c030", notice_fg="#1e293b", notice_icon="#d93829",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "綠色體系": dict(
        bg="#0b3d2e", header="#1f6f50", male="#1b7a4f", sub="#b7e4cf",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1f2937", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fefce8", notice_border="#f0c030", notice_fg="#14532d", notice_icon="#d97706",
        tag_m_bg="#d1fae5", tag_m_fg="#065f46", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "灰色體系": dict(
        bg="#1f2937", header="#4b5563", male="#374151", sub="#d1d5db",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1f2937", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#f8fafc", notice_border="#cbd5e1", notice_fg="#1f2937", notice_icon="#e11d48",
        tag_m_bg="#f3f4f6", tag_m_fg="#374151", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "墨黑體系": dict(
        bg="#111111", header="#3a3a3a", male="#3f3f46", sub="#d4d4d8",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1f2937", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fef7e6", notice_border="#f0c030", notice_fg="#18181b", notice_icon="#dc2626",
        tag_m_bg="#f4f4f5", tag_m_fg="#27272a", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "紫色體系": dict(
        bg="#2a1a5e", header="#5b3fa5", male="#5b3fa5", sub="#d8ccf5",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1f2937", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#faf5ff", notice_border="#d8b4fe", notice_fg="#3b0764", notice_icon="#7c3aed",
        tag_m_bg="#ede9fe", tag_m_fg="#5b21b6", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "青藍綠體系": dict(
        bg="#0c3b45", header="#1f6f7d", male="#1a6b7a", sub="#bde3ea",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1f2937", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#f0fdfa", notice_border="#5eead4", notice_fg="#134e4a", notice_icon="#0f766e",
        tag_m_bg="#ccfbf1", tag_m_fg="#115e59", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    # --- 更多與藍色體系同風格深色系 ---
    "寶石藍體系": dict(
        bg="#0f295c", header="#1d4ed8", male="#1e40af", sub="#bfdbfe",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1e3a8a", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#eff6ff", notice_border="#f0c030", notice_fg="#1e293b", notice_icon="#d93829",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "靛紫藍體系": dict(
        bg="#1e1b4b", header="#4338ca", male="#3730a3", sub="#c7d2fe",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#312e81", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#eef2ff", notice_border="#f0c030", notice_fg="#1e1b4b", notice_icon="#dc2626",
        tag_m_bg="#e0e7ff", tag_m_fg="#3730a3", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "湖水藍體系": dict(
        bg="#082f49", header="#0369a1", male="#0284c7", sub="#bae6fd",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#0c4a6e", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#f0f9ff", notice_border="#f0c030", notice_fg="#0c4a6e", notice_icon="#ea580c",
        tag_m_bg="#e0f2fe", tag_m_fg="#0369a1", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "深紅體系": dict(
        bg="#450a18", header="#9f1239", male="#1d4f9f", sub="#fecdd3",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#4c0519", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fff1f2", notice_border="#f0c030", notice_fg="#4c0519", notice_icon="#e11d48",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "酒紅體系": dict(
        bg="#3b0722", header="#831843", male="#1d4f9f", sub="#fbcfe8",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#500724", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fdf2f8", notice_border="#f0c030", notice_fg="#500724", notice_icon="#be185d",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "深橘體系": dict(
        bg="#431407", header="#c2410c", male="#9a3412", sub="#fed7aa",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#431407", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fff7ed", notice_border="#f0c030", notice_fg="#431407", notice_icon="#ea580c",
        tag_m_bg="#ffedd5", tag_m_fg="#9a3412", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "琥珀金體系": dict(
        bg="#3d2606", header="#b45309", male="#92400e", sub="#fde68a",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#451a03", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fefce8", notice_border="#f0c030", notice_fg="#451a03", notice_icon="#d97706",
        tag_m_bg="#fef3c7", tag_m_fg="#92400e", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "咖啡體系": dict(
        bg="#291a12", header="#6b4423", male="#78350f", sub="#e7d3c3",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#291a12", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#faf5f0", notice_border="#f0c030", notice_fg="#291a12", notice_icon="#b45309",
        tag_m_bg="#f5ebe0", tag_m_fg="#6b4423", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "橄欖綠體系": dict(
        bg="#1f2e12", header="#4d7c0f", male="#3f6212", sub="#d9f99d",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#1a2e05", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#f7fee7", notice_border="#f0c030", notice_fg="#1a2e05", notice_icon="#4d7c0f",
        tag_m_bg="#ecfccb", tag_m_fg="#3f6212", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "玫瑰桃紅體系": dict(
        bg="#4a0e36", header="#be185d", male="#1d4f9f", sub="#fbcfe8",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#500724", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fdf2f8", notice_border="#f0c030", notice_fg="#500724", notice_icon="#be185d",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    # --- 新增亮色系 ---
    "晴空亮藍 (亮色)": dict(
        bg="#eef6ff", header="#2563eb", male="#1d4ed8", sub="#1e40af",
        title="#0f172a", badge="#2563eb", date_accent="#1d4ed8",
        tag_l_bg="#facc15", tag_l_fg="#1e293b",
        tag_r_bg="#ffffff", tag_r_fg="#1e3a8a", tag_r_border="#93c5fd",
        card_border="#bfdbfe",
        notice_bg="#ffffff", notice_border="#60a5fa", notice_fg="#1e3a8a", notice_icon="#2563eb",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "清新薄荷 (亮色)": dict(
        bg="#ecfdf5", header="#059669", male="#047857", sub="#065f46",
        title="#064e3b", badge="#059669", date_accent="#047857",
        tag_l_bg="#fbbf24", tag_l_fg="#1f2937",
        tag_r_bg="#ffffff", tag_r_fg="#065f46", tag_r_border="#6ee7b7",
        card_border="#a7f3d0",
        notice_bg="#ffffff", notice_border="#34d399", notice_fg="#064e3b", notice_icon="#059669",
        tag_m_bg="#d1fae5", tag_m_fg="#065f46", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "陽光暖橘 (亮色)": dict(
        bg="#fff7ed", header="#ea580c", male="#c2410c", sub="#9a3412",
        title="#431407", badge="#ea580c", date_accent="#c2410c",
        tag_l_bg="#fbbf24", tag_l_fg="#431407",
        tag_r_bg="#ffffff", tag_r_fg="#9a3412", tag_r_border="#fdba74",
        card_border="#fed7aa",
        notice_bg="#ffffff", notice_border="#fb923c", notice_fg="#7c2d12", notice_icon="#ea580c",
        tag_m_bg="#ffedd5", tag_m_fg="#9a3412", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "晨曦金黃 (亮色)": dict(
        bg="#fefce8", header="#d97706", male="#b45309", sub="#92400e",
        title="#451a03", badge="#d97706", date_accent="#b45309",
        tag_l_bg="#fde047", tag_l_fg="#451a03",
        tag_r_bg="#ffffff", tag_r_fg="#78350f", tag_r_border="#fcd34d",
        card_border="#fde68a",
        notice_bg="#ffffff", notice_border="#fbbf24", notice_fg="#78350f", notice_icon="#d97706",
        tag_m_bg="#fef3c7", tag_m_fg="#92400e", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "櫻花粉紅 (亮色)": dict(
        bg="#fff1f2", header="#e11d48", male="#0369a1", sub="#9f1239",
        title="#4c0519", badge="#e11d48", date_accent="#be123c",
        tag_l_bg="#fbbf24", tag_l_fg="#4c0519",
        tag_r_bg="#ffffff", tag_r_fg="#9f1239", tag_r_border="#fda4af",
        card_border="#fecdd3",
        notice_bg="#ffffff", notice_border="#fb7185", notice_fg="#881337", notice_icon="#e11d48",
        tag_m_bg="#e0f2fe", tag_m_fg="#0369a1", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "薰衣草紫 (亮色)": dict(
        bg="#f5f3ff", header="#7c3aed", male="#5b21b6", sub="#5b21b6",
        title="#2e1065", badge="#7c3aed", date_accent="#6d28d9",
        tag_l_bg="#facc15", tag_l_fg="#2e1065",
        tag_r_bg="#ffffff", tag_r_fg="#5b21b6", tag_r_border="#c4b5fd",
        card_border="#ddd6fe",
        notice_bg="#ffffff", notice_border="#a78bfa", notice_fg="#4c1d95", notice_icon="#7c3aed",
        tag_m_bg="#ede9fe", tag_m_fg="#5b21b6", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "湖水亮青 (亮色)": dict(
        bg="#ecfeff", header="#0891b2", male="#0e7490", sub="#155e75",
        title="#083344", badge="#0891b2", date_accent="#0e7490",
        tag_l_bg="#facc15", tag_l_fg="#083344",
        tag_r_bg="#ffffff", tag_r_fg="#155e75", tag_r_border="#67e8f9",
        card_border="#a5f3fc",
        notice_bg="#ffffff", notice_border="#22d3ee", notice_fg="#164e63", notice_icon="#0891b2",
        tag_m_bg="#cffafe", tag_m_fg="#155e75", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "極簡亮白 (亮色)": dict(
        bg="#f8fafc", header="#334155", male="#1e40af", sub="#475569",
        title="#0f172a", badge="#334155", date_accent="#1e293b",
        tag_l_bg="#facc15", tag_l_fg="#0f172a",
        tag_r_bg="#ffffff", tag_r_fg="#334155", tag_r_border="#cbd5e1",
        card_border="#cbd5e1",
        notice_bg="#f1f5f9", notice_border="#94a3b8", notice_fg="#0f172a", notice_icon="#e11d48",
        tag_m_bg="#e2e8f0", tag_m_fg="#1e293b", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    # --- 更多粉色系 ---
    "粉霧玫瑰體系": dict(
        bg="#501230", header="#be185d", male="#1d4f9f", sub="#fbcfe8",
        title="#ffffff", badge=ACCENT_YELLOW, date_accent=ACCENT_YELLOW,
        tag_l_bg=ACCENT_YELLOW, tag_l_fg="#1f1a05",
        tag_r_bg="#ffffff", tag_r_fg="#500724", tag_r_border="transparent",
        card_border="transparent",
        notice_bg="#fdf2f8", notice_border="#f472b6", notice_fg="#500724", notice_icon="#db2777",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "甜美粉紅 (亮色)": dict(
        bg="#fdf2f8", header="#ec4899", male="#1d4ed8", sub="#9d174d",
        title="#831843", badge="#ec4899", date_accent="#be185d",
        tag_l_bg="#facc15", tag_l_fg="#500724",
        tag_r_bg="#ffffff", tag_r_fg="#9d174d", tag_r_border="#f9a8d4",
        card_border="#fbcfe8",
        notice_bg="#ffffff", notice_border="#f472b6", notice_fg="#831843", notice_icon="#ec4899",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#fce7f3", tag_f_fg="#be185d",
    ),
    "草莓牛奶 (亮色)": dict(
        bg="#fce7f3", header="#db2777", male="#1d4ed8", sub="#9d174d",
        title="#500724", badge="#db2777", date_accent="#be185d",
        tag_l_bg="#fde047", tag_l_fg="#500724",
        tag_r_bg="#ffffff", tag_r_fg="#831843", tag_r_border="#f472b6",
        card_border="#f9a8d4",
        notice_bg="#ffffff", notice_border="#ec4899", notice_fg="#500724", notice_icon="#db2777",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "蜜桃粉橘 (亮色)": dict(
        bg="#fff5f5", header="#fb7185", male="#0369a1", sub="#be123c",
        title="#4c0519", badge="#f43f5e", date_accent="#e11d48",
        tag_l_bg="#fde047", tag_l_fg="#4c0519",
        tag_r_bg="#ffffff", tag_r_fg="#9f1239", tag_r_border="#fda4af",
        card_border="#fecdd3",
        notice_bg="#ffffff", notice_border="#fda4af", notice_fg="#881337", notice_icon="#f43f5e",
        tag_m_bg="#e0f2fe", tag_m_fg="#0369a1", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "乾燥玫瑰 (亮色)": dict(
        bg="#fdf4f5", header="#b9385b", male="#1e40af", sub="#881337",
        title="#4a1024", badge="#b9385b", date_accent="#9f1239",
        tag_l_bg="#fbbf24", tag_l_fg="#4a1024",
        tag_r_bg="#ffffff", tag_r_fg="#881337", tag_r_border="#e5a3b3",
        card_border="#f3d0d7",
        notice_bg="#ffffff", notice_border="#d9778f", notice_fg="#4a1024", notice_icon="#b9385b",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a",
    ),
    "粉紫丁香 (亮色)": dict(
        bg="#fae8ff", header="#c026d3", male="#1d4ed8", sub="#86198f",
        title="#4a044e", badge="#c026d3", date_accent="#a21caf",
        tag_l_bg="#fde047", tag_l_fg="#4a044e",
        tag_r_bg="#ffffff", tag_r_fg="#86198f", tag_r_border="#f0abfc",
        card_border="#f5d0fe",
        notice_bg="#ffffff", notice_border="#e879f9", notice_fg="#4a044e", notice_icon="#c026d3",
        tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#fae8ff", tag_f_fg="#a21caf",
    ),
}

CUSTOM_THEME_LABEL = "🎨 自訂色系 (自行選色)"

def _hex_to_rgb(hex_str):
    h = hex_str.lstrip("#")
    if len(h) != 6:
        return (19, 33, 75)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _is_light_color(hex_str):
    r, g, b = _hex_to_rgb(hex_str)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    return luminance >= 0.6

def _mix_hex(hex1, hex2, ratio):
    r1, g1, b1 = _hex_to_rgb(hex1)
    r2, g2, b2 = _hex_to_rgb(hex2)
    r = int(r1 * (1 - ratio) + r2 * ratio)
    g = int(g1 * (1 - ratio) + g2 * ratio)
    b = int(b1 * (1 - ratio) + b2 * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"

def build_custom_theme(bg, header, accent, title_color, sub_and_icon_color):
    """依使用者自選顏色組裝色系，並自動計算反差與卡片邊框。"""
    is_light_bg = _is_light_color(bg)
    is_light_header = _is_light_color(header)
    is_light_accent = _is_light_color(accent)
    return dict(
        bg=bg,
        header=header,
        header_fg="#1e293b" if is_light_header else "#ffffff",
        male="#1d4f9f",
        sub=sub_and_icon_color,
        title=title_color,
        badge=accent,
        date_accent=header if is_light_bg else accent,
        tag_l_bg=accent,
        tag_l_fg="#1e293b" if is_light_accent else "#ffffff",
        tag_r_bg="#ffffff",
        tag_r_fg="#1e293b",
        tag_r_border=_mix_hex(header, "#ffffff", 0.55) if is_light_bg else "transparent",
        card_border=_mix_hex(header, "#ffffff", 0.65) if is_light_bg else "transparent",
        notice_bg="#ffffff" if is_light_bg else "#fef7e6",
        notice_border=accent,
        notice_fg="#1e293b",
        notice_icon=sub_and_icon_color if is_light_bg else header,
        tag_m_bg="#dbeafe",
        tag_m_fg="#1e40af",
        tag_f_bg="#ffe4e6",
        tag_f_fg="#be1e4a",
    )

# -----------------------------------------------------------------------------
# 中文字型 (PNG 用：轉成 base64 內嵌)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_font_base64():
    font_path = os.path.abspath("NotoSansTC.ttf")
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            return ""
    try:
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

# -----------------------------------------------------------------------------
# Session State 初始化
# -----------------------------------------------------------------------------
MAX_TOTAL_DAYS = 10
MAX_EXTRA_DAYS = MAX_TOTAL_DAYS - 2  # 主編輯區已有第 1、2 天，最多再擴充 8 天（共 10 天）

if "g_date1" not in st.session_state:
    st.session_state["g_date1"] = ""
if "g_text1" not in st.session_state:
    st.session_state["g_text1"] = ""
if "g_date2" not in st.session_state:
    st.session_state["g_date2"] = ""
if "g_text2" not in st.session_state:
    st.session_state["g_text2"] = ""

if "personal_text" not in st.session_state:
    st.session_state["personal_text"] = ""

if "extra_days_count" not in st.session_state:
    st.session_state["extra_days_count"] = 1
for _idx in range(1, MAX_EXTRA_DAYS + 1):
    if f"g_extra_date_{_idx}" not in st.session_state:
        st.session_state[f"g_extra_date_{_idx}"] = ""
    if f"g_extra_text_{_idx}" not in st.session_state:
        st.session_state[f"g_extra_text_{_idx}"] = ""

# -----------------------------------------------------------------------------
# 解析整體流程表文字 → 卡片 HTML (同時間且同組別以「、」自動合併選手)
# -----------------------------------------------------------------------------
def parse_text_to_cards(text):
    groups = {}   
    order = []
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    for line in lines:
        normalized_line = line.replace("｜", "|")
        parts = [p.strip() for p in normalized_line.split("|")]
        if len(parts) >= 3:
            time_str, cate, players = parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            time_str, cate, players = parts[0], "", parts[1]
        else:
            continue
            
        if time_str not in groups:
            groups[time_str] = []
            order.append(time_str)
            
        found = False
        for entry in groups[time_str]:
            if entry[0] == cate:
                entry[1].append(players)
                found = True
                break
        if not found:
            groups[time_str].append((cate, [players]))

    cards_html = ""
    for time_str in order:
        items_html = ""
        for cate, player_list in groups[time_str]:
            players_str = "、".join(player_list)
            players_e = html_lib.escape(players_str)
            if cate:
                cls = "cate-f" if ("女" in cate and "男" not in cate) else "cate-m"
                items_html += f'<div class="item"><span class="{cls}">【{html_lib.escape(cate)}】</span>{players_e}</div>'
            else:
                items_html += f'<div class="item">{players_e}</div>'
                
        cards_html += f"""
        <div class="card">
          <div class="time-header">{html_lib.escape(time_str)}</div>
          <div class="content">{items_html}</div>
        </div>"""
    return cards_html, len(order)

# -----------------------------------------------------------------------------
# 解析選手個人賽程文字 (支援多天、分類與管線格式)
# -----------------------------------------------------------------------------
def parse_personal_integrated_text(text):
    blocks = []
    current_date_title = ""
    current_lines = []
    
    lines = text.strip().split("\n")
    for line in lines:
        raw_l = line.strip()
        if not raw_l:
            continue
        if ("【" in raw_l and "】" in raw_l) or ("月" in raw_l and ":" not in raw_l and "｜" not in raw_l and "|" not in raw_l and "男" not in raw_l and "女" not in raw_l):
            if current_lines or current_date_title:
                blocks.append((current_date_title, current_lines))
                current_lines = []
            current_date_title = raw_l
        else:
            current_lines.append(raw_l)
            
    if current_lines or current_date_title:
        blocks.append((current_date_title, current_lines))

    full_html = ""
    total_metric = 0

    for date_title, block_lines in blocks:
        if date_title:
            full_html += f'<div class="p-main-date">{html_lib.escape(date_title)}</div>'
            
        sections = {}
        sec_order = []
        current_sec = "選手個人賽程"
        
        for line in block_lines:
            if "｜" in line or "|" in line:
                parts = [p.strip() for p in line.replace("｜", "|").split("|")]
                if len(parts) >= 3:
                    time_p, cate_p, player_p = parts[0], parts[1], parts[2]
                    gender_str = "女" if ("女" in cate_p and "男" not in cate_p) else "男"
                    line = f"{gender_str}  {player_p} ({cate_p}) : {time_p}"

            if not (":" in line or "｜" in line or "|" in line or line.startswith("男") or line.startswith("女")):
                current_sec = line.replace("【", "").replace("】", "")
                if current_sec not in sections:
                    sections[current_sec] = []
                    sec_order.append(current_sec)
                continue
                
            if current_sec not in sections:
                sections[current_sec] = []
                sec_order.append(current_sec)
            sections[current_sec].append(line)

        for sec in sec_order:
            items = sections[sec]
            if not items:
                continue
            total_metric += len(items) + 1
            
            rows_html = ""
            for item in items:
                parts = item.split(":", 1)
                left_part = parts[0].strip()
                time_part = parts[1].strip() if len(parts) > 1 else ""
                
                if left_part.startswith("女") or ("女" in left_part and "男" not in left_part):
                    gender = "女"
                    name_cate = left_part[1:].strip() if left_part.startswith("女") else left_part
                else:
                    gender = "男"
                    name_cate = left_part[1:].strip() if (left_part.startswith("男") or left_part.startswith("女")) else left_part
                
                gender_class = "gender-f" if gender == "女" else "gender-m"
                
                rows_html += f"""
                <div class="p-row">
                  <span class="gender-badge {gender_class}">{gender}</span>
                  <span class="p-main-text">{html_lib.escape(name_cate)} : {html_lib.escape(time_part)}</span>
                </div>
                """
                
            full_html += f"""
            <div class="p-section-title">{html_lib.escape(sec)}</div>
            <div class="p-box">
              {rows_html}
            </div>
            """

    return full_html, max(1, total_metric)

# -----------------------------------------------------------------------------
# 羽球拍與羽球組合專屬圖示 (預設圖示) 與 公告喇叭圖示
# -----------------------------------------------------------------------------
def badge_svg(bg, accent=ACCENT_YELLOW):
    return f"""<svg width="68" height="76" viewBox="0 0 68 76" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="24" cy="26" rx="15" ry="19" fill="none" stroke="{accent}" stroke-width="3.5"/>
  <path d="M17 14 L17 38 M31 14 L31 38 M10 20 L38 20 M10 32 L38 32" stroke="{bg}" stroke-width="1.5" opacity="0.8"/>
  <path d="M24 45 L24 68" stroke="{accent}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M22 56 L26 56 M21 61 L27 61" stroke="{bg}" stroke-width="2"/>
  <path d="M46 26 L58 22 L54 42 L44 39 Z" fill="{accent}"/>
  <circle cx="49" cy="42" r="3.5" fill="{accent}"/>
  <path d="M47 28 L55 25" stroke="{bg}" stroke-width="1.5"/>
  <path d="M48 33 L56 30" stroke="{bg}" stroke-width="1.5"/>
</svg>"""

def notice_svg(color, size=34):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0;">
  <g transform="rotate(-10 18 18)">
    <path d="M8 14.5L23.5 8V28L8 21.5V14.5Z" fill="{color}" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/>
    <path d="M4.5 15.2C3.67 15.2 3 15.87 3 16.7V19.3C3 20.13 3.67 20.8 4.5 20.8H8V15.2H4.5Z" fill="{color}"/>
    <path d="M11 22.5L13.5 29C13.8 29.8 14.7 30.2 15.5 29.9C16.3 29.6 16.7 28.7 16.4 27.9L14.3 22.5" stroke="{color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M27.5 13L31.5 10.5" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>
    <path d="M28.2 18H33" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>
    <path d="M27.5 23L31.5 25.5" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>
  </g>
</svg>"""

def uploaded_file_to_data_uri(uploaded_file):
    """將使用者上傳的圖片轉為內嵌 data URI，過大的點陣圖自動等比例縮放。"""
    if uploaded_file is None:
        return ""
    raw_bytes = uploaded_file.getvalue()
    if not raw_bytes:
        return ""
    name = (uploaded_file.name or "").lower()
    if name.endswith(".svg"):
        b64 = base64.b64encode(raw_bytes).decode()
        return f"data:image/svg+xml;base64,{b64}"

    mime = "image/png"
    if name.endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    elif name.endswith(".webp"):
        mime = "image/webp"

    try:
        img = Image.open(io.BytesIO(raw_bytes))
        max_dim = 400
        if img.width > max_dim or img.height > max_dim:
            resample = getattr(Image, "Resampling", Image).LANCZOS
            img.thumbnail((max_dim, max_dim), resample)
            buf = io.BytesIO()
            fmt = "PNG"
            if mime == "image/jpeg":
                img = img.convert("RGB")
                fmt = "JPEG"
            elif mime == "image/webp":
                fmt = "WEBP"
            img.save(buf, format=fmt)
            raw_bytes = buf.getvalue()
    except Exception:
        pass

    b64 = base64.b64encode(raw_bytes).decode()
    return f"data:{mime};base64,{b64}"

# -----------------------------------------------------------------------------
# 產生海報 HTML 核心函式 (預覽時移除外網字型載入以大幅加速)
# -----------------------------------------------------------------------------
def generate_poster_html(sub_title, main_title, tag_left, tag_right,
                         date1_title, data1_text, date2_title, data2_text,
                         extra_date="", extra_text="", extra_days=None,
                         notice_text="", notice_font_size=26, badge_data_uri="",
                         body_font_size=28, theme_name="藍色體系", custom_theme=None,
                         title_font_size=66, mode="整體流程表", preview=True):
    theme = custom_theme if custom_theme is not None else THEMES[theme_name]
    bg_color = theme["bg"]
    header_fg = theme.get("header_fg", "#ffffff")

    total_metric = 0
    body_content = ""

    if mode == "整體流程表":
        days_list = [(date1_title, data1_text)]
        if data2_text.strip():
            days_list.append((date2_title, data2_text))
        if extra_days:
            for d_title, d_text in extra_days:
                if d_text.strip():
                    days_list.append((d_title, d_text))
        elif extra_text.strip():
            days_list.append((extra_date, extra_text))

        sections_html = ""
        for idx, (d_title, d_text) in enumerate(days_list):
            if idx > 0 and not d_text.strip():
                continue
            cards_html, count_d = parse_text_to_cards(d_text)
            title_d_html = f'<div class="section-title">{html_lib.escape(d_title)}</div>' if d_title.strip() else ""
            if idx == 0 and not d_text.strip() and len(days_list) > 1:
                continue
            sections_html += f"{title_d_html}<div class=\"grid\">{cards_html}</div>"
            total_metric += count_d

        body_content = f"""
  <div class="section-container">
    {sections_html}
  </div>"""
    else:
        body_content_html, total_metric = parse_personal_integrated_text(data1_text)
        body_content = f"""
  <div class="section-container">
    {body_content_html}
  </div>"""

    sub_title = html_lib.escape(sub_title)
    main_title = html_lib.escape(main_title)
    tag_left = html_lib.escape(tag_left)
    tag_right = html_lib.escape(tag_right)
    notice_clean = html_lib.escape(notice_text.strip())

    has_sub = bool(sub_title.strip())
    has_main = bool(main_title.strip())
    has_tag_l = bool(tag_left.strip())
    has_tag_r = bool(tag_right.strip())
    has_notice = bool(notice_clean)
    
    sub_html = f'<div class="sub-title">{sub_title}</div>' if has_sub else ''
    main_html = f'<div class="main-title">{main_title}</div>' if has_main else ''
    
    tags_inner = ""
    if has_tag_l:
        tags_inner += f'<span class="tag-yellow">{tag_left}</span>'
    if has_tag_r:
        tags_inner += f'<span class="tag-white">{tag_right}</span>'
        
    tags_html = f'<div class="tags">{tags_inner}</div>' if (has_tag_l or has_tag_r) else ''
    notice_icon_size = max(24, int(notice_font_size * 1.25))
    notice_html = (
        f'<div class="notice-banner">{notice_svg(theme["notice_icon"], size=notice_icon_size)}'
        f'<span class="notice-text">{notice_clean}</span></div>'
        if has_notice else ''
    )

    if badge_data_uri:
        badge_inner = f'<img src="{badge_data_uri}" alt="badge" class="badge-img" />'
    else:
        badge_inner = badge_svg(bg_color, theme["badge"])

    has_header_content = bool(badge_data_uri or has_sub or has_main or has_tag_l or has_tag_r or has_notice)
    badge_html = f'<div class="badge-icon">{badge_inner}</div>' if has_header_content else ''
    
    header_content = ""
    if has_header_content:
        header_content = f"""
  <div class="header">
    {badge_html}
    {sub_html}
    {main_html}
    {tags_html}
    {notice_html}
  </div>"""

    if preview:
        font_css = ""
    else:
        b64 = get_font_base64()
        font_css = ""
        if b64:
            font_css = f"""<style>
@font-face {{
  font-family: 'Noto Sans TC';
  font-weight: 100 900;
  src: url('data:font/ttf;base64,{b64}') format('truetype');
}}
</style>"""

    preview_script = ""
    if preview:
        preview_script = f"""
<script>
  const W = {POSTER_WIDTH};
  function fit() {{
    const wrap = document.getElementById('wrap');
    const poster = document.getElementById('poster');
    const scale = wrap.clientWidth / W;
    poster.style.transform = 'scale(' + scale + ')';
    const h = Math.ceil(poster.offsetHeight * scale);
    wrap.style.height = h + 'px';
    try {{ window.frameElement.style.height = h + 'px'; }} catch (e) {{}}
  }}
  window.addEventListener('load', fit);
  window.addEventListener('resize', fit);
  setTimeout(fit, 100);
</script>"""

    wrap_open = '<div id="wrap">' if preview else ''
    wrap_close = '</div>' if preview else ''

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{font_css}
<style>
  html, body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    background-color: {bg_color};
  }}
  #wrap {{
    width: 100%;
    overflow: hidden;
    position: relative;
  }}
  #poster {{
    background-color: {bg_color};
    font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', sans-serif;
    color: {theme['title']};
    width: {POSTER_WIDTH}px;
    padding: 60px 54px {BOTTOM_PAD}px 54px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    transform-origin: top left;
  }}
  .header {{ text-align: center; margin-bottom: 40px; width: 100%; }}
  .badge-icon {{
    min-height: 76px; max-height: 92px; margin-bottom: 14px; line-height: 0;
    display: flex; justify-content: center; align-items: center;
  }}
  .badge-img {{
    max-height: 88px; max-width: 260px; width: auto; height: auto;
    object-fit: contain; border-radius: 8px;
  }}
  .sub-title {{ color: {theme['sub']}; font-size: 40px; font-weight: 800; line-height: 1.3; }}
  .main-title {{
    font-size: {title_font_size}px; font-weight: 800; line-height: 1.2;
    margin: 4px 0 20px 0; color: {theme['title']}; letter-spacing: 1px;
  }}
  .tags {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }}
  .tag-yellow {{
    background-color: {theme['tag_l_bg']}; color: {theme['tag_l_fg']}; font-weight: 700;
    padding: 12px 38px; border-radius: 40px; font-size: 28px; line-height: 1.4;
  }}
  .tag-white {{
    background-color: {theme['tag_r_bg']}; color: {theme['tag_r_fg']}; font-weight: 700;
    padding: 12px 38px; border-radius: 40px; font-size: 28px; line-height: 1.4;
    border: 2px solid {theme['tag_r_border']};
  }}
  .notice-banner {{
    width: 100%;
    box-sizing: border-box;
    margin-top: 22px;
    padding: 14px 28px;
    border-radius: 999px;
    background-color: {theme['notice_bg']};
    border: 2px solid {theme['notice_border']};
    color: {theme['notice_fg']};
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
  }}
  .notice-text {{
    font-size: {notice_font_size}px;
    font-weight: 800;
    line-height: 1.4;
    text-align: left;
  }}
  .section-container {{ width: 100%; }}
  .section-title {{
    background-color: {theme['header']}; color: {header_fg}; text-align: center;
    font-size: {body_font_size}px; font-weight: 700; padding: 14px;
    border-radius: 12px; margin: 26px 0 20px 0;
  }}
  .grid {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 22px 20px; margin-bottom: 22px;
  }}
  .card {{
    background-color: #ffffff; border-radius: 14px; overflow: hidden;
    display: flex; flex-direction: column;
    border: 2px solid {theme['card_border']};
  }}
  .time-header {{
    background-color: {theme['header']}; text-align: center; padding: 16px 0;
    font-size: {body_font_size}px; font-weight: 700; color: {header_fg}; line-height: 1.4;
  }}
  .content {{
    flex: 1; background-color: #ffffff; padding: 16px 28px;
    display: flex; flex-direction: column; justify-content: center; gap: 6px;
  }}
  .item {{ font-size: {body_font_size}px; color: #1e293b; font-weight: 700; line-height: 1.4; }}
  .cate-m {{ color: {theme['male']}; font-weight: 800; }}
  .cate-f {{ color: {FEMALE_COLOR}; font-weight: 800; }}

  /* 個人賽程專屬樣式 */
  .p-main-date {{
    font-size: {body_font_size + 4}px; font-weight: 800; color: {theme['date_accent']};
    text-align: center; margin: 30px 0 14px 0; letter-spacing: 1px;
  }}
  .p-section-title {{
    background-color: {theme['header']}; color: {header_fg}; text-align: center;
    font-size: {body_font_size}px; font-weight: 700; padding: 16px;
    border-radius: 12px; margin: 20px 0 14px 0;
  }}
  .p-box {{
    background-color: #ffffff; border-radius: 14px; overflow: hidden;
    padding: 10px 24px; margin-bottom: 16px;
    border: 2px solid {theme['card_border']};
  }}
  .p-row {{
    display: flex; align-items: center; padding: 12px 0;
    border-bottom: 1px solid #f1f5f9; font-size: {body_font_size}px; color: #1e293b; font-weight: 700;
  }}
  .p-row:last-child {{ border-bottom: none; }}
  .gender-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 38px; height: 38px; border-radius: 50%; font-size: 22px; font-weight: 700;
    margin-right: 18px; flex-shrink: 0;
  }}
  .gender-m {{ background-color: {theme['tag_m_bg']}; color: {theme['tag_m_fg']}; }}
  .gender-f {{ background-color: {theme['tag_f_bg']}; color: {theme['tag_f_fg']}; }}
  .p-main-text {{ flex: 1; text-align: left; }}
</style>
</head>
<body>
{wrap_open}
<div id="poster">
  {header_content}
  {body_content}
</div>
{wrap_close}
{preview_script}
</body>
</html>"""
    return html_content, max(1, total_metric)

# -----------------------------------------------------------------------------
# 輸出 PNG
# -----------------------------------------------------------------------------
def render_png(html_str, total_metric, out_path="generated_schedule.png"):
    tall_height = 1000 + total_metric * 120

    if os.path.exists(out_path):
        os.remove(out_path)

    hti = Html2Image(
        output_path=".",
        custom_flags=[
            "--no-sandbox",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--virtual-time-budget=10000",
        ],
    )
    hti.screenshot(html_str=html_str, save_as=out_path, size=(POSTER_WIDTH, tall_height))

    img = Image.open(out_path).convert("RGB")
    bg = img.getpixel((2, 2))
    diff = ImageChops.difference(img, Image.new("RGB", img.size, bg))
    bbox = diff.getbbox()
    if bbox:
        new_h = min(bbox[3] + BOTTOM_PAD, img.height)
        img = img.crop((0, 0, POSTER_WIDTH, new_h))
    img.save(out_path)
    return out_path

# -----------------------------------------------------------------------------
# 主畫面 (雙表並排架構)
# -----------------------------------------------------------------------------
st.title("🏸 羽球隊賽程圖片產生器 (雙表同步產出)")
st.write(f"請在下方設定共用樣式，並分別填入**整體流程表**與**選手個人賽程**資料，系統將同時產出兩張完整海報！")

# 1. 標題、版型與樣式設定
st.header("⚙️ 1. 標題、版型與樣式設定 (兩張表共用)")
col_s1, col_s2 = st.columns(2)
with col_s1:
    main_title = st.text_input("主標題 (選填)", value="MAUC 秋季賽")
    sub_title = st.text_input("副標題 / 隊伍名稱 (選填)", value="2026年牧羽盃全國四季聯賽")
    notice_text = st.text_input(
        "公告 / 注意事項橫幅 (選填，前方會自動加上喇叭符號)",
        value="",
        placeholder="例如：此賽事需要全隊低中高年級團進團出，再請留意！"
    )
with col_s2:
    tag_right = st.text_input("右側標籤 / 日期 (選填)", value="日期：2026/09/28（一）")
    tag_left_gen = st.text_input("整體流程表左側標籤", value="整體流程表")
    tag_left_per = st.text_input("選手個人賽程左側標籤", value="選手個人賽程")

col_c1, col_c2, col_c3, col_c4 = st.columns(4)
with col_c1:
    theme_options = list(THEMES.keys()) + [CUSTOM_THEME_LABEL]
    theme_name = st.selectbox("整體色系", theme_options)
with col_c2:
    body_font_size = st.slider("內文字體大小 (px)", min_value=18, max_value=40, value=26)
with col_c3:
    title_font_size = st.slider("主標題字體大小 (px)", min_value=48, max_value=130, value=66)
with col_c4:
    notice_font_size = st.slider("公告橫幅字體大小 (px)", min_value=18, max_value=44, value=26)

custom_theme = None
if theme_name == CUSTOM_THEME_LABEL:
    st.caption("🎨 自訂色盤：可自由挑選背景、標題列與重點色，系統會自動搭配卡片邊框與文字反差。")
    cp1, cp2, cp3, cp4, cp5 = st.columns(5)
    with cp1:
        c_bg = st.color_picker("海報背景色", "#fce7f3", key="cp_bg")
    with cp2:
        c_header = st.color_picker("卡片標題列色", "#ec4899", key="cp_header")
    with cp3:
        c_accent = st.color_picker("徽章與左側標籤色", "#facc15", key="cp_accent")
    with cp4:
        c_title = st.color_picker("主標題文字色", "#831843", key="cp_title")
    with cp5:
        c_sub = st.color_picker("副標題與喇叭色", "#be185d", key="cp_sub")
    custom_theme = build_custom_theme(c_bg, c_header, c_accent, c_title, c_sub)

badge_file = st.file_uploader(
    "頂部圖示 / 隊徽 (選填，未上傳則使用預設羽球圖示)",
    type=["png", "jpg", "jpeg", "webp", "svg"],
    key="badge_upload",
    help="預設顯示內建羽球拍圖示；上傳圖片後將自動取代頂部圖示（建議使用去背 PNG 或 SVG）。"
)
badge_data_uri = uploaded_file_to_data_uri(badge_file)

st.markdown("---")

# 2 & 3. 賽程資料編輯區 (左右並排，使用 key 確保輸入不被重置)
col_input1, col_input2 = st.columns(2)

with col_input1:
    st.header("📝 2. 賽程資料編輯區 (整體流程表)")
    st.info("💡 請先將賽程截圖並用 AI 處理文字。給 AI 提示詞範例：'請將這張圖改成可直接複製到網頁的格式(包含斷行)，選手僅帶出XX國小的即可。格式：時間 ｜ 組別 ｜ 選手 (如：08:00 | 國小五年級男單 | 王大明)'")
    
    st.text_input("第一天日期說明 (整體)", key="g_date1")
    st.text_area("第一天賽程 (整體)", key="g_text1", height=180, placeholder="09:00 ｜ 低男單 ｜ 王大明")
    
    st.text_input("第二天日期說明 (整體・若無可留空)", key="g_date2")
    st.text_area("第二天賽程 (整體)", key="g_text2", height=180, placeholder="若無第二天請保持空白...")

with col_input2:
    st.header("📝 3. 賽程資料編輯區 (選手個人賽程)")
    st.info("💡 請先將賽程截圖並用 AI 處理文字。給 AI 提示詞範例：'依據附圖格式，將所有選手按日期、年級組別進行歸類與整合，並列出每位選手參加的項目與所有出場時間。'")
    
    st.text_area(
        "選手個人賽程內容 (一格貼全部)",
        key="personal_text",
        height=420,
        placeholder=""
    )

def _add_extra_day():
    if st.session_state["extra_days_count"] < MAX_EXTRA_DAYS:
        st.session_state["extra_days_count"] += 1

def _remove_extra_day():
    if st.session_state["extra_days_count"] > 1:
        idx = st.session_state["extra_days_count"]
        st.session_state[f"g_extra_date_{idx}"] = ""
        st.session_state[f"g_extra_text_{idx}"] = ""
        st.session_state["extra_days_count"] -= 1

# 額外天數擴充 (僅整體流程表，上限共 10 天)
with st.expander("➕ 點此新增更多天數賽程 (整體流程表專用)"):
    cur_extra = st.session_state["extra_days_count"]
    total_days_now = 2 + cur_extra
    col_btn_add, col_btn_rem, col_day_info = st.columns([1.2, 1.2, 2.6])
    with col_btn_add:
        st.button(
            "➕ 新增一天" if total_days_now < MAX_TOTAL_DAYS else "已達上限 10 天",
            on_click=_add_extra_day,
            disabled=(total_days_now >= MAX_TOTAL_DAYS),
            key="btn_add_day",
            use_container_width=True,
        )
    with col_btn_rem:
        st.button(
            "➖ 移除最後一天",
            on_click=_remove_extra_day,
            disabled=(cur_extra <= 1),
            key="btn_rem_day",
            use_container_width=True,
        )
    with col_day_info:
        st.caption(f"目前共有第 1 ～ {total_days_now} 天（上限 {MAX_TOTAL_DAYS} 天）")

    for i in range(1, cur_extra + 1):
        day_num = 2 + i
        st.markdown(f"**第 {day_num} 天**")
        st.text_input(f"第 {day_num} 天日期說明 (整體)", key=f"g_extra_date_{i}")
        st.text_area(f"第 {day_num} 天賽程 (整體)", key=f"g_extra_text_{i}", height=120, placeholder=f"請貼上第 {day_num} 天賽程內容...")

st.markdown("---")

# 4. 即時預覽與圖片下載 (左右並排呈現兩張海報 - 長度依內容自動調整)
st.header("🖼️ 4. 即時預覽與圖片下載 (左右兩張)")

col_prev1, col_prev2 = st.columns(2)

extra_days_payload = [
    (st.session_state[f"g_extra_date_{i}"], st.session_state[f"g_extra_text_{i}"])
    for i in range(1, st.session_state["extra_days_count"] + 1)
]
has_gen_content = (
    bool(st.session_state["g_text1"].strip())
    or bool(st.session_state["g_text2"].strip())
    or any(t.strip() for _, t in extra_days_payload)
)

# 組裝整體流程表參數
kwargs_gen = dict(
    sub_title=sub_title, main_title=main_title,
    tag_left=tag_left_gen, tag_right=tag_right,
    date1_title=st.session_state["g_date1"], data1_text=st.session_state["g_text1"],
    date2_title=st.session_state["g_date2"], data2_text=st.session_state["g_text2"],
    extra_days=extra_days_payload,
    notice_text=notice_text, notice_font_size=notice_font_size,
    badge_data_uri=badge_data_uri,
    body_font_size=body_font_size, theme_name=theme_name, custom_theme=custom_theme,
    title_font_size=title_font_size, mode="整體流程表"
)

# 組裝選手個人賽程參數
kwargs_per = dict(
    sub_title=sub_title, main_title=main_title,
    tag_left=tag_left_per, tag_right=tag_right,
    date1_title="", data1_text=st.session_state["personal_text"],
    date2_title="", data2_text="",
    notice_text=notice_text, notice_font_size=notice_font_size,
    badge_data_uri=badge_data_uri,
    body_font_size=body_font_size, theme_name=theme_name, custom_theme=custom_theme,
    title_font_size=title_font_size, mode="選手個人賽程"
)

notice_extra_px = (notice_font_size + 44) if notice_text.strip() else 0

with col_prev1:
    st.subheader("🌐 【整體流程表】預覽")
    if has_gen_content:
        html_g_prev, metric_g = generate_poster_html(preview=True, **kwargs_gen)
        preview_height_g = int(350 + notice_extra_px + metric_g * 65)
        st.components.v1.html(html_g_prev, height=preview_height_g, scrolling=False)
        
        if st.button("🚀 產出【整體流程表】PNG 圖片", type="primary", key="btn_g"):
            with st.spinner("正在轉換為高解析圖片..."):
                html_g_png, metric_g = generate_poster_html(preview=False, **kwargs_gen)
                path_g = render_png(html_g_png, metric_g, out_path="general_schedule.png")
                if os.path.exists(path_g):
                    st.image(path_g, caption="整體流程表產出預覽", use_container_width=True)
                    with open(path_g, "rb") as f:
                        st.download_button("⬇️ 下載整體流程表 (PNG)", data=f, file_name="整體流程表.png", mime="image/png", key="dl_g")
    else:
        st.info("請在左上方填入整體流程表資料以顯示預覽。")

with col_prev2:
    st.subheader("🌐 【選手個人賽程】預覽")
    if st.session_state["personal_text"].strip():
        html_p_prev, metric_p = generate_poster_html(preview=True, **kwargs_per)
        preview_height_p = int(350 + notice_extra_px + metric_p * 65)
        st.components.v1.html(html_p_prev, height=preview_height_p, scrolling=False)
        
        if st.button("🚀 產出【選手個人賽程】PNG 圖片", type="primary", key="btn_p"):
            with st.spinner("正在轉換為高解析圖片..."):
                html_p_png, metric_p = generate_poster_html(preview=False, **kwargs_per)
                path_p = render_png(html_p_png, metric_p, out_path="personal_schedule.png")
                if os.path.exists(path_p):
                    st.image(path_p, caption="選手個人賽程產出預覽", use_container_width=True)
                    with open(path_p, "rb") as f:
                        st.download_button("⬇️ 下載選手個人賽程 (PNG)", data=f, file_name="選手個人賽程.png", mime="image/png", key="dl_p")
    else:
        st.info("請在右上方填入選手個人賽程資料以顯示預覽。")
