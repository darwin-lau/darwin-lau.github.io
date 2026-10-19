# Darwin 的技术笔记

一个以中文技术实践和研究思考为主的个人博客，使用 Astro、AstroPaper 和 Markdown。

目标地址：<https://darwin-lau.github.io/>。

## 本地使用

需要 **Node.js 24 LTS** 和 **pnpm 10**，以仓库记录的版本和锁文件为准。

```sh
pnpm install --frozen-lockfile
pnpm dev
```

开发服务默认地址为 `http://localhost:4321`。完整构建后可预览包含搜索索引的生产版本：

```sh
pnpm build
pnpm test
pnpm preview
```

`pnpm build` 执行内容和类型检查、生成静态页面及 Pagefind 搜索索引；`pnpm test` 检查构建产物中的页面、订阅源、站点地图和草稿隔离。

## 写文章

文章放在 `src/content/posts/`，使用英文短横线文件名，例如 `why-agent-harness.md`。从 [`templates/post.md`](templates/post.md) 复制内容，修改标题、摘要、日期、标签和正文。模板默认 `draft: true`。

具体字段、图片、目录及发布流程见[写作说明](docs/writing.md)。[`layout-sample.md`](src/content/posts/layout-sample.md) 是保留为草稿的排版样例。

**公开仓库中的 Markdown、图片和 Git 历史都可被访问。`draft: true` 只控制网站展示，不提供保密能力。未准备公开的笔记不要提交到公开仓库。**

## GitHub Pages 发布

仓库目标名称为 `darwin-lau.github.io`，默认分支为 `main`。GitHub Pages 的构建来源使用 **GitHub Actions**。

- Pull Request 运行检查和构建，不发布站点。
- 推送到 `main` 或手动触发发布工作流时，检查通过后自动部署。
- 构建或部署失败时，检查 Actions 日志；GitHub Pages 保留上次成功发布的版本。
- 恢复旧内容时，使用 `git revert` 生成回退提交，再通过相同工作流发布。

首次创建远程仓库、推送源码及启用 Pages，需要按当前环境的授权要求确认后操作。本地构建完成不代表站点已经上线。

## 项目约定

- 博客名称：Darwin 的技术笔记；作者：Darwin。
- 全站使用简体中文，日期按 `Asia/Shanghai` 显示。
- 发布后保持文章文件名稳定，避免改变已有链接。
- 文章末尾使用 Giscus 评论，登录 GitHub 后可发表评论；不包含后台、访问统计或自建数据库。

## 评论管理

评论保存在本仓库的 [Discussions / Announcements](https://github.com/darwin-lau/darwin-lau.github.io/discussions/categories/announcements)，可在 GitHub 管理、锁定或删除讨论。新文章会在第一次收到评论或表情反应时自动创建对应讨论。

评论按文章路径关联，修改标题不影响已有评论；发布后更改文件名或路径需要同步迁移讨论。草稿预览不加载评论。

Giscus App 需要安装到本仓库，并保持 Discussions 开启。组件配置位于 `src/components/Comments.astro`；`giscus.json` 将可嵌入评论的来源限定为正式博客和本地预览。评论区接近视口时才加载，跟随站点明暗主题；无法加载时可使用旁边的 GitHub 讨论区链接。

## 上游与许可证

本项目基于 [AstroPaper v6.1.0](https://github.com/satnaing/astro-paper/releases/tag/v6.1.0)。保留了上游的 [MIT 许可证](LICENSE) 与 Sat Naing 的版权声明。
