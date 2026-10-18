# Agent 时代，Workflow 产品还有没有必要：研究底稿

研究日期：2026-10-18。只使用实际读取过的一手公开正文；本文件是事实与论证底稿，不是产品测评或最终文章。网页会更新，产品能力和套餐边界以读者实际使用版本为准。

## 核心判断（作者观点）

Agent 会压缩一部分 workflow 产品的价值，但不能从“模型会规划”推出“业务流程、工作流运行机制、可视化产品同时消失”。这三件事需要分开：

1. **业务流程**规定谁有权执行什么、什么条件必须成立、失败如何处置。这是企业自己的决定，模型能力提高不能替企业取消。
2. **运行机制**处理状态、等待、恢复、重试和外部副作用。可以用普通代码、状态机、队列或专门的 durable execution 系统实现，不天然需要画布。
3. **可视化平台**是开发、交付、协作和维护产品。只有在它确实降低总成本时才有价值。前两者必需，不能自动证明第三者必需。

真正被压缩的，是为补足旧模型能力而手工拆解的推理流程，以及只包装模型调用、提示词和 API 的胶水。Agent 也降低了普通代码的开发成本，因此 no-code 不能只与过去昂贵的定制开发比较，应与今天借助 Agent 编写的小服务比较。

产品的合理方向是容纳动态探索与确定边界：让模型处理如何找证据、如何澄清和探索；把授权、金额限制、幂等和最终动作交给明确逻辑。但“产品有一个 Agent 节点”只是共存的证据，不是生产可靠性的背书。

## 一手事实与短证据

### 1. Anthropic 的界线在控制权，不在画布

来源：Anthropic, *Building effective agents*，发表于 2024-12-19。

- URL：https://www.anthropic.com/engineering/building-effective-agents
- 实读证据：“Workflows are systems where LLMs and tools are orchestrated through predefined code paths.”
- 实读证据：“Agents … LLMs dynamically direct their own processes and tool usage.”
- 选择建议：“workflows offer predictability and consistency for well-defined tasks”；agents 适合需要灵活性与模型决策的任务。
- 官方建议先找最简单方案，复杂性只在必要时增加。agentic systems 常以延迟和成本换取更好的任务表现；很多应用优化单次调用、检索和示例就足够。
- 官方也提示框架抽象可能遮蔽底层 prompt/response，增加调试难度；使用框架应理解其底层代码。

文章可据此说：代码也能实现 workflow，画布内也可以运行 agent；把节点和箭头当作技术落后的标志，没有架构依据。不要据此说所有动态委派都与 workflow 互斥：原文还把 orchestrator-workers、evaluator-optimizer 列为常见 workflow 模式，现实是组合谱系而非纯粹二元分类。

当前原文顶部已有提示：工具格局自 2024 年变化，读者可参考 Managed Agents 新资料。本文仅使用其仍然适用的控制权区分，不拿它证明 2026 年具体产品能力。

### 2. Dify：Workflow、Chatflow 和 Agent 能共存

来源：Dify 官方 *Workflow & Chatflow*。

- URL：https://docs.dify.ai/en/cloud/use-dify/build/workflow-chatflow
- 页面显示最后修改 2026-07-02。
- 实读证据：“Both are built on a shared visual canvas and node system.”
- Workflow 一次从输入运行到结果；Chatflow 叠加会话层，每条消息触发设计好的流程。
- 节点可调用模型、检索知识、运行代码或按条件分支。Workflow 也可由定时、webhook 和集成事件触发；Chatflow 由用户消息启动。

来源：Dify 官方 *Agent*。

- URL：https://docs.dify.ai/en/cloud/use-dify/nodes/agent
- 实读证据：“The classic Agent node gives your LLM autonomous control over tools … iteratively decide which tools to use and when to use them.”
- 经典节点支持 Function Calling、ReAct 策略，并可限制最大迭代次数。工具具有授权、说明和参数配置；节点输出包含结果、工具输出、迭代次数和日志。
- 同页还有 beta 的新 Agent 节点，描述为可在独立 sandbox 中执行完整 worker。为避免把试验特性当通用保证，文章无需引用该 beta 能力。

能证明：workflow 产品并不只会执行固定的 prompt 链，已经能把动态工具循环放在流程内部。

不能证明：其所有 Agent 能力、模型或插件在所有部署版本、套餐中相同；节点存在不等于具备端到端生产保证。

### 3. Dify Human Input：有暂停与分支，不能直接等同企业授权审批

来源：Dify 官方 *Human Input*。

