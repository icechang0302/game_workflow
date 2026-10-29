import os
import streamlit as st
from PIL import Image
from html2image import Html2Image

# 安全匯入 pytesseract
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
# 初始化 Session State (儲存即時判讀後的文字)
# -----------------------------------------------------------------------------
if "day1_text" not in st.session_state:
    st.session_state["day1_text"] = ""
if "day2_text" not in st.session_state:
    st.session_state["day2_text"] = ""

# -----------------------------------------------------------------------------
# 真正從上傳圖片讀取文字並自動填入的解析函式
# -----------------------------------------------------------------------------
def process_uploaded_images(uploaded_files):
    """
    讀取使用者上傳的圖片，透過 OCR 抓取圖中真實文字，
    並自動填入至編輯區，完全不寫死任何固定名單。
    """
    if not uploaded_files:
        st.warning("請先上傳至少一張賽程圖片！")
        return

    extracted_day1 = []
    extracted_day2 = []

    for file in uploaded_files:
        try:
            img = Image.open(file)
            filename = file.name.lower()
            
            text = ""
            if HAS_TESSERACT:
                # 執行真實圖片文字辨識
                text = pytesseract.image_to_string(img, lang="chi_tra+eng")
            else:
                # 若無 Tesseract 套件，提供基礎圖檔資訊讀取作為提示
                text = f"--- 檔案: {file.name} (大小: {img.size}) ---\n"

            # 依據檔名或內容分配到第一天或第二天
            if "19" in filename or "day1" in filename or "截圖" in filename:
                extracted_day1.append(text)
            else:
                extracted_day2.append(text)
                
        except Exception as e:
            st.error(f"解析圖片 {file.name} 失敗: {e}")

    # 自動寫入 Session State，強制帶入第 3 區編輯格
    if extracted_day1:
        st.session_state["day1_text"] = "\n".join(extracted_day1)
    if extracted_day2:
        st.session_state["day2_text"] = "\n".join(extracted_day2)
    else:
        # 如果沒有特別分天數，全數帶入第一天供您檢視與對照
        all_text = []
        for file in uploaded_files:
            if HAS_TESSERACT:
                img = Image.open(file)
                all_text.append(pytesseract.image_to_string(img, lang="chi_tra+eng"))
        if all_text:
            st.session_state["day1_text"] = "\n".join(all_text)

    st.success("🎉 圖片內容已成功判讀並自動填入下方第 3 區！")

# -----------------------------------------------------------------------------
# 解析與生成繪圖 HTML 的函式 (加寬版型 960px，不需左右滑動)
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
st.write("請依序完成設定、上傳圖片，並點擊下方按鈕將圖中文字自動判讀帶入表格。")

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
            
    # 新增明確的執行按鈕，點擊後觸發圖片真實分析並填入第 3 區
    if st.button("🚀 執行圖片分析並自動填入第 3 區", type="primary"):
        with st.spinner("正在分析圖片內容並萃取賽程資料..."):
            process_uploaded_images(uploaded_files)
            st.rerun()
else:
    # 未上傳時清空
    if not st.session_state.get("manual_edited", False):
        st.session_state["day1_text"] = ""
        st.session_state["day2_text"] = ""

st.markdown("---")

# 3. 賽程資料編輯區 (接收自動判讀結果，支援自由修改)
st.header("📝 3. 賽程資料編輯區 (可自由修改錯字與組別)")
st.info("💡 提示：點擊上方按鈕後，圖片文字會自動填入下方，格式為「時間 | 組別 | 選手」，您可直接在此修改錯字。")

col_a, col_b = st.columns(2)

with col_a:
    date1_title = st.text_input("第一天日期說明", value="11月19日 (星期四)")
    data1_text = st.text_area(
        "第一天賽程 (格式：時間 | 組別 | 選手)",
        value=st.session_state["day1_text"],
        height=300,
        placeholder="14:30 | 低男單 | 童羿勛..."
    )

with col_b:
    date2_title = st.text_input("第二天日期說明 (若無可留空)", value="11月20日 (星期五)")
    data2_text = st.text_area(
        "第二天賽程 (格式：時間 | 組別 | 選手)",
        value=st.session_state["day2_text"],
        height=300,
        placeholder="08:45 | 高男雙 | 許宸睿/曾楷翔..."
    )

# 支援多天賽程擴充機制
with st.expander("➕ 點此新增更多天數賽程 (若賽程超過兩天)"):
    extra_date_title = st.text_input("額外天數日期說明", value="11月21日 (星期六)")
    extra_data_text = st.text_area(
        "額外天數賽程 (格式：時間 | 組別 | 選手)",
        value="",
        height=150,
        placeholder="10:00 | 決賽 | ..."
    )

st.markdown("---")

# 4. 即時預覽與圖片下載 (寬度加寬至 960px，完美呈現不需左右滑動)
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
