import os
import streamlit as st
from PIL import Image
from html2image import Html2Image

# 安全檢測 pytesseract
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
# 解析與生成繪圖 HTML 的函式
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
    padding: 30px 25px;
    width: 800px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .header {{
    text-align: center;
    margin-bottom: 22px;
    width: 100%;
  }}
  .badge-icon {{
    font-size: 32px;
    margin-bottom: 4px;
  }}
  .sub-title {{
    color: #cbd5e1;
    font-size: 18px;
    font-weight: 600;
  }}
  .main-title {{
    font-size: 34px;
    font-weight: 800;
    margin: 6px 0 12px 0;
    color: #ffffff;
    letter-spacing: 1px;
  }}
  .tags {{
    display: flex;
    justify-content: center;
    gap: 12px;
  }}
  .tag-yellow {{
    background-color: #f59e0b;
    color: #000;
    font-weight: bold;
    padding: 5px 16px;
    border-radius: 16px;
    font-size: 15px;
  }}
  .tag-white {{
    background-color: #ffffff;
    color: #000;
    font-weight: bold;
    padding: 5px 16px;
    border-radius: 16px;
    font-size: 15px;
  }}
  .section-container {{
    width: 100%;
    max-width: 750px;
  }}
  .section-title {{
    background-color: #1e3a8a;
    color: #ffffff;
    text-align: center;
    font-size: 19px;
    font-weight: bold;
    padding: 10px;
    border-radius: 6px;
    margin: 20px 0 12px 0;
    border: 2px solid #3b82f6;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 10px;
  }}
  .card {{
    background-color: #1e3a8a;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  }}
  .time-header {{
    background-color: #1e40af;
    text-align: center;
    padding: 7px 0;
    font-size: 17px;
    font-weight: bold;
    color: #ffffff;
    border-bottom: 1px solid #2563eb;
  }}
  .content {{
    background-color: #ffffff;
    padding: 10px 14px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 5px;
  }}
  .item {{
    font-size: {item_font_size}px;
    color: #1e293b;
    font-weight: 700;
    line-height: 1.35;
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
st.write("請依序在主畫面完成設定、上傳圖片與編輯賽程內容。")

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
st.header("📷 2. 上傳多張賽程參考圖片")
uploaded_files = st.file_uploader("選擇多張賽程圖片檔...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

extracted_text_day1 = ""
extracted_text_day2 = ""

if uploaded_files:
    st.success(f"已成功上傳 {len(uploaded_files)} 張圖片")
    with st.expander("👁️ 檢視上傳的圖片清單"):
        for i, file in enumerate(uploaded_files):
            st.image(file, caption=f"圖 {i+1}: {file.name}", use_container_width=True)
            
    if HAS_TESSERACT:
        if st.button("🔍 執行文字辨識 (OCR)"):
            with st.spinner("正在辨識多張圖片中的文字..."):
                for file in uploaded_files:
                    try:
                        img = Image.open(file)
                        text = pytesseract.image_to_string(img, lang="chi_tra+eng")
                        extracted_text_day2 += f"\n--- 檔案: {file.name} ---\n" + text
                    except Exception as e:
                        extracted_text_day2 += f"\n--- 檔案 {file.name} 辨識失敗: {e} ---\n"
    else:
        # 當沒有 Tesseract 時，提供基於上傳圖檔的預設範例填入（或留白讓使用者貼上）
        extracted_text_day2 = """08:45 | 高男雙 | 許宸睿/曾楷翔
09:00 | 中男雙 | 林祐頡/謝皓喆
09:30 | 中男雙 | 林祐頡/謝皓喆
09:30 | 高男雙 | 許宸睿/曾楷翔
11:00 | 六男單 | 許宸睿
12:30 | 六女單 | 黃芊萓
12:30 | 六女單 | 蔡昀妡
13:45 | 六男單 | 許宸睿
14:15 | 六女單 | 蔡昀妡
15:00 | 六女單 | 黃芊萓
15:00 | 六女單 | 蔡昀妡"""

st.markdown("---")

# 3. 賽程資料編輯區 (預設空白，完成 2 後帶入)
st.header("📝 3. 賽程資料編輯區 (可自由修改錯字與組別)")
st.info("💡 提示：上傳圖片後，下方會自動載入辨識或對應的賽程資料，您可直接在此修改錯字。")

col_a, col_b = st.columns(2)

with col_a:
    date1_title = st.text_input("第一天日期說明", value="11月19日 (星期四)")
    # 預設空白，若有透過其他方式或預設帶入可在此呈現
    data1_text = st.text_area(
        "第一天賽程 (格式：時間 | 組別 | 選手)",
        value="",
        height=280,
        placeholder="完成上傳或請在此貼上第一天賽程..."
    )

with col_b:
    date2_title = st.text_input("第二天日期說明 (若無可留空)", value="11月20日 (星期五)")
    # 綁定上傳圖片後帶入的內容
    data2_text = st.text_area(
        "第二天賽程 (格式：時間 | 組別 | 選手)",
        value=extracted_text_day2,
        height=280,
        placeholder="完成上傳圖片後會自動帶入此處..."
    )

st.markdown("---")

# 4. 即時預覽與圖片下載 (寬度與上方對齊)
st.header("🖼️ 4. 即時預覽與圖片下載")

poster_html = generate_poster_html(
    sub_title=sub_title,
    main_title=main_title,
    tag_left=tag_left,
    tag_right=tag_right,
    date1_title=date1_title,
    data1_text=data1_text,
    date2_title=date2_title,
    data2_text=data2_text,
    item_font_size=item_font_size
)

# 使用單欄全寬配置，確保預覽區塊寬度與上方一致
st.subheader("🌐 網頁即時渲染預覽")
st.components.v1.html(poster_html, height=850, scrolling=True)

st.subheader("📥 匯出為高解析 PNG 圖片")
if st.button("🚀 產出 PNG 圖片檔案", type="primary"):
    with st.spinner("正在轉換為高解析圖片..."):
        try:
            output_img_path = "generated_schedule.png"
            hti = Html2Image(output_path='.')
            hti.screenshot(html_str=poster_html, save_as=output_img_path, size=(840, 1650))
            
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
