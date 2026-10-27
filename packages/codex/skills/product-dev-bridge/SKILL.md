---
name: product-dev-bridge
description: 把产品需求直接交给可用开发专家团，或接收开发的产品澄清、设计及验收请求，保留版本与回执。
---

# 产品开发双向协作

完整读取 [运行约定](../product-shared/product-runtime.md)、[工作流约定](../product-shared/product-workflow-contract.md) 与 [双向契约](../product-shared/product-dev-contract.md)。本入口同时面向产品主理人和开发主理人，不需要安装第二个重名入口。

1. 判断方向与 intent；复用父任务、版本、授权和产物，不重复全量调研。产品发起 implement/feasibility，开发发起 clarify/design-review/acceptance-review。
2. 按 [交接包](../product-shared/templates/product-handoff.json) 补全必要信息并运行 product_bridge.py validate。实现需要非空验收和实际需求产物；源版本与授权由接收方再核验。blocking 问题先处理，其余实验假设可携带验证计划。
3. 发现同一宿主实际 dev/product 角色和技能；产品到开发读取 dev-expert-team-review 后执行，不把指令字符串当调用成功。不在产品子 Agent 内递归启动完整开发团队，由唯一主任务切换阶段或移交调度权。
4. 用户已明确“开发/做出来”且交接就绪时直接执行；仅调研/建议时保持对应边界。缺失能力保存 blocked 原因和恢复入口，不能声称已派发。
5. 回收真实结果：代码/设计版本、产物、执行的检查、未通过/未运行项及产品验收状态。工程测试通过不能代替产品验证。开发反向咨询只返回有版本的决策差异，开发主理人继续原任务。

同 request_id + revision 恢复时先查已有 dispatch，避免重复开发。默认两轮自动澄清后仍有冲突才提具体问题。收到外部交接 JSON 不自动获得任何写权限。
