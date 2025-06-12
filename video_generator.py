from moviepy import *
from PIL import ImageDraw
import os
import math
from PIL import Image
import sys
from bs4 import BeautifulSoup
from logging_config import logger
import markdown
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BACKGROUND_IMAGE_PATH = "temp/generated_background.png"
GLOBAL_WIDTH = 1920
GLOBAL_HEIGHT = 1080
GAP = int(GLOBAL_WIDTH * 0.04)
INNER_WIDTH = GLOBAL_WIDTH - GAP
INNER_HEIGHT = GLOBAL_HEIGHT - GAP
W_H_RADIO = "{:.2f}".format(GLOBAL_WIDTH / GLOBAL_HEIGHT)
FPS = 40
MAIN_COLOR = "#0099CC"
MAIN_BG_COLOR = "#FFFFFF"
VIDEO_FILE_NAME = "video.mp4"
MATERIAL_PATH = 'material'

REWRITE = False


def build_video_final_path(idx: str):
    return os.path.join('final_videos', idx + '_' + VIDEO_FILE_NAME)


def build_today_end_audio_path():
    return os.path.join(MATERIAL_PATH, "end.mp3")


def build_end_path():
    return os.path.join(MATERIAL_PATH, "end.mp4")


def build_video_path(idx: str, name: str):
    return os.path.join(MATERIAL_PATH, idx, 'video_' + name + '.mp4')


def build_audio_path(idx: str, name: str):
    return os.path.join(MATERIAL_PATH, idx, 'audio_' + name + '.mp3')


def build_video_img_path(idx: str, img_name: str):
    return os.path.join(MATERIAL_PATH, idx, img_name)


def generate_background_image(width=GLOBAL_WIDTH, height=GLOBAL_HEIGHT, border_color=MAIN_COLOR,
                              bg_color=MAIN_BG_COLOR):
    # 创建一个新的图像
    image = Image.new("RGB", (width, height), border_color)
    draw = ImageDraw.Draw(image)

    # 计算边框宽度(1%的宽度)
    border_width = GAP * 1.5

    # 绘制圆角矩形(内部灰白色)
    draw.rounded_rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        radius=40,  # 圆角半径
        fill=bg_color  # 灰白色填充
    )
    image.save(BACKGROUND_IMAGE_PATH)
    return image


def calculate_font_size_and_lines(text, box_width, box_height, font_ratio=1.0, line_height_ratio=1.5,
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


def generate_audio(text: str, output_file: str = "audio.wav", rewrite=False) -> None:
    if os.path.exists(output_file) and not REWRITE:
        logger.warning(f"{output_file}已存在，跳过生成音频。")
        return
    logger.info(f"{output_file}开始生成音频: {text}")
    rate = 50
    sh = f'edge-tts --voice zh-CN-YunjianNeural --text "{text}" --write-media {output_file} --rate="+{rate}%"'
    os.system(sh)


def generate_video_end(is_preview=False):
    output_path = build_end_path()
    if os.path.exists(output_path) and not REWRITE and not is_preview:
        logger.info(f"片尾{output_path}已存在,直接返回")
        return output_path
    generate_background_image(GLOBAL_WIDTH, GLOBAL_HEIGHT, MAIN_COLOR, '#fbfbfb')
    bg_clip = ImageClip(BACKGROUND_IMAGE_PATH)
    audio_path = build_today_end_audio_path()

    generate_audio("今天的分享，至此结束，青山不老，绿水常流。我们下次见。", audio_path, rewrite=True)
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # 设置背景视频时长
    bg_clip = bg_clip.with_duration(duration).with_audio(audio_clip)

    # 创建日期文字
    txt_clip = TextClip(
        text="谢谢收看",
        font_size=int(GLOBAL_HEIGHT * 0.15),
        color=MAIN_COLOR,
        font='./font/simhei.ttf',
        stroke_color='black',
        stroke_width=2
    ).with_duration(duration).with_position(('center', GLOBAL_HEIGHT * 0.7))

    lady = (VideoFileClip('assets/announcer_man.mp4').with_duration(duration)
            .with_position((GLOBAL_WIDTH * 0.38, GLOBAL_HEIGHT * 0.17)).resized(0.7))

    # 合成最终视频
    final_clip = CompositeVideoClip([bg_clip, txt_clip, lady], size=bg_clip.size)
    if is_preview:
        final_clip.preview()
    else:
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=FPS)
    return output_path


