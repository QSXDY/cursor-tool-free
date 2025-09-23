# 字体文件说明

此目录用于存放应用程序内置字体文件。

## 支持的字体

将以下字体文件放置在此目录中：

1. **HarmonyOS_Sans_SC_Regular.ttf** - 鸿蒙字体常规版
2. **HarmonyOS_Sans_SC_Bold.ttf** - 鸿蒙字体粗体版

## 字体获取方式

### 方法1：从系统中复制（如果已安装）
- Windows: `C:\Windows\Fonts\`
- macOS: `/Library/Fonts/` 或 `/System/Library/Fonts/`
- Linux: `/usr/share/fonts/` 或 `~/.fonts/`

### 方法2：官方下载
- 华为开发者官网
- GitHub开源项目
- 字体设计网站

## 使用说明

1. 将字体文件放入此目录
2. 确保文件名与 `font_manager.py` 中的配置一致
3. 重启应用程序即可生效

## 注意事项

- 请确保有字体的使用授权
- 字体文件会增加应用程序的打包大小
- 如果字体文件不存在，程序会自动回退到系统字体
