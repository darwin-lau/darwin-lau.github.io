---
title: "Markdown 排版样例"
description: "用于本地核对中文标题、目录、代码、表格、图片与链接的草稿样例。"
pubDatetime: 2026-10-18T09:00:00+08:00
author: Darwin
tags:
  - 排版样例
draft: true
timezone: Asia/Shanghai
---

这是一份排版样例，用于检查阅读体验，不包含个人经历或正式研究结论。

验证标记：`BLOG_DRAFT_SAMPLE_2026`。

## 目录

## 中文正文与标题

好的技术文章应让读者看清问题、依据与结论。正文支持**加粗**、*强调*、`行内代码`，以及指向[关于页面](/about/)的站内链接。

### 子主题：阅读顺序

先说明问题，再展示证据，最后写出结论与限制。段落宜围绕一个主题展开。

#### 更细的层次

只有内容确实需要分层时才继续增加标题。下面这段引用用于核对中文标点与留白：

> 示例中的“成功”只是一个字符串。真实系统的完成条件需要明确、可验证。

## 代码与长行

```typescript
const note = { title: "技术笔记", draft: true };
console.log(note.title);
```

下面故意保留一行较长代码，用于检查窄屏横向滚动：

```typescript
const longLineForHorizontalScroll = "这是一条用于检查移动端代码滚动的长行；保留完整内容，以便确认代码不会挤压正文，也不会让整个页面产生横向滚动。This line continues with enough characters to make horizontal scrolling necessary on a narrow screen.";
```

## 表格与列表

| 内容 | 用途 | 检查重点 |
| --- | --- | --- |
| 标题 | 标识章节 | 层次与目录跳转 |
| 代码 | 说明实现 | 高亮与长行滚动 |
| 图片 | 辅助理解 | 清晰度、替代文本与手机宽度 |

写作前可以依次确认：

1. 问题是否具体。
2. 例子是否可理解。
3. 结论是否有依据。

## 图片与链接

![三个依次排列的方框，分别标注问题、证据、结论，并由箭头连接](@/assets/images/layout-sample.svg)

这张本地 SVG 用于测试资源路径和图片布局。外部链接示例：[Markdown 基础语法](https://www.markdownguide.org/basic-syntax/)。

## 检查结束

在手机宽度下确认目录可展开、标题可跳转、图片不越界，长代码块可以单独横向滚动。该文件保持草稿状态，不应出现在生产站点及搜索结果中。
