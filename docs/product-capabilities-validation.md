# 产品专家团 1.2.0 能力升级验收

日期：2026-10-27；基线 9dc152f；直接在 master 修改。macOS arm64、Bash、Python 3.14.6。提交/远端状态以 Git 为准。

## 变更

新增按需用户反馈归纳、UI 完成度方法及轻量模板。反馈保留来源、去重依据、身份/事件不确定性、反证和严重少数问题，再形成机会、决定及需求映射。UI 设计师定义任务和界面契约，reviewer 对实际产物及相关状态独立审查；审美标签不自动阻断，未观察项目不得称通过。现有角色/入口、Graph schema=1 和桥接 schema 保持兼容，无 Agency 安装。

开发交接携带需求/页面/路径 ID、版本/快照、预期/实际、证据、环境、未测、owner 与复验。产品侧定义性能需求口径和依据，开发侧测量和核验实现；两套无需互相安装才能使用自己的方法。

## 验证

- 产品离线测试 62 项通过（实施角色执行并返回 exit 0）；覆盖缺资源预检、受管更新/保护、引用与元数据、既有 Graph/桥接。12 个双端 Skill 格式校验通过；Claude 同源检查 35 文件、0 差异。
- 独立前向执行：8 条合成反馈归为 7 条去重记录，6 个确认用户及未知身份范围，保留反证与待复现隐私风险；只有口述和截图文件名的 UI 交接判为实际检查 not_run、交付 inconclusive，不凭偏好改版。[反馈报告](evidence/capabilities-20261027/qa-results/feedback-report.md)、[UI 报告](evidence/capabilities-20261027/qa-results/ui-report.md)。这些是方法演练，非真实用户研究或实际页面验收。
- 独立代码/安全审查通过，无阻断；Graph/桥接兼容、两仓交接字段一致、安装命名空间和权限不扩大。[结果摘要](evidence/capabilities-20261027/validation-summary.json)。
- 真实旧基线组合升级：导出产品 9dc152f 和开发 b91de1a 包，在隔离中文/空格用户目录分别安装旧版→两套新版→双 check；Codex 与 Claude 个人安装均通过且有备份。[结果](evidence/capabilities-20261027/upgrade-coexist.json)。
- 真实宿主隔离验证：Claude Code 2.1.201 市场安装、发现、更新、卸载通过；Codex CLI 0.164.0-alpha.11.1 发现 6 技能、原生委派 schema 含 8 角色。[日志](evidence/capabilities-20261027/host-smoke.log)。schema 检查仅本机回环捕获，未调用模型。
- 本机 Codex 产品 1.2.0 安装/源码/manifest 41 文件一致；开发 Codex 3.1.0 的 31 文件及已有 Claude 个人版 23 文件同步通过。未新增产品 Claude 全局安装。安装及开发侧定向修正的备份链已核对，Codex config、全局 AGENTS、已存在 Claude settings 哈希未变化。[前](evidence/capabilities-20261027/installed-before.json)、[后](evidence/capabilities-20261027/installed-after.json)。

源码范围见 [版本快照](evidence/capabilities-20261027/source-snapshot.json)。本轮没有真实用户访谈、设计平台写入、实际页面交互或生产性能实验；未做 Windows/Linux 原生验收。新开聊天加载新版指令，若仍使用缓存再重启应用。

开发侧首次性能演练曾输出协议外回执，已保留失败记录并通过一次方法澄清及新的独立复验；详见本目录结果摘要和开发仓库验收报告。此修正未改变产品方法或产品侧验证输入。
