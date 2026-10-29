import os
import urllib.request
import streamlit as st
from PIL import Image
from html2image import Html2Image

st.set_page_config(
    page_title="羽球隊賽程圖片產生器",
    page_icon="🏸",
    layout="centered"
)

# -----------------------------------------------------------------------------
# 初始化中文字型 (確保下載 PNG 絕不出現方塊字亂碼)
# -----------------------------------------------------------------------------
@st.cache_resource
def setup_chinese_font():
    font_filename = "NotoSansTC-Regular.ttf"
    font_path = os.path.abspath(font_filename)
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass
    return font_path

font_path = setup_chinese_font()

# -----------------------------------------------------------------------------
# 初始化 Session State
# -----------------------------------------------------------------------------
if "day1_text" not in st.session_state:
    st.session_state["day1_text"] = ""
if "day2_text" not in st.session_state:
    st.session_state["day2_text"] = ""

# -----------------------------------------------------------------------------
# 解析與生成繪圖 HTML 的函式
# -----------------------------------------------------------------------------
def parse_text_to_cards(text):
    cards_html = ""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    for line in lines:
        normalized_line = line.replace("｜", "|")
        parts = [p.strip() for p in normalized_line.split("|")]
        
        if len(parts) >= 3:
            time_str, cate, players = parts[0], parts[1], parts[2]
            cards_html += f"""
            <div class="card">
              <div class="time-header">{time_str}</div>
              <div class="content">
                <div class="item"><span class="cate">【{cate}】</span>{players}</div>
              </div>
            </div>
            """
        elif len(parts) == 2:
            time_str, players = parts[0], parts[1]
            cards_html += f"""
            <div class="card">
              <div class="time-header">{time_str}</div>
              <div class="content">
                <div class="item">{players}</div>
              </div>
            </div>
            """
    return cards_html, len(lines)

