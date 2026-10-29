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
BOTTOM_PAD = 120         # 海報底部留白 (px)，預覽與 PNG 共用
FEMALE_COLOR = "#be1e4a" # 女子組別文字色 (固定，不隨色系變動)
ACCENT_YELLOW = "#f0c030"  # 黃色標籤與圖示 (固定)

# 色系：只改原本「藍色」的部分 (背景、時間列、男子組別文字、副標題)
# 白色卡片內容區、黃色標籤、白色標籤、女子紅字都不變
THEMES = {
    "藍色體系": dict(bg="#13214b", header="#23407c", male="#1d4f9f", sub="#c3cdf2"),
    "綠色體系": dict(bg="#0b3d2e", header="#1f6f50", male="#1b7a4f", sub="#b7e4cf"),
    "灰色體系": dict(bg="#1f2937", header="#4b5563", male="#374151", sub="#d1d5db"),
    "墨黑體系": dict(bg="#111111", header="#3a3a3a", male="#3f3f46", sub="#d4d4d8"),
    "紫色體系": dict(bg="#2a1a5e", header="#5b3fa5", male="#5b3fa5", sub="#d8ccf5"),
    "青藍綠體系": dict(bg="#0c3b45", header="#1f6f7d", male="#1a6b7a", sub="#bde3ea"),
}

# -----------------------------------------------------------------------------
# 中文字型 (PNG 用：轉成 base64 內嵌，避免 file:// 讀不到而變成方塊字)
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
# Session State
# -----------------------------------------------------------------------------
if "day1_text" not in st.session_state:
    st.session_state["day1_text"] = ""
if "day2_text" not in st.session_state:
    st.session_state["day2_text"] = ""

# -----------------------------------------------------------------------------
# 解析文字 → 卡片 HTML
# 同一個時間的多筆資料會合併在同一張卡片 (多行)
# 組別含「女」→ 紅色；其餘 (男) → 色系顏色
# -----------------------------------------------------------------------------
def parse_text_to_cards(text):
    groups = {}   # time -> list of (cate, players)
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
        groups[time_str].append((cate, players))

    cards_html = ""
    for time_str in order:
        items_html = ""
        for cate, players in groups[time_str]:
            players_e = html_lib.escape(players)
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
# 產生海報 HTML
# preview=True  → 加上縮放腳本，讓海報剛好塞進預覽區 (無 scroll bar)
# preview=False → 原尺寸，用於輸出 PNG
# 兩者使用「同一份」版面 CSS，所以預覽與下載圖片一致
# -----------------------------------------------------------------------------
def generate_poster_html(sub_title, main_title, tag_left, tag_right,
                         date1_title, data1_text, date2_title, data2_text,
                         body_font_size=28, theme_name="藍色體系", title_font_size=100,
                         preview=True):
    theme = THEMES[theme_name]
    bg_color = theme["bg"]

    c1, count1 = parse_text_to_cards(data1_text)
    show_day2 = bool(data2_text.strip())
    c2, count2 = parse_text_to_cards(data2_text) if show_day2 else ("", 0)

    sub_title = html_lib.escape(sub_title)
    main_title = html_lib.escape(main_title)
    tag_left = html_lib.escape(tag_left)
    tag_right = html_lib.escape(tag_right)

    title1_html = (f'<div class="section-title">{html_lib.escape(date1_title)}</div>'
                   if date1_title.strip() else "")
    title2_html = (f'<div class="section-title">{html_lib.escape(date2_title)}</div>'
                   if date2_title.strip() else "")

    # 字型：預覽用 Google Fonts，PNG 用內嵌 base64
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

    day2_html = (f'{title2_html}<div class="grid">{c2}</div>' if show_day2 else "")

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
</style>
</head>
<body>
{wrap_open}
<div id="poster">
  <div class="header">
    <div class="badge-icon">{badge_svg(bg_color)}</div>
    <div class="sub-title">{sub_title}</div>
    <div class="main-title">{main_title}</div>
    <div class="tags">
      <span class="tag-yellow">{tag_left}</span>
      <span class="tag-white">{tag_right}</span>
    </div>
  </div>

  <div class="section-container">
    {title1_html}
    <div class="grid">{c1}</div>
    {day2_html}
  </div>
