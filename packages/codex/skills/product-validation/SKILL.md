---
name: product-validation
description: 独立检查产品假设、需求、设计或实际实现，制定验证并区分交付质量与真实用户效果。
---

# 产品验证与验收

读取 [运行约定](../product-shared/product-runtime.md)、[工作流约定](../product-shared/product-workflow-contract.md) 和 [研究协议](../product-shared/product-research.md)。明确本次被审版本、阶段、验收目标与真实可用证据；不自动启动生产代码修复。

product-reviewer 独立评审，按任务选择而非强制全做：
- 机会验证：问题证据、替代方案、价值假设、可失败的实验。
- 需求就绪：核心规则、范围、异常、AC、阻断问题与技术可行性。
- UX/UI：实际产物、流程完整性、必要状态、可访问性与真实预览。
- 开发后验收：需求/设计与实际行为的差异，引用开发测试回执并注明覆盖边界。
- 用户效果：实际用户任务、样本与测量，区分首次理解、持续使用和付费，避免以点击量替代价值。

每项发现给证据、影响、优先级、是否阻断和具体修订建议。输出 pass/fail/not_run/inconclusive 及适用范围；没有用户数据可通过需求可实施性审查，但用户价值仍未验证。缺独立执行面时标记自查，不冒充独立评审。

产品文档/设计修订回对应 owner；代码缺陷经 product-dev-bridge 返回开发，不由 reviewer 偷改。遵守同版本两轮自动修订上限。使用 [验证记录](../product-shared/templates/product-validation.md)，只在相关输入变化后重验。