def generate_poster_html(sub_title, main_title, tag_left, tag_right, date1_title, data1_text, date2_title, data2_text, item_font_size=16, bg_color="#0d1b2a", title_font_size=46):
    c19, count1 = parse_text_to_cards(data1_text)
    c20, count2 = parse_text_to_cards(data2_text)

    # 動態計算高度
    total_cards = max(count1, count2) if date2_title.strip() and data2_text.strip() else count1
    dynamic_height = max(1600, 500 + (total_cards * 110))

    # 使用絕對路徑確保 html2image 能夠完美讀取中文字型
    font_url_path = font_path.replace("\\", "/")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'Noto Sans TC';
    src: url('file://{font_url_path}');
  }}
  body {{
    background-color: {bg_color};
    font-family: 'Noto Sans TC', sans-serif;
    color: #ffffff;
    margin: 0;
    padding: 50px 50px 100px 50px;
    width: 1580px;
    height: {dynamic_height}px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .header {{
    text-align: center;
    margin-bottom: 35px;
    width: 100%;
  }}
  .badge-icon {{
    font-size: 46px;
    margin-bottom: 10px;
  }}
  .sub-title {{
    color: #cbd5e1;
    font-size: 24px;
    font-weight: 600;
  }}
  .main-title {{
    font-size: {title_font_size}px;
    font-weight: 800;
    margin: 12px 0 18px 0;
    color: #ffffff;
    letter-spacing: 1.5px;
  }}
  .tags {{
    display: flex;
    justify-content: center;
    gap: 18px;
  }}
  .tag-yellow {{
    background-color: #f59e0b;
    color: #000;
    font-weight: bold;
    padding: 8px 24px;
    border-radius: 22px;
    font-size: 18px;
  }}
  .tag-white {{
    background-color: #ffffff;
    color: #000;
    font-weight: bold;
    padding: 8px 24px;
    border-radius: 22px;
    font-size: 18px;
  }}
  .section-container {{
    width: 100%;
    max-width: 1460px;
  }}
  .section-title {{
    background-color: #1e3a8a;
    color: #ffffff;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    padding: 15px;
    border-radius: 10px;
    margin: 30px 0 18px 0;
    border: 2px solid #3b82f6;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 15px;
  }}
  .card {{
    background-color: #1e3a8a;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 6px 16px rgba(0,0,0,0.4);
  }}
  .time-header {{
    background-color: #1e40af;
    text-align: center;
    padding: 11px 0;
    font-size: 21px;
    font-weight: bold;
    color: #ffffff;
    border-bottom: 1px solid #2563eb;
  }}
  .content {{
    background-color: #ffffff;
    padding: 16px 22px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
  }}
  .item {{
    font-size: {item_font_size}px;
    color: #1e293b;
    font-weight: 700;
    line-height: 1.4;
  }}
  .cate {{
    color: #dc2626;
    font-weight: bold;
  }}
</style>
</head>
<body>
  <div class="header">
    <div class="badge-icon">🏸</div>
    <div class="sub-title">{sub_title}</div>
    <div class="main-title">{main_title}</div>
    <div class="tags">
      <span class="tag-yellow">{tag_left}</span>
      <span class="tag-white">{tag_right}</span>
    </div>
  </div>

  <div class="section-container">
    <div class="section-title">📅 {date1_title}</div>
    <div class="grid">
      {c19}
    </div>

    {f'<div class="section-title">📅 {date2_title}</div><div class="grid">{c20}</div>' if date2_title.strip() and data2_text.strip() else ''}
  </div>
</body>
</html>"""
    return html_content, dynamic_height

# -----------------------------------------------------------------------------
# Streamlit 主畫面佈局
# -----------------------------------------------------------------------------
st.title("🏸 羽球隊賽程圖片產生器")
st.write("請依照下方步驟，將賽程圖片轉為文字後貼入編輯區，即可即時產出 1580px 寬版完整海報。")

# 1. 標題、版型與樣式設定
st.header("⚙️ 1. 標題、版型與樣式設定")
col_s1, col_s2 = st.columns(2)
with col_s1:
    main_title = st.text_input("主標題", value="MAUC 秋季賽")
    tag_left = st.text_input("左側標籤", value="整體流程表")
with col_s2:
    sub_title = st.text_input("副標題 / 隊伍名稱", value="2026年會稽國小羽球隊賽程表")
    tag_right = st.text_input("右側標籤 (日期)", value="日期：2026/09/28 (一)")

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    bg_color_option = st.selectbox(
        "海報背景主題", 
        ["經典深藍 (#0d1b2a)", "質感墨黑 (#111111)", "沉穩深灰 (#1e293b)", "運動深綠 (#064e3b)"]
    )
    bg_color_map = {
        "經典深藍 (#0d1b2a)": "#0d1b2a",
        "質感墨黑 (#111111)": "#111111",
        "沉穩深灰 (#1e293b)": "#1e293b",
        "運動深綠 (#064e3b)": "#064e3b"
    }
    selected_bg = bg_color_map[bg_color_option]

with col_c2:
    item_font_size = st.slider("選手名字字體大小 (px)", min_value=12, max_value=28, value=18)

with col_c3:
    title_font_size = st.slider("主標題字體大小 (px)", min_value=32, max_value=60, value=46)

st.markdown("---")

# 2. 賽程圖片轉文字指引與指令
st.header("📷 2. 賽程圖片轉文字指引")
st.info("💡 **操作說明**：請將賽程截圖提供給 AI，並使用下方指定的提示詞，將結果直接複製貼到第 3 區的編輯格中。")

ai_prompt_text = f"""請將這張圖改成可直接複製到網頁的格式(包含斷行)，選手僅帶出{sub_title.replace('賽程表', '').replace('隊', '')}的即可，單打項目的組別名稱請去掉「男單」、「女單」（例如：國小五年級男單改為國小五年級）。
日期
時間 | 組別 | 選手"""

with st.expander("📋 點此查看/複製 AI 轉換指令"):
    st.code(ai_prompt_text, language="text")

st.markdown("---")

# 3. 賽程資料編輯區
st.header("📝 3. 賽程資料編輯區")
st.info("💡 請將 AI 整理好的賽程文字分別貼入下方對應的日期欄位中（格式：時間 ｜ 組別 ｜ 選手，全半形皆可）。")

col_a, col_b = st.columns(2)

with col_a:
    date1_title = st.text_input("第一天日期說明", value="9月28日 (星期一)")
    data1_text = st.text_area(
        "第一天賽程 (格式：時間 ｜ 組別 ｜ 選手)",
        value=st.session_state["day1_text"],
        height=300,
        placeholder="例如：\n09:00 ｜ 國小一 ｜ 王大明"
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

# 4. 即時預覽與圖片下載
st.header("🖼️ 4. 即時預覽與圖片下載")

combined_day2_text = data2_text
if extra_date_title and extra_data_text.strip():
    combined_day2_text += f"\n{extra_data_text}"

poster_html, dynamic_height = generate_poster_html(
    sub_title=sub_title,
    main_title=main_title,
    tag_left=tag_left,
    tag_right=tag_right,
    date1_title=date1_title,
    data1_text=data1_text,
    date2_title=date2_title,
    data2_text=combined_day2_text,
    item_font_size=item_font_size,
    bg_color=selected_bg,
    title_font_size=title_font_size
)

st.subheader("🌐 網頁即時渲染預覽 (完整呈現・無捲動軸)")
# 將元件高度直接設為動態高度，並關閉 scrolling，徹底消除 scroll bar
st.components.v1.html(poster_html, height=dynamic_height, scrolling=False)

st.subheader("📥 匯出為高解析 PNG 圖片")
if st.button("🚀 產出 PNG 圖片檔案", type="primary"):
    with st.spinner("正在轉換為 1580px 高解析圖片..."):
        try:
            output_img_path = "generated_schedule.png"
            hti = Html2Image(output_path='.')
            # 確保下載的圖片尺寸與動態高度完全一致，且字型絕對不會變成方塊字
            hti.screenshot(html_str=poster_html, save_as=output_img_path, size=(1580, dynamic_height))
            
            if os.path.exists(output_img_path):
                st.image(output_img_path, caption="已產出圖檔預覽 (1580px 寬高畫質)", use_container_width=True)
                with open(output_img_path, "rb") as file:
                    st.download_button(
                        label="⬇️ 點此下載圖檔 (PNG)",
                        data=file,
                        file_name=f"{main_title}_賽程表.png",
                        mime="image/png"
                    )
        except Exception as e:
            st.error(f"圖片產出失敗：{e}")
