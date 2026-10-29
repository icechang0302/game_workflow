import os
import math
import base64
import html as html_lib
import urllib.request

import streamlit as st
from PIL import Image, ImageChops
from html2image import Html2Image

st.set_page_config(
    page_title="羽球隊賽程圖片產生器",
    page_icon="🏸",
    layout="centered"
)

POSTER_WIDTH = 1080      # 海報固定寬度 (px)
BOTTOM_PAD = 120         # 海報底部留白 (px)
FEMALE_COLOR = "#be1e4a" # 女子組別文字色
ACCENT_YELLOW = "#f0c030"  # 黃色標籤與圖示

# 色系設定
THEMES = {
    "藍色體系": dict(bg="#13214b", header="#23407c", male="#1d4f9f", sub="#c3cdf2", tag_m_bg="#dbeafe", tag_m_fg="#1e40af", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a"),
    "綠色體系": dict(bg="#0b3d2e", header="#1f6f50", male="#1b7a4f", sub="#b7e4cf", tag_m_bg="#d1fae5", tag_m_fg="#065f46", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a"),
    "灰色體系": dict(bg="#1f2937", header="#4b5563", male="#374151", sub="#d1d5db", tag_m_bg="#f3f4f6", tag_m_fg="#374151", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a"),
    "墨黑體系": dict(bg="#111111", header="#3a3a3a", male="#3f3f46", sub="#d4d4d8", tag_m_bg="#f4f4f5", tag_m_fg="#27272a", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a"),
    "紫色體系": dict(bg="#2a1a5e", header="#5b3fa5", male="#5b3fa5", sub="#d8ccf5", tag_m_bg="#ede9fe", tag_m_fg="#5b21b6", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a"),
    "青藍綠體系": dict(bg="#0c3b45", header="#1f6f7d", male="#1a6b7a", sub="#bde3ea", tag_m_bg="#ccfbf1", tag_m_fg="#115e59", tag_f_bg="#ffe4e6", tag_f_fg="#be1e4a"),
}

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
if "mode" not in st.session_state:
    st.session_state["mode"] = "整體流程表"
if "day1_text" not in st.session_state:
    st.session_state["day1_text"] = ""
if "day2_text" not in st.session_state:
    st.session_state["day2_text"] = ""
if "p_day1_text" not in st.session_state:
    st.session_state["p_day1_text"] = """【2026-11-19】

低年級
男  童羿勛 (低男單) : 12:00、14:30
男  謝皓喆 (低男單) : 12:00
男  廖胤期 (低男單) : 12:15、14:30
男  吳家丞 (低男單) : 14:30
女  林子晴 (低女單) : 15:15、15:45

中年級
男  林祐頡 (中男單) : 08:45、10:00
男  謝皓宇 (中男單) : 10:00、11:15
女  吳雨恩 (中女單) : 11:45、13:00
女  凃萬希 (中女單) : 12:00、13:15

高年級
男  張智勛 (高男單) : 08:00、10:30
男  謝翔宇 (高男單) : 08:00、09:15
男  林靖洋 (高男單) : 09:15、10:30
男  曾楷翔 (高男單) : 09:30、10:45"""

if "p_day2_text" not in st.session_state:
    st.session_state["p_day2_text"] = """【2026-11-20】

中年級
男  林祐頡 (中男雙) : 09:00、09:30
男  謝皓喆 (中男雙) : 09:00、09:30

高年級
男  曾楷翔 (高男雙) : 08:45、09:30
男  許宸睿 (高男單/高男雙) : 08:45、09:30、11:00、13:45
女  黃芊萱 (高女單) : 12:30、15:00
女  蔡昀忻 (高女單) : 12:30、14:15、15:00"""

# -----------------------------------------------------------------------------
# 解析模式 1：整體流程表文字 → 卡片 HTML
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
            players_str = " ".join(player_list)
            players_e = html_lib.escape(players_str)
            if cate:
                cls = "cate-f" if "女" in cate else "cate-m"
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
# 解析模式 2：選手個人賽程文字 → 分组區塊 HTML
# -----------------------------------------------------------------------------
def parse_personal_text(text):
    sections = {} # section_name -> list of lines
    sec_order = []
    current_sec = "選手個人賽程"
    
    lines = text.strip().split("\n")
    for line in lines:
        raw_l = line.strip()
        if not raw_l:
            continue
        # 檢查是否為大標題分類 (例如 低年級、中年級、高年級 或 【2026-11-19】)
        if not (":" in raw_l or "｜" in raw_l or "|" in raw_l or "男" in raw_l or "女" in raw_l):
            current_sec = raw_l.replace("【", "").replace("】", "")
            if current_sec not in sections:
                sections[current_sec] = []
                sec_order.append(current_sec)
            continue
            
        if current_sec not in sections:
            sections[current_sec] = []
            sec_order.append(current_sec)
        sections[current_sec].append(raw_l)

    result_html = ""
    total_items = 0
    
    for sec in sec_order:
        items = sections[sec]
        if not items:
            continue
        total_items += len(items) + 1
        
        rows_html = ""
        for item in items:
            # 格式範例：男  童羿勛 (低男單) : 12:00、14:30
            parts = item.split(":", 1)
            left_part = parts[0].strip()
            time_part = parts[1].strip() if len(parts) > 1 else ""
            
            gender = "男" if left_part.startswith("男") else "女"
            name_cate = left_part[1:].strip() # 剩下 童羿勛 (低男單)
            
            gender_class = "gender-f" if gender == "女" else "gender-m"
            
            rows_html += f"""
            <div class="p-row">
              <span class="gender-badge {gender_class}">{gender}</span>
              <span class="p-info">{html_lib.escape(name_cate)}</span>
              <span class="p-colon">:</span>
              <span class="p-time">{html_lib.escape(time_part)}</span>
            </div>
            """
            
        result_html += f"""
        <div class="p-section-title">{html_lib.escape(sec)}</div>
        <div class="p-box">
          {rows_html}
        </div>
        """
    return result_html, total_items

# -----------------------------------------------------------------------------
# 羽球圖示 (黃色)
# -----------------------------------------------------------------------------
def badge_svg(bg):
    return f"""<svg width="46" height="76" viewBox="0 0 48 80" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 4 H39 L31 58 H17 Z" fill="{ACCENT_YELLOW}"/>
  <path d="M10 18 H38 M12.5 32 H35.5 M14.5 46 H33.5 M17.5 4 L20.5 58 M24 4 V58 M30.5 4 L27.5 58"
        stroke="{bg}" stroke-width="2.6" fill="none"/>
  <circle cx="24" cy="68" r="7" fill="none" stroke="{ACCENT_YELLOW}" stroke-width="4"/>
</svg>"""

# -----------------------------------------------------------------------------
# 產生海報 HTML (支援兩種模式)
# -----------------------------------------------------------------------------
def generate_poster_html(sub_title, main_title, tag_left, tag_right,
                         date1_title, data1_text, date2_title, data2_text,
                         body_font_size=28, theme_name="藍色體系", title_font_size=100,
                         mode="整體流程表", preview=True):
    theme = THEMES[theme_name]
    bg_color = theme["bg"]

    if mode == "整體流程表":
        c1, count1 = parse_text_to_cards(data1_text)
        show_day2 = bool(data2_text.strip())
        c2, count2 = parse_text_to_cards(data2_text) if show_day2 else ("", 0)
        title1_html = (f'<div class="section-title">{html_lib.escape(date1_title)}</div>' if date1_title.strip() else "")
        title2_html = (f'<div class="section-title">{html_lib.escape(date2_title)}</div>' if date2_title.strip() else "")
        day2_html = (f'{title2_html}<div class="grid">{c2}</div>' if show_day2 else "")
        body_content = f"""
  <div class="section-container">
    {title1_html}
    <div class="grid">{c1}</div>
    {day2_html}
  </div>"""
        total_metric = count1 + count2
    else:
        # 選手個人賽程模式：將 day1 與 day2 合併解析
        full_p_text = data1_text + "\n" + data2_text
        body_content_html, total_metric = parse_personal_text(full_p_text)
        body_content = f"""
  <div class="section-container">
    {body_content_html}
  </div>"""

    sub_title = html_lib.escape(sub_title)
    main_title = html_lib.escape(main_title)
    tag_left = html_lib.escape(tag_left)
    tag_right = html_lib.escape(tag_right)

    has_sub = bool(sub_title.strip())
    has_main = bool(main_title.strip())
    has_tag_l = bool(tag_left.strip())
    has_tag_r = bool(tag_right.strip())
    
    sub_html = f'<div class="sub-title">{sub_title}</div>' if has_sub else ''
    main_html = f'<div class="main-title">{main_title}</div>' if has_main else ''
    
    tags_inner = ""
    if has_tag_l:
        tags_inner += f'<span class="tag-yellow">{tag_left}</span>'
    if has_tag_r:
        tags_inner += f'<span class="tag-white">{tag_right}</span>'
        
    tags_html = f'<div class="tags">{tags_inner}</div>' if (has_tag_l or has_tag_r) else ''
    badge_html = f'<div class="badge-icon">{badge_svg(bg_color)}</div>' if (has_sub or has_main or has_tag_l or has_tag_r) else ''
    
    header_content = ""
    if badge_html or sub_html or main_html or tags_html:
        header_content = f"""
  <div class="header">
    {badge_html}
    {sub_html}
    {main_html}
    {tags_html}
  </div>"""

    if preview:
        font_css = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;800&display=swap" rel="stylesheet">"""
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
  if (document.fonts && document.fonts.ready) {{ document.fonts.ready.then(fit); }}
  setTimeout(fit, 300);
  setTimeout(fit, 1200);
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
    color: #ffffff;
    width: {POSTER_WIDTH}px;
    padding: 60px 54px {BOTTOM_PAD}px 54px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    transform-origin: top left;
  }}
  .header {{ text-align: center; margin-bottom: 46px; width: 100%; }}
  .badge-icon {{ height: 76px; margin-bottom: 14px; line-height: 0; }}
  .sub-title {{ color: {theme['sub']}; font-size: 40px; font-weight: 800; line-height: 1.3; }}
  .main-title {{
    font-size: {title_font_size}px; font-weight: 800; line-height: 1.2;
    margin: 4px 0 20px 0; color: #ffffff; letter-spacing: 1px;
  }}
  .tags {{ display: flex; justify-content: center; gap: 20px; }}
  .tag-yellow {{
    background-color: {ACCENT_YELLOW}; color: #1f1a05; font-weight: 700;
    padding: 12px 38px; border-radius: 40px; font-size: 28px; line-height: 1.4;
  }}
  .tag-white {{
    background-color: #ffffff; color: #1f2937; font-weight: 700;
    padding: 12px 38px; border-radius: 40px; font-size: 28px; line-height: 1.4;
  }}
  .section-container {{ width: 100%; }}
  .section-title {{
    background-color: {theme['header']}; color: #ffffff; text-align: center;
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
  }}
  .time-header {{
    background-color: {theme['header']}; text-align: center; padding: 16px 0;
    font-size: {body_font_size}px; font-weight: 700; color: #ffffff; line-height: 1.4;
  }}
  .content {{
    flex: 1; background-color: #ffffff; padding: 16px 28px;
    display: flex; flex-direction: column; justify-content: center; gap: 6px;
  }}
  .item {{ font-size: {body_font_size}px; color: #1e293b; font-weight: 700; line-height: 1.4; }}
  .cate-m {{ color: {theme['male']}; font-weight: 800; }}
  .cate-f {{ color: {FEMALE_COLOR}; font-weight: 800; }}

  /* 個人賽程專屬樣式 */
  .p-section-title {{
    background-color: {theme['header']}; color: #ffffff; text-align: center;
    font-size: {body_font_size}px; font-weight: 700; padding: 16px;
    border-radius: 12px; margin: 26px 0 16px 0;
  }}
  .p-box {{
    background-color: #ffffff; border-radius: 14px; overflow: hidden;
    padding: 10px 24px; margin-bottom: 16px;
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
  .p-info {{ flex: 1; }}
  .p-colon {{ margin: 0 8px; color: #64748b; }}
  .p-time {{ color: #0f172a; font-weight: 800; }}
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
    return html_content, total_metric

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
# 主畫面
# -----------------------------------------------------------------------------
st.title("🏸 羽球隊賽程圖片產生器")
st.write(f"請依照下方步驟，選擇海報產出模式並貼入對應文字，即可即時產出 {POSTER_WIDTH}px 寬的完整海報。")

# 模式切換器
st.session_state["mode"] = st.radio(
    "📌 選擇海報產出模式",
    ["整體流程表", "選手個人賽程"],
    horizontal=True
)

st.markdown("---")
st.header("⚙️ 1. 標題、版型與樣式設定")
st.caption("💡 提示：標題、副標題與標籤欄位皆為選填，若不需要可直接留空，海報對應區塊將自動隱藏。")

col_s1, col_s2 = st.columns(2)
with col_s1:
    default_main = "MAUC 秋季賽" if st.session_state["mode"] == "整體流程表" else "MAUC 秋季賽"
    main_title = st.text_input("主標題 (選填)", value=default_main)
    
    default_tag_l = "整體流程表" if st.session_state["mode"] == "整體流程表" else "選手個人賽程"
    tag_left = st.text_input("左側標籤 (選填)", value=default_tag_l)
with col_s2:
    sub_title = st.text_input("副標題 / 隊伍名稱 (選填)", value="2026年牧羽盃全國四季聯賽")
    tag_right = st.text_input("右側標籤 / 日期 (選填)", value="日期：2026/09/28（一）")

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    theme_name = st.selectbox("整體色系", list(THEMES.keys()))
with col_c2:
    body_font_size = st.slider("內文字體大小 (px)", min_value=18, max_value=40, value=26)
with col_c3:
    title_font_size = st.slider("主標題字體大小 (px)", min_value=48, max_value=130, value=100)

st.markdown("---")

# 根據不同模式顯示對應的編輯區
if st.session_state["mode"] == "整體流程表":
    st.header("📝 3. 賽程資料編輯區 (整體流程表)")
    st.info("💡 格式：時間 ｜ 組別 ｜ 選手（全半形皆可）。同時間且**同組別**的多筆選手會自動合併在同一行。")

    col_a, col_b = st.columns(2)
    with col_a:
        date1_title = st.text_input("第一天日期說明 (不需要可留空)", value="")
        data1_text = st.text_area(
            "第一天賽程 (格式：時間 ｜ 組別 ｜ 選手)",
            value=st.session_state["day1_text"],
            height=300,
            placeholder="例如：\n09:00 ｜ 低男單 ｜ 王大明"
        )
    with col_b:
        date2_title = st.text_input("第二天日期說明 (若無可留空)", value="")
        data2_text = st.text_area(
            "第二天賽程 (格式：時間 ｜ 組別 ｜ 選手)",
            value=st.session_state["day2_text"],
            height=300,
            placeholder="若無第二天請保持空白..."
        )
else:
    st.header("📝 3. 選手個人賽程資料編輯區")
    st.info("💡 格式支援類似範例的結構（包含日期區塊、分組標題與選手時間）。")

    col_a, col_b = st.columns(2)
    with col_a:
        date1_title = "" # 整合在文字內
        data1_text = st.text_area(
            "第一天 / 選手個人賽程文字",
            value=st.session_state["p_day1_text"],
            height=350,
        )
    with col_b:
        date2_title = ""
        data2_text = st.text_area(
            "第二天 / 選手個人賽程文字 (若無可留空)",
            value=st.session_state["p_day2_text"],
            height=350,
        )

st.markdown("---")
st.header("🖼️ 4. 即時預覽與圖片下載")

poster_kwargs = dict(
    sub_title=sub_title,
    main_title=main_title,
    tag_left=tag_left,
    tag_right=tag_right,
    date1_title=date1_title,
    data1_text=data1_text,
    date2_title=date2_title,
    data2_text=data2_text,
    body_font_size=body_font_size,
    theme_name=theme_name,
    title_font_size=title_font_size,
    mode=st.session_state["mode"],
)

preview_html, total_metric = generate_poster_html(preview=True, **poster_kwargs)

st.subheader("🌐 網頁即時預覽 (自動縮放符合畫面・無捲動軸)")
st.components.v1.html(preview_html, height=900, scrolling=False)

st.subheader("📥 匯出為高解析 PNG 圖片")
st.caption(f"下載的圖片與上方預覽使用同一份版面，完整 {POSTER_WIDTH}px 寬、高度依內容自動裁切。")

if st.button("🚀 產出 PNG 圖片檔案", type="primary"):
    with st.spinner(f"正在轉換為 {POSTER_WIDTH}px 高解析圖片..."):
        try:
            png_html, total_metric = generate_poster_html(preview=False, **poster_kwargs)
            out_path = render_png(png_html, total_metric)
            if os.path.exists(out_path):
                st.image(out_path, caption=f"已產出圖檔預覽 ({POSTER_WIDTH}px 寬)", use_container_width=True)
                with open(out_path, "rb") as file:
                    file_name_prefix = main_title if main_title.strip() else "羽球隊賽程表"
                    st.download_button(
                        label="⬇️ 點此下載圖檔 (PNG)",
                        data=file,
                        file_name=f"{file_name_prefix}_{st.session_state['mode']}.png",
                        mime="image/png"
                    )
        except Exception as e:
            st.error(f"圖片產出失敗：{e}")
