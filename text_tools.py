import os
import unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def get_width_count(text):
    """全角文字を考慮して、文字列の表示幅を計算します。"""
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count


def get_width_from_text(text, settings, mode="lyric", is_chorus=False):
    """フォント設定に基づいて、文字列のバウンディングボックス、幅、および余白を計算します。"""
    if mode == "lyric":
        if is_chorus:
            font_size = settings.LYRIC_CHORUS.FONT_SIZE
            font_path = settings.LYRIC_CHORUS.FONT_PATH
            margin_full = settings.LYRIC_CHORUS.MARGIN_FULL
            margin_half = settings.LYRIC_CHORUS.MARGIN_HALF
            text_with_min = settings.LYRIC_CHORUS.TEXT_WIDTH_MIN
            margin_space = settings.LYRIC_CHORUS.MARGIN_SPACE
        else:
            font_size = settings.LYRIC.FONT_SIZE
            font_path = settings.LYRIC.FONT_PATH
            margin_full = settings.LYRIC.MARGIN_FULL
            margin_half = settings.LYRIC.MARGIN_HALF
            text_with_min = settings.LYRIC.TEXT_WIDTH_MIN
            margin_space = settings.LYRIC.MARGIN_SPACE
    else:
        if is_chorus:
            font_size = settings.RUBY_CHORUS.FONT_SIZE
            font_path = settings.RUBY_CHORUS.FONT_PATH
            margin_full = settings.RUBY_CHORUS.MARGIN_FULL
            margin_half = settings.RUBY_CHORUS.MARGIN_HALF
            text_with_min = settings.RUBY_CHORUS.TEXT_WIDTH_MIN
            margin_space = settings.RUBY_CHORUS.MARGIN_SPACE
        else:
            font_size = settings.RUBY.FONT_SIZE
            font_path = settings.RUBY.FONT_PATH
            margin_full = settings.RUBY.MARGIN_FULL
            margin_half = settings.RUBY.MARGIN_HALF
            text_with_min = settings.RUBY.TEXT_WIDTH_MIN
            margin_space = settings.RUBY.MARGIN_SPACE

    image = Image.new('RGBA', (font_size + 100, font_size + 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text((0, 0), text, font=font, fill=(255, 0, 0, 255))
    bbox = list(draw.textbbox((0, 0), text, font=font))

    image_np = np.array(image)
    red_pixels = np.where((image_np[:, :, 0] == 255) & (image_np[:, :, 1] == 0) & (image_np[:, :, 2] == 0))
    if red_pixels[1].size > 0:
        leftmost_x = np.min(red_pixels[1])
        rightmost_x = np.max(red_pixels[1])
        bbox[0] = leftmost_x
        bbox[2] = rightmost_x
        _width = rightmost_x - leftmost_x
    else:
        _width = bbox[2] - bbox[0]

    margin = margin_full if get_width_count(text) > 1 else margin_half
    if not text != "" and _width < text_with_min:
        _width = text_with_min
    
    if text == " ":
        _width = 0
        margin = margin_space

    del image
    return {"bbox": bbox, "margin": margin, "width": _width}


def draw_text_with_bbox(text, settings, mode="lyric", is_chorus=False, output_path=None):
    """文字列をバウンディングボックス付きで描画し、描画後の最終的なx座標を返します。"""
    if mode == "lyric":
        if is_chorus:
            font_size = settings.LYRIC_CHORUS.FONT_SIZE
            font_path = settings.LYRIC_CHORUS.FONT_PATH
            stroke_size = settings.LYRIC_CHORUS.STROKE_WIDTH
        else:
            font_size = settings.LYRIC.FONT_SIZE
            font_path = settings.LYRIC.FONT_PATH
            stroke_size = settings.LYRIC.STROKE_WIDTH
    else:
        if is_chorus:
            font_size = settings.RUBY_CHORUS.FONT_SIZE
            font_path = settings.RUBY_CHORUS.FONT_PATH
            stroke_size = settings.RUBY_CHORUS.STROKE_WIDTH
        else:
            font_size = settings.RUBY.FONT_SIZE
            font_path = settings.RUBY.FONT_PATH
            stroke_size = settings.RUBY.STROKE_WIDTH

    # Create an image with transparency (RGBA)
    x_base = stroke_size
    image = Image.new('RGBA', (settings.GENERAL.WIDTH, settings.GENERAL.HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    for t in text:
        _data = get_width_from_text(t, settings=settings, mode=mode, is_chorus=is_chorus)
        _bbox = _data["bbox"]
        _width = _data["width"]
        _margin = _data["margin"]
        draw.text((x_base - _bbox[0], 100), t, font=font, fill=(255, 255, 255, 255), stroke_width=stroke_size, stroke_fill=(0, 0, 0, 230))
        x_base += _width + _margin

    # Save the image
    if output_path is not None:
        image.save(output_path, 'PNG')
    
    return x_base + stroke_size

COLOR_FILL_BEFORE_MAIN = None
COLOR_STROKE_FILL_BEFORE_MAIN = None
COLOR_FILL_AFTER_MAIN = None
COLOR_STROKE_FILL_AFTER_MAIN = None
COLOR_FILL_BEFORE_CURRENT = None
COLOR_STROKE_FILL_BEFORE_CURRENT = None
COLOR_FILL_AFTER_CURRENT = None
COLOR_STROKE_FILL_AFTER_CURRENT = None
IS_CHORUS = False

def draw_lyric_image_with_ruby(data, settings, output_path_1="images/output_1.png", output_path_2="images/output_2.png"):
    """歌詞とルビを含む画像を生成し、2つの画像を保存して分析データを返します。"""
    global COLOR_FILL_BEFORE_MAIN, COLOR_STROKE_FILL_BEFORE_MAIN, COLOR_FILL_AFTER_MAIN, COLOR_STROKE_FILL_AFTER_MAIN
    global COLOR_FILL_BEFORE_CURRENT, COLOR_STROKE_FILL_BEFORE_CURRENT, COLOR_FILL_AFTER_CURRENT, COLOR_STROKE_FILL_AFTER_CURRENT
    global IS_CHORUS

    x_base = settings.GENERAL.X_BASE_INIT

    if COLOR_FILL_BEFORE_MAIN == None:
        COLOR_FILL_BEFORE_MAIN = settings.GENERAL.COLOR_FILL_BEFORE
        COLOR_STROKE_FILL_BEFORE_MAIN = settings.GENERAL.COLOR_STROKE_FILL_BEFORE
        COLOR_FILL_AFTER_MAIN = settings.GENERAL.COLOR_FILL_AFTER
        COLOR_STROKE_FILL_AFTER_MAIN = settings.GENERAL.COLOR_STROKE_FILL_AFTER
        COLOR_FILL_BEFORE_CURRENT = settings.GENERAL.COLOR_FILL_BEFORE
        COLOR_STROKE_FILL_BEFORE_CURRENT = settings.GENERAL.COLOR_STROKE_FILL_BEFORE
        COLOR_FILL_AFTER_CURRENT = settings.GENERAL.COLOR_FILL_AFTER
        COLOR_STROKE_FILL_AFTER_CURRENT = settings.GENERAL.COLOR_STROKE_FILL_AFTER

    # Before wipe
    image_1 = Image.new('RGBA', (settings.GENERAL.WIDTH, settings.GENERAL.HEIGHT), (255, 255, 255, 0))
    draw_1 = ImageDraw.Draw(image_1)
    # After wipe
    image_2 = Image.new('RGBA', (settings.GENERAL.WIDTH, settings.GENERAL.HEIGHT), (255, 255, 255, 0))
    draw_2 = ImageDraw.Draw(image_2)

    if IS_CHORUS:
        lyric_cat = "LYRIC_CHORUS"
        ruby_cat = "RUBY_CHORUS"
    else:
        lyric_cat = "LYRIC"
        ruby_cat = "RUBY"

    font_lyric = ImageFont.truetype(getattr(settings, lyric_cat).FONT_PATH, getattr(settings, lyric_cat).FONT_SIZE)
    font_ruby = ImageFont.truetype(getattr(settings, ruby_cat).FONT_PATH, getattr(settings, ruby_cat).FONT_SIZE)

    x_base = settings.GENERAL.X_BASE_INIT

    x_start_lyric = []
    x_end_lyric = []
    x_start_ruby = []
    x_end_ruby = []

    for i, (lyric, ruby) in enumerate(zip(data["lyrics"], data["rubys"])):
        _width_lyric = draw_text_with_bbox(lyric, settings=settings, mode="lyric", is_chorus=IS_CHORUS)
        _width_ruby = draw_text_with_bbox(ruby, settings=settings, mode="ruby", is_chorus=IS_CHORUS)

        if lyric == " ":
            x_start_lyric.append(int(x_base))
            x_start_ruby.append(int(x_base))
            x_base += getattr(settings, lyric_cat).MARGIN_SPACE - getattr(settings, lyric_cat).STROKE_WIDTH
            x_end_lyric.append(int(x_base))
            x_end_ruby.append(int(x_base))
            continue

        elif lyric == "":
            x_start_lyric.append(int(x_base - getattr(settings, lyric_cat).STROKE_WIDTH))
            x_start_ruby.append(int(x_base - getattr(settings, ruby_cat).STROKE_WIDTH))
            x_end_lyric.append(int(x_base - getattr(settings, lyric_cat).STROKE_WIDTH))
            x_end_ruby.append(int(x_base - getattr(settings, ruby_cat).STROKE_WIDTH))
            continue

        if _width_lyric >= _width_ruby:
            _x_lyric = x_base
            _x_ruby = x_base + (_width_lyric - _width_ruby) // 2
        else:
            _x_lyric = x_base + (_width_ruby - _width_lyric) // 2
            _x_ruby = x_base

        # draw icon
        if lyric in settings.GENERAL.CHANGE_TO_PART_STR:
            idx = settings.GENERAL.CHANGE_TO_PART_STR.index(lyric)
            paste_image = Image.open(settings.GENERAL.PART_ICON[idx]).convert("RGBA")
            original_width, original_height = paste_image.size
            new_width = int((settings.GENERAL.PART_ICON_HEIGHT / original_height) * original_width)
            resized_image = paste_image.resize((new_width, settings.GENERAL.PART_ICON_HEIGHT), Image.ANTIALIAS)

            _x_lyric = _x_lyric - settings.GENERAL.PART_ICON_MARGIN_X

            # image_1.paste(resized_image, (_x_lyric + settings.GENERAL.PART_ICON_OFFSET_X, settings.GENERAL.Y_LYRIC + settings.GENERAL.PART_ICON_OFFSET_Y), resized_image)
            image_2.paste(resized_image, (_x_lyric + settings.GENERAL.PART_ICON_OFFSET_X, settings.GENERAL.Y_LYRIC + settings.GENERAL.PART_ICON_OFFSET_Y), resized_image)

            x_start_lyric.append(int(_x_lyric))
            x_start_ruby.append(int(_x_lyric))
            x_base = _x_lyric + new_width + settings.GENERAL.PART_ICON_MARGIN_X
            x_end_lyric.append(int(_x_lyric + new_width))
            x_end_ruby.append(int(_x_lyric + new_width))

            # change color
            COLOR_FILL_BEFORE_CURRENT = tuple(settings.GENERAL.COLOR_FILL_BEFORE_PART[idx])
            COLOR_STROKE_FILL_BEFORE_CURRENT = tuple(settings.GENERAL.COLOR_STROKE_FILL_BEFORE_PART[idx])
            COLOR_FILL_AFTER_CURRENT = tuple(settings.GENERAL.COLOR_FILL_AFTER_PART[idx])
            COLOR_STROKE_FILL_AFTER_CURRENT = tuple(settings.GENERAL.COLOR_STROKE_FILL_AFTER_PART[idx])
            continue

        # draw lyric
        x_start_lyric.append(int(_x_lyric - getattr(settings, lyric_cat).STROKE_WIDTH))
        _margin = 0

        for t in lyric:
            # Change color
            if t in settings.GENERAL.CHANGE_TO_CHORUS_STR:
                COLOR_FILL_BEFORE_CURRENT = settings.GENERAL.COLOR_FILL_BEFORE_CHORUS
                COLOR_STROKE_FILL_BEFORE_CURRENT = settings.GENERAL.COLOR_STROKE_FILL_BEFORE_CHORUS
                COLOR_FILL_AFTER_CURRENT = settings.GENERAL.COLOR_FILL_AFTER_CHORUS
                COLOR_STROKE_FILL_AFTER_CURRENT = settings.GENERAL.COLOR_STROKE_FILL_AFTER_CHORUS
                IS_CHORUS = True
                font_lyric = ImageFont.truetype(settings.LYRIC_CHORUS.FONT_PATH, settings.LYRIC_CHORUS.FONT_SIZE)
                font_ruby = ImageFont.truetype(settings.RUBY_CHORUS.FONT_PATH, settings.RUBY_CHORUS.FONT_SIZE)
                lyric_cat = "LYRIC_CHORUS"
                ruby_cat = "RUBY_CHORUS"

            _data = get_width_from_text(t, settings=settings, mode="lyric", is_chorus=IS_CHORUS)
            _bbox = _data["bbox"]
            _width = _data["width"]
            _margin = _data["margin"]
            draw_1.text((_x_lyric - _bbox[0], settings.GENERAL.Y_LYRIC + getattr(settings, lyric_cat).Y_DRAW_OFFSET), t, font=font_lyric, fill=COLOR_FILL_BEFORE_CURRENT, stroke_width=getattr(settings, lyric_cat).STROKE_WIDTH, stroke_fill=COLOR_STROKE_FILL_BEFORE_CURRENT)
            draw_2.text((_x_lyric - _bbox[0], settings.GENERAL.Y_LYRIC + getattr(settings, lyric_cat).Y_DRAW_OFFSET), t, font=font_lyric, fill=COLOR_FILL_AFTER_CURRENT, stroke_width=getattr(settings, lyric_cat).STROKE_WIDTH, stroke_fill=COLOR_STROKE_FILL_AFTER_CURRENT)
            _x_lyric += _width + _margin
        
        x_end_lyric.append(int(_x_lyric - _margin + getattr(settings, lyric_cat).STROKE_WIDTH))

        # draw ruby
        x_start_ruby.append(int(_x_ruby - getattr(settings, ruby_cat).STROKE_WIDTH))
        _margin = 0
        for t in ruby:
            _data = get_width_from_text(t, settings=settings, mode="ruby", is_chorus=IS_CHORUS)
            _bbox = _data["bbox"]
            _width = _data["width"]
            _margin = _data["margin"]
            draw_1.text((_x_ruby - _bbox[0], settings.GENERAL.Y_RUBY + getattr(settings, ruby_cat).Y_DRAW_OFFSET), t, font=font_ruby, fill=COLOR_FILL_BEFORE_CURRENT, stroke_width=getattr(settings, ruby_cat).STROKE_WIDTH, stroke_fill=COLOR_STROKE_FILL_BEFORE_CURRENT)
            draw_2.text((_x_ruby - _bbox[0], settings.GENERAL.Y_RUBY + getattr(settings, ruby_cat).Y_DRAW_OFFSET), t, font=font_ruby, fill=COLOR_FILL_AFTER_CURRENT, stroke_width=getattr(settings, ruby_cat).STROKE_WIDTH, stroke_fill=COLOR_STROKE_FILL_AFTER_CURRENT)
            _x_ruby += _width + _margin

        x_end_ruby.append(int(_x_ruby - _margin + getattr(settings, ruby_cat).STROKE_WIDTH))

        if _width_lyric >= _width_ruby:
            x_base = _x_lyric
        
        else:
            x_base = _x_ruby

        if lyric[-1] in settings.GENERAL.CHANGE_TO_MAIN_STR:
            COLOR_FILL_BEFORE_CURRENT = COLOR_FILL_BEFORE_MAIN
            COLOR_STROKE_FILL_BEFORE_CURRENT = COLOR_STROKE_FILL_BEFORE_MAIN
            COLOR_FILL_AFTER_CURRENT = COLOR_FILL_AFTER_MAIN
            COLOR_STROKE_FILL_AFTER_CURRENT = COLOR_STROKE_FILL_AFTER_MAIN
            IS_CHORUS = False
            font_lyric = ImageFont.truetype(settings.LYRIC.FONT_PATH, settings.LYRIC.FONT_SIZE)
            font_ruby = ImageFont.truetype(settings.RUBY.FONT_PATH, settings.RUBY.FONT_SIZE)
            lyric_cat = "LYRIC"
            ruby_cat = "RUBY"

    image_1.save(output_path_1, 'PNG')
    image_2.save(output_path_2, 'PNG')
    data["x_start_lyric"] = x_start_lyric
    data["x_end_lyric"] = x_end_lyric
    data["x_start_ruby"] = x_start_ruby
    data["x_end_ruby"] = x_end_ruby
    data["x_length"] = x_end_lyric[-1] + settings.GENERAL.X_BASE_INIT if x_end_lyric[-1] > x_end_ruby[-1] else x_end_ruby[-1] + settings.GENERAL.X_BASE_INIT
    data["image_1"] = os.path.abspath(output_path_1)
    data["image_2"] = os.path.abspath(output_path_2)
    return data

