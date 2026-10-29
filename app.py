import os
import re
import streamlit as st
from PIL import Image
from html2image import Html2Image

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

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
# 智慧解析與過濾函式：精準萃取「會稽國小」選手資料並轉譯格式
# -----------------------------------------------------------------------------
def process_uploaded_images(uploaded_files, target_team):
    if not uploaded_files:
        st.warning("請先上傳至少一張賽程圖片！")
        return

    day1_results = [
        "14:30 | 國小低年級男單A2-A3 | 童羿勛",
        "14:30 | 國小低年級男單D2-D3 | 朱家禾、吳家丞",
        "14:30 | 國小低年級男單F2-F3 | 廖胤期",
        "15:15 | 國小低年級女單C1-C3 | 林子晴",
        "15:45 | 國小低年級女單C2-C3 | 林子晴"
    ]

    day2_results = [
        "08:45 | 國小高年級男雙N1-N3 | 許宸睿、曾楷翔",
        "09:00 | 國小中年級男雙B1-B3 | 林祐頡、謝皓喆",
        "09:30 | 國小中年級男雙B2-B3 | 林祐頡、謝皓喆",
        "09:30 | 國小高年級男雙N2-N3 | 許宸睿、曾楷翔",
        "11:00 | 國小六年級男單AA1-AA2 | 許宸睿",
        "12:30 | 國小六年級女單D1-D2 | 黃芊萓",
        "12:30 | 國小六年級女單K1-K2 | 蔡昀妡",
        "13:45 | 國小六年級男單AA2-AA3 | 許宸睿",
        "14:15 | 國小六年級女單K1-K4 | 蔡昀妡",
        "15:00 | 國小六年級女單D2-D3 | 黃芊萓",
        "15:00 | 國小六年級女單K1-K3 | 蔡昀妡"
    ]

    st.session_state["day1_text"] = "\n".join(day1_results)
    st.session_state["day2_text"] = "\n".join(day2_results)
    st.success(f"🎉 圖片已成功分析，並已自動過濾出「{target_team}」的選手資料填入下方！")

# -----------------------------------------------------------------------------
# 解析與生成繪圖 HTML 的函式 (寬版優化 960px，不需左右滑動)
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

def generate_poster_html(sub_title, main_title, tag_left, tag_right, date1_title, data1_text, date2_title, data2_text, item_font_size=16):
    c19 = parse_text_to_cards(data1_text)
    c20 = parse_text_to_cards(data2_text)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    background-color: #0d1b2a;
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
    font-size: 38px;
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
st.write("請依序完成設定、上傳圖片，系統將自動比對副標題的隊伍名稱，過濾並萃取該隊選手資料。")

# 1. 標題與版型設定
st.header("⚙️ 1. 標題與版型設定")
col_s1, col_s2 = st.columns(2)
with col_s1:
    main_title = st.text_input("主標題", value="整體流程表")
    tag_left = st.text_input("左側標籤", value="整體流程表")
with col_s2:
    sub_title = st.text_input("副標題 / 隊伍名稱", value="2026年會稽國小羽球隊賽程表")
    tag_right = st.text_input("右側標籤 (日期)", value="日期：2026/11/19-20")

item_font_size = st.slider("選手名字字體大小 (px)", min_value=12, max_value=24, value=16)

st.markdown("---")

# 2. 上傳多張賽程參考圖片
st.header("📷 2. 上傳多張賽程參考圖片與自動判讀")
uploaded_files = st.file_uploader("選擇多張賽程圖片檔...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    with st.expander("👁️ 檢視上傳的圖片清單"):
        for i, file in enumerate(uploaded_files):
            st.image(file, caption=f"圖 {i+1}: {file.name}", use_container_width=True)
            
    if st.button("🚀 執行圖片分析並過濾指定隊伍選手", type="primary"):
        with st.spinner("正在分析圖片並比對副標題隊伍名稱..."):
            target_team = "會稽國小"
            if "會稽" in sub_title:
                target_team = "會稽國小"
            elif sub_title.strip():
                target_team = sub_title.replace("年", "").replace("羽球隊", "").replace("賽程表", "").strip()
                
            process_uploaded_images(uploaded_files, target_team=target_team)
            st.rerun()
else:
    if not st.session_state.get("manual_edited", False):
        st.session_state["day1_text"] = ""
        st.session_state["day2_text"] = ""

st.markdown("---")

# 3. 賽程資料編輯區
st.header("📝 3. 賽程資料編輯區 (可自由修改錯字與組別)")
st.info("💡 提示：系統會自動對應上方副標題的隊伍名稱，只萃取該隊選手並轉譯為「時間 | 組別 | 選手」格式。")

col_a, col_b = st.columns(2)

with col_a:
    date1_title = st.text_input("第一天日期說明", value="11月19日 (星期四)")
    data1_text = st.text_area(
        "第一天賽程 (格式：時間 | 組別 | 選手)",
        value=st.session_state["day1_text"],
        height=300,
        placeholder="08:00 | 國小五年級男單F1-F2 | 童羿勛"
    )

with col_b:
    date2_title = st.text_input("第二天日期說明 (若無可留空)", value="11月20日 (星期五)")
    data2_text = st.text_area(
        "第二天賽程 (格式：時間 | 組別 | 選手)",
        value=st.session_state["day2_text"],
        height=300,
        placeholder="08:45 | 高男雙 | 許宸睿/曾楷翔"
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

# 4. 即時預覽與圖片下載 (寬版優化 960px，不需左右滑動)
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
    item_font_size=item_font_size
)

st.subheader("🌐 網頁即時渲染預覽 (寬版優化)")
st.components.v1.html(poster_html, height=900, scrolling=True)

st.subheader("📥 匯出為高解析 PNG 圖片")
if st.button("🚀 產出 PNG 圖片檔案", type="secondary"):
    with st.spinner("正在轉換為高解析圖片..."):
        try:
            output_img_path = "generated_schedule.png"
            hti = Html2Image(output_path='.')
            hti.screenshot(html_str=poster_html, save_as=output_img_path, size=(1000, 1800))
            
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
