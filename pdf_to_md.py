"""
PDF转Markdown转换工具
将PDF文件转换为Markdown格式，并提取图片
使用PyMuPDF手动提取并按位置排序，确保图片位置准确
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
import re


def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_page_elements(page, img_output_dir, page_num, pdf_name):
    """
    提取页面中的所有元素（文本块和图片），并按y坐标排序

    Args:
        page: PyMuPDF页面对象
        img_output_dir: 图片保存目录
        page_num: 页码
        pdf_name: PDF文件名

    Returns:
        排序后的元素列表，每个元素包含 type, content, y0 等信息
    """
    elements = []

    # 1. 提取文本块
    blocks = page.get_text("blocks")
    for block in blocks:
        # block 格式: (x0, y0, x1, y1, "text", block_no, block_type)
        if len(block) >= 7:
            x0, y0, x1, y1, text, block_no, block_type = block[:7]
            # block_type: 0=text, 1=image
            if block_type == 0 and text.strip():  # 文本块
                elements.append({
                    'type': 'text',
                    'content': text.strip(),
                    'y0': y0,
                    'y1': y1,
                    'x0': x0,
                    'x1': x1
                })

    # 2. 提取图片
    image_list = page.get_images(full=True)
    for img_index, img_info in enumerate(image_list):
        xref = img_info[0]

        # 获取图片位置
        img_rects = page.get_image_rects(xref)
        if not img_rects:
            continue

        # 使用第一个矩形的位置
        rect = img_rects[0]

        # 提取并保存图片
        try:
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # 生成图片文件名
            img_filename = f"{pdf_name}-{page_num}-{img_index}.{image_ext}"
            img_path = os.path.join(img_output_dir, img_filename)

            # 保存图片
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)

            # 添加图片元素
            elements.append({
                'type': 'image',
                'content': img_filename,
                'y0': rect.y0,
                'y1': rect.y1,
                'x0': rect.x0,
                'x1': rect.x1
            })
        except Exception as e:
            print(f"警告：提取图片失败 (页{page_num}, 图{img_index}): {e}")
            continue

    # 按 y0 坐标排序（从上到下），如果 y0 相同则按 x0 排序（从左到右）
    elements.sort(key=lambda e: (e['y0'], e['x0']))

    return elements


def elements_to_markdown(elements, img_folder_name):
    """
    将元素列表转换为 Markdown 格式

    Args:
        elements: 元素列表
        img_folder_name: 图片文件夹名称（用于生成相对路径）

    Returns:
        Markdown 格式的文本
    """
    markdown_lines = []

    for element in elements:
        if element['type'] == 'text':
            # 处理文本
            text = element['content']

            # 按行处理
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    markdown_lines.append('')
                    continue

                # 检测是否为标题
                # 1. 以 # 开头的
                if line.startswith('#'):
                    markdown_lines.append(f"\n{line}\n")
                # 2. 以数字开头且较短的（可能是编号标题）
                elif re.match(r'^\d+[\.\、]', line) and len(line) < 80:
                    markdown_lines.append(f"\n### {line}\n")
                # 3. 较短的行（可能是标题）
                elif len(line) < 50 and not line.endswith(('，', '。', ',', '.')):
                    markdown_lines.append(f"\n**{line}**\n")
                # 4. 普通文本
                else:
                    markdown_lines.append(line)

        elif element['type'] == 'image':
            # 添加图片引用
            img_path = f"./{img_folder_name}/{element['content']}"
            markdown_lines.append(f"\n![]({img_path})\n")

    return '\n'.join(markdown_lines)


def pdf_to_markdown(pdf_path, md_output_path, img_output_dir):
    """
    将PDF转换为Markdown文件

    Args:
        pdf_path: 源PDF文件路径
        md_output_path: Markdown文件保存路径
        img_output_dir: 图片保存目录
    """
    # 确保输出目录存在
    ensure_dir(os.path.dirname(md_output_path))
    ensure_dir(img_output_dir)

    # 获取图片文件夹名称（相对于markdown文件的路径）
    img_folder_name = os.path.basename(img_output_dir.rstrip('/'))

    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    print("正在转换PDF为Markdown并提取图片...")

    # 打开 PDF
    doc = fitz.open(pdf_path)
    all_markdown = []

    total_pages = len(doc)
    for page_num in range(total_pages):
        page = doc[page_num]

        # 显示进度
        if (page_num + 1) % 10 == 0 or page_num == 0 or page_num == total_pages - 1:
            print(f"处理页面 {page_num + 1}/{total_pages}...")

        # 提取页面元素并排序
        elements = get_page_elements(page, img_output_dir, page_num, pdf_name)

        # 转换为 Markdown
        page_markdown = elements_to_markdown(elements, img_folder_name)
        all_markdown.append(page_markdown)

        # 添加页面分隔符（可选）
        # all_markdown.append(f"\n\n---\n<!-- Page {page_num + 1} -->\n\n")

    doc.close()

    # 合并所有页面的 Markdown
    md_text = '\n\n'.join(all_markdown)

    # 保存 Markdown 文件
    with open(md_output_path, "w", encoding="utf-8") as md_file:
        md_file.write(md_text)

    print(f"转换完成！Markdown文件已保存到: {md_output_path}")
    print(f"图片已保存到: {img_output_dir}")


if __name__ == "__main__":
    # 配置路径
    PDF_PATH = "/Users/craig/Downloads/个人设备.pdf"
    MD_OUTPUT_PATH = "/Users/craig/Downloads/转换/个人设备.md"
    IMG_OUTPUT_DIR = "/Users/craig/Downloads/转换/assets/"

    # 检查PDF文件是否存在
    if not os.path.exists(PDF_PATH):
        print(f"错误：PDF文件不存在 - {PDF_PATH}")
        exit(1)

    # 执行转换
    pdf_to_markdown(PDF_PATH, MD_OUTPUT_PATH, IMG_OUTPUT_DIR)
