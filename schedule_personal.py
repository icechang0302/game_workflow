#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# 🎨 顏色與字型大小自訂設定區 (CONFIG)
# ==========================================
CONFIG = {
    # 顏色設定 (HEX 碼)
    "BG_COLOR": "#0d1b2a",          # 畫布背景色 (深藍)
    "HEADER_BG": "#1E3A8A",         # 區塊標題背景色
    "CARD_BODY_BG": "#ffffff",      # 選手列表外框底色
    "TEXT_MAIN": "#ffffff",         # 主要文字顏色
    "TEXT_SUB": "#CBD5E1",          # 副標題顏色
    "TEXT_TEXT": "#0F172A",         # 姓名與項目文字顏色
    "TEXT_TIME": "#0F172A",         # 時間文字顏色
    
    # 性別標籤顏色設定
    "MALE_BG": "#E0F2FE",           # 男生標籤背景色 (淺藍)
    "MALE_FG": "#0369A1",           # 男生標籤文字色 (深藍)
    "FEMALE_BG": "#FCE7F3",         # 女生標籤背景色 (淺粉)
    "FEMALE_FG": "#BE185D",         # 女生標籤文字色 (深粉)

    # 字型大小設定 (pt / px)
    "SIZE_BADGE": 30,
    "SIZE_SUB_TITLE": 18,
    "SIZE_MAIN_TITLE": 32,
    "SIZE_TAG": 14,
    "SIZE_SECTION": 18,
    "SIZE_GENDER": 13,
    "SIZE_TEXT": 16,                # 選手姓名與項目大小
    "SIZE_TIME": 15,                # 右側時間大小
}
# ==========================================

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def draw_rounded_rectangle(draw, xy, radius, fill, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

def get_font(size, bold=False):
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf"
    ]
    index = 1 if bold else 0
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=index)
            except Exception:
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
    return ImageFont.load_default()

