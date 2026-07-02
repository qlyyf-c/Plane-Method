import os
import json
import markdown
from pathlib import Path

def build_specifications():
    """构建规范条文数据"""

    # 定义各个类别的源文件目录
    categories = {
        'beam': 'beam',
        'column': 'column',
        'general': 'general'
    }

    for category, folder in categories.items():
        source_dir = Path('source') / folder
        output_file = Path('build') / f'{folder}_rules.json'

        specifications = []

        # 遍历源文件目录中的所有Markdown文件
        for md_file in source_dir.glob('*.md'):
            # 读取Markdown文件内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content_markdown = f.read()

            # 提取文件名（不带扩展名）作为条文ID
            spec_id = md_file.stem

            # 从文件内容中提取标题和条款号
            # Markdown 标题格式：# 4.2 标题内容 或#2.2.1 柱纵向钢筋构造要求
            lines = content_markdown.split('\n')
            title_line = lines[0] if lines else ""

            # 移除开头的 # 符号，然后提取条款号和标题
            import re
            match = re.match(r'^#\s*(\d+[\d.~]*|[\d.~]+)\s*(.*)', title_line)
            if match:
                clause_number = match.group(1)  # 条款号（如 4.2, 2.2.1, 8.3.1~8.3.2）
                title = match.group(2).strip()   # 标题内容
            else:
                # 如果没有匹配到条款号，使用整个标题行作为标题
                clause_number = ""
                title = title_line.lstrip('#').strip()

            # 转换Markdown为HTML
            content_html = markdown.markdown(content_markdown, extensions=['extra', 'smarty'])

            # 创建规范条文对象
            specification = {
                "id": spec_id,
                "clause_number": clause_number,
                "title": title,
                "category": category,
                "content_html": content_html,
                "related_calc": None,
                "related_ann_type": category if category != 'general' else None
            }

            specifications.append(specification)

        # 写入JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(specifications, f, ensure_ascii=False, indent=2)

        print(f"已构建 {len(specifications)} 条 {category} 类别规范条文")

if __name__ == '__main__':
    build_specifications()