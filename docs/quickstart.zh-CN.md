# 中文上手指南

这套框架来自现有课件的通用部分：Python 负责把 Markdown、图片、字体和主题打包，Remark.js 负责在浏览器中放映。白底、Droid Serif、Inconsolata、留白、右上角页码和双栏图解保持原来的设计语言。

## 先运行示例

需要 Python 3.10 或更新版本。HTML 构建不用安装 pip 或 npm 依赖。

```bash
git clone https://github.com/Sky-Right/technical-slide-kit.git
cd technical-slide-kit
python3 build.py
```

双击 `dist/index.html` 即可播放，不需要联网。想通过本地网址预览：

```bash
python3 -m http.server 8000 --directory dist
```

打开 http://localhost:8000/。Windows 可以把命令中的 `python3` 换成 `py`。

## 写自己的内容

在 GitHub 点击 **Use this template** 创建自己的项目，或复制到一个新目录。用 VS Code 修改 `content/slides.md`。如果想从干净的三页模板开始：

```bash
python3 build.py content/starter.md --out dist/my-talk.html --title "我的技术分享" --lang zh-CN
```

每页用 `---` 分隔；标题用 `#`；`???` 后面写讲者备注；用 `--` 做同一页的分步展示。完整语法见 [authoring.md](authoring.md)。

常用双栏：

```markdown
class: command

# 这一条命令做了什么

.left[
这里放命令和少量说明。
]

.right[
![状态变化图](../assets/architecture.svg)
]

???

这里写你上课时要讲的话和演示步骤。
```

图片放在 `assets/`，相对于 Markdown 写路径。框架附带可编辑的 SVG 流程图和架构图，可以换成自己的图。截图也可以放进去，但只截与讲解有关的区域。

## 改风格和 Logo

优先在 `theme/custom.css` 改强调色等小细节。保留字号和间距，可以让不同课程保持统一。

默认没有任何组织 Logo。需要右下角 Logo 时，把有权使用的文件放进 `assets/`，再执行：

```bash
python3 build.py --logo assets/example-logo.svg
```

这里用的是占位 Logo，换成自己的文件即可。原课件的组织 Logo 和真实截图没有放入开源框架。中文默认使用系统字体回退；如果需要每台机器完全一致，可按 [customization.md](customization.md) 加入有适当许可的本地中文字体。

## 放映、打印和发布

- 方向键翻页，`P` 打开讲者模式，`C` 打开第二显示窗口，`F` 全屏，`?` 查看帮助。
- 浏览器打印时选择保存为 PDF，并开启背景图形。每页只打印最终展开状态，不会把每个渐进步骤都重复打印。
- 框架主要生成 HTML；浏览器导出的是 PDF，不是可编辑的 PowerPoint 文件。
- 自己的 GitHub 仓库在 Settings → Pages 中选择 GitHub Actions。之后推送 `main`，现成的工作流会测试、构建并发布 `dist/`。
- 每次改完源文件都重新运行构建；不要直接改生成的 HTML。

讲者备注也在最终 HTML 内，发布前一起检查。不要把个人工作目录、账号凭据或无关文件复制进新项目。

## 来源

Git 入门课程仍在原来的独立仓库中。这里只保留通用框架、示例、说明、必要依赖和许可证，没有复制整套课程或其他项目的历史。

项目代码、模板和新示例采用 Apache-2.0；保留了 container.training 的来源说明、Remark.js 的 MIT 许可和字体各自的许可。复制框架时一并保留 `LICENSE`、`NOTICE` 和第三方许可文件。
