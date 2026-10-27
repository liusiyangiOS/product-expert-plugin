# 产品专家团外部机制比较

调研日期：2026-10-27。项目基线 `0633d8b`；以下本地现状以该基线的 Codex 端文件为依据，1.1.0 的实际落地见末节及升级验收。研究只覆盖下列选定源文件，不代表对各仓库所有能力的穷尽。外部仓库 HEAD 和 GitHub 官方源文件通过 GitHub 连接器读取，未运行其工作流，也未验证其实际产品效果。主理人同期核验四仓星标依次为 27,421、7,700、54,620、164,406；这是当时的可变仓库指标，既非全球排名，也不能证明实践有效。

## 结论与当前差距

建议复用现有 discovery、research、validation、产品状态和桥接约定，按需增加轻量的关系、指标和决策记录；不引入外部框架或把所有用户任务变成一套强制流程。外部的机会树和角色文档主要是给模型执行的指令；图形化表达或声称记忆不等于持久知识图、自动指标采集或可靠实验执行。BMad PRD 指令还调用真实脚本维护运行日志，但本次未执行脚本，不推断其在本项目可用。

| 决策问题 | 本项目基线已有 / 部分 / 缺口 | 建议落点 |
| --- | --- | --- |
| 机会、假设、实验 | 已有：`product-discovery/SKILL.md` 和 `product-research.md` 要求场景、假设、证据、最小实验及成功/停止条件；部分：`templates/product-brief.md` 有假设但没有完整关系记录。 | 在较复杂的发现任务按需记录目标→机会→方案→假设→实验及证据链接；未发生实验标记未验证。 |
| 指标可观测性 | 已有：`product-manager.toml` 要求可观测验收；`product-validation` 区分价值验证和交付验收。部分：未在所查模板中规定指标口径、窗口、来源和保护指标。 | 需要衡量效果时补指标定义、分子/分母、时间窗、基线、数据源、目标与护栏；缺数据写未知，不虚构。 |
| 优先级、风险 | 已有：`product-research.md` 主张可解释比较、避免伪精确 ROI；`product-project-audit` 要求投入/风险和优先级。部分：未规定依据情境选择方法的记录形式。 | 写选择理由、证据强弱、依赖与不确定性；量化数据不足时用相对比较，避免把分数当事实。 |
| 需求就绪 | 已有：`product-validation/SKILL.md` 检查业务规则、范围、异常、AC 和阻断项；`product_bridge.py` 真实校验交接包结构与部分就绪条件。部分：结构通过并不核验授权、引用内容和实际验收。 | 针对风险审查决策、取舍、非目标、可测试结果和引用一致性；区分阻断业务问题与可通过实验验证的假设。 |
| 图与恢复 | 已有：`product-workflow-contract.md` 要求复杂跨阶段记录任务依赖和证据；`product-tech-analyst.toml` 可复用已有代码 graph 并核对新鲜度。未在上述基线文件中见自动维护产品知识图的实现，不能据此断言全仓完全不存在。 | 按需用带来源和版本的关系记录支持追溯；任务依赖图、产品知识图和代码图分别标识。由主任务评估实际实现、失效及验证，不把 Markdown 宣称为执行引擎。 |

## 四个一手来源与取舍

