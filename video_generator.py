from moviepy import *
from PIL import ImageDraw
from datetime import datetime
import json
from zhdate import ZhDate
import os
import math
from PIL import Image
from moviepy.video.fx import Loop
from ollama_client import OllamaClient
from logging_config import logger
import sys
from edge_tts import Communicate

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BACKGROUND_IMAGE_PATH = "temp/generated_background.png"
GLOBAL_WIDTH = 1920
GLOBAL_HEIGHT = 1080
GAP = int(GLOBAL_WIDTH * 0.02)
INNER_WIDTH = GLOBAL_WIDTH - GAP
INNER_HEIGHT = GLOBAL_HEIGHT - GAP
W_H_RADIO = "{:.2f}".format(GLOBAL_WIDTH / GLOBAL_HEIGHT)
FPS = 40
MAIN_COLOR = "##0099CC"
MAIN_BG_COLOR = "#FFFFFF"
VIDEO_FILE_NAME = "video.mp4"
MATERIAL_PATH = 'material'

import time

REWRITE = False


def build_video_final_path(idx: str):
    return os.path.join(MATERIAL_PATH, idx, VIDEO_FILE_NAME)


def build_video_path(idx: str, name: str):
    return os.path.join(MATERIAL_PATH, idx, 'video_' + name + '.mp4')


def build_audio_path(idx: str, name: str):
    return os.path.join(MATERIAL_PATH, idx, 'audio_' + name + '.mp4')


def build_video_img_path(idx: str, img_name: str):
    return os.path.join(MATERIAL_PATH, idx, img_name)


def check_orientation_horizontal_screen_by_path(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    aspect_ratio = width / height
    return aspect_ratio > 1


def check_orientation_horizontal_screen_by_img(img):
    width, height = img.size
    aspect_ratio = width / height
    return aspect_ratio > 1


def generate_background_image(width=GLOBAL_WIDTH, height=GLOBAL_HEIGHT, color=MAIN_COLOR):
    # 创建一个新的图像
    image = Image.new("RGB", (width, height), color)  # 橘色背景
    draw = ImageDraw.Draw(image)

    # 计算边框宽度(1%的宽度)
    border_width = GAP * 1.5

    # 绘制圆角矩形(内部灰白色)
    draw.rounded_rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        radius=40,  # 圆角半径
        fill="#FCFEFE"  # 灰白色填充
    )

    image.save(BACKGROUND_IMAGE_PATH)
    return image


def add_newline_every_n_chars(text, n):
    """
    每隔固定的字数在文本中添加换行符

    参数:
    text (str): 需要添加换行符的长文本
    n (int): 指定的固定字数

    返回:
    str: 添加换行符后的文本
    """
    if n <= 0:
        return text

    return '\n'.join([text[i:i + n] for i in range(0, len(text), n)])


def calculate_font_size_and_line_length(text, box_width, box_height, font_ratio=1.0, line_height_ratio=1.5,
                                        start_size=72):
    """
    计算适合文本框的字体大小和每行字数

    参数:
    text (str): 要显示的文本
    box_width (int): 文本框宽度（像素）
    box_height (int): 文本框高度（像素）
    font_ratio (float): 字体大小与平均字符宽度的比例系数
    line_height_ratio (float): 行高与字体大小的比例系数
    start_size (int): 开始尝试的最大字体大小

    返回:
    dict: 包含计算结果的字典，键为 'font_size' 和 'chars_per_line'
    """
    # 从最大字体开始尝试，逐步减小直到文本适应文本框
    for font_size in range(start_size, 0, -1):
        # 计算每个字符的平均宽度和行高
        char_width = font_size * font_ratio
        line_height = font_size * line_height_ratio

        # 计算每行可容纳的字符数
        chars_per_line = max(1, math.floor(box_width / char_width))

        # 计算所需的总行数
        total_lines = math.ceil(len(text) / chars_per_line)

        # 计算所需的总高度
        total_height = total_lines * line_height

        # 如果高度符合要求，返回当前字体大小和每行字符数
        if total_height <= box_height:
            return font_size, chars_per_line

    return 40, len(text)


def truncate_after_find_period(text: str, end_pos: int = 400) -> str:
    if len(text) <= end_pos:
        return text
    # 从end_pos位置开始向后查找第一个句号
    last_period = text.find('。', end_pos)

    if last_period != -1:
        # 截取至句号位置（包含句号）
        return text[:last_period + 1]
    else:
        # 300字符后无句号，返回全文（或截断并添加省略号）
        return text  # 或返回 text[:end_pos] + "..."（按需选择）


