import os
import io
import streamlit as st
from PIL import Image

# 匯入您之前寫好的兩個圖片產生模組
import schedule_team
import schedule_personal

st.set_page_config(
    page_title="會稽國小羽球隊 - 賽程圖產生器",
    page_icon="🏸",
    layout="centered"
)

st.title("🏸 羽球隊賽程圖片產生器")
st.caption("輕鬆線上預覽並下載高畫質團隊總流程圖與個人賽程圖")

# 建立分頁
tab1, tab2 = st.tabs(["📊 團隊整體流程圖", "👤 選手個人賽程圖"])

# ----------------------------------------------------
# 分頁 1：團隊整體流程圖
# ----------------------------------------------------
with tab1:
    st.header("團隊整體流程賽程表")
    st.write("點擊下方按鈕即可產生最新版團隊總流程圖片：")
    
    if st.button("🚀 產生團隊賽程圖", key="btn_team"):
        with st.spinner("圖片繪製中，請稍候..."):
            team_img_path = "2026_羽球總流程表.png"
            schedule_team.create_team_schedule(output_filename=team_img_path)
            
            if os.path.exists(team_img_path):
                image = Image.open(team_img_path)
                st.image(image, caption="團隊賽程預覽圖", use_column_width=True)
                
                # 將圖片轉為 Bytes 提供下載
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 下載團隊賽程圖片 (PNG)",
                    data=byte_im,
                    file_name="2026_會稽國小羽球隊_整體賽程表.png",
                    mime="image/png"
                )

# ----------------------------------------------------
# 分頁 2：選手個人賽程圖
# ----------------------------------------------------
with tab2:
    st.header("選手個人賽程對照表")
    st.write("按個人條列比賽時間，方便家長與選手對照：")
    
    if st.button("🚀 產生個人賽程圖", key="btn_personal"):
        with st.spinner("圖片繪製中，請稍候..."):
            personal_img_path = "2027_個人賽程精美版.png"
            schedule_personal.generate_styled_personal_schedule(output_filename=personal_img_path)
            
            if os.path.exists(personal_img_path):
                image = Image.open(personal_img_path)
                st.image(image, caption="個人賽程預覽圖", use_column_width=True)
                
                # 將圖片轉為 Bytes 提供下載
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 下載個人賽程圖片 (PNG)",
                    data=byte_im,
                    file_name="2027_會稽國小羽球隊_選手個人賽程.png",
                    mime="image/png"
                )