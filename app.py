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
# 初始化中文字型 (確保雲端 Linux 環境不產生 □□□ 亂碼)
# -----------------------------------------------------------------------------
@st.cache_resource
def setup_chinese_font():
    font_path = "NotoSansTC-Regular.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass
setup_chinese_font()

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
    return cards_html, len(lines)

def generate_poster_html(sub_title, main_title, tag_left, tag_right, date1_title, data1_text, date2_title, data2_text, item_font_size=16, bg_color="#0d1b2a", title_font_size=40):
    c19, count1 = parse_text_to_cards(data1_text)
    c20, count2 = parse_text_to_cards(data2_text)

    # 根據總卡片數動態計算網頁總高度，確保內容再多也絕不被裁切
    total_cards = max(count1, count2) if date2_title.strip() and data2_text.strip() else count1
    # 每一行大約佔 90px，加上標題與留白空間
    dynamic_height = max(1200, 350 + (total_cards * 95))

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'Noto Sans TC';
    src: url('NotoSansTC-Regular.ttf');
  }}
  body {{
    background-color: {bg_color};
    font-family: 'Noto Sans TC', sans-serif;
    color: #ffffff;
    margin: 0;
    padding: 40px 35px;
    width: 1050px;
    box-sizing: border-box;
    display
