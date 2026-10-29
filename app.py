import streamlit as st
from html2image import Html2Image
import os

st.set_page_config(page_title="羽球賽程圖片產生器", page_icon="🏸", layout="centered")

st.title("🏸 羽球賽程圖片產生器")
st.write("上傳或輸入賽程資訊，自訂標題與日期，一鍵生成手機版精美流程圖！")

# --- 1. 使用者自訂設定 ---
st.sidebar.header("⚙️ 圖片基本設定")
main_title_input = st.sidebar.text_input("主標題", value="整體流程表")
sub_title_input = st.sidebar.text_input("副標題 / 賽事名稱", value="2026年會稽國小羽球隊賽程表")
tag_left = st.sidebar.text_input("標籤 (左)", value="整體流程表")
tag_right = st.sidebar.text_input("標籤 (右)", value="日期：2026/11/19-20")

# --- 2. 日期與賽程區塊設定 ---
st.subheader("📅 賽程資料填寫")
col1, col2 = st.columns(2)

with col1:
    section_1_title = st.text_input("第一區塊標題", value="11月19日 (星期四)")
    # 預設範例文字，使用者可自行在文字框中修改任何錯字或內容
    data_1_text = st.text_area(
        "第一區塊賽程 (格式：時間 | 組別 | 選手，每行一筆)",
        value="08:00 | 五男單 | 張智勛、謝翔宇\n08:45 | 三男單 | 林祐頡\n09:15 | 五男單 | 林靖洋、謝翔宇\n09:30 | 五男單 | 曾楷翔\n10:00 | 三男單 | 林祐頡、謝皓宇\n10:30 | 五男單 | 張智勛、林靖洋\n10:45 | 五男單 | 曾楷翔\n11:15 | 三男單 | 謝皓宇\n11:45 | 三女單 | 吳雨恩\n12:00 | 三女單 | 凃萭希\n12:00 | 低男單 | 童羿勛、謝皓喆\n12:15 | 低男單 | 廖胤期\n13:00 | 三女單 | 吳雨恩\n13:15 | 三女單 | 凃萭希\n13:15 | 低男單 | 謝皓喆、吳家丞\n14:15 | 三女單 | 凃萭希\n14:30 | 低男單 | 童羿勛、吳家丞、廖胤期\n15:15 | 低女單 | 林子晴\n15:45 | 低女單 | 林子晴",
        height=300
    )

with col2:
    section_2_title = st.text_input("第二區塊標題", value="11月20日 (星期五)")
    data_2_text = st.text_area(
        "第二區塊賽程 (格式：時間 | 組別 | 選手，每行一筆)",
        value="08:45 | 高男雙 | 許宸睿/曾楷翔\n09:00 | 中男雙 | 林祐頡/謝皓喆\n09:30 | 中男雙 | 林祐頡/謝皓喆\n09:30 | 高男雙 | 許宸睿/曾楷翔\n11:00 | 六男單 | 許宸睿\n12:30 | 六女單 | 黃芊萓、蔡昀妡\n13:45 | 六男單 | 許宸睿\n14:15 | 六女單 | 蔡昀妡\n15:00 | 六女單 | 黃芊萓、蔡昀妡",
        height=300
    )

# 解析文字轉換成清單的函式
def parse_text_to_cards(text):
    cards_html = ""
    lines = text.strip().split("\n")
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            time_str = parts[0]
            cate = parts[1]
            players = parts[2]
            cards_html += f"""
            <div class="card">
              <div class="time-header">{time_str}</div>
              <div class="content">
                <div class="item"><span class="cate">【{cate}】</span>{players}</div>
              </div>
            </div>
            """
    return cards_html

# --- 3. 產出圖片按鈕 ---
if st.button("🎨 一鍵生成賽程圖片", type="primary"):
    with st.spinner("正在為您排版並生成圖片中..."):
        c19 = parse_text_to_cards(data_1_text)
        c20 = parse_text_to_cards(data_2_text)

        html_template = f"""
        <!DOCTYPE html>
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
            font-size: 16px;
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
            <div class="sub-title">{sub_title_input}</div>
            <div class="main-title">{main_title_input}</div>
            <div class="tags">
              <span class="tag-yellow">{tag_left}</span>
              <span class="tag-white">{tag_right}</span>
            </div>
          </div>

          <div class="section-container">
            <div class="section-title">📅 {section_1_title}</div>
            <div class="grid">{c19}</div>

            <div class="section-title">📅 {section_2_title}</div>
            <div class="grid">{c20}</div>
          </div>
        </body>
        </html>
        """

        # 產出圖片
        output_filename = "generated_schedule.png"
        hti = Html2Image(output_path='.')
        hti.screenshot(html_str=html_template, save_as=output_filename, size=(840, 1650))

        # 在網頁上顯示圖片供預覽與下載
        st.success("🎉 圖片生成成功！")
        st.image(output_filename, caption="預覽圖", use_container_width=True)
        
        with open(output_filename, "rb") as file:
            st.download_button(
                label="📥 下載這張賽程圖片",
                data=file,
                file_name="羽球賽程流程表.png",
                mime="image/png"
            )
