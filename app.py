import os
import io
import streamlit as st
from PIL import Image

# 匯入圖片產生模組
import schedule_team
import schedule_personal

# 頁面配置
st.set_page_config(
    page_title="羽球隊賽程圖片產生器",
    page_icon="🏸",
    layout="wide"
)

# 注入自訂深色主題 CSS
st.markdown("""
<style>
    /* 全域背景深藍風格 */
    .stApp {
        background-color: #0b1329;
        color: #f1f5f9;
    }
    
    /* 標題與內文顏色 */
    h1, h2, h3, h4, h5, label {
        color: #ffffff !important;
    }
    
    /* 卡片式容器區塊 */
    div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
        background-color: #131f3d;
        border: 1px solid #1e2d52;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* 上傳檔案區域虛線框風格 */
    div[data-testid="stFileUploader"] {
        background-color: #0d172e;
        border: 2px dashed #2563eb;
        border-radius: 10px;
        padding: 15px;
    }

    /* 按鈕樣式 (黃色按鈕) */
    .stButton>button {
        background-color: #f59e0b;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #d97706;
        color: #000000;
    }

    /* 下載按鈕 (黃/橙色風格) */
    .stDownloadButton>button {
        background-color: #f59e0b;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stDownloadButton>button:hover {
        background-color: #d97706;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 頂部 Header
# ----------------------------------------------------
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.title("🏸 羽球隊賽程圖片產生器")
    st.caption("免安裝軟體・線上編輯錯字・一鍵導出手機 A4 高解析圖")

with col_btn:
    st.write("") # 間距調整

# ----------------------------------------------------
# 區塊 1：多圖辨識 / 快速帶入賽程
# ----------------------------------------------------
st.subheader("🪄 多圖辨識 / 快速帶入賽程")
st.caption("您一次可以選擇多張紙本賽程照片，系統將批次辨識並自動分類整理至下方。")

uploaded_files = st.file_uploader(
    "點擊選擇多張賽程照片 (或拖曳至此)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    help="可同時選擇多張 PNG, JPG, WEBP 檔案"
)

if uploaded_files:
    st.success(f"已成功上傳 {len(uploaded_files)} 張照片，系統準備為您處理！")

st.markdown("---")

# ----------------------------------------------------
# 頁籤設定：選擇編輯整體還是個人賽程
# ----------------------------------------------------
tab1, tab2 = st.tabs(["📊 團隊整體流程圖編輯", "👤 選手個人賽程圖編輯"])

# ----------------------------------------------------
# TAB 1: 團隊整體賽程圖設定
# ----------------------------------------------------
with tab1:
    st.subheader("📝 賽程表基本標題與字體微調")
    
    c1, c2 = st.columns(2)
    with c1:
        main_title = st.text_input("主標題 (大字)", value="整體流程表", key="team_main")
        tag_left = st.text_input("標籤 (左邊黃標)", value="整體流程表", key="team_tag_l")
    with c2:
        sub_title = st.text_input("副標題 / 隊名賽事", value="2026年會稽國小羽球隊賽程表", key="team_sub")
        tag_right = st.text_input("標籤 (右邊白標)", value="日期：2026/11/19-20", key="team_tag_r")

    # 滑桿控制選手名字字體大小
    player_font_size = st.slider("🔤 選手名字字體大小 (px)", min_value=12, max_value=24, value=16, step=1, key="team_font_slider")

    st.markdown("---")
    
    # 產生圖片按鈕區
    if st.button("🚀 產生團隊賽程圖片", key="btn_gen_team"):
        with st.spinner("繪製高品質圖片中..."):
            # 動態更新設定檔
            schedule_team.CONFIG["SIZE_PLAYER"] = player_font_size
            
            output_file = "2026_羽球總流程表.png"
            schedule_team.create_team_schedule(output_filename=output_file)
            
            if os.path.exists(output_file):
                img = Image.open(output_file)
                st.image(img, caption="團隊賽程即時預覽圖", use_column_width=True)
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                
                st.download_button(
                    label="📥 下載賽程圖片 (PNG)",
                    data=buf.getvalue(),
                    file_name="2026_會稽國小羽球隊_整體賽程表.png",
                    mime="image/png"
                )

# ----------------------------------------------------
# TAB 2: 個人賽程圖設定
# ----------------------------------------------------
with tab2:
    st.subheader("📝 個人賽程表標題與字體微調")
    
    c1, c2 = st.columns(2)
    with c1:
        p_main_title = st.text_input("主標題 (大字)", value="MAUC 春季賽", key="p_main")
        p_tag_left = st.text_input("標籤 (左邊黃標)", value="選手個人賽程", key="p_tag_l")
    with c2:
        p_sub_title = st.text_input("副標題 / 隊名賽事", value="2027年牧羽盃全國四季聯賽", key="p_sub")
        p_tag_right = st.text_input("標籤 (右邊白標)", value="日期：2027/03/15 (一)", key="p_tag_r")

    p_player_font_size = st.slider("🔤 選手名字與項目字體大小 (px)", min_value=12, max_value=24, value=16, step=1, key="p_font_slider")

    st.markdown("---")

    if st.button("🚀 產生個人賽程圖片", key="btn_gen_personal"):
        with st.spinner("繪製高品質圖片中..."):
            schedule_personal.CONFIG["SIZE_TEXT"] = p_player_font_size
            
            output_file = "2027_個人賽程精美版.png"
            schedule_personal.generate_styled_personal_schedule(
                main_title=p_main_title,
                sub_title=p_sub_title,
                tag_left=p_tag_left,
                tag_right=p_tag_right,
                output_filename=output_file
            )
            
            if os.path.exists(output_file):
                img = Image.open(output_file)
                st.image(img, caption="個人賽程即時預覽圖", use_column_width=True)
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                
                st.download_button(
                    label="📥 下載個人賽程圖片 (PNG)",
                    data=buf.getvalue(),
                    file_name="2027_選手個人賽程.png",
                    mime="image/png"
                )
