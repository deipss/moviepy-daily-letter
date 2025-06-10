import mistune
from mistune.plugins import plugin_table, plugin_strikethrough, plugin_task_lists
from bs4 import BeautifulSoup
from logging_config import logger


def parse_markdown_file(input_file, output_file: str = 'output.html'):
    try:
        # 读取 Markdown 文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        # 创建支持扩展语法的渲染器
        renderer = mistune.HTMLRenderer(escape=False)
        markdown = mistune.create_markdown(
            renderer=renderer,
            plugins=[
                plugin_table,  # 支持表格
                plugin_strikethrough,  # 支持删除线
                plugin_task_lists,  # 支持任务列表
            ]
        )
        # 解析 Markdown 内容为 HTML
        html_content = markdown(markdown_content)
        # 如果指定了输出文件，则写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"已成功将 {input_file} 转换为 {output_file}")
        return html_content

    except FileNotFoundError:
        logger.info(f"错误: 文件 {input_file} 未找到")
    except Exception as e:
        logger.info(f"错误: 处理文件时发生异常: {e}")


def count_h2_tags(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        h2_tags = soup.find_all('h2')
        logger.info(f" 中找到 {len(h2_tags)} 个二级标题：")
        for i, h2 in enumerate(h2_tags, 1):
            h3_tags = h2.find_all('h3')
            for j, h3 in enumerate(h3_tags, 1):
                li_tags = h3.find_all('li')
                logger.info(f"{i}.{j} {h2.get_text(strip=True)} {h3.get_text(strip=True)}")
        return len(h2_tags)
    except Exception as e:
        logger.info(f"错误：解析文件时发生异常：{e}")


if __name__ == "__main__":
    # 使用示例
    input_md_file = 'material/1/script.md'  # 请替换为实际的 Markdown 文件路径
    output_html_file = 'output.html'  # 请替换为实际的输出 HTML 文件路径

    # 方式一：将结果保存到文件
    html_content = parse_markdown_file(input_md_file, output_html_file)
    count_h2_tags(html_content)
    # 方式二：获取 HTML 字符串并打印
    # html = parse_markdown_file(input_md_file)
    # logger.info(html)