def generate_styled_personal_schedule(
    main_title="MAUC 春季賽",
    sub_title="2027年牧羽盃全國四季聯賽",
    tag_left="選手個人賽程",
    tag_right="日期：2027/03/15 (一)",
    sections_data=None,
    output_filename="2027_個人賽程精美版.png"
):
    cfg = CONFIG

    if sections_data is None:
        sections_data = [
            ("國小低年級組", [
                ("男", "童羿勛", "低男單", "09:15、10:30、12:45、13:15"),
                ("女", "凃萭希", "低女單", "09:30、11:00、12:30、13:45"),
            ]),
            ("國小中年級組", [
                ("男", "林祐頡", "中男單/中男雙", "10:15、12:00、13:30、14:45"),
                ("男", "謝皓宇", "中男單", "10:45、12:15"),
                ("女", "吳雨恩", "中女單/中女雙", "11:30、13:00、14:15、15:30"),
                ("女", "蔡昀妡", "中女單", "11:45、13:15"),
                ("女", "黃芊萓", "中女單", "12:00、13:30"),
            ]),
            ("國小高年級組", [
                ("男", "許宸睿", "高男單/高男雙", "14:00、15:15、16:30、17:45"),
                ("男", "張智勛", "高男單", "14:30、15:45"),
                ("男", "林靖洋", "高男單", "14:45、16:00"),
                ("男", "曾楷翔", "高男單/高男雙", "15:15、16:15、17:30、18:00"),
                ("女", "凃萭希", "高女單", "14:15、15:30、16:45"),
                ("女", "蔡昀妡", "高女單", "14:30、15:45、17:00"),
            ])
        ]

    img_width = 800
    padding_x = 30

    total_content_h = 0
    for sec_title, players_list in sections_data:
        total_content_h += 42 + len(players_list) * 54 + 20

    img_height = 220 + total_content_h + 30

    image = Image.new("RGB", (img_width, img_height), hex_to_rgb(cfg["BG_COLOR"]))
    draw = ImageDraw.Draw(image)

    font_badge = get_font(cfg["SIZE_BADGE"])
    font_sub = get_font(cfg["SIZE_SUB_TITLE"], bold=True)
    font_main = get_font(cfg["SIZE_MAIN_TITLE"], bold=True)
    font_tag = get_font(cfg["SIZE_TAG"], bold=True)
    font_sec = get_font(cfg["SIZE_SECTION"], bold=True)
    font_gender = get_font(cfg["SIZE_GENDER"], bold=True)
    font_text = get_font(cfg["SIZE_TEXT"], bold=True)
    font_times = get_font(cfg["SIZE_TIME"], bold=True)

    y_cursor = 32
    draw.text((img_width // 2, y_cursor), "🏸", fill=cfg["TEXT_MAIN"], font=font_badge, anchor="mm")
    y_cursor += 34
    draw.text((img_width // 2, y_cursor), sub_title, fill=cfg["TEXT_SUB"], font=font_sub, anchor="mm")
    y_cursor += 30
    draw.text((img_width // 2, y_cursor), main_title, fill=cfg["TEXT_MAIN"], font=font_main, anchor="mm")
    y_cursor += 38

    draw_rounded_rectangle(draw, [img_width//2 - 130, y_cursor - 14, img_width//2 - 10, y_cursor + 14], radius=14, fill=hex_to_rgb("#F59E0B"))
    draw.text((img_width//2 - 70, y_cursor), tag_left, fill="#000000", font=font_tag, anchor="mm")

    draw_rounded_rectangle(draw, [img_width//2 + 10, y_cursor - 14, img_width//2 + 160, y_cursor + 14], radius=14, fill=hex_to_rgb("#FFFFFF"))
    draw.text((img_width//2 + 85, y_cursor), tag_right, fill="#000000", font=font_tag, anchor="mm")
    
    y_cursor += 42

    for sec_title, players_list in sections_data:
        sec_box_h = 42
        draw_rounded_rectangle(draw, [padding_x, y_cursor, img_width - padding_x, y_cursor + sec_box_h], radius=6, fill=hex_to_rgb(cfg["HEADER_BG"]), outline=hex_to_rgb("#3B82F6"), width=2)
        draw.text((img_width // 2, y_cursor + sec_box_h // 2), sec_title, fill=cfg["TEXT_MAIN"], font=font_sec, anchor="mm")
        y_cursor += sec_box_h + 8

        card_bg_h = len(players_list) * 54 + 10
        draw_rounded_rectangle(draw, [padding_x, y_cursor, img_width - padding_x, y_cursor + card_bg_h], radius=8, fill=hex_to_rgb(cfg["CARD_BODY_BG"]))

        row_y = y_cursor + 5
        for idx, (gender, name, category, times) in enumerate(players_list):
            row_h = 48

            if idx > 0:
                draw.line([padding_x + 12, row_y - 2, img_width - padding_x - 12, row_y - 2], fill=hex_to_rgb("#F1F5F9"), width=1)

            if gender == "男":
                g_bg, g_fg = cfg["MALE_BG"], cfg["MALE_FG"]
            else:
                g_bg, g_fg = cfg["FEMALE_BG"], cfg["FEMALE_FG"]

            bx1 = padding_x + 16
            by1 = row_y + 12
            bx2 = bx1 + 24
            by2 = by1 + 24
            draw_rounded_rectangle(draw, [bx1, by1, bx2, by2], radius=6, fill=hex_to_rgb(g_bg))
            draw.text(((bx1 + bx2) // 2, (by1 + by2) // 2), gender, fill=hex_to_rgb(g_fg), font=font_gender, anchor="mm")

            text_start_x = bx2 + 12
            full_text = f"{name} ({category})"
            draw.text((text_start_x, row_y + 24), full_text, fill=hex_to_rgb(cfg["TEXT_TEXT"]), font=font_text, anchor="lm")
            draw.text((img_width - padding_x - 18, row_y + 24), times, fill=hex_to_rgb(cfg["TEXT_TIME"]), font=font_times, anchor="rm")

            row_y += row_h + 6

        y_cursor += card_bg_h + 16

    image.save(output_filename)
    print(f"✅ 個人賽程圖已產出：{os.path.abspath(output_filename)}")

if __name__ == "__main__":
    generate_styled_personal_schedule()