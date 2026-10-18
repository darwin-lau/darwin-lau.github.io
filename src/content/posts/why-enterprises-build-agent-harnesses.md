---
title: "现成 Agent 已经很好用，企业为什么还要自建 Harness？"
description: "Stripe 复用 Goose，却自己建设 Minions；LangChain 不换模型，改 Harness 就改变了基准表现。企业真正该自己做的是什么？"
pubDatetime: 2026-10-18T17:48:00+08:00
modDatetime: 2026-10-18T22:47:32+08:00
author: Darwin
tags:
  - Agent
  - 工程实践
  - 技术选型
draft: false
timezone: Asia/Shanghai
---

Stripe 的 CI 发现不稳定测试后，会自动开工单。工单里有一个按钮，可以启动 Minion 去修；工程师也能从讨论问题的 Slack 线程发起任务。它读取上下文、修改代码，目标是交回一份通过 CI、可供人审的 PR，过程不需要有人守着终端。[^stripe-start]

这家公司已经给工程师提供了 Cursor 和 Claude Code，却又做了一套自己的编码 Agent。为什么？是现成工具不够聪明，还是公司大了就总想造点轮子？

把 Minions 拆开看，会发现“自建 Harness”这个说法，掩盖了不少真正值得花钱的工作。

## Stripe 在修一条交付链

Minions 的核心来自 Block 的 Goose。Stripe 在 2024 年底 fork 了它，接入自己的基础设施，逐渐向无人值守的任务倾斜。它没有先从零实现一遍所有通用能力。[^stripe-build]

外围的安排更有意思：任务领到的是预热好的隔离开发环境，代码和缓存已经准备妥当；写完代码必须经过 lint、push 和 CI，这些步骤由程序执行；首轮 CI 失败，可以自动修复或让 Agent 再改一次，第二轮之后就交人处理。[^stripe-build]

![Stripe Minions 简化交付链：工单进入隔离环境，由 Agent 实现任务，再执行确定的 lint、push 和 CI；通过则交人审查，失败最多再修正并运行一轮 CI](@/assets/images/stripe-minions-flow.svg)

_图 1：根据 Stripe 官方描述重绘，省略部分实现细节。绿色节点允许 Agent 自主处理，固定检查由代码执行；图中没有自动合并或生产发布。_

这很像给一个新同事办入职。人招到了，电脑、仓库权限、开发环境、测试命令和交付方式仍然得有人安排。招到高手，也不会因此取消 CI。模型会写代码，和它能在这家公司交付代码，中间隔着这一整套工作条件。

这里“最多两轮 CI”尤其值得琢磨。Agent 会继续尝试，恰恰意味着系统得决定何时停止：继续修可能成功，也可能只是在消耗时间和算力。把这个决定留给一个无限循环，不能叫自动化做得彻底。

到 2026 年 2 月 19 日，Stripe 自报每周已有超过 **1,300 个合并 PR** 完全由 Minions 产出代码，仍由人类评审。[^stripe-build] 这是运行规模，既不是成功率，也不能换算成省了多少工程师。它至少让“企业为什么还要做一层自己的东西”有了一个具体答案：把已有的工程体系接到无人值守任务上。

如果照着这个案例立项，我会先看工单怎样进来、修改怎样验收、失败怎样交回人手。至于最后的成果要不要叫“自研 Harness”，倒没那么要紧。

## 同一个模型，差了 13.7 个百分点

当然，执行内核也不是永远不用碰。LangChain 的一次实验把这个问题说得很具体。

他们在运行记录里发现一种常见失败：模型写完代码，再读一遍自己的代码，觉得没问题，就结束了。看起来完成了，测试却没有真正跑过。团队随后调整提示词、工具和中间件，在退出前提醒验收，并把环境与时间约束主动送进上下文。[^langchain]

固定使用 GPT-5.2-Codex，Terminal-Bench 2.0 的报告得分从 **52.8% 变成 66.5%**，相差 13.7 个百分点。[^langchain]

![LangChain 自测：固定 GPT-5.2-Codex，整体 Harness 调整前后 Terminal-Bench 2.0 得分由 52.8% 到 66.5%，差 13.7 个百分点；调整包含推理配置](@/assets/images/harness-benchmark.svg)

_图 2：LangChain 2026 年 2 月 17 日公布的自测。TB2.0 有 89 项任务；改动含推理配置，不是同预算单因素实验。原文未披露这组结果的重复次数与置信区间。_

还有个反直觉的细节：全程开最高推理档 `xhigh`，得分是 53.9%；用 `high` 则是 63.6%。原文给出的原因是超时。[^langchain] 有截止时间的工作，不能只追求每一步想得更久，还得给执行和验证留时间。

这组结果说明，模型的能力并不会自动、完整地兑现成任务结果。可它对自建项目提出的要求也更高了：你得像这样知道失败发生在哪里，再改系统，而不是看见有十几个可调参数，就逐个拧一遍。

“模型没有验收就停了”是一条能复现的失败；“我们需要一个更企业级的 Agent 平台”还不是。

## 先看你究竟缺哪一块

回到 Claude Code、Codex、Pi。今天它们已有 SDK、工具权限、hooks 或扩展接口，可以让企业接入自己的工具和运行逻辑。[^runtimes] Stripe 在 2024 年选择 fork 的经历，不能直接替 2026 年的团队证明：现成接口仍然不够用。

我倾向于先复用，原因很实际。假如任务卡在读不到工单、找不到项目的测试命令，重写模型循环并不会让那两个接口自己长出来。先把数据、环境和验收接好，才能看见下一层问题。

也有相反的情况。设想一个只做依赖升级的服务：读版本、修改锁文件、跑固定测试、提 PR，状态和停止条件都很窄。为了嵌入一个通用交互式 Agent，反而要持续适配它的会话、资源加载和升级行为。此时维护一个小循环，可能比维护一层层补丁更省事。这个例子是设计取舍，不是我测出的成本结论。

对于复杂任务，如果上下文压缩总丢掉关键状态、恢复逻辑无法表达业务要求，每次升级又要重打补丁，改内核也完全合理。只是那笔账要包含后续的回归和维护，不能只算第一版跑通用了几天。

我支持企业掌握自己的任务标准、工具契约和失败记录。它们会告诉你什么时候值得改 Harness，也会告诉你哪些“自研能力”其实可以删掉。没有这些东西，拥有源码也可能只是拥有了更多待维护代码。

Stripe 值得学的地方，是它把一张工单送到人工评审之前的路修得很细。自建项目最好从这条路上一个具体的堵点开始，而不是从一份 Agent 平台功能清单开始。

## 来源

资料核对日期：2026 年 10 月 18 日。图表按公开原值重绘；本文没有复现实验或审计 Stripe 的私有实现。

[^stripe-start]: Alistair Gray，[Minions: Stripe’s one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)，2026-02-09。提供工单、Slack 入口及交付方式。

[^stripe-build]: Alistair Gray，[Minions, Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)，2026-02-19。提供 Goose fork、开发环境、Blueprint、CI 预算与每周合并 PR 的口径。

[^langchain]: Vivek Trivedy，[Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)，2026-02-17。得分为框架团队自测，多个环节同时调整，未按单项改动归因。

[^runtimes]: [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)、[Codex SDK](https://developers.openai.com/codex/sdk)、[Pi coding-agent](https://github.com/earendil-works/pi/tree/main/packages/coding-agent)。这些是可复用和扩展的入口，不是所有产品形态、权限和部署条件完全相同的承诺。
