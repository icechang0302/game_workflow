import os
import streamlit as st
from PIL import Image
from html2image import Html2Image

st.set_page_config(
    page_title="羽球隊賽程圖片產生器",
    page_icon="🏸",
    layout="centered"
)

# -----------------------------------------------------------------------------
# 初始化 Session State
# -----------------------------------------------------------------------------
if "day1_text" not in st.session_state:
    st.session_state["day1_text"] = ""
if "day2_text" not in st.session_state:
    st.session_state["day2_text"] = ""

# -----------------------------------------------------------------------------
# 解析與生成繪圖 HTML 的函式 (支援自訂背景色與字型大小)
# -----------------------------------------------------------------------------
def parse_text_to_cards(text):
    cards_html = ""
    lines = text.strip().split("\n")
    for line in lines:
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")]
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
    return cards_html

def generate_poster_html(sub_title, main_title, tag_left, tag_right, date1_title, data1_text, date2_title, data2_text, item_font_size=16, bg_color="#0d1b2a", title_font_size=38):
    c19 = parse_text_to_cards(data1_text)
    c20 = parse_text_to_cards(data2_text)

    # 動態計算高度或使用足夠寬敞的版型，避免內部捲動
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    background-color: {bg_color};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans TC", sans-serif;
    color: #ffffff;
    margin: 0;
    padding: 35px 30px;
    width: 960px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .header {{
    text-align: center;
    margin-bottom: 25px;
    width: 100%;
  }}
  .badge-icon {{
    font-size: 36px;
    margin-bottom: 6px;
  }}
  .sub-title {{
    color: #cbd5e1;
    font-size: 20px;
    font-weight: 600;
  }}
  .main-title {{
    font-size: {title_font_size}px;
    font-weight: 800;
    margin: 8px 0 14px 0;
    color: #ffffff;
    letter-spacing: 1px;
  }}
  .tags {{
    display: flex;
    justify-content: center;
    gap: 14px;
  }}
  .tag-yellow {{
    background-color: #f59e0b;
    color: #000;
    font-weight: bold;
    padding: 6px 18px;
    border-radius: 18px;
    font-size: 16px;
  }}
  .tag-white {{
    background-color: #ffffff;
    color: #000;
    font-weight: bold;
    padding: 6px 18px;
    border-radius: 18px;
    font-size: 16px;
  }}
  .section-container {{
    width: 100%;
    max-width: 900px;
  }}
  .section-title {{
    background-color: #1e3a8a;
    color: #ffffff;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    padding: 12px;
    border-radius: 8px;
    margin: 22px 0 14px 0;
    border: 2px solid #3b82f6;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 12px;
  }}
  .card {{
    background-color: #1e3a8a;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
  }}
  .time-header {{
    background-color: #1e40af;
    text-align: center;
    padding: 8px 0;
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
    border-bottom: 1px solid #2563eb;
  }}
  .content {{
    background-color: #ffffff;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
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

    {f'<div class="section-title">📅 {date2_title}</div><div class="grid">{c20}</div>' if date2_title.strip() else ''}
  </div>
</body>
</html>"""
    return html_content

# -----------------------------------------------------------------------------
# Streamlit 主畫面佈局
# -----------------------------------------------------------------------------
st.title("🏸 羽球隊賽程圖片產生器")
st.write("請依照下方步驟，將賽程圖片轉為文字後貼入編輯區，即可即時產出海報。")

# 1. 標題、版型與樣式設定
st.header("⚙️ 1. 標題、版型與樣式設定")
col_s1, col_s2 = st.columns(2)
with col_s1:
    main_title = st.text_input("主標題", value="整體流程表")
    tag_left = st.text_input("左側標籤", value="整體流程表")
with col_s2:
    sub_title = st.text_input("副標題 / 隊伍名稱", value="2026年會稽國小羽球隊賽程表")
    tag_right = st.text_input("右側標籤 (日期)", value="日期：2026/11/19-20")

# 新增背景色與字型大小自訂選項
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    bg_color_option = st.selectbox(
        "海報背景主題", 
        ["經典深藍 (#0d1b2a)", "質感墨黑 (#111111)", "沉穩深灰 (#1e293b)", "運動深綠 (#064e3b)"]
    )
    # 對應色彩代碼
    bg_color_map = {
        "經典深藍 (#0d1b2a)": "#0d1b2a",
        "質感墨黑 (#111111)": "#111111",
        "沉穩深灰 (#1e293b)": "#1e293b",
        "運動深綠 (#064e3b)": "#064e3b"
    }
    selected_bg = bg_color_map[bg_color_option]

with col_c2:
    item_font_size = st.slider("選手名字字體大小 (px)", min_value=12, max_value=24, value=16)

with col_c3:
    title_font_size = st.slider("主標題字體大小 (px)", min_value=28, max_value=48, value=38)

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
st.info("💡 請將 AI 整理好的賽程文字直接貼入下方對應的日期欄位中（格式：時間 | 組別 | 選手）。")

col_a, col_b = st.columns(2)

with col_a:
    date1_title = st.text_input("第一天日期說明", value="11月19日 (星期四)")
    data1_text = st.text_area(
        "第一天賽程 (格式：時間 | 組別 | 選手)",
        value=st.session_state["day1_text"],
        height=300,
        placeholder="例如：\n14:30 | 國小低年級 | 童羿勛\n14:30 | 國小低年級 | 朱家禾、吳家丞"
    )

with col_b:
    date2_title = st.text_input("第二天日期說明 (若無可留空)", value="11月20日 (星期五)")
    data2_text = st.text_area(
        "第二天賽程 (格式：時間 | 組別 | 選手)",
        value=st.session_state["day2_text"],
        height=300,
        placeholder="例如：\n08:45 | 國小高年級男雙 | 許宸睿、曾楷翔"
    )

with st.expander("➕ 點此新增更多天數賽程 (若賽程超過兩天)"):
    extra_date_title = st.text_input("額外天數日期說明", value="11月21日 (星期六)")
    extra_data_text = st.text_area(
        "額外天數賽程 (格式：時間 | 組別 | 選手)",
        value="",
        height=150,
        placeholder="10:00 | 決賽 | ..."
    )

st.markdown("---")

# 4. 即時預覽與圖片下載 (取消 scroll bar，設定高彈性高度且 scolling=False)
st.header("🖼️ 4. 即時預覽與圖片下載")

combined_day2_text = data2_text
if extra_date_title and extra_data_text.strip():
    combined_day2_text += f"\n{extra_data_text}"

poster_html = generate_poster_html(
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

st.subheader("🌐 網頁即時渲染預覽 (無捲動軸優化)")
# 將 scrolling 設為 False，並給予足夠展開的高度 (例如 1800px)，徹底消滅內嵌捲動軸
st.components.v1.html(poster_html, height=1800, scrolling=False)

st.subheader("📥 匯出為高解析 PNG 圖片")
if st.button("🚀 產出 PNG 圖片檔案", type="primary"):
    with st.spinner("正在轉換為高解析圖片..."):
        try:
            output_img_path = "generated_schedule.png"
            hti = Html2Image(output_path='.')
            hti.screenshot(html_str=poster_html, save_as=output_img_path, size=(1000, 2200))
            
            if os.path.exists(output_img_path):
                st.image(output_img_path, caption="已產出圖檔預覽", use_container_width=True)
                with open(output_img_path, "rb") as file:
                    st.download_button(
                        label="⬇️ 點此下載圖檔 (PNG)",
                        data=file,
                        file_name=f"{main_title}_賽程表.png",
                        mime="image/png"
                    )
        except Exception as e:
            st.error(f"圖片產出失敗：{e}")