1. **phuryn/pm-skills**，HEAD `07b34f64ee828df08953f505b7f747aef85ae7c6`。其 [机会方案树](https://github.com/phuryn/pm-skills/blob/07b34f64ee828df08953f505b7f747aef85ae7c6/pm-product-discovery/skills/opportunity-solution-tree/SKILL.md) 将结果、用户机会、方案和实验分层；[假设排序](https://github.com/phuryn/pm-skills/blob/07b34f64ee828df08953f505b7f747aef85ae7c6/pm-product-discovery/skills/prioritize-assumptions/SKILL.md) 结合影响与风险选择测试；[指标设计](https://github.com/phuryn/pm-skills/blob/07b34f64ee828df08953f505b7f747aef85ae7c6/pm-product-discovery/skills/metrics-dashboard/SKILL.md) 规定口径、数据源、目标和告警。均为文本技能指令；适合借关系与字段，不强制每个机会都造三个方案、也不机械照搬公式。
2. **deanpeters/Product-Manager-Skills**，HEAD `cfcb697f14b8891d8b3ec43c16c3547df3e70e13`。[优先级顾问](https://github.com/deanpeters/Product-Manager-Skills/blob/cfcb697f14b8891d8b3ec43c16c3547df3e70e13/skills/prioritization-advisor/SKILL.md) 根据产品阶段、团队和数据可得性选方法，并复用用户已提供的上下文。借其情境选择思想；不将逐题问答设为默认门槛，也不把 RICE 计算包装为真实数据。
3. **bmad-code-org/BMAD-METHOD**，HEAD `61e01f82644c4bb533750cfa0d6d61ab61d2cc9b`。[PRD 质量规则](https://github.com/bmad-code-org/BMAD-METHOD/blob/61e01f82644c4bb533750cfa0d6d61ab61d2cc9b/skills/bmad-prd/assets/prd-validation-checklist.md) 强调实际决策、可测试完成条件、明确非目标和引用一致性，按项目风险调整审查深度。[PRD 工作流](https://github.com/bmad-code-org/BMAD-METHOD/blob/61e01f82644c4bb533750cfa0d6d61ab61d2cc9b/skills/bmad-prd/SKILL.md) 描述经脚本追加运行日志与恢复；它依赖自身配置与脚本。可借审查问题和决策记录，不引入整套初始化、运行目录及默认研究子代理。
4. **msitarzewski/agency-agents**，HEAD `b37b5bb33b78f2c1d6567d98e25ca818e3259219`。[实验角色](https://github.com/msitarzewski/agency-agents/blob/b37b5bb33b78f2c1d6567d98e25ca818e3259219/project-management/project-management-experiment-tracker.md) 涵盖假设、主要和保护指标、数据质量、结果及风险；[优先级角色](https://github.com/msitarzewski/agency-agents/blob/b37b5bb33b78f2c1d6567d98e25ca818e3259219/product/product-sprint-prioritizer.md) 提及依赖与容量。它们是角色提示，并非验证过的数据平台。可借实验闭环；不采用文件中的统一统计阈值、实验成功率目标、固定 sprint 仪式或额外角色作为通用硬要求。

## 最小接入和回退

优先在现有共享研究/验证约定与模板补必要字段，复杂任务才持久化关系；简单讨论维持轻量。若图索引不可用、过期或缺少可靠来源，用带来源的文本记录和精确检索回退，不能以缺边断言关系不存在。指标缺实际数据时记录采集计划和 unknown；没有真实用户实验时，只交实验设计，不声称价值验证。现有产品→开发桥接边界保持不变，不新增反向自动路由或跨聊天通信。

## 许可证核验边界

本次只按各仓根目录原始 LICENSE 文件记录，不判断特定文件是否另有许可，也不提供法律结论：[pm-skills MIT](https://github.com/phuryn/pm-skills/blob/07b34f64ee828df08953f505b7f747aef85ae7c6/LICENSE)、[Product-Manager-Skills CC BY-NC-SA 4.0](https://github.com/deanpeters/Product-Manager-Skills/blob/cfcb697f14b8891d8b3ec43c16c3547df3e70e13/LICENSE)、[BMAD MIT及商标声明](https://github.com/bmad-code-org/BMAD-METHOD/blob/61e01f82644c4bb533750cfa0d6d61ab61d2cc9b/LICENSE)、[agency-agents MIT](https://github.com/msitarzewski/agency-agents/blob/b37b5bb33b78f2c1d6567d98e25ca818e3259219/LICENSE)。仅归纳机制并自行表述，未复制模板或源码；若未来复制或改编具体材料，应再次检查适用许可和使用场景。

## 1.1.0 实际落地

- `product-shared/product-methods.md` 承接机会/方案、关键假设、指标、优先级和就绪检查；`templates/product-experiment.md` 与 `product-decision.md` 保存实验设计、结果和决策依据。既有 brief、requirement、design-delivery、validation 模板补充对应字段。
- `product-shared/product-graph.md` 定义三类图及来源版本规则，`product_graph.py` 实际提供 validate、impact、ready、check-files；图模板为合成示例，真实任务必须替换证据。
- 8 角色和 6 工作流均引用所需方法与图协议。简单任务按需跳过建图，复杂任务才维护追溯关系；并未增加角色数量、强制会议、数据库或外部框架依赖。
- 现有产品/开发桥接保持原有机制，只允许在已有 artifacts 中附带产品图上下文。详细结果和未验证范围见 [升级验收](product-graph-upgrade-validation.md)。
