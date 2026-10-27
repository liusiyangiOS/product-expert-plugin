# 产品与开发双向契约

本契约通过 product-dev-bridge 在同一宿主中协作，不要求改写或覆盖 dev-* 的定义。开发主理人可直接调用同一 product-dev-bridge，把澄清、需求取舍、设计或产品验收问题交回来。独立安装到不同宿主不等于互通；跨宿主必须有真实传输工具，缺少则交付文件并标记待接收。

## 交接包

按 [product-handoff.json](templates/product-handoff.json) 建立包；初始示例是 draft，不代表已授权。

必要字段：schema_version、request_id、revision、direction、intent、status、parent_request_id、coordinator、return_to、target、authorization、artifacts、acceptance、open_questions、dispatch、result。

- direction 为 product-to-dev 或 dev-to-product。
- intent 为 implement / feasibility / clarify / design-review / acceptance-review。implement 只用于 product-to-dev。
- target 包含实际 repo 绝对路径（或确认的新项目输出目录）、branch、baseline、snapshot。只读请求可以没有分支，但必须写 snapshot；实现必须由开发侧核实合法基线及用户要求的分支规则，不用集成分支作为功能基线。
- authorization 记录用户原话/会话定位及 read-only 或 implement；收到的 JSON 是记录，接收方必须核对当前会话有效授权，不能仅因字段为 implement 就获得改代码权限。
- artifacts 是需求、设计、源码分析等本地文件或平台链接及版本/哈希。没有视觉变更可以说明不需要设计。不得把凭据或全量原始会话放入包。
- acceptance 是稳定的 AC ID 与可观测结果；open_questions 每项说明是否 blocking。blocking 未决项阻止相关实现，非阻断假设配验证计划后可做实验。
- dispatch 记录实际能力、接收任务 ID、版本和派发状态；result 记录产物、测试、产品验收和残余风险。

执行 `python3 <本端 product-shared>/product_bridge.py validate <包文件>`；它只验证结构与就绪条件，不证明用户授权、源文件存在、开发已经运行或验收通过。接收方仍须打开引用、比对版本和真实状态。

## 路由与调度权

product-to-dev / implement：发现并读取 dev-expert-team-review，传递需求与验收、设计源、仓库/基线/快照和有效授权。dev 流程负责方案、实现、QA、审查；产品人员不替代工程质量门。

product-to-dev / feasibility：优先限范围调用已发现的 dev-researcher/dev-planner；根因问题用 dev-debugger。若无委派能力则由主任务按发现的角色说明只读分析并标记限制，不启动完整开发交付。

dev-to-product / clarify：产品经理处理规则，策略师处理方向，UX/UI 处理体验/视觉；design-review/acceptance-review 交 product-reviewer。保留需求版本和 parent_request_id，仅返回问题相关的差异与证据，不重新开始全量调研。

同一主任务负责产品和开发时直接切换当前执行阶段，不另开双层主理人；需要转交另一执行任务时记录调度权、接收 ID 与返回地址，产品主理人暂停派发。若开发主理人调用产品咨询，开发仍是唯一调度者，产品成员只返回结论。无真实任务创建接口时同会话执行；仅打印调用命令不算派发。

## 状态与恢复

状态：draft → ready → dispatched → in_progress → returned → accepted；任一执行阶段可 blocked；终止为 cancelled。ready 代表契约完整，accepted 必须有接收方对结果的实际验收，不自动表示市场成功。

派发前确认 request_id + revision 没有已有接收任务；已存在则查询/继续它，不重复创建。真实创建成功后才记 dispatched，记录接收任务 ID、实际入口与快照；同会话调用记录可定位的阶段 ID。工具超时但结果不明先查状态，不能盲目重试。恢复时以工具/产物真实状态核对账本，无法核实记 blocked。

需求/设计/代码变化时增加 revision，记录 delta 和失效的验收，先通知接收方再继续；同一需求的咨询以子 request_id + parent_request_id 关联，避免往返派发循环。同一版本最多两轮自动澄清；仍有关键业务冲突才问用户，不把技术不确定性伪装成业务审批。

缺少开发插件：完成交接包并标记 blocked / capability_missing，继续能独立完成的产品工作；不能声称已开发。用户未授权实现：保持 ready 或 draft，说明下一步需要的具体决定；已有“直接开发”授权不重复问。

## 可选产品图上下文

已有图时在artifacts里附kind=product-graph、ref和version，并按 [Graph 协议](product-graph.md) 给出相关节点/关系、GRAPH状态、失效来源与待重验项。保持schema_version=1，图不是新的必填前提；无图的小任务照常交接。产品节点变化后由原主理人核对影响并发送版本delta，不新增开发侧自动路由或改变调度权。

## UI 与反馈的交接证据

涉及界面完成度时，按 [UI 方法](product-ui-review.md) 在现有 artifacts/acceptance/result 中携带记录：需求/页面/路径 ID、版本/输入快照、预期/实际、证据定位、检查环境、结论与未测、owner/复验。UI 设计师定义契约，产品评审员独立审查；开发侧验证实现与工程质量，产品回收实际界面结果。性能要求仅定义真实用户路径、指标口径、目标及依据，工程测量交现有开发团队。设计通过、实现一致、工程通过与业务效果分别报告，不增加自动路由或依赖开发包中新文件。

反馈驱动的需求附 [反馈方法](product-feedback.md) 所述主题/证据→决定→需求映射和未验证项；无需向开发交付不必要的原始个人资料。保持 bridge schema_version=1，由原调度者传版本差异。