- URL：https://docs.dify.ai/en/cloud/use-dify/nodes/human-input
- 实读证据：“The Human Input node pauses workflows at key points to deliver a customizable request form.”
- 表单可以展示流程变量、收集输入，按预设决策按钮走不同执行分支。
- 默认等待时间为 3 天。超时走 timeout branch；没有连接超时分支则流程结束。
- 支持 web app 和邮件递送；Trigger 启动的 workflow 不支持 web app 递送。
- **重要边界**：邮件链接任何持有者都可响应，不需要 Dify 账号；无论递送方式，首次响应后请求关闭。短证据：“Anyone with the link can respond, no Dify account required.” / “The request closes after the first response.”

能证明：有人类输入参与的暂停、恢复与分支机制。

不能证明：分级审批、特定岗位的强身份授权、多人会签、金额与审批对象版本绑定、防链接转发等企业语义已经自动解决。不能把“表单有人点批准”直接写成“合法责任人批准了这笔业务”。也不能从暂停文档推出跨任意进程崩溃、升级和外部系统的事务保证。

来源：Dify 官方 *Workflow App API*。

- URL：https://docs.dify.ai/en/api-reference/guides/workflow
- Workflow 每次调用运行已发布流程；不同调用之间没有会话状态。
- `task_id` 控制活跃任务，`workflow_run_id` 标识持久记录。
- 文档描述 Human Input 事件、表单 token 和提交后重新订阅事件流。
- Stream Workflow Events 可在连接中断或暂停后重开事件流，可先重放已执行节点状态。

**注意**：重连事件流不是重新执行工作流，也不是已产生外部副作用被自动事务化。文章只需说“API 包括运行和人类输入生命周期”，无需用此延伸出没有证据的持久执行 SLA。

### 4. Dify 错误处理、重试、版本、DSL、日志的实际边界

**错误处理**：

- URL：https://docs.dify.ai/en/cloud/use-dify/build/predefined-error-handling-logic
- 官方明确 LLM、HTTP、Code、Tool 节点原生支持错误处理。
- 节点失败可停止整个流程、给默认值继续，或走失败分支。
- Loop 任一子节点失败立即终止；Iteration 可停止、跳过失败项（输出 null）或移除异常输出。
- 这些是控制流策略，不是跨节点或跨外部服务的事务回滚。

**HTTP 重试**：

- URL：https://docs.dify.ai/en/cloud/use-dify/nodes/http-request
- 实读证据：“Retry Settings automatically retry failed requests up to 10 times with configurable intervals (maximum 5000ms).”
- 有连接、读、写超时和失败分支。
- 不能从“可重试 10 次”推出“付款只发生一次”。网络超时不等于远端没有处理成功；业务 API 仍需幂等与状态确认。

**版本控制**：

- URL：https://docs.dify.ai/en/cloud/use-dify/build/version-control
- 页面显示最后修改 2026-07-17。
- 有 Current Draft（非线上）、Latest Version（当前发布）和 Previous Versions。
- 发布会让草稿成为线上版本；可浏览历史、命名版本、增加发布说明。
- 重要套餐边界：“Restoring a version, exporting a specific version’s DSL, and running a specific published version through the Service API are available on paid plans.” Sandbox 总运行最新发布版本。
- 回滚产品配置不自动回答“一个已暂停的业务应使用哪个规则版本”或外部操作能否撤回。

**DSL**：

- URL：https://docs.dify.ai/en/cloud/use-dify/workspace/app-management
- DSL YAML 可导出 app 配置、编排与节点设置、模型参数与 prompt、知识库连接。
- 不导出实际知识库内容、第三方工具 API key、日志与分析数据；Secret 类型环境变量可能由用户选择导出。
- 因此 DSL 有助迁移与备份配置，但不是数据备份、凭据迁移、跨任意平台可执行的开放标准，更不是消除平台锁定的充分条件。

**观测**：

- URL：https://docs.dify.ai/en/cloud/use-dify/monitor/logs
- workflow run 可看到输入输出、状态、token、逐节点 trace，定位失败或慢节点；可用同样参数在编辑器重跑。
- Chatflow/Workflow 编辑器 Preview/Test Run 不列入此生产使用日志。
- 日志保留有套餐差异；Sandbox 是 30 天，付费 workflow 旧日志会归档。文章无需列套餐细节，但不能泛称永久审计。
- 日志有完整输入输出并不等于所有外部动作经过授权，也不等于有业务证据链、合规认证或逐笔账务对账。

**源码补证（不用于作过度性能判断）**：

