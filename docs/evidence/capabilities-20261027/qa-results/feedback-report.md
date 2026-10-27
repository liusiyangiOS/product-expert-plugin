# 反馈归纳与建议

## 范围与口径
合成材料 feedback.json，2026-10-21 至 2026-10-24，纳入全部 8 条，渠道为客服、社区、评论、访谈、问卷；其他渠道未提供。自愿反馈、总体分母未知，不能计算发生率或代表总体。f2 明确转载 f1 且同人、同事件，合并为一次；保留其来源链接。其余不按相似措辞去重。共 8 条记录、7 条去重后反馈记录，其中 6 个明确不同事件 ID，匿名 f4 的事件是否重复未知，故实际不同事件为 6 或 7。已确认 6 个不同用户 u1–u6，f4 身份未知，可能为已有用户或另一用户。所有用户数只限于这份材料。

## 主题与决定
| 相对优先级 | 主题、证据及反证 | 建议和依据 | 风险、投入与验证 |
| --- | --- | --- | --- |
| P0 | 隐私隔离：f7 / support/ticket-51，u5，退出后下一位登录者看到私人记录。1 条、1 个已确认用户；复现和影响范围未知。 | 立即作为严重风险调查并限制暴露：在隔离环境复现账号切换，核对本地缓存、账号绑定及退出清理；在未证实前不指定根因。必要时按实际授权先采取临时防护。 | 潜在隐私泄露影响大，即便少数也优先；投入及方案待工程评估。验证不同账号切换、退出后及重启后不可见他人记录；未实际执行。 |
| P1 | 保存后的列表可见性：f1 / support/ticket-18 与转载 f2 / community/post-23 同一次；f3 / support/ticket-31 独立一次；f4 / review/anon-1 身份和事件未知。至少 2 个已知用户、2 个独立已知事件，另 1 条未知身份记录。反证 f8 / survey/r8，u6 保存后立即看到。 | 优先调查触发条件，建议保证成功保存后当前列表及时呈现该条目；保存失败则清晰提示并保留输入。不能断言数据丢失或普遍发生。 | 核心任务信任受损；投入未知。隔离环境覆盖新建、筛选、账号、刷新和失败/重试，记录成功响应与可见结果；对照 f8 场景。 |
| P2 | 清理效率与误删恢复：f5 / support/ticket-40 希望批量删除；f6 / interview/session-2 反对一键删除，担心误删后找不回。各 1 个已知老用户，不是同一意见。 | 暂不直接采用一键删除。先研究带明确选择、数量确认和可恢复机制的批量清理候选，同时比较不开发功能的现有逐条清理指引。 | 误删风险高；范围、成本及现有恢复能力未知。先测试用户能否辨认选择范围并恢复误删，再决定实现；不承诺已有回收站。 |

## 首个需求草案：账号切换时保护记录
目标：同一设备切换账号时，当前账号只能看到其有权访问的记录。候选验收：账号 A 新增私人记录，退出后 B 登录，B 的列表、详情和缓存恢复路径均不显示 A 记录；B 退出后 A 重新登录，A 的合法记录仍可访问。离线、共享数据、权限模型及服务端/本地边界尚未给出，需先确认并与开发制定测试数据和范围。优先级是风险判断，不代表真实故障已复现或修复方案已确定。

## 证据索引及缺口
f1–f8 的稳定 ID、来源、时间、人群均见同目录上级 fixtures/feedback.json；上表保留了所有条目的关联。匿名评论、用户规模、渠道覆盖、系统版本和复现步骤未知。无需联网或联系反馈者；未读取代码、运行产品或测量用户效果。可用现有材料建议优先调查，不能从中推断实际能力、部署状态、总体满意度或收益。GRAPH=not_needed：本次为单份材料的局部分析，以表格保留主题→证据→决定，未建立持久跨阶段图。

## 实际读取文件及 SHA-256

- `/Users/liusiyang/.agents/skills/dev-shared/expert-platform.md`: `a6633604fe5c9ba367e54b828fc1e682cae3e640ea4c477d09949d10610f64ae`
- `/Users/liusiyang/.agents/skills/dev-shared/expert-role-contract.md`: `5663aa08e117c042543612453b8663659c5f4b0f8a49782be6ddcefffe888d0f`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-project-audit/SKILL.md`: `16bb3b216b782260f58561a382f4a98bbccf0ed345cfceaaa08c0754070498f7`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-validation/SKILL.md`: `a4340cbee85236d202122e11cf5ba7bbe1d41b8226fa5b6fe7116fc6d9327603`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product-runtime.md`: `589e1f0039d6f812d840c3f06c06801f6872f04cd4374281a2062526906cf31e`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product-workflow-contract.md`: `d9a72df63c5157f7dfdd873aa7efde1b4727e1265ed907263501635316d1b726`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product-research.md`: `603400d61928520636d091dd195c2313654db29ba03af64fc416fb2aa5a1fdaa`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product-feedback.md`: `3481e24072c1fd655975432575120384bb56ff781d634061304f48fe6e7fd2b7`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product-ui-review.md`: `dc5c551ad2eeabb02a7311ba63029e72d807fdb9caf1f1b03e30db56ad7c4f34`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product-methods.md`: `ac7368fe7429bff8e12e398f429a95c1b5d8462910f45f1a2d4d2098905d4a3a`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product-graph.md`: `6eedd7b51c4b16c674114b41531002b912e67444a82d9a5637c65329c4311918`
- `/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/templates/product-validation.md`: `86d6af0cd23beb79318ad3dc69828f08c7df54e25881219ec577b2517d15ac38`
- `/var/folders/2r/3t3s5pkj769fkwqc1_d3qgf0b0g8g4/T/expert-capabilities-htb3nrvc/fixtures/feedback.json`: `5f85a2818734e0760c4b9a0576bfabc6de11bc55e7ce9097038f50694f733718`

执行环境：macOS Darwin arm64，Bash；以本地文件读取、`shasum -a 256` 和 Python 标准库离线分析。无联网、联系用户、启动服务或负载；未修改仓库或真实安装。
