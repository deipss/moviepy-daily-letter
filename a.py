import mistune
from mistune.plugins import plugin_table, plugin_strikethrough, plugin_task_lists
from bs4 import BeautifulSoup
def parse_markdown_file(input_file, output_file: str = 'output.html'):
    """
    使用 Mistune 解析 Markdown 文件并转换为 HTML

    参数:
    input_file (str): 输入的 Markdown 文件路径
    output_file (str, optional): 输出的 HTML 文件路径，若为 None 则返回 HTML 字符串

    返回:
    str: 转换后的 HTML 内容（仅当 output_file 为 None 时）
    """
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
            print(f"已成功将 {input_file} 转换为 {output_file}")
        return html_content

    except FileNotFoundError:
        print(f"错误: 文件 {input_file} 未找到")
    except Exception as e:
        print(f"错误: 处理文件时发生异常: {e}")


def count_h2_tags(html_content):
    """统计 HTML 文件中二级标题 (<h2>) 的数量"""
    try:

        # 创建 BeautifulSoup 对象
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找所有 h2 标签
        h2_tags = soup.find_all('h2')

        # 输出每个 h2 标签的文本内容和位置
        print(f" 中找到 {len(h2_tags)} 个二级标题：")
        for index, h2 in enumerate(h2_tags, 1):
            print(f"{index}. {h2.get_text(strip=True)}")

        return len(h2_tags)

    except Exception as e:
        print(f"错误：解析文件时发生异常：{e}")

if __name__ == "__main__":
    # 使用示例
    input_md_file = 'material/1/script.md'  # 请替换为实际的 Markdown 文件路径
    output_html_file = 'output.html'  # 请替换为实际的输出 HTML 文件路径

    # 方式一：将结果保存到文件
    html_content = parse_markdown_file(input_md_file, output_html_file)
    count_h2_tags(html_content)
    # 方式二：获取 HTML 字符串并打印
    # html = parse_markdown_file(input_md_file)
    # print(html)
