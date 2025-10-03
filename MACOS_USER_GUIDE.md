# 🍎 macOS用户使用指南

## 📥 下载应用

从GitHub Releases页面下载：
- `CursorToolFree-macOS.dmg` （推荐，标准安装包）
- `CursorToolFree-macOS.zip` （备选，解压即用）

## 🚀 首次打开应用

### ⚠️ 为什么会提示"无法打开"？

从macOS 10.15开始，Apple要求所有应用都需要经过公证。由于本应用是开源免费项目，未购买Apple开发者证书（99美元/年），因此使用了**ad-hoc自签名**。

这不影响应用安全性，只需要简单的步骤即可使用。

---

## ✅ 解决方法（三选一）

### 🌟 方法1：右键打开（推荐，最简单）

1. **找到应用**：双击打开`.dmg`文件（或解压`.zip`）
2. **拖拽到应用程序**：将`CursorToolFree.app`拖到`Applications`文件夹
3. **右键打开**：
   - 在`Applications`文件夹中找到`CursorToolFree.app`
   - **右键点击** → 选择**"打开"**
   - 在弹出对话框中点击**"打开"**按钮

4. **完成**：之后可以正常双击使用

![右键打开](https://support.apple.com/library/content/dam/edam/applecare/images/zh_CN/macos/Big-Sur/macos-big-sur-control-click-open.jpg)

---

### 🔧 方法2：系统设置（如果方法1不行）

1. **尝试打开**：双击应用（会提示无法打开）
2. **打开系统设置**：
   ```
   系统偏好设置 → 安全性与隐私 → 通用
   ```
3. **点击"仍要打开"**：在底部会看到被阻止的应用提示
4. **确认打开**：点击"打开"按钮

---

### 💻 方法3：命令行（适合高级用户）

打开终端（Terminal），执行：

```bash
# 移除隔离属性
xattr -d com.apple.quarantine /Applications/CursorToolFree.app

# 或者如果应用在其他位置
xattr -d com.apple.quarantine ~/Downloads/CursorToolFree.app
```

之后可以正常双击打开。

---

## 🔒 安全性说明

### ✅ 应用是安全的

- **开源代码**：所有代码可在GitHub查看
- **本地运行**：数据存储在本地，不上传到任何服务器
- **社区验证**：可以自行审查源码或从源码构建
- **Ad-hoc签名**：已签名，只是未经Apple公证

### 🛡️ 如何验证签名

打开终端，运行：

```bash
# 检查签名状态
codesign -dv --verbose=4 /Applications/CursorToolFree.app

# 验证签名
codesign --verify --deep --strict /Applications/CursorToolFree.app
```

你会看到应用已签名（ad-hoc），只是没有开发者证书。

---

## ❓ 常见问题

### Q1: 为什么不购买开发者证书？

A: Apple开发者证书需要99美元/年。本项目是完全免费开源，ad-hoc签名已经能满足使用需求。

### Q2: 以后每次打开都要右键吗？

A: 不需要。**只有首次打开需要右键确认**，之后可以正常双击使用。

### Q3: 能不能让应用不提示？

A: 可以通过方法3的命令行移除隔离属性，或者使用系统设置允许"任何来源"的应用（不推荐，会降低系统安全性）。

### Q4: 应用会不会有病毒？

A: 
- 项目完全开源，代码透明
- 可以在GitHub查看所有源代码
- 可以自行从源码构建应用
- 使用杀毒软件扫描也不会有问题

### Q5: 下载后显示"已损坏"怎么办？

A: 这是macOS的隔离机制，使用方法3的命令行即可：

```bash
xattr -d com.apple.quarantine /Applications/CursorToolFree.app
```

---

## 🛠️ 自行构建（100%安全）

如果你不放心预编译版本，可以自己从源码构建：

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/cursor_tool_free.git
cd cursor_tool_free

# 2. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 3. 构建应用（自动签名）
chmod +x build_macos.sh
./build_macos.sh

# 4. 应用在 dist/CursorToolFree.app
```

这样构建的应用100%安全，因为是你自己编译的。

---

## 📞 需要帮助？

- **GitHub Issues**: 在项目页面提交问题
- **查看源码**: 所有代码都在GitHub上公开
- **社区讨论**: 加入讨论了解更多

---

## 🎉 享受使用

完成上述任一方法后，您就可以正常使用CursorToolFree了！

**记住：只有首次打开需要确认，之后就和其他应用一样使用！**

