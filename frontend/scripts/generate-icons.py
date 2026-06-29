#!/usr/bin/env python3
"""生成PWA图标 - 使用PIL从SVG生成多尺寸PNG"""

import os
import sys
from pathlib import Path

# 图标尺寸列表
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def generate_icons():
    """生成PWA图标"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("错误: 需要安装Pillow库")
        print("运行: pip install Pillow")
        sys.exit(1)

    # 图标输出目录
    output_dir = Path(__file__).parent.parent / "public" / "icons"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 土木工程蓝色主题
    PRIMARY_COLOR = (25, 118, 210)  # #1976d2
    PRIMARY_DARK = (13, 71, 161)    # #0d47a1

    for size in ICON_SIZES:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 圆角矩形背景
        radius = size // 8
        draw.rounded_rectangle(
            [(0, 0), (size, size)],
            radius=radius,
            fill=PRIMARY_COLOR
        )

        # 添加渐变效果（简单模拟）
        for i in range(min(size // 4, radius)):
            alpha = int(255 * (1 - i / (size // 4)) * 0.1)
            overlay_color = (255, 255, 255, alpha)
            new_radius = max(radius - i, 0)
            if new_radius > 0 and size - i > i:
                draw.rounded_rectangle(
                    [(i, i), (size - i - 1, size - i - 1)],
                    radius=new_radius,
                    fill=overlay_color
                )

        # 尝试加载字体，如果不存在则使用默认字体
        try:
            # 尝试使用系统字体
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 5)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size // 7)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 绘制文字
        text_y_offset = size // 8

        # "平法" - 主标题
        text = "平法"
        bbox = draw.textbbox((0, 0), text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (size - text_width) // 2
        text_y = size // 4 - text_y_offset
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font_large)

        # "助手" - 副标题
        text = "助手"
        bbox = draw.textbbox((0, 0), text, font=font_small)
        text_width = bbox[2] - bbox[0]
        text_x = (size - text_width) // 2
        text_y = size * 3 // 5 - text_y_offset
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 230), font=font_small)

        # 保存图标
        output_path = output_dir / f"icon-{size}x{size}.png"
        img.save(output_path, "PNG")
        print(f"生成: {output_path}")

    print(f"\n图标生成完成！共 {len(ICON_SIZES)} 个尺寸")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    generate_icons()