- 实读 URL：https://github.com/langgenius/dify/blob/main/api/core/workflow/human_input_adapter.py
- 文件说明为 “Workflow-to-Graphon adapters for persisted node payloads”；公开源码确认保存的 workflow graph、编辑器 payload 和执行模型之间还有适配层，不能把前端画布本身当执行器。
- 本次只读该边界适配文件，未审计 Dify runtime 的崩溃恢复实现、数据库一致性和集群故障行为。

### 5. Coze Studio：开源、自部署、Agent/Workflow 资源与 API

来源：Coze Studio 官方 GitHub README。

- URL：https://github.com/coze-dev/coze-studio
- README 的公开定义是面向 Agent 的可视化开发工具，核心能力包括 prompt、RAG、plugin、workflow。
- 功能清单有 build/publish/manage agent、创建发布 app、创建修改发布 workflow，以及 API/SDK。
- Quickstart 提供 Docker / Docker Compose 本地部署流程。
- README 将 Agent 开发、工作流、资源和本地业务系统集成并列；明确开源与商业版存在功能差异。
- README 特别区分 Eino 提供 Agent/Workflow **runtime engines**，FlowGram 提供前端 workflow **canvas editor**。这是“画布不等于运行机制”的直接一手例子。

来源：Coze Studio 官方 API wiki。

- URL：https://github.com/coze-dev/coze-studio/wiki/6.-API-Reference
- `POST {{host}}/v1/workflow/run`：执行已发布 workflow；响应含 debug_url，可查看逐节点输入输出。
- `POST {{host}}/v1/workflow/stream_run`：流式执行，支持输出、问题节点、启用流输出的结束节点。
- `POST {{host}}/v1/workflow/stream_resume`：回答问题节点以恢复中断。文档的明确场景是问答与补充参数；最多恢复询问三次仍不满足预期则失败。
- `POST {{host}}/v1/workflows/chat`：已发布 chatflow；`workflow_version` 对资源库 workflow 可指定版本，不指定默认最新版本。
- 授权用 Personal Access Token；调用者 token 与工作区权限、关联 agent 的发布状态有要求。
- API wiki 列出了请求尺寸和超时等限制，但本次不推荐正文抄入具体限制，以免在版本、开源/商业实现间混用。

能证明：Coze Studio 不是静态流程图工具，存在运行、发布、对话与中断接口，可自己部署。

不能证明：`stream_resume` 是任意节点崩溃后持久恢复 API；公开源码与商业 SaaS 的能力、规模、安全和 SLA 相同；“自部署”自动解决权限、安全、运维成本和供应链问题。

来源：Coze Studio 官方架构 wiki。

- URL：https://github.com/coze-dev/coze-studio/wiki/7.-Development-Standards
- 后端有 API / application / domain / infrastructure 分层；workflow 为领域实现之一，结构化存储、缓存、消息队列和对象存储分别承担职责。
- 这也说明平台交付的不仅是一张画布；但组件多也意味着自部署存在真实维护成本。后一句是推论，不是官方性能结论。

资料限制：商业 Coze 中英文文档 URL 通过 Firecrawl 仅返回页面元数据、没有正文。本研究没有用搜索摘要填补，关于 Coze 的产品事实以上述官方开源 README/wiki 为准，不冒充商业版全面能力描述。

### 6. LangGraph：有状态与恢复仍需显式工程设计

来源：LangGraph 官方 *Persistence*。

- 实读 URL：https://docs.langchain.com/oss/python/langgraph/persistence
- 请求旧的 durable-execution URL 当前跳转至 persistence，因此最终文章应优先引用实际正文地址或更具体 interrupts 页。
- Checkpointer 保存线程图状态以支持会话延续、人类输入、时间旅行和容错；Store 负责跨线程应用数据。
- `InMemorySaver` / `MemorySaver` 存 RAM，进程重启会丢失；生产要使用持久 checkpointer。

来源：LangGraph 官方 *Interrupts*。

- URL：https://docs.langchain.com/oss/python/langgraph/interrupts
- 暂停需要 checkpointer、稳定 thread ID；生产应使用数据库等持久后端。
- 实读证据：“The node restarts from the beginning … so any code before the interrupt runs again.”
- 最直接幂等段落：https://docs.langchain.com/oss/python/langgraph/interrupts#side-effects-called-before-interrupt-must-be-idempotent
- 实读证据：“Because interrupts work by re-running the nodes … side effects called before interrupt should (ideally) be idempotent.”
- 可将副作用置于适当边界，并需要考虑重复执行。

不能泛称：用了 LangGraph 就自动拥有所有持久化；示例的内存 saver 不能承受重启。也不要从“中断后代码位置”简单推出整套系统外部操作 exactly-once。

### 7. Temporal：可靠编排不替代外部幂等

