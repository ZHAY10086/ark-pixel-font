import logging
import os

import math
from PIL import Image, ImageFont, ImageDraw

import configs
from configs import path_define
from utils import fs_util

logger = logging.getLogger('image-service')


def _load_alphabet(px):
    txt_file_path = os.path.join(path_define.outputs_dir, configs.font_config_map[px].alphabet_txt_file_name)
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    alphabet = list(text)
    return alphabet


def _load_font(px, language_specific, size):
    font_file_path = os.path.join(path_define.outputs_dir, configs.font_config_map[px].get_font_file_name(language_specific, 'otf'))
    return ImageFont.truetype(font_file_path, size)


def _draw_text(image, xy, text, font, text_color=(0, 0, 0), shadow_color=None, line_height=None, line_gap=0, is_horizontal_centered=False, is_vertical_centered=False):
    draw = ImageDraw.Draw(image)
    x, y = xy
    default_line_height = sum(font.getmetrics())
    if line_height is None:
        line_height = default_line_height
    y += (line_height - default_line_height) / 2
    spacing = line_height + line_gap - font.getsize('A')[1]
    if is_horizontal_centered:
        x -= draw.textbbox((0, 0), text, font=font)[2] / 2
    if is_vertical_centered:
        y -= line_height / 2
    if shadow_color is not None:
        draw.text((x + 1, y + 1), text, fill=shadow_color, font=font, spacing=spacing)
    draw.text((x, y), text, fill=text_color, font=font, spacing=spacing)


def _draw_text_background(image, alphabet, step, box_size, font, text_color):
    draw = ImageDraw.Draw(image)
    alphabet_index = 0
    for index, c in enumerate(alphabet):
        code_point = ord(c)
        if code_point >= 0x4E00:
            alphabet_index = index
            break
    x_count = math.ceil(image.width / box_size)
    y_count = math.ceil(image.height / box_size)
    x_offset = (image.width - x_count * box_size) / 2 + (box_size - font.size) / 2
    y_offset = (image.height - y_count * box_size) / 2 + (box_size - font.size) / 2
    for y in range(y_count):
        for x in range(x_count):
            alphabet_index += step
            draw.text((x_offset + x * box_size, y_offset + y * box_size), alphabet[alphabet_index], fill=text_color, font=font)


