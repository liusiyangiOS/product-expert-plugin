# 产品专家团 1.0.0 初始验证报告

日期：2026-10-27（Asia/Taipei）。范围：本地 1.0.0 源码；macOS、Python 3.14.6、Claude Code 2.1.201、Codex CLI 0.164.0-alpha.11.1。

## 结论

插件源码、双端发行、隔离安装及宿主发现检查通过。每端 8 个专家、6 个 skill，公共资源目录为 product-shared。未安装到真实个人目录、未修改开发专家团、未初始化 Git、未提交/推送或发布。

这是安装与协议层验收；不表示真实设计平台、实际业务开发和市场效果已经验收。

## 自动检查

| 检查 | 结果 | 范围 |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py' -v` | 26 tests / OK | 名称、独立包、引用、元数据、安装/更新/卸载、冲突预检、备份、路径与清单保护、异常回滚、双向交接条件 |
| `python3 scripts/product_sync_packages.py --check` | PASS | Claude 生成内容与 Codex 源角色/技能一致，运行文件独立 |
| skill-creator `quick_validate.py` | 12 / PASS | 两端各 6 个 SKILL.md 的 frontmatter、名称与脚手架检查 |
| `claude plugin validate .` 及 `packages/claude` | PASS | 本地市场及 Claude 插件元数据 |
| Claude 隔离真实 CLI | PASS | 市场添加、插件安装、6 skills / 8 agents 发现、缓存文件一致、更新、卸载 |
| Codex 隔离真实 CLI | PASS | 宿主上下文发现全部 6 个 skill；原生委派工具 schema 包含全部 8 个角色 |

安装测试使用临时用户目录；包含中文/空格路径。设置开发团文件、开发团安装清单与用户配置为 sentinel，产品团安装、更新和卸载后仍保持原内容。不会用真实用户配置或凭据证明安装可用。

Codex 角色测试在 127.0.0.1 捕获宿主请求，故意返回拒绝以阻止模型推理，不调用远程模型。初次 sandbox 拒绝本机端口绑定；经工具批准仅重跑该隔离检查后通过。Windows/Linux 未运行的范围不能由 macOS 结果推出。

## 独立行为验证及修复

独立子 Agent 对四种请求作前向验证：无点子提案、已有产品只读分析、指定 Figma 但工具只读、授权开发后反向澄清与恢复。

- 前三种场景按实际资料和能力边界选择正确入口；属于协议行为模拟，没有生成真实产品设计或读取真实目标产品。
- 第四种场景执行了真实交接 JSON 校验，发现 P1：校验器一律拒绝 blocking 问题，使澄清任务无法接收它要解决的问题。
- 修复为仅 implement 就绪门禁拒绝 blocking；clarify 和 feasibility 可带阻断父实现的问题。
- 独立复验复用原始澄清 JSON，Codex/Claude 均 exit 0；同类 blocking 实现包两端均 exit 1。没有放开实现门禁。

[独立完整报告](evidence/product-forward-test/report.md) 保留初次发现与修复后结论；[最终复验回执](evidence/product-forward-test/final-retest-results.json) 记录真实退出码与校验器哈希。目录内 JSON 都是合成测试材料，字段中的授权、任务 ID、基线和业务规则不是真实用户批准或实际派发记录。

两端最终 product_bridge.py 的 SHA-256：

```text
b497cc11b841d9e08614c9c5516889ad10591bd33e57137206150322e07235bd
```

## 尚未执行

- Windows、WSL、Linux 的实机安装与宿主发现。
- 真实 Figma / Penpot / Sketch 等平台的创建、编辑、导出及预览；本包提供能力发现/交付协议，未内置全平台 SDK。
- 接收真实产品需求，实际派发开发专家并完成业务开发、反向澄清及恢复的端到端验收。
- 真实用户研究、可用性实验、留存/收入等产品效果验证。
- 个人目录正式安装、新会话加载、远端 CI 或公开发布。

## 可复现命令

在仓库根执行：

```bash
python3 scripts/product_sync_packages.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tests/product_host_smoke.py --platform claude
python3 tests/product_host_smoke.py --platform codex --codex-wire
```

真实宿主检查需要已安装对应 CLI；角色 schema 检查需要允许本机回环监听。缺少能力时记录 not_run/环境限制，不称插件通过端到端验收。运行文件快照见 [product-source-sha256-v1.0.0.json](evidence/product-source-sha256-v1.0.0.json)。
