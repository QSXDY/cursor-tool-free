#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单图标生成脚本 - 为发布版本创建基础图标
"""

from PIL import Image, ImageDraw, ImageFont


def create_simple_icon():
    """创建简单的应用图标"""
    # 创建256x256的图标
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制圆形背景
    padding = 20
    circle_bbox = [padding, padding, size - padding, size - padding]
    draw.ellipse(circle_bbox, fill="#007ACC", outline="#005999", width=4)

    # 绘制文字 "C"
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except OSError:
        font = ImageFont.load_default()

    text = "C"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10

    draw.text((x, y), text, fill="white", font=font)

    # 保存为不同格式
    img.save("icon.png")
    img.save("icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

    print("✅ 图标创建完成: icon.png, icon.ico")


if __name__ == "__main__":
    try:
        create_simple_icon()
        print("\n🎉 图标生成完成！")
        print("📋 生成的文件:")
        print("  • icon.png - 通用PNG图标")
        print("  • icon.ico - Windows ICO图标")
    except ImportError:
        print("⚠️ 需要安装PIL: pip install Pillow")
        print("💡 或者手动提供icon.png和icon.ico文件")
