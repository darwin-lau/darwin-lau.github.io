# 企业为什么还要自建 Agent Harness：一手调研记录

调研日期：2026-10-18。用途：支持公开博客观点与事实核查，不是产品采购推荐。仅访问公开资料；未上传任何本地、公司或用户文件。原始公开页面缓存未提交，未修改配置。

## 结论先行

**我的判断：多数企业应先复用现成执行内核；拥有业务 Agent 系统，不等于重写 Agent 循环。** 企业真正需要决定和控制的是任务边界、业务授权、工具契约、验收标准、运行责任。它们可以通过现成产品、SDK、扩展点及既有业务基础设施实现；不能把这些需求的存在直接当成自建通用 Harness 的证据。

这不是“厂商只有玩具，企业才有安全”的论证。Claude Agent SDK 已提供 Claude Code 同源的工具、循环和上下文管理，以及 permissions、hooks、sessions、MCP；Codex 有 SDK、App Server、操作系统沙箱与管理员强制配置；Pi 明确以小核心、扩展和 SDK 为定位。[S1–S12]

**也不能反过来说永远不必自建。** 极窄、稳定、工具很少的任务可能用专用小循环更合算；现成实现无法经济地表达的上下文策略、持久化、执行调度、故障恢复或部署条件，也可能形成自建理由。但需通过真实任务对比证明，不能以“可控”“自主”“模型无关”代替约束说明。

## 先纠正几个容易偷换的概念

1. **模型 API 客户端 ≠ Agent Harness。** 调模型只完成推理的一环。Harness 还涉及输入/上下文组织、工具调用和反馈、会话状态、继续和结束条件。Anthropic 的评测文章直接把 agent harness 定义为处理输入、编排工具调用、返回结果的系统；评测的是模型与 Harness 的组合。[S14]
2. **接内网 API、加企业入口、配置 hooks ≠ 重写 Harness 内核。** 这通常是扩展或集成现成 Harness。不要为了证明“企业需要自研”而把所有适配工作都改叫自研内核。
3. **自有业务标准 ≠ 每个基础设施组件必须自己写。** 企业必须定义验收和负责运行结果，但评测框架、日志平台、任务队列、工作流基础设施可以复用或采购。
4. **开发者终端体验 ≠ 所有产品形态的能力上限。** Claude、Codex、Pi 都有程序化嵌入入口，不应只拿 CLI 与企业平台比较。[S1、S5、S6、S10、S12]
5. **有权限、沙箱、hooks ≠ 已自动符合某家企业的全部业务制度。** 现成运行机制可以表达和执行规则；“某人在某窗口能否重启某服务”还需真实身份、资源归属和服务端授权。该语义必须由业务系统提供，不应让提示词承担授权。

## 一手事实与原文证据

以下摘录均来自实际抓取并阅读的页面正文，不以搜索摘要代替。文档是取阅时的当前版本，产品能力与支持范围会变化。

### S1. Claude Agent SDK：复用 Claude Code 的执行核心

- 来源：[Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)，原平台入口 `https://platform.claude.com/docs/en/agent-sdk/overview` 当前指向此文档。
- 官方原文：
  > “The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.”
- 对比表还写：
  > “A library that runs the Claude Code binary, with Claude Code’s capabilities, such as built-in tools, permissions, sessions, and hooks.”
- 文档能力表列出 built-in tools、hooks、subagents、MCP、permissions、sessions、skills/commands/memory、plugins。
- 可支持的事实：企业能在自己运营的 Python/TypeScript 应用中复用 Claude Code 的能力，不必先重写工具循环。
- 不支持的推论：SDK 自动提供完整企业租户管理、业务授权或保证任务成功。
- 授权边界：文档同时说未经事先批准，不允许第三方在自家产品里提供 claude.ai 登录或订阅限额，指向 API key 认证与商业条款。技术能嵌入与可用授权是两件事，不宜把个人订阅直接视作可任意转售的运行配额。

### S2. Claude SDK permissions：规则、模式、运行时决定已存在

- 来源：[Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)。
- 官方原文：
  > “The Claude Agent SDK provides permission controls to manage how Claude uses tools.”
  > “Use permission modes and rules to define what’s allowed automatically, and the canUseTool callback to handle everything else at runtime.”
