# 产品专家团 1.1.0 升级验收

日期：2026-10-27。平台：macOS 26.3.1 arm64；Python 3.14.6。源码基线 `0633d8b772bb8cda39777dfb7546e165dd0d23aa`；验证在 `feature/1027/product-graph-upgrade` 工作区进行，随后按用户要求转到 `master` 提交。本报告绑定运行文件快照，完整哈希见 [源码快照](evidence/product-source-sha256-v1.1.0.json)。

## 交付范围

- 结合四个公开项目，补充机会与方案分层、关键假设、实验和指标口径、优先级选择、按风险审查需求就绪。保留 8 角色、6 入口和 product- 命名空间；比较与具体来源见 [研究报告](product-reference-comparison-20261027.md)。
- 区分产品知识关系图、任务依赖 DAG、代码关系索引。新增只读 `product_graph.py` 和产品图/实验/决策模板，接入角色、工作流及共享协议。
- 版本更新为 1.1.0；Codex 为源，Claude 独立包同源生成。桥接 schema 仍为 1，没有增加开发侧自动回调或跨聊天通信，没有修改开发专家团。

## 验证证据

| 验证层 | 实际结果与边界 |
| --- | --- |
| 离线测试 | `python3 -m unittest discover -s tests -p 'test_*.py' -v`，58/58 通过。覆盖图格式、环路/悬空引用、依赖就绪与阻断、影响方向和依据保留、本地来源变化/不安全路径/未核验 URL，以及安装、旧版升级与受管文件保护。[运行日志](evidence/product-upgrade-20261027/unittest.log) |
| 独立 QA | 单独用合成来源执行 validate/impact/ready/check-files。证据变化传播至假设→需求→设计→验收；保留 observed/inferred/hypothesis 及 challenges；URL 返回 remote_unverified/退出码 2；blocked 祖先穿过 done 中间项仍阻断后继。[场景文件与结果](evidence/product-upgrade-20261027/qa-scenario/graph.json)、[检查结果](evidence/product-upgrade-20261027/qa-scenario/changed.json)、[QA 脚本](evidence/product-upgrade-20261027/product_graph_qa_1027.py) |
| 独立代码审查 | 无阻断项。独立运行 58 项测试，并从真实旧基线导出两端包，分别验证旧版安装→1.1.0 升级→check，Codex 37 文件、Claude 31 文件与备份均通过。审查后只修正文案，说明哈希需读取字节和上游阻断语义；未改执行代码。 |
| 独立安全审查 | 无 P0/P1/P2 阻断。24 项图测试和 8 unsafe + 1 missing 临时探针通过，覆盖路径越界、凭据名称、软硬链接、FIFO；输出未包含合成来源内容。脚本不联网、不执行任务；安装白名单拒绝 dev 命名空间。未验证 Windows junction/ADS 或并发恶意目录替换竞态。 |
| 包与文档 | 同源检查 31 文件、0 差异；12 个 Skill 格式校验通过；Claude 根市场和独立插件 validate 通过；git diff --check 通过。 |
| 真实宿主发现 | `python3 tests/product_host_smoke.py --platform both --codex-wire` 通过。Claude Code 2.1.201 在隔离目录真实市场安装、发现 6 技能/8 角色、更新和卸载；Codex CLI 0.164.0-alpha.11.1 发现 6 技能，原生委派请求 schema 含全部 8 角色。本地请求捕获未调用模型，不能据此称实际产品流程验收通过。 |
| 本机 Codex 升级 | 受管安装从 1.0.0 升至 1.1.0，变更 28 文件，最终 37 文件与当前源码一致；实际安装后的图工具 validate 通过。未使用 --replace。 |
| 开发团共存 | 升级前后开发团 28 个受管文件及 config.toml 哈希完全相同；开发团自身 check 通过。[升级前](evidence/product-upgrade-20261027/installed-before.json)、[升级后](evidence/product-upgrade-20261027/installed-after.json) |

旧版自动备份：`~/.codex/product-expert-team/backups/20261027T124533498753Z`，已核对备份与升级前文件哈希一致。Claude 分发包已更新并做隔离宿主验证，本次没有更新用户全局 Claude 个人安装。

## 尚未验证的范围

- 未进行新版端到端模型产品任务、真实用户实验、实际设计平台写入或需求开发交付；结构和方法验证不代表商业效果。
- Graphify 只确认本机 CLI 能力及可选接入协议，本仓没有现成代码图，本次源码审查使用精确检索回退；没有构建新的 Graphify 索引或安装图数据库。
- Windows/Linux 没有原生实机验收，跨平台源码和临时目录测试不替代这些验收。
- 已打开聊天可能仍使用缓存角色指令；使用新版时新开 Codex 聊天，若仍旧则完全重启应用后再打开。当前磁盘安装成功与聊天运行时加载是两个不同证据层。

本报告是本机有界升级验收，不是全平台或真实产品效果证明；提交及推送状态以 Git 历史和远端引用为准。
