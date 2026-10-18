# Harness 案例与数据核验

核验日期：2026-10-18。用途：重写第一篇博客，向第二篇提供一个真实的 Agent + Workflow 混合案例。只采用下列一手来源；不把厂商自述写成独立实验证明。

## 可直接采用的判断

1. **固定模型并不意味着固定能力表现。** LangChain 在固定 `gpt-5.2-codex` 的情况下，报告整体 harness 调整使 Terminal-Bench 2.0 得分从 52.8% 变为 66.5%。但调整范围包括提示词、工具、中间件和推理档位，不能写成“仅一条提示词带来 13.7% 提升”，也不是同预算下的单因素实验。
2. **“自建”常常是接通企业已有的生产工具，而非重写模型调用循环。** Stripe Minions 核心基于 Block Goose 的内部 fork；企业自己建设隔离开发环境、上下文装配、工具选择、测试反馈和交付流程。同时仍让工程师使用 Cursor、Claude Code。
3. **自动化系统里依旧存在固定流程，而且是有意保留的。** Stripe Blueprint 将自主写代码/修复 CI 的 Agent 节点，与确定执行的 lint/push 节点混合。它能证明工作流仍有工程价值；不能据此证明 Dify/Coze 的可视化画布必然有商业价值。

以上是作者可作出的推断；下文分开记录来源事实。

## 案例一：LangChain 固定模型，修改整体 harness

### 来源与读取范围

- 标题：Improving Deep Agents with harness engineering
- 作者：Vivek Trivedy，LangChain
- 发布时间：2026-02-17
- URL：<https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering>
- 实际读取：官方全文的实验设置、trace 分析、四类改动、推理配置和局限相关段落。
- 公开 traces 链接：<https://smith.langchain.com/public/29393299-8f31-48bb-a949-5a1f5968a744/d?tab=2>。本文核验未对公开 traces 逐条复算，不应宣称复现实验。

### 短摘录

> We only tweaked the harness and kept the model fixed, `gpt-5.2-codex`.

### 图表原始数值

建议主图仅使用下表两柱。纵轴从 0 起，单位为百分比；差值写“13.7 个百分点”。

| 条目 | 模型 | 基准 | 官方报告得分 |
| --- | --- | --- | ---: |
| 默认 harness | gpt-5.2-codex | Terminal-Bench 2.0 | 52.8% |
| 调整后 harness | gpt-5.2-codex | Terminal-Bench 2.0 | 66.5% |

可另用一张小表解释推理预算的反直觉结果，但不要把它与上表拼成连续的四阶段增长曲线：

| 推理设置 | 官方报告得分 | 官方解释 |
| --- | ---: | --- |
| 全程 xhigh | 53.9% | 更多超时 |
| high | 63.6% | 相比全程 xhigh 更好 |
| xhigh-high-xhigh | 66.5% | 规划和验证阶段更多推理，执行阶段 high |

计算得到：`66.5 - 52.8 = 13.7` 个百分点。若写相对增幅约 25.9% 容易引发混淆，没有必要采用。

### 具体改动：案例可以写进故事的细节

- 默认常见失败模式是：模型写完代码，自己再读一遍，认为没有问题，然后结束；缺少真正测试。
- 系统提示要求经历计划/实现/验证/修复；验证须运行测试、读完整输出、按任务要求验收。
- `PreCompletionChecklistMiddleware` 在模型准备结束时拦截并提醒它按任务规格自检。这不是再加一个聊天界面，而是修改“什么时候可以停工”。
- `LocalContextMiddleware` 在启动时勘查工作目录、父子目录与 Python 等工具，主动注入环境信息，减少模型自己搜索环境时出错。
- 注入剩余时间提示，促使模型给验证留时间。
- `LoopDetectionMiddleware` 记录同一文件的编辑次数，达到阈值后提示重新考虑方案；原文的坏循环 traces 中，同一路径可反复尝试 10 次以上。
- 团队分析 LangSmith traces，归纳失败原因后再修改 harness；不是凭审美堆 middleware。

### 可比性、定义与限制