def calculate_segment_times(duration, num_segments):
    """
    将总时长分成若干段，并计算每段的开始和结束时间。

    参数:
    duration (float): 总时长（秒）
    num_segments (int): 分段数量

    返回:
    list: 每段的开始和结束时间列表，格式为 [(start_time, end_time), ...]
    """
    segment_duration = duration / num_segments
    segment_times = []
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        segment_times.append((start_time, end_time))
    return segment_times


def generate_three_layout_video(audio_txt, image_list: list[dict], title, idx: str,
                                is_preview=False):
    # 计算各区域尺寸
    title_height = INNER_HEIGHT * 0.15
    top_height_ratio = 0.85
    top_height = int((INNER_HEIGHT - title_height) * top_height_ratio)
    bottom_height = INNER_HEIGHT - top_height - title_height
    logger.info(f"title_height={title_height} - top_height={top_height} - bottom_height={bottom_height} ")

    # 加载背景和音频
    bg_clip = ColorClip(size=(INNER_WIDTH, INNER_HEIGHT), color=(255, 255, 255))  # 白色背景
    communicate = Communicate(text=audio_txt, voice="zh-CN-YunyangNeural")
    audio_temp_path = build_audio_path(idx, title)
    communicate.save(audio_temp_path)
    audio_clip = AudioFileClip(audio_temp_path)
    duration = audio_clip.duration
    bg_clip = bg_clip.with_duration(duration).with_audio(audio_clip)

    # 图片处理

    all_img_len = len(image_list)

    if all_img_len == 1:
        first_img = image_list[0]








    # 标题
    title_font_size = int(title_height * 0.9)
    top_title = TextClip(
        interline=title_font_size // 2,
        text=title,
        font_size=title_font_size,
        color='black',
        font='./font/simhei.ttf',
        method='label'
    ).with_duration(duration).with_position(('left', 'top'))

    # 合成最终视频
    image_clip_list = []
    image_clip_list.insert(0, bg_clip)
    image_clip_list.insert(3, top_title)
    final_video = CompositeVideoClip(clips=image_clip_list, size=(INNER_WIDTH, INNER_HEIGHT))
    if is_preview:
        final_video.preview()
    else:
        final_video.write_videofile(build_video_path(idx, title), remove_temp=True, codec="libx264", audio_codec="aac",
                                    fps=FPS)


def get_full_date(today=datetime.now()):
    """获取完整的日期信息：公历日期、农历日期和星期"""

    # 获取公历日期
    solar_date = today.strftime("%Y年%m月%d日")

    # 获取农历日期
    lunar_date = ZhDate.from_datetime(today).chinese()

    # 获取星期几
    weekday_map = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = f"星期{weekday_map[today.weekday()]}"
    return "今天是{}, \n农历{}, \n{},欢迎收看【今日快电】".format(solar_date, lunar_date, weekday)


def get_weekday_color():
    # 星期与颜色的映射关系 (0 = Monday, 6 = Sunday)
    weekday_color_map = {
        0: 'Red',  # 周一 - 红色
        1: 'Orange',  # 周二 - 橙色
        2: 'Yellow',  # 周三 - 黄色
        3: 'Green',  # 周四 - 绿色
        4: 'Blue',  # 周五 - 蓝色
        5: 'Purple',  # 周六 - 紫色
        6: 'Pink'  # 周日 - 粉色
    }

    # 获取当前星期几 (0=Monday, 6=Sunday)
    weekday = datetime.today().weekday()

    # 返回对应颜色
    return weekday_color_map[weekday]




import argparse

if __name__ == "__main__":
    logger.info("=======================开始执行=========================")

    if not os.path.exists('temp'):
        os.mkdir('temp')
    if not os.path.exists('final_videos'):
        os.mkdir('final_videos')
    if not os.path.exists('material'):
        os.mkdir('material')

    logger.info(
        f"GLOBAL_WIDTH:{GLOBAL_WIDTH}\nGLOBAL_HEIGHT:{GLOBAL_HEIGHT}\n W_H_RADIO:{W_H_RADIO}\n  FPS:{FPS}\n  BACKGROUND_IMAGE_PATH:{BACKGROUND_IMAGE_PATH}\nGAP:{GAP}\nINNER_WIDTH:{INNER_WIDTH}\nINNER_HEIGHT:{INNER_HEIGHT}")

    parser = argparse.ArgumentParser(description="视频生成工具")
    parser.add_argument("--today", type=str, default=datetime.now().strftime("%Y%m%d"), help="指定日期")
    parser.add_argument("--rewrite", type=bool, default=False, help="是否重写")
    args = parser.parse_args()
    logger.info(f"新闻视频生成工具 参数args={args}")

    if args.rewrite:
        REWRITE = True
        logger.info("指定强制重写")

    # combine_videos(today=args.today)
