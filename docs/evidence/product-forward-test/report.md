# 产品专家团独立前向测试

日期：2026-10-27。范围：packages/codex 的 8 个角色、6 个技能、product-shared 协议/模板/校验器。未修改插件、未启动开发团队或业务开发、未向外部平台写入。全部生成物位于本临时目录。场景 1–3 是独立阅读后按指令作出的行为模拟，场景 4 额外运行真实 Python CLI；均不构成宿主端到端验收。Python 3.14.6。

## 场景 1：没点子，两天，自用微信小程序

入口：product-discovery；主任务直接承担主理人和策略思考即可，不需要八角色齐开。不先要求用户写 PRD，也不因为“想做”自动创建代码项目。

实际初步提案（均为未验证假设，个人使用场景未知）：

| 候选 | 问题与替代 | 两天内范围 | 最小实验与成功/停止条件 |
| --- | --- | --- | --- |
| 出门防漏清单 | 出门后忘记钥匙/耳机；现有替代是备忘录 | 场景模板、开始一次检查、勾选；暂不做定位和自动提醒 | 先用备忘录跑3次出门，若确实减少漏带且愿意继续打开则做原型；若无漏带问题或备忘录足够则停止 |
| 家里放哪了 | 低频物品找不到；替代是相册+文字搜索 | 物品名、位置、检索；照片可后置 | 录入10件物品后做3次查找任务；若录入负担比查找收益大则停止 |
| 周末三件事 | 想做的事情太多；替代是纸笔/待办 | 每周最多3项、完成、周末复盘；不做社交和AI拆解 | 先用纸笔完成一个周末；若不需要再次使用则停止，不以新鲜感判断长期价值 |

条件推荐：优先试“出门防漏清单”，原因是核心路径少、两天可验证，但用户若没有漏带问题应淘汰。投入为相对估计，未确认技术栈、微信开发环境和发布条件，不承诺两天正式上线。若接着做研究，会现场核验当前微信能力/规则和替代工具，不虚构竞品证据。

产物：本轮直接回复候选/取舍/实验即可；方向选定且跨阶段继续才写 product-brief。停止于用户选方向或确认问题，不设置监控、不直接进入开发。未发现阻断缺陷。

## 场景 2：已有产品，只读，路由存在但没有运行证据

入口：product-project-audit，product-tech-analyst 直接阅读具体项目指令与核心旅程源码。实际报告条目为“功能路由：源码存在；接入情况需继续查调用链/开关；运行验证 not_run；部署/用户使用 unverified”。不会仅凭路由把用户目标标成完整 implemented，也不把没有运行证据写成 absent。

动作：绑定 HEAD+相关脏改动指纹，追踪路由→页面→接口→权限/开关→持久化；只有源码证据的能力与真实业务成功分栏。建议先验证该用户旅程，再决定优化优先级；不虚构转化率/用户满意度。请求未提供实际目标仓库，当前模拟没有项目级代码结论。

产物：现状能力矩阵、证据索引、建议 backlog、需求草案及用户证据缺口。停止于分析交付；不启动服务、不安装依赖、不修代码、不启动完整开发团。未发现阻断缺陷。

## 场景 3：指定 Figma 可编辑高保真，但只有读取及本地 HTML 渲染能力

入口：product-design。明确能力矩阵为 Figma read=yes / create=no / edit=no，本地 HTML 可编辑和渲染可用。先加载必要 Figma 技能再执行合法读取；复用既定需求、文件及品牌，UX定义路径/必要状态，UI准备页面/组件。

独立可推进动作：制作带真实内容的本地 HTML/CSS 高保真源、tokens、组件状态、交互标注与需求映射，真实渲染预览。设计清单标记 ARTIFACT_KIND=local-editable；截图单独标记 static-render。指定 Figma 原生可编辑交付仍 blocked/capability_missing，不能把截图或“可导入HTML”称成已完成 Figma。