</div>
{wrap_close}
{preview_script}
</body>
</html>"""
    return html_content, count1, count2

# -----------------------------------------------------------------------------
# 輸出 PNG：先用足夠高的視窗截圖，再依實際內容裁切底部，
# 結果會與預覽的完整版面一致
# -----------------------------------------------------------------------------
def render_png(html_str, count1, count2, out_path="generated_schedule.png"):
    rows = math.ceil(count1 / 2) + math.ceil(count2 / 2)
    tall_height = 1000 + rows * 380      # 保守高估，之後會裁切

    if os.path.exists(out_path):
        os.remove(out_path)

    hti = Html2Image(
        output_path=".",
        custom_flags=[
            "--no-sandbox",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--virtual-time-budget=10000",   # 等字型載入完成
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
st.write(f"請依照下方步驟，將賽程圖片轉為文字後貼入編輯區，即可即時產出 {POSTER_WIDTH}px 寬的完整海報。")

st.header("⚙️ 1. 標題、版型與樣式設定")
col_s1, col_s2 = st.columns(2)
with col_s1:
    main_title = st.text_input("主標題", value="MAUC 秋季賽")
    tag_left = st.text_input("左側標籤", value="整體流程表")
with col_s2:
    sub_title = st.text_input("副標題 / 隊伍名稱", value="2026年牧羽盃全國四季聯賽")
    tag_right = st.text_input("右側標籤 (日期)", value="日期：2026/09/28（一）")

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    theme_name = st.selectbox("整體色系", list(THEMES.keys()))
with col_c2:
    body_font_size = st.slider("內文字體大小 (px)（日期／時間／選手同大小）", min_value=18, max_value=40, value=28)
with col_c3:
    title_font_size = st.slider("主標題字體大小 (px)", min_value=48, max_value=130, value=100)

st.markdown("---")

st.header("📷 2. 賽程圖片轉文字指引")
st.info("💡 **操作說明**：請將賽程截圖提供給 AI，並使用下方指定的提示詞，將結果直接複製貼到第 3 區的編輯格中。")

ai_prompt_text = f"""請將這張圖改成可直接複製到網頁的格式(包含斷行)，選手僅帶出{sub_title.replace('賽程表', '').replace('隊', '')}的即可，單打項目的組別名稱請去掉「男單」、「女單」（例如：國小五年級男單改為國小五年級）。
日期
時間 | 組別 | 選手"""

with st.expander("📋 點此查看/複製 AI 轉換指令"):
    st.code(ai_prompt_text, language="text")

st.markdown("---")

st.header("📝 3. 賽程資料編輯區")
st.info("💡 格式：時間 ｜ 組別 ｜ 選手（全半形皆可）。同一個時間的多筆資料會自動合併在同一張卡片；組別含「女」會顯示紅色。日期說明若留空，海報上就不會顯示日期標題列。")

col_a, col_b = st.columns(2)
with col_a:
    date1_title = st.text_input("第一天日期說明 (不需要可留空)", value="")
    data1_text = st.text_area(
        "第一天賽程 (格式：時間 ｜ 組別 ｜ 選手)",
        value=st.session_state["day1_text"],
        height=300,
        placeholder="例如：\n09:00 ｜ 低男單 ｜ 童羿勛、謝皓喆"
    )
with col_b:
    date2_title = st.text_input("第二天日期說明 (若無可留空)", value="")
    data2_text = st.text_area(
        "第二天賽程 (格式：時間 ｜ 組別 ｜ 選手)",
        value=st.session_state["day2_text"],
        height=300,
        placeholder="若無第二天請保持空白..."
    )

with st.expander("➕ 點此新增更多天數賽程 (若賽程超過兩天)"):
    extra_date_title = st.text_input("額外天數日期說明", value="")
    extra_data_text = st.text_area(
        "額外天數賽程 (格式：時間 ｜ 組別 ｜ 選手)",
        value="",
        height=150,
        placeholder="10:00 ｜ 決賽 ｜ ..."
    )

st.markdown("---")

st.header("🖼️ 4. 即時預覽與圖片下載")

combined_day2_text = data2_text
if extra_data_text.strip():
    combined_day2_text += f"\n{extra_data_text}"

poster_kwargs = dict(
    sub_title=sub_title,
    main_title=main_title,
    tag_left=tag_left,
    tag_right=tag_right,
    date1_title=date1_title,
    data1_text=data1_text,
    date2_title=date2_title,
    data2_text=combined_day2_text,
    body_font_size=body_font_size,
    theme_name=theme_name,
    title_font_size=title_font_size,
)

preview_html, n1, n2 = generate_poster_html(preview=True, **poster_kwargs)

st.subheader("🌐 網頁即時預覽 (自動縮放符合畫面・無捲動軸)")
# 初始高度只是暫時值，載入後由 iframe 內的腳本依縮放比例自動調整，因此不會出現 scroll bar
st.components.v1.html(preview_html, height=900, scrolling=False)

st.subheader("📥 匯出為高解析 PNG 圖片")
st.caption(f"下載的圖片與上方預覽使用同一份版面，完整 {POSTER_WIDTH}px 寬、高度依內容自動裁切。")

if st.button("🚀 產出 PNG 圖片檔案", type="primary"):
    with st.spinner(f"正在轉換為 {POSTER_WIDTH}px 高解析圖片..."):
        try:
            png_html, n1, n2 = generate_poster_html(preview=False, **poster_kwargs)
            out_path = render_png(png_html, n1, n2)
            if os.path.exists(out_path):
                st.image(out_path, caption=f"已產出圖檔預覽 ({POSTER_WIDTH}px 寬)", use_container_width=True)
                with open(out_path, "rb") as file:
                    st.download_button(
                        label="⬇️ 點此下載圖檔 (PNG)",
                        data=file,
                        file_name=f"{main_title}_賽程表.png",
                        mime="image/png"
                    )
        except Exception as e:
            st.error(f"圖片產出失敗：{e}")
