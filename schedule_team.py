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
    "CARD_HEADER_BG": "#1e40af",    # 卡片時間列背景色
    "CARD_BODY_BG": "#ffffff",      # 卡片內文底色 (白)
    "TEXT_MAIN": "#ffffff",         # 主要文字顏色
    "TEXT_SUB": "#CBD5E1",          # 副標題顏色
    "TEXT_TIME": "#ffffff",         # 卡片時間文字顏色
    "TEXT_CATE": "#DC2626",         # 組別標籤文字顏色 (紅)
    "TEXT_PLAYER": "#1E293B",       # 選手名字顏色
    
    # 字型大小設定 (pt / px)
    "SIZE_BADGE": 30,
    "SIZE_SUB_TITLE": 18,
    "SIZE_MAIN_TITLE": 32,
    "SIZE_TAG": 14,
    "SIZE_SECTION": 18,
    "SIZE_TIME": 17,
    "SIZE_PLAYER": 16,
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

def create_team_schedule(output_filename="2026_羽球總流程表.png"):
    cfg = CONFIG
    
    data1_items = [
        ("08:00", "五男單", "張智勛、謝翔宇"),
        ("08:45", "三男單", "林祐頡"),
        ("09:15", "五男單", "林靖洋、謝翔宇"),
        ("09:30", "五男單", "曾楷翔"),
        ("10:00", "三男單", "林祐頡、謝皓宇"),
        ("10:30", "五男單", "張智勛、林靖洋"),
        ("10:45", "五男單", "曾楷翔"),
        ("11:15", "三男單", "謝皓宇"),
        ("11:45", "三女單", "吳雨恩"),
        ("12:00", "三女單", "凃萭希"),
        ("12:00", "低男單", "童羿勛、謝皓喆"),
        ("12:15", "低男單", "廖胤期"),
        ("13:00", "三女單", "吳雨恩"),
        ("13:15", "三女單", "凃萭希"),
        ("13:15", "低男單", "謝皓喆、吳家丞"),
        ("14:15", "三女單", "凃萭希"),
        ("14:30", "低男單", "童羿勛、吳家丞、廖胤期"),
        ("15:15", "低女單", "林子晴"),
        ("15:45", "低女單", "林子晴"),
    ]

    data2_items = [
        ("08:45", "高男雙", "許宸睿/曾楷翔"),
        ("09:00", "中男雙", "林祐頡/謝皓喆"),
        ("09:30", "中男雙", "林祐頡/謝皓喆"),
        ("09:30", "高男雙", "許宸睿/曾楷翔"),
        ("11:00", "六男單", "許宸睿"),
        ("12:30", "六女單", "黃芊萓、蔡昀妡"),
        ("13:45", "六男單", "許宸睿"),
        ("14:15", "六女單", "蔡昀妡"),
        ("15:00", "六女單", "黃芊萓、蔡昀妡"),
    ]

    img_width = 800
    padding_x = 30

    def calc_grid_height(items):
        rows = (len(items) + 1) // 2
        return rows * 92 + (rows - 1) * 12

    grid1_h = calc_grid_height(data1_items)
    grid2_h = calc_grid_height(data2_items)
    img_height = 240 + 50 + grid1_h + 60 + grid2_h + 50

    image = Image.new("RGB", (img_width, img_height), hex_to_rgb(cfg["BG_COLOR"]))
    draw = ImageDraw.Draw(image)

    font_badge = get_font(cfg["SIZE_BADGE"])
    font_sub = get_font(cfg["SIZE_SUB_TITLE"], bold=True)
    font_main = get_font(cfg["SIZE_MAIN_TITLE"], bold=True)
    font_tag = get_font(cfg["SIZE_TAG"], bold=True)
    font_sec = get_font(cfg["SIZE_SECTION"], bold=True)
    font_time = get_font(cfg["SIZE_TIME"], bold=True)
    font_player = get_font(cfg["SIZE_PLAYER"], bold=True)

    y_cursor = 35
    draw.text((img_width // 2, y_cursor), "🏸", fill=cfg["TEXT_MAIN"], font=font_badge, anchor="mm")
    y_cursor += 35
    draw.text((img_width // 2, y_cursor), "2026年會稽國小羽球隊賽程表", fill=cfg["TEXT_SUB"], font=font_sub, anchor="mm")
    y_cursor += 32
    draw.text((img_width // 2, y_cursor), "整體流程表", fill=cfg["TEXT_MAIN"], font=font_main, anchor="mm")
    y_cursor += 38

    draw_rounded_rectangle(draw, [img_width//2 - 130, y_cursor - 14, img_width//2 - 10, y_cursor + 14], radius=14, fill=hex_to_rgb("#F59E0B"))
    draw.text((img_width//2 - 70, y_cursor), "整體流程表", fill="#000000", font=font_tag, anchor="mm")

    draw_rounded_rectangle(draw, [img_width//2 + 10, y_cursor - 14, img_width//2 + 160, y_cursor + 14], radius=14, fill=hex_to_rgb("#FFFFFF"))
    draw.text((img_width//2 + 85, y_cursor), "日期：2026/11/19-20", fill="#000000", font=font_tag, anchor="mm")
    y_cursor += 45

    def draw_section(sec_title, data_items, start_y):
        cur_y = start_y
        draw_rounded_rectangle(draw, [padding_x, cur_y, img_width - padding_x, cur_y + 42], radius=6, fill=hex_to_rgb(cfg["HEADER_BG"]), outline=hex_to_rgb("#3B82F6"), width=2)
        draw.text((img_width // 2, cur_y + 21), sec_title, fill=cfg["TEXT_MAIN"], font=font_sec, anchor="mm")
        cur_y += 54

        card_w = (img_width - padding_x * 2 - 14) // 2
        card_h = 88

        for idx, (time_str, cate, players) in enumerate(data_items):
            col = idx % 2
            row = idx // 2
            x1 = padding_x + col * (card_w + 14)
            y1 = cur_y + row * (card_h + 12)
            x2 = x1 + card_w
            y2 = y1 + card_h

            draw_rounded_rectangle(draw, [x1, y1, x2, y2], radius=8, fill=hex_to_rgb(cfg["CARD_HEADER_BG"]))
            draw_rounded_rectangle(draw, [x1, y1, x2, y1 + 32], radius=8, fill=hex_to_rgb(cfg["CARD_HEADER_BG"]))
            draw.rectangle([x1, y1 + 20, x2, y1 + 32], fill=hex_to_rgb(cfg["CARD_HEADER_BG"]))
            draw.text(((x1 + x2) // 2, y1 + 16), time_str, fill=cfg["TEXT_TIME"], font=font_time, anchor="mm")

            draw_rounded_rectangle(draw, [x1, y1 + 32, x2, y2], radius=8, fill=hex_to_rgb(cfg["CARD_BODY_BG"]))
            draw.rectangle([x1, y1 + 32, x2, y1 + 42], fill=hex_to_rgb(cfg["CARD_BODY_BG"]))

            content_y = y1 + 32 + (card_h - 32) // 2
            cate_text = f"【{cate}】"
            
            cate_bbox = font_player.getbbox(cate_text)
            player_bbox = font_player.getbbox(players)
            cate_w = cate_bbox[2] - cate_bbox[0]
            player_w = player_bbox[2] - player_bbox[0]
            total_w = cate_w + player_w
            
            start_x = (x1 + x2) // 2 - total_w // 2
            draw.text((start_x, content_y), cate_text, fill=hex_to_rgb(cfg["TEXT_CATE"]), font=font_player, anchor="lm")
            draw.text((start_x + cate_w, content_y), players, fill=hex_to_rgb(cfg["TEXT_PLAYER"]), font=font_player, anchor="lm")

        rows = (len(data_items) + 1) // 2
        return cur_y + rows * (card_h + 12)

    y_cursor = draw_section("📅 11月19日 (星期四)", data1_items, y_cursor)
    y_cursor += 15
    y_cursor = draw_section("📅 11月20日 (星期五)", data2_items, y_cursor)

    image.save(output_filename)
    print(f"✅ 團隊賽程圖已產出：{os.path.abspath(output_filename)}")

if __name__ == "__main__":
    create_team_schedule()