产物：本地备选源+预览+设计清单+明确未完成的 Figma 项。停止于本地交付/无法写入的边界，恢复入口为具备 Figma 创建编辑工具后创建→回读→预览。模拟没有实际需求正文或设计资产，因而未编造一份 UI，不宣称真实渲染通过。未发现协议阻断缺陷；真实平台端到端 not_run。

## 场景 4：授权开发，反向澄清，再恢复

入口：product-dev-bridge。主理人复用有效授权，验证需求/验收/设计与合法基线，读取同宿主开发入口后实际切换阶段；不再次索要开发许可，也不在产品子 Agent 内套完整开发团。

预期执行轨迹：父 implement ready→in_progress；发现删除恢复规则未定，阻断受影响实现；开发仍为唯一调度者，发子 dev-to-product/clarify，parent_request_id 指向父请求，return_to 指向原开发阶段；产品经理读取既有规则，只返回有版本的决策差异。不能根据AI共识擅定恢复期；两轮内仍有关键业务冲突时向用户提出具体选项。解决后 revision 增加、记录 delta/失效AC、通知原接收者，并查询/恢复原开发任务，不重新启动一套开发。

真实 CLI 校验结果（JSON中的授权、任务ID、基线及恢复期全部为合成测试数据，不是真实派发或用户批准）：

| 文件 | exit | 结果 |
| --- | --- | --- |
| 01-implement-ready.json | 0 | 初始实现包可表达 |
| 02-implement-in-progress.json | 0 | 同会话阶段及派发回执可表达 |
| 03-parent-blocked.json | 0 | 父任务带 blocking 问题可暂停 |
| 04-clarify-blocking-ready.json | 1 | “未通过：存在阻断未决项” |
| 05-clarify-mislabeled-nonblocking.json | 0 | 仅把同一问题 blocking 改为 false 后通过 |
| 06-clarify-returned.json | 0 | 版本决策差异可放入结果并返回 |
| 07-resume-existing-dev-task.json | 0 | revision=2 保留原 task_id 可表达恢复 |

## 确认缺陷

P1：反向澄清无法携带真正阻断实现的问题进入就绪状态。

位置：packages/codex/skills/product-shared/product_bridge.py:63–68，尤其第68行。对所有 ACTIVE 状态一律拒绝 blocking open_questions，没有区分 implement 与 clarify/feasibility。契约 product-dev-contract.md:16 说 blocking 阻止相关实现，:27 允许开发反向澄清规则；product-dev-bridge/SKILL.md:11 强制先校验。按真实含义标注 blocking=true 的 child clarify 会在执行前失败，无法启动解决阻断的咨询；调用方只能把真实阻断改成 false、移出规定字段、或绕过校验，均损害契约。

复现证据：04 与05只差 blocking 布尔值，CLI exit 1→0。建议让实现就绪门禁与澄清输入分开定义，例如允许 clarify 携带“阻断父实现”的问题，同时保持父实现阻断；本轮未修改。

其余已通过的 JSON 仅证明结构能表达，未证明字段真实性、引用已被开发接收、去重查询执行、同宿主角色加载或恢复成功。validator 本来就声明不是调度引擎，因此没有把缺少自动调度/防重复数据库当成缺陷。


## 修复后独立复验

复用原始 04-clarify-blocking-ready.json，不改变 blocking=true；另由原始实现就绪包添加同一 open_questions 生成 08-implement-blocking-ready.json。分别实际调用最终 Codex/Claude 校验器。

- codex / 04-clarify-blocking-ready：exit 0，符合预期。
- codex / 08-implement-blocking-ready：exit 1，符合预期。未通过：存在阻断实现的未决项
- claude / 04-clarify-blocking-ready：exit 0，符合预期。
- claude / 08-implement-blocking-ready：exit 1，符合预期。未通过：存在阻断实现的未决项

结论：原 P1 已在两份最终校验器中消失。澄清可以携带阻断父实现的问题；实现请求本身仍受阻断门禁约束。两份校验器 SHA256 一致：b497cc11b841d9e08614c9c5516889ad10591bd33e57137206150322e07235bd。证据见 final-retest-results.json。此为真实 CLI 回归，未增加宿主跨团队或平台端到端验证。
