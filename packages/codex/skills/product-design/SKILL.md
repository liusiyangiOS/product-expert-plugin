---
name: product-design
description: 根据需求制作 UX 原型及实际高保真 UI、组件与开发标注，定义 UI 完成度契约；按可用能力适配设计平台。
---

# 产品界面设计

读取 [运行约定](../product-shared/product-runtime.md)、[工作流约定](../product-shared/product-workflow-contract.md) 和 [平台交付协议](../product-shared/product-design-platforms.md)。先确认需求版本、用户任务、指定平台/现有文件、目标设备和交付是否要求原生可编辑。

product-ux-designer 先定义核心路径、信息结构和必要状态；已有充分原型则复用。product-ui-designer 将其制作成实际高保真页面与组件，保留现有品牌资产。不以架构图、线框或 prompt 代替 UI 成果。

工具可写时实际创建/编辑，回读或导出并预览；用户指定 Figma 等平台时先加载该平台相关技能，其他平台同样核验工具能力。无法完成指定平台写入时明确缺口，能独立推进则先交付标注格式的本地 HTML/SVG 备选，指定交付仍未完成。

至少覆盖核心任务涉及的页面、可见状态与关键交互，并附设计 tokens、组件规则、资源、开发标注、需求映射及预览证据。按实际产物声明 ARTIFACT_KIND 与可编辑程度，不承诺一键无损跨平台。

product-reviewer 对固定产物检查需求一致性、视觉层级、可访问性和完整性；如果没有渲染能力如实记录 not_run。交接使用 [设计清单](../product-shared/templates/product-design-delivery.md)，需要开发时送 product-dev-bridge。

## 设计变更追踪

已有产品图或跨页面需求时，按 [Graph 协议](../product-shared/product-graph.md) 保留需求→页面/组件→验收关系及真实平台版本。设计改动先核对受影响的需求与状态，由主理人合并增量；本地文件哈希不能代替远端平台回读。小型设计保持轻量，不为图强制扩大交付。

## UI 完成度契约与审查

设计交付或界面评审按需读取 [UI 方法](../product-shared/product-ui-review.md)。product-ui-designer 负责用户任务、信息/操作层级、密度/交互/窄屏和品牌约束契约；product-reviewer 对固定版本的实际界面与相关状态独立审查，按 [记录模板](../product-shared/templates/product-ui-review.md) 交付可定位问题、影响、未测与复验方法。工程实现验证沿用 product-dev-bridge。