- 关键细节：权限按 hooks、deny、ask、permission mode、allow、canUseTool 顺序评估；并非所有工具调用都会经过 `canUseTool`。文档明确：
  > “Auto-approved tools never reach canUseTool.”
- 对必须覆盖所有工具调用的校验，文档建议 `PreToolUse` hook。
- 可支持的事实：不能声称 Claude SDK “没有权限控制”；同时，随意放一个 callback 并不代表校验覆盖完整执行路径。
- 本文不建议照抄具体配置：规则、模式及支持版本变化较快，企业部署需核对实际版本和所有通道。

### S3. Claude SDK hooks：拦截、审计、改输入、审批都有扩展点

- 来源：[Control execution with hooks](https://code.claude.com/docs/en/agent-sdk/hooks)。
- 官方原文列出：
  > “Block dangerous operations before they execute”
  > “Log and audit tool calls for compliance, debugging, or analytics”
  > “Transform inputs and outputs”
  > “Require human approval for sensitive actions like database writes or API calls”
- 示例通过 `PreToolUse` 阻止写 `.env`；事件表有 `PostToolUse` 与失败、会话生命周期等事件。
- 支持结论：现成 Harness 允许企业接入自己的执行策略和日志链路。这里的 hooks 是机制，业务规则和可信的审计归档仍需要实施。
- 限制：异步 hooks 不可阻止或修改已经继续的操作；权限校验不能挂在只能做旁路副作用的回调里。文档原文：
  > “Async outputs can’t block, modify, or inject context into the operation since the agent has already moved on.”

### S4. Claude Code sandbox：有操作系统边界，但覆盖范围需读清

- 来源：[Sandboxing](https://code.claude.com/docs/en/sandboxing)。
- 官方原文：
  > “The Bash sandbox is a boundary that the operating system enforces around the shell commands Claude runs on your machine.”
  > “The sandbox covers shell commands only. Claude’s file tools, MCP servers, and hooks run outside it.”
- 文档明确 shell 子进程受文件与网络边界约束；文件/web 工具另走权限规则，MCP、hooks 等不是自动被 Bash sandbox 包住。
- 官方建议如果需要统一外层边界，将 Claude Code 进程本身放入容器、虚拟机或 sandbox runtime。
- 支持结论：不能说“现成没有沙箱”，也不能说“开了沙箱，一切工具就都隔离”。企业该审核的是实际部署的完整调用路径。
- 当前文档还区分 macOS/Linux/WSL2 与原生 Windows，以及开关和失败行为。不要把某个环境的默认值泛化为所有部署。

### S5. Claude Code 企业设置：不是只能相信个人自觉

- 来源：[Claude Code settings](https://code.claude.com/docs/en/settings)。
- 官方原文：
  > “Managed settings: settings your organization deploys, by a managed-settings.json file, an MDM policy, or server-managed settings from the claude.ai console. Nothing in your own settings files or --settings overrides a managed key.”
- 文档展示 managed、CLI、project local、shared project、user 的层级；也明确有少数安全键、环境变量与宿主配置的例外，不能简化成所有字段在所有形态完全一样。
- 支持结论：组织级强制策略已是现成产品的一部分。“我们需要强制策略，所以必须重写”不成立，先检查可配置机制和覆盖边界。

### S6. Codex SDK：自动化和内嵌并非只能操作 CLI 界面

- 来源：[Codex SDK](https://developers.openai.com/codex/sdk)。
- 官方原文列出用途：
  > “Control Codex as part of your CI/CD pipeline”
  > “Build Codex into your own internal tools and workflows”
  > “Integrate Codex within your own application”
- TypeScript library 支持 start、continue、resume local threads；当前页面也有 Python library。
- 支持结论：企业可以选择程序化运行与工作流集成，不应把“开发者终端”误当唯一交付形态。
- 不需要在博客堆砌语言、版本号：足以引用“存在官方 SDK 和可恢复线程”。

### S7. Codex App Server：已有认证、会话、审批和事件协议

- 来源：[Codex App Server](https://developers.openai.com/codex/app-server)。
- 官方开篇：
  > “Use it when you want a deep integration inside your own product: authentication, conversation history, approvals, and streamed agent events.”
- 页面定义 thread、turn、item，支持启动、继续、分叉、流式通知与中断；审批由 server 发 JSON-RPC 请求，client 返回决定。
- 还提到 `clientInfo.name` 用于 OpenAI Compliance Logs Platform，并提示企业集成联系 OpenAI 纳入已知客户端名单。
- 支持结论：不能声称“Codex 无法嵌入自有前端”“只能抓命令行输出”“无审批协议”。
- 重要成熟度限制：当前页面远程 Code Mode 小节出现：
  > “The app-server command and WebSocket transport are experimental and aren’t supported for production workloads.”
  不应把所有传输/远程部署能力包装为已经无条件适合生产。正文说“存在集成接缝”成立；采购和上线需进一步核对实际支持范围。
- 授权边界：当前页面也区分本地/开源应用与商业托管使用的认证方式；不宜在博客给出“用个人 ChatGPT 登录为所有员工转供”的建议。

### S8. Codex 管理员配置：不可覆盖要求与可覆盖默认值不同

- 来源：[Managed configuration](https://developers.openai.com/codex/enterprise/managed-configuration)。
- 官方原文：
  > “Requirements: admin-enforced constraints that users can’t override.”
  > “Configuration defaults: system or cloud-managed config.toml settings that users can override.”
- `requirements.toml` 能约束 approval policy、reviewer、sandbox/permission profiles、web search、managed hooks、可启用 MCP server、插件市场来源等。
- 官方原文：
  > “Requirements constrain security-sensitive settings … which MCP servers users can enable, and which plugin marketplace sources they can use.”
- 文档同时提醒支持依赖产品、client version、execution environment，local 与 cloud 控制需分别测试，某些通道不走命令网络代理。
- 支持结论：“企业统一配置”不是从零建设内核的充分理由，不能把个人可覆盖默认值与强制要求混写。
- 重要限制：文档说某些远程 MCP hook 的错误/超时/畸形响应不一定阻止工具，并强调：
  > “MCP hooks do not provide a complete Compliance API audit trail.”
  这支持“机制已存在，整条业务控制链仍需核实”，而非“hook 就是万能安全边界”。

### S9. Codex approvals 与 OS sandbox 是不同机制

- 来源：[Agent approvals & security](https://developers.openai.com/codex/agent-approvals-security)。
- 官方原文：
  > “Locally, Codex uses an OS-enforced sandbox … plus an approval policy that controls when it must stop and ask you before acting.”
- 文档定义：sandbox 决定技术上能访问/改动什么，approval policy 决定何时需征询批准。
- 支持结论：现成有执行边界与审批机制；业务资源授权还应在工具服务端核验。
- 不应泛化的细节：不同工具流量不共享同一个网络边界；一些示例与选项有部署/版本范围。当前不同页面的 destructive annotation 细节表述也不完全一致，因此本文只使用高层、稳定事实，不据此设计具体生产策略。

### S10. Pi：最小核心是一种复用路线，不是企业所有功能的成品

- 原来源：[badlogic/pi-mono/packages/coding-agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)，当前重定向 [earendil-works/pi/packages/coding-agent](https://github.com/earendil-works/pi/tree/main/packages/coding-agent)。
- README 原文：
  > “Pi is a minimal, extensible agent harness that you can make your own.”
  > “Customize Pi with extensions, skills, prompt templates, and themes.”
  > “Pi ships with powerful defaults but skips features like sub-agents and plan mode.”
  > “Use Pi interactively, automate it in print or JSON mode, control it over RPC, or build apps with the Pi TypeScript SDK.”
- 支持结论：Pi 的小核心与扩展接口适合形成不同宿主和策略；不必用一套闭包式平台才能获得控制。
- 不支持的推论：Pi 已提供所有企业管理能力；其扩展机制本身就是安全沙箱。
- 时间敏感提醒：当前 Pi 文档已有内置 MCP extension；不应照搬旧文章写“Pi 不支持 MCP”。

### S11. Pi extensions：可拦工具、改上下文，但扩展本身受信任

- 来源：[Extensions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)。
- 官方原文：
  > “An extension runs inside the Pi process with the same operating-system permissions. It can inspect prompts, tool calls, files, credentials, and session history, so load extensions only from sources you trust.”
- 文档集成点包括：`tool_call` authorize/modify，`tool_result` redact/replace，`context`/`context_with_system`，`registerTool`，session events。
- 原文：
  > “tool_call can mutate input or block execution.”
- 支持结论：扩展点能承载企业策略；安全边界与扩展供应链可信性要另行负责。

### S12. Pi SDK：明确允许将核心嵌入宿主

- 来源：[SDK](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md)。
- 原文：
  > “embeds Pi in a Node.js or Bun process. It provides direct TypeScript access to the agent, sessions, tools, models, and resources used by the command-line application.”
- `createAgentSession` 建立会话，包含模型、工具、排队消息、compaction 和 extension runtime；session manager 提供持久化/内存模式；有自定义 tools、models、resources 的入口。
- 支持结论：复用核心与控制宿主不是对立选项；SDK 已是合理的企业构建材料。

### S13. Anthropic 长任务案例：效果来自交接与验收安排，不等于重写 loop

- 来源：[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)。
- **真实发布日期：2025-11-26**，早于本次调研日期，非未来资料。
- 官方观察是在文章当时的 Claude Agent SDK + Opus 4.5 全栈应用实验里：只给高层提示再跨窗口循环，容易一次做太多、留半成品，或过早宣布完成；compaction 本身不够。
- 解决方案：initializer 生成 `init.sh`、feature list、progress notes 与初始 Git commit；后续会话增量做功能、读日志、测试、写交接。
- 最重要的脚注：
  > “We refer to these as separate agents in this context only because they have different initial user prompts. The system prompt, set of tools, and overall agent harness was otherwise identical.”
- 文章自己限制外推：
  > “Additionally, this demo is optimized for full-stack web app development. A future direction is to generalize these findings to other fields.”
- 适合博客的具体事实：Anthropic 自己也在现成 SDK 之上补任务清单、工作交接和端到端验收；这说明通用循环并不会自动知道“这家企业的完成标准”，但改进并不必然要求重写循环。
- 不能写成“目前所有模型、所有 SDK 长任务都做不好”；这是特定时间与场景的实验观察，没有给出可普适套用的 ROI 或成功率数字。

### S14. Anthropic evals：轨迹漂亮与业务状态正确是两回事

- 来源：[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。
- **发布日期：2026-01-09**。
- 原文区分 transcript 与 outcome：
  > “A flight-booking agent might say ‘Your flight has been booked’ at the end of the transcript, but the outcome is whether a reservation exists in the environment’s SQL database.”
- 原文对 agent harness 的定义：
  > “it processes inputs, orchestrates tool calls, and returns results. When we evaluate ‘an agent,’ we’re evaluating the harness and the model working together.”
- 评测建议：有明确成功标准、来自真实失败的任务、多次 trial、隔离环境、代码/模型/人工 grader 的合理组合；不要只看结果分数，需读轨迹诊断模型错误与评测错误。
- 对基础设施投入的反证：
  > “It’s often best to quickly pick a framework that fits your workflow, then invest your energy in the evals themselves by iterating on high-quality test cases and graders.”
- 支持结论：企业需要拥有并迭代验收题和标准；不意味着必须自建又一套通用评测平台。
- 未引用其中厂商/客户百分比宣传，也不把 toy 示例当作真实效果基准。

### S15. Building effective agents：复杂度必须买来可验证收益

- 来源：[Building effective agents](https://www.anthropic.com/research/building-effective-agents)。
- **原始发布日期：2024-12-19**。当前页面明确说 2024 年后的工具格局已变，并链接到现在的 Managed Agents；引用其架构原则，不将当前更新后的产品名当作 2024 年原文已有能力。
- 原文：
  > “When building applications with LLMs, we recommend finding the simplest solution possible, and only increasing complexity when needed.”
  > “Agentic systems often trade latency and cost for better task performance.”
  > “you should consider adding complexity only when it demonstrably improves outcomes.”
- 术语区别：workflow 的路径由预定义代码控制，agent 的过程与工具使用由模型动态决定。二者是系统模式，并非产品阵营。
- 这也挑战“必须选一个宏大 Agent 框架”的假设：任务适合单次推理、检索或少量固定步骤时，不一定需要通用自主系统。

## 对拟定论点的反向挑战

### “企业要掌握权限、运行、审计，所以要自建控制平面”仍可能过度

现成产品已经具备组织管理和不少强制策略，SDK 也有会话、审批、恢复和事件。不能简单把内核划为采购层，再把所有上层自动划为自建层。更严谨的说法是：**企业要掌握责任与标准；实现可买、可接、可配置，只建设实际缺口。**

同理，“我们要评测，所以要造评测平台”也不成立。可以先用稳定的既有框架，投入到业务任务、可靠环境和评分规则；这是 S14 直接建议的方向。

### “能扩展，所以绝不重写”也不成立

可扩展只说明技术上存在接缝，不证明适配成本合理。若每次升级都需大面积 patch、会话语义不适合自己的任务、或极小任务要背负大量通用假设，一个小而专用的循环可能是最少工程。应拿实际成本比较，而不是等到理论上绝对不能做才准许自建。

### “自建有助于多模型”是条件命题

能切换 endpoint 不等于跨模型保持质量。不同模型的工具理解、错误恢复、上下文利用不同；要用同一业务任务集证明换模型后的成功、风险、时延与人工修正成本。没有跑过的基准，不应承诺“模型无关”。本报告不虚构跨模型效果数据。

### “企业都需要自己的 Agent 平台”本身也应收敛

小团队的需求可能只是受管理的 Claude Code/Codex 席位，加几个业务工具和团队规范。不要为了反对自建内核，顺手立项另一套大型平台。文章结尾宜强调需要自有业务规则与验收能力，未必需要一个独立平台项目。

## 建议成稿的投资边界

| 观察到的实际问题 | 应先验证的最小措施 | 何时才牵涉内核 |
| --- | --- | --- |
| 工具拿不到正确数据或参数容易错 | 修业务 API、tool schema、数据访问和错误信息 | 工具调用/选择语义确实无法通过接口表达 |
| 生产权限与人员/资源/窗口相关 | 在服务端绑定身份与资源授权，使用 SDK 的 hook/approval 接缝 | 接缝不能覆盖要求的所有执行路径，且外层隔离也不经济 |
| 长任务丢交接、提前宣布完成 | 明确任务清单、持久化交接、可验证状态、端到端验收 | 所需状态恢复、压缩或调度语义无法经济表达 |
| 看似流畅但业务失败 | 失败样本、业务 outcome grader、人工复核与回归任务 | 对比可归因地证明失败来自执行内核，改内核持续改善 |
| 多模型或部署限制 | 核验现有 SDK/自托管方案、商业授权与数据条件 | 有具体不可满足条件，且专用原型证明总成本合理 |
| 功能极窄、固定少量工具 | 单次调用、简单 workflow 或小型专用 loop | 此时自建可能就是最小方案，无需升级为通用框架 |

我建议比较三组：现成方案、必要扩展后的方案、最小自建原型。在相同工具、权限、测试数据、预算与环境下，看业务验收成功、不可接受错误、人工接管/返工、完成时延及每个成功任务总成本。把集成与维护人力算进去。没有真实测量，不给 ROI 数字。

## 对博客稿的核查

核读文件：`src/content/posts/why-enterprises-build-agent-harnesses.md`，未修改。

- 事实段关于 Claude SDK、Codex App Server、managed configuration、Pi extensions/SDK 的说法均可由 S1–S12 支撑；复核时正文已补对应脚注。
- 正文已加入 S13 的长任务案例，关于初始用户提示不同、其余 system prompt/tools/harness 一致的说法与原文脚注相符。
- 初稿“企业当然会有自己的 Agent 平台”偏绝对，已反馈；复核版本改为“是否需要统一的 Agent 平台，取决于任务和规模”，避免把小团队也推向平台项目。
- 建议保留 App Server 的 experimental/支持范围提醒，不将接口存在写成所有部署形态都成熟。
- dsh 身份用户未明确，本报告没有猜测其项目或能力，也没有把它扩写为某个产品。

## 未覆盖与证据限制

- 本调研未运行实际 SDK、搭建企业策略实验，也未测性能/成本；功能事实来自官方当前文档与仓库。
- 无厂商销售报价、真实企业部署样本或跨模型同场 benchmark，因此不对具体企业承诺自建/采购的定量回报。
- Anthropic 工程文章属于第一方实验与经验，不是独立复现；本文明确其任务、时间、模型及外推边界。
- GitHub README/docs 基于当前 main，仓库名称与 API 会变化；公开博客宜优先讲稳定架构事实，避免硬编码将迅速过时的版本与默认开关。
- 没有确认 dsh 的指代，不能给其能力下结论。