来源：Temporal 官方 *What is an Activity?*。

- URL：https://docs.temporal.io/activities
- Activity 失败按 retry policy 重试；重试从初始状态开始，除非代码用 heartbeat payload 做 checkpoint。
- 官方建议幂等以免重试产生重复副作用。

来源：Temporal 官方 *Activity Definition — Idempotency*。

- URL：https://docs.temporal.io/activity-definition#idempotency
- 明确故障窗口：Activity 成功执行后，worker 在告知 Temporal 之前崩溃，Event History 没记录成功，任务会被重试；不幂等可能导致重复收费。
- 实读证据：“These [idempotency keys] are enforced by the service you are calling … not by the Activity itself.”
- retry policy 段还区分：Activity 会被观察为完成恰好一次，但实际代码可能执行、甚至部分完成多次。

这为博客的退款超时例子提供了准确工程依据。不能反过来写 Temporal 自带任意跨业务系统 ACID 事务，也不能把 Temporal 这种专门运行机制的设计自动归于每个 AI workflow 产品。

## 建议论证与反论点（均为作者观点）

### 为什么“只售卖 prompt 胶水”会贬值

- 当模型更能处理澄清、规划、工具选择和中间结果校正，以前人工堆出的许多推理步骤未必继续提高质量；应拿相同验收数据测量，而非坚持节点越多越可靠。
- 当 Agent 编程工具缩短小服务开发时间，可视化平台节省的开发劳动也在变化。“不用写代码”不再自动意味着总成本低。
- 模型调用、工具循环和普通连接器可复制，不能只因拥有这些能力就推断长期竞争优势。这是经济与产品判断，不是本次验证出的市场份额预测。

### Workflow 仍有必要，也不等于该买平台

- 确定批处理、格式转换、稳定路由已能用普通代码表达，强行每步交模型规划可能增加成本与不确定性。
- 授权规则、幂等、状态恢复是系统责任，可由已有业务服务、队列、状态机或编排引擎解决；不要为了证明 Dify/Coze 有用，把它们说成唯一实现方式。
- 业务团队若真的能独立完成有测试、有发布边界的变更，可视化有协作价值；若所有修改仍依赖工程师、逻辑散落代码节点与服务，平台可能是额外维护负担。
- DSL 可导出只能减少某些迁移负担，不能消灭节点语义、插件、数据和凭据的依赖。
- “流程透明”也要问实际维护者能否看懂。上百个框、嵌套循环、变量映射和外部代码节点不必然比代码易理解。

### 假想案例，不能包装为真实客户故事

用退款申请串起两层责任：Agent 搜集聊天记录与订单事实、追问缺失材料、给有证据建议；确定逻辑核对额度与授权、锁定被批准的版本、用稳定业务幂等键执行退款并查询不确定结果。

如果调用超时，不能简单让 Agent“重试付款”。如果审批后金额改变，不能沿用旧批准。等待几天再恢复，也要明确使用哪个规则版本。这个例子是本研究为解释问题构造的，不代表 Dify、Coze 或某客户出现过事故。

### 最值得做的对照实验

同模型、工具、输入集和验收标准，对比已有平台与最小代码/Agent 实现。除结果质量、费用、延迟，还做一次真实需求变更、工具故障、中断与恢复，记录：谁能改、改多久、谁能定位、有没有重复外部动作、能否导出和迁移。

这比争论“workflow 会不会死”更能证明某个平台的采购、保留或淘汰决策。不要凭一次顺利 demo 证明生产能力，也不要把理论上的治理需要等同于每个团队都应该建设复杂平台。

## 对当前博客初稿的核对结果

已读 `src/content/posts/agent-workflows-after-agents.md`，核心论证与产品事实成立。

唯一建议精确化的句子：将泛指“LangGraph 持久执行文档讨论恢复与重放、任务边界”改为具体的“LangGraph 中断文档明确恢复会从节点开头重跑、中断前副作用要幂等、生产要持久 checkpointer”，与本次实际读取正文吻合。

正文 Dify/Coze 小段建议关联四个来源即可：Agent、Human Input、Coze README、Coze API wiki。无需为了显示调研量堆满功能清单。

## 未验证内容

- 未部署 Dify、Coze Studio、LangGraph 或 Temporal 做故障注入、压测或安全审计。
- 未核查所有自部署发行版与 SaaS 套餐能力一致性。
- 未读取 Coze 商业文档正文；未把其搜索摘要当证据。
- 未对 Dify/Coze 作端到端事务、恰好一次外部执行或无限期恢复保证。
- 没有使用真实企业内部案例或数据。
