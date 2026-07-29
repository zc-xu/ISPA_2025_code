# How We Can Edit the Overleaf Manuscript

## 当前状态

我目前不能直接操作你截图里的 Overleaf 窗口。Codex 可控的浏览器标签页现在是空白页，不是你的 Overleaf 页面。本地工作区也没有 `.tex`/`.bib` 源文件，所以我无法直接给原稿打补丁。

## 最稳的方式：下载 Overleaf 源码给我

在 Overleaf 中：

1. 点击左上角 `Menu`。
2. 选择 `Download Source`。
3. 把下载得到的 `.zip` 放到 `D:\EdgeComputing_journal`，或直接拖进 Codex 对话。
4. 我解压后会直接修改 `.tex`、`.bib`，并保留一个带修订标记的版本。

优点：最稳定，适合大段 LaTeX 修改、全文变量替换、表格和 caption 修改。

## 可选方式：Overleaf Git

如果你的 Overleaf 项目支持 Git：

1. 在 Overleaf 菜单中找到 Git URL。
2. 把 Git URL 发给我。
3. 我可以 clone 到本地、修改、编译检查，再由你决定是否 push。

注意：如果 Git URL 需要账号密码或 token，不要直接把密码发给我。可以用 Overleaf 提供的只读/可写 Git 链接，或你本地先 clone 后把文件放进工作区。

## 可选方式：在可控浏览器里打开 Overleaf

如果你希望我直接在网页里操作：

1. 需要把 Overleaf 项目打开在 Codex 的可控浏览器里，而不是你截图中的普通浏览器窗口。
2. 我可以帮你点击、查找、粘贴文本。
3. 这种方式不适合大规模修改，因为网页编辑器容易发生定位错误、滚动丢失、自动保存冲突。

## 修改标记

编辑部要求修改处要标记。LaTeX 中推荐加：

```tex
\usepackage[normalem]{ulem}
\usepackage{xcolor}
\newcommand{\rev}[1]{\textcolor{blue}{\uline{#1}}}
\newcommand{\del}[1]{\textcolor{red}{\sout{#1}}}
```

新增或重大修改内容用：

```tex
\rev{new or revised text}
```

删除内容用：

```tex
\del{deleted text}
```
