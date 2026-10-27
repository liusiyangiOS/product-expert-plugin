---
name: product-design
description: 根据需求制作 UX 原型及实际高保真 UI、组件与开发标注；按可用能力适配不同设计平台。
---

# 产品界面设计

读取 [运行约定](../product-shared/product-runtime.md)、[工作流约定](../product-shared/product-workflow-contract.md) 和 [平台交付协议](../product-shared/product-design-platforms.md)。先确认需求版本、用户任务、指定平台/现有文件、目标设备和交付是否要求原生可编辑。

product-ux-designer 先定义核心路径、信息结构和必要状态；已有充分原型则复用。product-ui-designer 将其制作成实际高保真页面与组件，保留现有品牌资产。不以架构图、线框或 prompt 代替 UI 成果。

工具可写时实际创建/编辑，回读或导出并预览；用户指定 Figma 等平台时先加载该平台相关技能，其他平台同样核验工具能力。无法完成指定平台写入时明确缺口，能独立推进则先交付标注格式的本地 HTML/SVG 备选，指定交付仍未完成。

至少覆盖核心任务涉及的页面、可见状态与关键交互，并附设计 tokens、组件规则、资源、开发标注、需求映射及预览证据。按实际产物声明 ARTIFACT_KIND 与可编辑程度，不承诺一键无损跨平台。

product-reviewer 对固定产物检查需求一致性、视觉层级、可访问性和完整性；如果没有渲染能力如实记录 not_run。交接使用 [设计清单](../product-shared/templates/product-design-delivery.md)，需要开发时送 product-dev-bridge。