- 模型固定，但推理档位并非固定；**不能写“同样的推理预算、环境、工具，纯提示词优化”**。
- 使用 Harbor 编排、Daytona 沙箱，记录 LangSmith traces。官方把这些作为统一实验设置介绍，但没有逐次运行的完整配置清单，不能额外保证硬件/时间预算/依赖版本逐项一致。
- 指标是 Terminal-Bench 2.0 的任务完成得分/通过率，不是企业真实业务收入、节省工时，也不是所有软件开发任务的成功率。
- 官方正文未披露这组 52.8%/66.5% 实验各自重复次数、置信区间、逐项消融贡献以及总成本。公开 traces 的存在不等于本文已经复算。
- 团队根据基准失败 traces 迭代并在同一基准上报告结果；没有独立留出集效果。作者自己也提醒任务过拟合会伤害泛化。
- “Top 30 → Top 5”是发布时间附近的历史表述，最好不作为本文主数据。当前 Terminal-Bench 首页已是 4.0，不能用今天的主页排名回证历史。
- 不采用文中 Claude Opus 4.6 的 59.6% 来跨模型排名：原文说明它用的是较早 harness，且未针对 Claude 做相同优化。

推荐图注：

> LangChain 2026-02-17 报告的厂商自测。模型固定为 gpt-5.2-codex；整体调整含提示词、中间件及推理配置。正文未给出重复次数与置信区间，不能将差值归因于某一项改动。

## 口径佐证：Terminal-Bench 2.0 原始论文

- 标题：Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces
- 发布日期：2026-01-17，arXiv v1
- URL：<https://arxiv.org/html/2601.11868v1>
- 实际读取：摘要、任务定义、数据集构造、实验设置以及有关 agent/model 不易解耦的段落。
- 89 个任务；每个任务含容器环境、任务说明、验证测试、参考解和时限。任务涉及机器学习、系统配置、调试等终端操作，并非纯函数代码生成测验。
- **这份论文自己**对兼容的 model-agent 组合至少运行五次；**不能把这个次数移植给 LangChain 后来的博客实验**。
- 论文也直接指出：模型与 Agent 的表现很难分离，scaffold 往往针对某些模型特点工程化。

## 案例二：Stripe Minions，复用 Goose，改造交付链

### 来源与读取范围

1. Alistair Gray，Minions: Stripe’s one-shot, end-to-end coding agents，2026-02-09。
   <https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents>
2. Alistair Gray，Minions: Stripe’s one-shot, end-to-end coding agents—Part 2，2026-02-19。
   <https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2>

实际读取：两篇文章正文全文，包括自建原因、工单/Slack 使用场景、Goose、devbox、Blueprint、MCP、规则文件和 CI 反馈限制。

### 短摘录

Part 1：

> The core agent loop runs on a fork of Block’s coding agent goose.

Part 2：

> Blueprints are workflows defined in code that direct a minion run.

### 有来源的具体场景

Stripe 的 CI 检测 flaky tests 后，创建工单；工单界面内有启动 Minion 的按钮。工程师也可从讨论问题的 Slack 线程直接启动，Agent 获取线程及链接上下文。完成后产出通过 CI、等待人工评审的 PR。这里有可讲述的工作场景，而无需编造某个失败测试的名字或修复细节。

### 企业到底做了什么

