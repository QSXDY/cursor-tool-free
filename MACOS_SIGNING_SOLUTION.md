# 🍎 macOS代码签名解决方案

## 📋 问题分析

### 现象
在macOS上运行应用时提示：
- "无法打开，因为无法验证开发者"
- "已损坏，无法打开"
- 应用被macOS Gatekeeper阻止

### 根本原因
从macOS 10.15 Catalina开始，Apple要求所有应用必须：
1. **代码签名**：使用开发者证书签名
2. **公证**：经过Apple公证服务器验证

没有这两步，macOS默认会阻止应用运行。

---

## ✅ 实施的解决方案

### 方案选择：Ad-hoc自签名

**优点**：
- ✅ 完全免费（无需99美元/年的开发者账号）
- ✅ 可在CI/CD自动完成
- ✅ 生成标准.app应用包
- ✅ 用户体验可接受（首次右键打开即可）

**效果**：
- 用户首次打开需要：右键 → 打开 → 确认（仅一次）
- 之后可以正常双击使用
- 比完全不签名体验好很多

---

## 🛠️ 技术实现

### 1. 更新PyInstaller配置（CursorToolFree.spec）

```python
# 添加macOS平台检测
import sys

# 根据平台选择不同的图标和配置
exe = EXE(
    ...
    version='version_info.txt' if sys.platform == 'win32' else None,
    icon='icon.icns' if sys.platform == 'darwin' else 'icon.ico'
)

# macOS专用：添加BUNDLE配置
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='CursorToolFree.app',
        icon='icon.icns',
        bundle_identifier='com.cursortool.free',
        info_plist={
            'CFBundleName': 'Cursor Tool Free',
            'CFBundleDisplayName': 'Cursor Tool Free',
            'CFBundleVersion': '1.0.3',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
            ...
        },
    )
```

**关键点**：
- 使用`BUNDLE`生成标准.app应用包
- 配置`info_plist`添加应用元数据
- 支持Retina显示屏
- 指定最低系统版本

### 2. 创建macOS构建脚本（build_macos.sh）

```bash
#!/bin/bash

# 1. 使用PyInstaller构建.app
pyinstaller CursorToolFree.spec

# 2. Ad-hoc签名（关键步骤）
codesign --force --deep --sign - "dist/CursorToolFree.app"

# 3. 验证签名
codesign --verify --deep --strict --verbose=2 "dist/CursorToolFree.app"

# 4. 创建DMG安装包
create-dmg ... "dist/CursorToolFree-macOS.dmg" "dist/CursorToolFree.app"
```

**签名命令说明**：
- `--force`：强制签名，覆盖已有签名
- `--deep`：递归签名所有内嵌框架和可执行文件
- `--sign -`：使用ad-hoc签名（`-`表示无证书）

### 3. 更新GitHub Actions（.github/workflows/release.yml）

```yaml
- name: Build macOS executable with spec file
  run: |
    pyinstaller CursorToolFree.spec --clean --noconfirm

- name: Sign macOS app (ad-hoc)
  run: |
    codesign --force --deep --sign - "dist/CursorToolFree.app"
    codesign --verify --deep --strict --verbose=2 "dist/CursorToolFree.app"

- name: Create DMG
  run: |
    brew install create-dmg
    create-dmg ... "CursorToolFree-macOS.dmg" "dist/"
```

**自动化流程**：
1. 在Apple Silicon和Intel两个平台分别构建
2. 每个构建自动执行ad-hoc签名
3. 打包成DMG安装包
4. 上传到GitHub Release

---

## 📚 创建的文档

### 1. MACOS_USER_GUIDE.md
**面向最终用户的详细指南**：
- 📥 如何下载和安装
- 🚀 三种打开应用的方法（右键、系统设置、命令行）
- 🔒 安全性说明
- ❓ 常见问题解答
- 🛠️ 自行从源码构建的方法

### 2. README.md更新
**添加macOS特别说明**：
- 🍎 macOS特别说明章节
- 首次打开应用的步骤
- 开发者构建说明
- macOS特性标注（代码签名说明）

### 3. MACOS_SIGNING_SOLUTION.md（本文档）
**技术实现文档**：
- 问题分析
- 解决方案选择
- 技术实现细节
- 使用方法

---

## 🎯 使用方法

### 开发者（本地构建）

```bash
# 在macOS上构建
cd cursor_tool_free
chmod +x build_macos.sh
./build_macos.sh

# 产物：
# - dist/CursorToolFree.app
# - dist/CursorToolFree-macOS.dmg（如果安装了create-dmg）
# - dist/CursorToolFree-macOS.zip（备选）
```

### 用户（使用发布版本）

1. **下载**：从GitHub Releases下载对应芯片的DMG
2. **安装**：打开DMG，拖拽到Applications
3. **首次打开**：右键 → 打开 → 确认
4. **后续使用**：正常双击使用

---

## 🔍 验证签名

用户可以验证应用已签名：

```bash
# 查看签名信息
codesign -dv --verbose=4 /Applications/CursorToolFree.app

# 验证签名有效性
codesign --verify --deep --strict /Applications/CursorToolFree.app

# 检查隔离属性
xattr -l /Applications/CursorToolFree.app
```

---

## 💡 其他方案对比

### 方案A：不签名 ❌
- **成本**：免费
- **用户体验**：很差，需要多个步骤才能打开
- **安全提示**：最严重

### 方案B：Ad-hoc签名 ✅✅✅（已实施）
- **成本**：免费
- **用户体验**：良好，首次右键打开即可
- **安全提示**：中等，可接受

### 方案C：开发者证书签名 ✅✅
- **成本**：99美元/年
- **用户体验**：较好，仍需首次确认
- **安全提示**：较少

### 方案D：开发者证书签名+公证 ✅✅✅
- **成本**：99美元/年 + 配置复杂
- **用户体验**：最佳，可直接打开
- **安全提示**：无

**结论**：对于开源免费项目，**方案B（ad-hoc签名）是最佳选择**。

---

## 🚀 后续优化（可选）

如果未来项目获得赞助或商业化，可以考虑：

1. **购买开发者证书**（$99/年）
   - 更好的用户体验
   - 更专业的形象

2. **公证流程**
   - 需要开发者证书
   - 配置CI/CD自动公证
   - 用户可直接打开，无需确认

3. **App Store分发**
   - 最佳用户体验
   - 需要开发者计划
   - 需通过审核

---

## 📞 问题反馈

如果用户遇到问题：
1. 查看 `MACOS_USER_GUIDE.md`
2. 在GitHub Issues提问
3. 尝试从源码自行构建

---

## ✅ 总结

通过实施ad-hoc签名方案，成功解决了macOS代码签名问题：
- ✅ 零成本（无需开发者账号）
- ✅ 自动化（CI/CD集成）
- ✅ 用户友好（清晰的使用指南）
- ✅ 安全可验证（可检查签名）

用户只需首次右键打开，之后可正常使用。这是开源免费项目的最佳实践！

