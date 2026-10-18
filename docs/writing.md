# 写作说明

## 新建文章

在 `src/content/posts/` 新建普通 `.md` 文件，复制 `templates/post.md` 的内容。文件名使用小写英文和短横线，如 `why-agent-harness.md`，对应地址为 `/posts/why-agent-harness`。

发布后不要随意重命名文件。修改中文标题不会改变文件对应的文章地址。

```yaml
---
title: "文章标题"
description: "用一两句话说明文章讨论的问题。"
pubDatetime: 2026-10-18T09:00:00+08:00
author: Darwin
tags:
  - 技术
draft: true
timezone: Asia/Shanghai
---
```

必填字段为 `title`、`description` 和 `pubDatetime`。`author` 和 `timezone` 通常保持模板值即可。日期使用包含时区偏移的 ISO 8601 格式，例如 `+08:00`。

需要记录实质性修订时，可增加 `modDatetime: 2026-10-19T09:00:00+08:00`。不要把编辑器自动保存时间当作文章修订时间。

## 正文排版

标题由页面自动显示，正文从 `##` 二级标题开始。用 `###` 表达子主题，尽量保持清晰的层次。

需要可折叠目录时，在正文前部单独写一行：

```markdown
## 目录
```

构建会根据后续标题生成目录，不需要手工维护链接。保留的上游写法 `## Table of contents` 也可使用。

代码围栏指定语言，例如 `typescript`、`bash` 或 `json`。长代码行支持横向滚动。普通 Markdown 表格、列表、引用和链接可直接使用。

图片统一放在 `src/assets/images/`，使用资源别名引用：

```markdown
![描述图片内容，帮助无法看到图片的读者理解](@/assets/images/layout-sample.svg)
```

使用清晰的替代文本，不把正文中的关键信息只放在图片里。引用外部资料时附上来源链接；图片优先使用仓库中的本地资源。

完整排版示例见 `src/content/posts/layout-sample.md`。它始终以 `draft: true` 保存，包含固定验证标记 `BLOG_DRAFT_SAMPLE_2026`，不会作为正式文章发布。

## 草稿与预览

`draft: true` 的文章不进入生产页面、搜索、RSS 和 sitemap。`pnpm dev` 会显示草稿，方便本地写作；`pnpm preview` 展示生产构建结果，草稿在其中不可见。

预览草稿时直接运行 `pnpm dev`，浏览对应文章地址，例如排版样例的 `/posts/layout-sample`。准备正式发布时才把该文章改为 `draft: false`；排版样例始终保持草稿状态。

`pnpm dev` 不保证已有最新搜索索引。验证搜索时先运行 `pnpm build`，再运行 `pnpm preview`。预览服务通常位于 `http://localhost:4321`。

## 发布检查

1. 核对标题、摘要、日期、标签、图片替代文本和引用链接。
2. 准备发布的文章设置 `draft: false`，确认 `pubDatetime` 不晚于当前时间；未来日期文章需到期后重新构建才能显示。
3. 执行 `pnpm build` 和 `pnpm test`，再用 `pnpm preview` 检查手机宽度、代码滚动、目录和搜索。
4. 核对 Git 差异，确认没有密钥、内部资料或不希望公开的草稿内容。
5. 提交并推送到 `main`，在 GitHub Actions 查看构建和部署结果；使用 Pull Request 时先完成构建检查，再合并到 `main`。
6. 发布后打开目标文章，确认链接、图片、搜索及订阅内容正常。

**草稿标记不隐藏公开仓库里的源码、附件或 Git 历史。未公开笔记应保留在仓库之外；删掉当前文件也不会自动删除过去提交中的内容。**

草稿引用的图片也可能被构建到静态资源中；草稿机制不适合保存任何需要保密的内容。