- **执行内核**：2024 年末内部 fork Block Goose，接 Stripe 的 LLM 基础设施，后续聚焦无人值守任务，而非人类陪跑工具；Cursor 和 Claude Code 仍供应工程师使用。不能写成从零造一个比 Claude Code 更聪明的 Agent。
- **熟悉的工作台**：复用人类工程师已有的 AWS EC2 devbox。提前克隆大仓、预热 Bazel/type-check 缓存、启动代码生成服务，目标约 10 秒即可领取可工作环境。不是每次 Agent 到来才从空容器安装仓库。
- **限定损害范围**：devbox 在 QA 环境，与生产服务、真实用户数据、任意网络外连隔离；另有工具安全控制。原文说因此不必逐动作向人请示；不能扩大解释为一切 Agent 可直接取消权限控制。
- **按需给知识**：几乎不用全局无条件规则，按子目录和文件模式装载；共享规则适配 Minions、Cursor、Claude Code，避免三份规则分叉。
- **按需给工具**：Toolshed 集中管理 MCP 工具，Agent 各拿精选子集；Part 1 说超过 400 个工具，Part 2 说近 500 个。这是工具库总规模，不是每次把近 500 个全部塞给模型。
- **不让模型决定每一个动作**：Blueprint 用 Agent 节点处理 `Implement task`、`Fix CI failures`；用确定代码节点运行 lint、push 等。可预测且必须执行的动作直接写成代码。
- **反馈尽量提前**：本地先自动 lint/修复，远端 CI 再运行相关测试。超过 300 万是 Stripe 总测试库规模，不是每个 PR 跑 300 万条。
- **停止条件写进系统**：初次 push 触发 CI；自动修复可修的失败；其余失败交 Agent 一次修正机会。第二次 push/CI 后无论结果如何交还人类，避免无限试错烧 token、算力和时间。

### 可使用的数字，以及不能推导什么

| 数字 | 日期/来源 | 严格定义 | 不应推导 |
| --- | --- | --- | --- |
| 每周超过 1,000 个 PR | Part 1，2026-02-09 | 已合并；全部代码由 Minion 产出，人类评审 | 任务成功率、人均增产比例、工时节省 |
| 每周超过 1,300 个 PR | Part 2，2026-02-19 | 同上；是发表时的自报运行量 | “两周增长 30%”的严格时间序列；前后均是约数/下界 |
| 约 10 秒 | 两篇均涉及 | 预热 devbox 可用目标/体验 | 端到端任务完成时长、PR 产出时长 |
| 最多 2 轮 CI | 两篇均涉及 | 标准 Minion 流程里的预算/停止策略 | 两次必成功、成功率达到某个百分比 |
| 超过 300 万个测试 | 两篇均涉及 | Stripe 既有总测试库 | 每项任务都运行全部测试 |
| 近 500 个 MCP 工具 | Part 2 | Toolshed 中央工具库总量 | 单 Agent 默认暴露所有工具 |

没有总启动任务数、失败分布、任务难度分布、成本、工时对照组、合并后缺陷率，因此不要把 PR 数画成“自建胜过购买”的效能柱状图。

### 最合适的图

按官方文字重绘简化链路，图题明确“依据 Stripe 官方描述绘制”，无需复制官方插图：

```text
讨论线程 / flaky-test 工单
          ↓
预热且隔离的 devbox + 相关规则/上下文
          ↓
Agent 实现任务（Goose fork）
          ↓
确定代码：本地 lint / 修复 → push → CI
          ↓
CI 失败：自动修复；必要时 Agent 再修一次
          ↓
第二轮 CI 后交人类评审
```

图中要表现 Agent 决策节点与固定代码节点的区别，但不要自行添加自动合并、生产发布或无限重试。

## 可写成正文的切口（作者表达建议，并非来源引文）

- 从一张 flaky-test 工单切入：“修复失败测试”四个字看似把工作说明白了；在大公司，拿到哪个环境、读取哪些规则、该运行哪些测试、什么时候停止重试，同样决定这张工单能否交付。
- 把 LangChain 中“重读代码就认定做完”这个细节放在数据前，读者能立即理解为什么退出前验收比再堆一个功能更值钱。
- 锐利但证据足够的判断：“自建的理由，应当是你已经找到了哪一步卡住交付；公司足够大、工具不够自主，都不是理由。”这是作者判断，不能写成 Stripe 的结论。
- 如果使用类比，最多保留一个，随后立刻落回真实系统。更推荐真实工单链路，避免“发动机与汽车”“厨师与厨房”之类常见包装。

## 未做的事与材料边界

没有复现 LangChain 实验，没有统计公开 traces，没有审计 Stripe 私有实现，没有把博客披露外推为产品横评。仅研究这些有力案例，未为凑数量继续铺产品说明书。
