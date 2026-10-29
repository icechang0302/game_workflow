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
# 初始化 Session State (保持絕對乾淨，不預設任何寫死名單)
# -----------------------------------------------------------------------------
if "day1_text" not in st.session_state:
    st.session_state["day1_text"] = ""
if "day2_text" not in st.session_state:
    st.session_state["day2_text"] = ""

# -----------------------------------------------------------------------------
# 動態解析上傳圖片表格的函式（完全依據上傳的圖檔內容進行欄位抓取與過濾）
# -----------------------------------------------------------------------------
def dynamic_parse_table_image(uploaded_files, target_team):
    """
    動態讀取上傳的圖片格線與文字，
    依據 target_team（副標題/隊伍名稱）過濾出該隊伍選手，
    並轉譯為「時間 | 組別 | 選手」格式。
    """
    if not uploaded_files:
        st.warning("請先上傳賽程圖片！")
        return

    extracted_day1 = []
    extracted_day2 = []

    for file in uploaded_files:
        try:
            img = Image.open(file)
            filename = file.name.lower()
            
            raw_text = ""
            if HAS_TESSERACT:
                # 若雲端/本機支援 Tesseract，進行真實 OCR 掃描
                raw_text = pytesseract.image_to_string(img, lang="chi_tra+eng")
            else:
                # 若無安裝 Tesseract 核心，提醒使用者並保持動態解析介面暢通
                st.info(f"💡 正在分析圖片：{file.name}。伺服器未安裝 OCR 核心時，請直接在下方編輯區對照圖片輸入或貼上。")
                continue

            # 依據表格列進行智慧過濾：只抓取包含 target_team 的行
            lines = raw_text.split("\n")
            for line in lines:
                line = line.strip()
                if not line or target_team not in line:
                    continue
                
                # 抓取時間 (例如 2026-11-19 14:30:00 轉為 14:30 或保留完整時間)
                time_match = re.search(r'(\d{2}:\d{2})', line)
                time_str = time_match.group(1) if time_match else ""
                
                # 抓取組別 (例如 國小低年級男單A2-A3)
                cate_match = re.search(r'(國小[\w\d\-\(\)]+)', line)
                cate_str = cate_match.group(1) if cate_match else "賽事組別"
                
                if time_str:
                    # 排除時間、標籤、與目標隊伍名稱後，剩下的即為選手
                    parts = [p.strip() for p in line.split() if p.strip()]
                    players = [p for p in parts if p != time_str and p != cate_str and "2026" not in p and target_team not in p and "預賽" not in p]
                    players_str = "、".join(players) if players else target_team + "選手"
                    
                    row_result = f"{time_str} | {cate_str} | {players_str}"
                    
                    # 依日期分類
                    if "19" in filename or "day1" in filename or "11-19" in line:
                        extracted_day1.append(row_result)
                    else:
                        extracted_day2.append(row_result)

        except Exception as e:
            st.error(f"解析圖片 {file.name} 發生錯誤: {e}")

    if extracted_day1:
        st.session_state["day1_text"] = "\n".join(extracted_day1)
    if extracted_day2:
        st.session_state["day2_text"] = "\n".join(extracted_day2)
    
    if extracted_day1 or extracted_day2:
        st.success(f"🎉 成功從圖片中過濾並萃取出「{target_team}」的賽程資料！")
    else:
        st.warning(f"⚠️ 在上傳的圖片中未自動檢測到包含「{target_team}」的文字，請手動在下方編輯區調整或對照輸入。")

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
    font-weight: bold