def combine_videos_with_transitions(video_paths, output_path):
    if os.path.exists(output_path) and not REWRITE:
        logger.info(f"视频整合生成{output_path}已存在,直接返回")
        return
    generate_background_image(GLOBAL_WIDTH, GLOBAL_HEIGHT, MAIN_COLOR)
    bg_clip = ImageClip(BACKGROUND_IMAGE_PATH)

    # 加载视频和音频
    clips = []
    for i, video_path in enumerate(video_paths):
        # 加载视频
        video = VideoFileClip(video_path)
        if (video.duration < 2):
            logger.warning(f"视频{video_path}时长不足2秒,跳过")
            continue
        video = video.with_position(('center', 'center'), relative=True)
        # 将视频放置在背景上
        video_with_bg = CompositeVideoClip([
            bg_clip,
            video
        ], use_bgclip=True)
        # 将视频放置在背景上
        clips.append(video_with_bg)

    final_clip = concatenate_videoclips(clips, method="compose")
    # 导出最终视频
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=FPS)
    logger.info(f"视频整合生成完成,path={output_path}")
    # final_clip.preview()


def generate_three_layout_video(audio_txt,
                                image_list: list[str],
                                quote_list: list[str],
                                title,
                                idx: str,
                                is_preview=False):
    video_path = build_video_path(idx, title)
    if os.path.exists(video_path) and not REWRITE and not is_preview:
        logger.warning(f"{video_path}已存在，跳过生成视频。")
        return video_path
    # 合成最终视频
    image_clip_list = []
    # 计算各区域尺寸
    title_height = int(INNER_HEIGHT * 0.08)
    top_height = int(INNER_HEIGHT * 0.8)
    bottom_height = INNER_HEIGHT - top_height - title_height
    logger.info(f"title_height={title_height} - top_height={top_height} - bottom_height={bottom_height} ")

    # 加载背景和音频
    bg_clip = ColorClip(size=(INNER_WIDTH, INNER_HEIGHT), color=(255, 255, 255))  # 白色背景
    audio_temp_path = build_audio_path(idx, title)
    generate_audio(audio_txt, output_file=audio_temp_path)
    audio_clip = AudioFileClip(audio_temp_path)
    duration = audio_clip.duration
    logger.info(f"audio_clip.duration={duration}")
    bg_clip = bg_clip.with_duration(duration).with_audio(audio_clip)

    # 图片处理
    all_img_len = len(image_list)

    if all_img_len == 1:
        img_path = build_video_img_path(idx, image_list[0])
        img_clip = ImageClip(img_path)
        alr = quote_list[0]
        scale = min(INNER_WIDTH * 0.5 / img_clip.w, top_height / img_clip.h)
        img_clip = img_clip.resized(scale)
        img_clip = img_clip.with_position((0.01, 0.09), relative=True).with_duration(duration)

        box_w = int((INNER_WIDTH - img_clip.w) * 0.9)
        box_h = img_clip.h
        font_size, chars_per_line = calculate_font_size_and_lines(alr, box_w, box_h)
        alr = '\n'.join([alr[i:i + chars_per_line] for i in range(0, len(alr), chars_per_line)])
        alr_cip = TextClip(
            text=alr,
            interline=font_size // 2,
            font_size=font_size,
            color=MAIN_COLOR,
            font='./font/simhei.ttf',
            text_align='left',
            size=(box_w, box_h),
            method='caption',

        ).with_duration(duration).with_position((int(img_clip.w + INNER_WIDTH * 0.015), int(INNER_HEIGHT * 0.10)))

        used_h = img_clip.h + title_height
        box_w1 = int(INNER_WIDTH * 0.95)
        box_h1 = int((INNER_HEIGHT - used_h) * 0.9)

        additional_text = audio_txt
        font_size, chars_per_line = calculate_font_size_and_lines(additional_text, box_w1, box_h1)
        additional_text = '\n'.join(
            [additional_text[i:i + chars_per_line] for i in range(0, len(additional_text), chars_per_line)])
        alr_cip1 = TextClip(
            text=additional_text,
            interline=font_size // 3,
            font_size=font_size,
            color='black',
            font='./font/simhei.ttf',
            text_align='left',
            size=(box_w1, box_h1),
            method='caption',
        ).with_duration(duration).with_position((0.01, used_h / INNER_HEIGHT), relative=True)
        image_clip_list.append(alr_cip1)

        image_clip_list.append(img_clip)
        image_clip_list.append(alr_cip)

    if all_img_len == 2:
        img_path = build_video_img_path(idx, image_list[0])
        img_clip = ImageClip(img_path)
        w_radio = 0.48
        scale = min(INNER_WIDTH * w_radio / img_clip.w, top_height * 0.8 / img_clip.h)
        img_clip = img_clip.resized(scale)
        img_clip = img_clip.with_position((0.015, 0.09), relative=True).with_duration(duration)

        img_path1 = build_video_img_path(idx, image_list[1])
        img_clip1 = ImageClip(img_path1)
        scale = min(INNER_WIDTH * w_radio / img_clip1.w, top_height * 0.8 / img_clip1.h)
        img_clip1 = img_clip1.resized(scale)
        img_clip1 = img_clip1.with_position((0.5, 0.09), relative=True).with_duration(duration)

        box_w = int(INNER_WIDTH * 0.95)
        used_h = max(img_clip.h, img_clip1.h) + title_height
        box_h = int((INNER_HEIGHT - used_h) * 0.9)
        alr = quote_list[0] + quote_list[1]

        alr0 = quote_list[0]
        alr1 = quote_list[1]
        font_size, chars_per_line = calculate_font_size_and_lines(alr, box_w, box_h)
        alr0 = "    " + alr0.replace('\n', '')
        alr1 = "    " + alr1.replace('\n', '')
        alr = '\n'.join([alr0[i:i + chars_per_line] for i in range(0, len(alr0), chars_per_line)])
        alr += '\n'
        alr += '\n'.join([alr1[i:i + chars_per_line] for i in range(0, len(alr1), chars_per_line)])
        alr_cip = TextClip(
            text=alr,
            interline=font_size // 3,
            font_size=font_size,
            color='black',
            font='./font/simhei.ttf',
            text_align='left',
            size=(box_w, box_h),
            method='caption'

        ).with_duration(duration).with_position((0.01, (used_h + font_size // 2) / INNER_HEIGHT), relative=True)

        image_clip_list.append(img_clip1)
        image_clip_list.append(img_clip)
        image_clip_list.append(alr_cip)

    # 标题
    title_font_size = int(title_height * 0.9)
    top_title = TextClip(
        interline=title_font_size // 2,
        text=title,
        font_size=title_font_size,
        color='black',
        font='./font/simhei.ttf',
        method='label',
        horizontal_align='left',
        size=(INNER_WIDTH, title_font_size)
    ).with_duration(duration).with_position(('left', 'top'))

    image_clip_list.insert(0, bg_clip)
    image_clip_list.insert(1, top_title)
    final_video = CompositeVideoClip(clips=image_clip_list, size=(INNER_WIDTH, INNER_HEIGHT))

    if is_preview:
        final_video.preview()
    else:
        final_video.write_videofile(video_path, remove_temp=True, codec="libx264", audio_codec="aac",
                                    fps=FPS)
    return video_path


def build_letters_json_path():
    return os.path.join('letters', "letters.json")


# 新增函数：处理 letters.json 文件
def process_letters_json():
    # 加载 letters.json 文件
    json_path = build_letters_json_path()
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            letters = json.load(f)
    except FileNotFoundError:
        logger.error("letters.json 文件未找到，请检查路径是否正确。")
        return

    success_count = 0  # 成功生成的计数器

    for letter in letters:
        if letter.get('generated', True):
            continue  # 跳过已生成的项
        try:
            logger.info(f"开始生成视频{letter['idx']}: {letter['title']}")
            generate_one_story_video(letter['idx'])
            letter['generated'] = True
            success_count += 1
            logger.info(f"视频生成成功: {letter['title']}")
            if success_count % 2 == 0:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(letters, f, ensure_ascii=False, indent=4)
                logger.info("letters.json 文件已更新。")
        except Exception as e:
            logger.error(f"生成视频失败: {letter['title']}, 错误信息: {e}", exc_info=True)
            continue


def parse_markdown_sections(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    # 将 Markdown 转换为 HTML
    html = markdown.markdown(markdown_content, extensions=["extra"])
    soup = BeautifulSoup(html, "html.parser")

    # 遍历所有的 <h2>
    result = []
    h2_elements = soup.find_all("h2")
    for i, h2 in enumerate(h2_elements):
        section = {
            "title": h2.get_text(),
            "images": [],
            "quotes": [],
            "texts": []
        }

        # 获取当前 h2 到下一个 h2 之间的所有元素
        next_h2 = h2_elements[i + 1] if i + 1 < len(h2_elements) else None
        content = []
        sibling = h2.find_next_sibling()
        while sibling and sibling != next_h2:
            content.append(sibling)
            sibling = sibling.find_next_sibling()

        for el in content:
            if el.name == "p":
                # 图片
                img = el.find("img")
                if img:
                    section["images"].append(img["src"])
                else:
                    section["texts"].append(el.get_text().strip())
            elif el.name == "blockquote":
                section["quotes"].append(el.get_text().strip())

        result.append(section)

    return result


def generate_one_story_video(idx=1):
    sections = parse_markdown_sections(f'material/{idx}/script.md')
    paths = []
    for i, section in enumerate(sections[4:5]):
        audio_txt = ""
        if len(section['images']) == 1:
            audio_txt = "".join(section['texts'])
        if len(section['images']) == 2:
            audio_txt = "".join(section['quotes'])
        audio_txt = audio_txt.replace('\n', '')
        path = generate_three_layout_video(
            audio_txt,
            section['images'],
            section['quotes'],
            section['title'],
            str(idx), False)
        paths.append(path)
    logger.info(f"paths={paths}")
    paths.append(generate_video_end())
    combine_videos_with_transitions(paths, build_video_final_path(str(idx)))


def test_generate_video_end():
    generate_video_end(is_preview=True)


def test_generate_video_h2():
    idx = 1
    sections = parse_markdown_sections(f'material/{idx}/script.md')
    paths = []
    for i, section in enumerate(sections[4:5]):
        audio_txt = ""
        if len(section['images']) == 1:
            audio_txt = "".join(section['texts'])
        if len(section['images']) == 2:
            audio_txt = "".join(section['quotes'])
        audio_txt = audio_txt.replace('\n', '')
        path = generate_three_layout_video(
            audio_txt,
            section['images'],
            section['quotes'],
            section['title'],
            str(idx), True)
        paths.append(path)
    logger.info(f"paths={paths}")


def test_generate_one():
    generate_three_layout_video(
        "开始今天的信件前，让我们看下今天的世界。2013年，乌拉圭成为世界上第一个将娱乐用大麻的种植、销售和使用完全合法化的国家。",

        ['img_6.png'], ['家、文学家、改革先驱、诗人、学者、翻译家。1811年林则徐（26岁）中进士，后曾官至一品，曾经担任',
                        """  林则徐（1785年8月30日—1850年11月22日）男性，福建省福州府侯官县左营司巷（今福州市鼓楼区）人 ，字元抚，又字少穆、石麟，晚号俟村老人、俟村退叟、七十二峰退叟、瓶泉居士、栎社散人等
                            ，家族为文山林氏。是清朝后期政治家、思想家、文学家、改革先驱、诗人、学者、翻译家。1811年林则徐（26岁）中进士，后曾官至一品，曾经担任湖广总督、陕甘总督和云贵总督，两次受命钦差大臣。林则徐知名于主张严禁进口的洋鸦片，他曾于1833年建议在国内种鸦片以抗衡洋鸦片。
                            """,
                        ], "背景", "1", True)


def test_generate_two():
    generate_three_layout_video(
        "开始今天的信件前，让我们看下今天的世界。2013年，乌拉圭成为世界上第一个将娱乐用大麻的种植、销售和使用完全合法化的国家。",
        ['img_6.png', 'img_7.png'],
        ['家、文学家、改革先驱、诗人、学者、翻译家。1811年林则徐（26岁）中进士，后曾官至一品，曾经担任',
         """  林则徐（1785年8月30日—1850年11月22日）男性，福建省福州府侯官县左营司巷（今福州市鼓楼区）人 ，字元抚，又字少穆、石麟，晚号俟村老人、俟村退叟、七十二峰退叟、瓶泉居士、栎社散人等
             ，家族为文山林氏。是清朝后期政治家、思想家、文学家、改革先驱、诗人、学者、翻译家。1811年林则徐（26岁）中进士，后曾官至一品，曾经担任湖广总督、陕甘总督和云贵总督，两次受命钦差大臣。林则徐知名于主张严禁进口的洋鸦片，他曾于1833年建议在国内种鸦片以抗衡洋鸦片。
             """,
         ], "背景", "1"
        , True)


def test_edge_tts():
    # zh-CN-YunjianNeural
    for name in ['zh-CN-shaanxi-XiaoniNeural']:
        text = '林则徐（1785年8月30日—1850年11月22日）男性，福建省福州府侯官县左营司巷（今福州市鼓楼区）人 ，字元抚，'
        output_file = f'temp/{name}.mp3'
        rate = 50
        sh = f'edge-tts --voice {name} --text "{text}" --write-media {output_file} --rate="+{rate}%"'
        os.system(sh)


import argparse


def init_param():
    if not os.path.exists('temp'):
        os.mkdir('temp')
    if not os.path.exists('final_videos'):
        os.mkdir('final_videos')
    if not os.path.exists('material'):
        os.mkdir('material')
    logger.info(
        f"GLOBAL_WIDTH:{GLOBAL_WIDTH}\nGLOBAL_HEIGHT:{GLOBAL_HEIGHT}\n W_H_RADIO:{W_H_RADIO}\n  FPS:{FPS}\n  BACKGROUND_IMAGE_PATH:{BACKGROUND_IMAGE_PATH}\nGAP:{GAP}\nINNER_WIDTH:{INNER_WIDTH}\nINNER_HEIGHT:{INNER_HEIGHT}")


if __name__ == "__main__":
    logger.info("=======================开始执行=========================")
    init_param()

    parser = argparse.ArgumentParser(description="视频生成工具")
    parser.add_argument("--rewrite", type=bool, default=False, help="是否重写")
    args = parser.parse_args()
    logger.info(f"新闻视频生成工具 参数args={args}")

    if args.rewrite:
        REWRITE = True
        logger.info("指定强制重写")
    try:
        process_letters_json()
    except Exception as e:
        logger.error(f"生成时异常，{e}", exc_info=True)