def make_preview_image_file(font_config):
    font_latin = _load_font(font_config.px, 'latin', font_config.px)
    font_zh_cn = _load_font(font_config.px, 'zh_cn', font_config.px)
    font_zh_tr = _load_font(font_config.px, 'zh_tr', font_config.px)
    font_ja = _load_font(font_config.px, 'ja', font_config.px)

    line_height = int(font_config.px * 1.5)

    image = Image.new('RGBA', (font_config.px * 35, font_config.px * 2 + line_height * 8), (255, 255, 255))
    _draw_text(image, (font_config.px, font_config.px), '方舟像素字体 / Ark Pixel Font', font_zh_cn, line_height=line_height)
    _draw_text(image, (font_config.px, font_config.px + line_height), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', font_zh_cn, line_height=line_height)
    _draw_text(image, (font_config.px, font_config.px + line_height * 2), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', font_zh_tr, line_height=line_height)
    _draw_text(image, (font_config.px, font_config.px + line_height * 3), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', font_ja, line_height=line_height)
    _draw_text(image, (font_config.px, font_config.px + line_height * 4), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, line_height=line_height)
    _draw_text(image, (font_config.px, font_config.px + line_height * 5), 'the quick brown fox jumps over a lazy dog.', font_latin, line_height=line_height)
    _draw_text(image, (font_config.px, font_config.px + line_height * 6), '0123456789', font_latin, line_height=line_height)
    _draw_text(image, (font_config.px, font_config.px + line_height * 7), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, line_height=line_height)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, font_config.preview_image_file_name)
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_github_banner():
    alphabet_12 = _load_alphabet(12)
    font_24_zh_cn = _load_font(12, 'zh_cn', 24)
    font_12_latin = _load_font(12, 'latin', 12)
    font_12_zh_cn = _load_font(12, 'zh_cn', 12)
    font_12_zh_tr = _load_font(12, 'zh_tr', 12)
    font_12_ja = _load_font(12, 'ja', 12)

    box_size = 14
    line_height = 18
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image_background = Image.open(os.path.join(path_define.images_dir, 'github-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (255, 255, 255, 0))
    _draw_text_background(image, alphabet_12, 6, box_size, font_12_zh_cn, (200, 200, 200))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 40 + line_height), '方舟像素字体 / Ark Pixel Font', font_24_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height * 2, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_12_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 5), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', font_12_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 6), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', font_12_zh_tr, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 7), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', font_12_ja, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 9), 'the quick brown fox jumps over a lazy dog.', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 10), '0123456789', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 11), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'github-banner.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_banner():
    alphabet_12 = _load_alphabet(12)
    font_24_zh_cn = _load_font(12, 'zh_cn', 24)
    font_12_zh_cn = _load_font(12, 'zh_cn', 12)

    box_size = 14
    line_height = 18
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image_background = Image.open(os.path.join(path_define.images_dir, 'itch-io-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (255, 255, 255, 0))
    _draw_text_background(image, alphabet_12, 12, box_size, font_12_zh_cn, (200, 200, 200))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 32), '方舟像素字体 / Ark Pixel Font', font_24_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height * 2, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 32 + line_height * 2), '★ 开源的泛中日韩像素字体 ★', font_12_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-banner.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_background():
    alphabet_12 = _load_alphabet(12)
    font_12_zh_cn = _load_font(12, 'zh_cn', 12)

    box_size = 14

    image = Image.new('RGBA', (box_size * 50, box_size * 50), (255, 255, 255, 0))
    _draw_text_background(image, alphabet_12, 2, box_size, font_12_zh_cn, (30, 30, 30))
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-background.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_cover():
    font_24_zh_cn = _load_font(12, 'zh_cn', 24)
    font_12_latin = _load_font(12, 'latin', 12)
    font_12_zh_cn = _load_font(12, 'zh_cn', 12)
    font_12_zh_tr = _load_font(12, 'zh_tr', 12)
    font_12_ja = _load_font(12, 'ja', 12)

    line_height = 18
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image = Image.open(os.path.join(path_define.images_dir, 'itch-io-cover-background.png'))
    _draw_text(image, (image.width / 2, 6), '方舟像素字体', font_24_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height * 2, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 2), '我们每天度过的称之为日常的生活，\n其实是一个个奇迹的连续也说不定。', font_12_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 4), '我們每天度過的稱之為日常的生活，\n其實是一個個奇跡的連續也說不定。', font_12_zh_tr, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 6), '日々、私たちが過ごしている日常は、\n 実は奇跡の連続なのかもしれない。', font_12_ja, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 9), 'the quick brown fox jumps over a lazy dog.', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 10), '0123456789', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 11), '★☆☺☹♠♡♢♣♤♥♦♧\n☀☼♩♪♫♬☂☁⚓✈⚔☯', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-cover.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_afdian_cover():
    font_24_zh_cn = _load_font(12, 'zh_cn', 24)
    font_12_latin = _load_font(12, 'latin', 12)
    font_12_zh_cn = _load_font(12, 'zh_cn', 12)
    font_12_zh_tr = _load_font(12, 'zh_tr', 12)
    font_12_ja = _load_font(12, 'ja', 12)

    line_height = 18
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image = Image.open(os.path.join(path_define.images_dir, 'afdian-cover-background.png'))
    _draw_text(image, (image.width / 2, 12), '方舟像素字体', font_24_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height * 2, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 12 + line_height * 2), 'Ark Pixel Font', font_12_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_12_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 5), '我们每天度过的称之为日常的生活，\n其实是一个个奇迹的连续也说不定。', font_12_zh_cn, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 7), '我們每天度過的稱之為日常的生活，\n其實是一個個奇跡的連續也說不定。', font_12_zh_tr, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 9), '日々、私たちが過ごしている日常は、\n 実は奇跡の連続なのかもしれない。', font_12_ja, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 11), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 12), 'the quick brown fox jumps over a lazy dog.', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 13), '0123456789', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 14), '★☆☺☹♠♡♢♣♤♥♦♧\n☀☼♩♪♫♬☂☁⚓✈⚔☯', font_12_latin, text_color=text_color, shadow_color=shadow_color, line_height=line_height, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'afdian-cover.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')
