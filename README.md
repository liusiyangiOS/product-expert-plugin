# 产品专家团 · Product Expert Plugin

把一个想法、一个还没有方向的愿望，或一个正在维护的产品，推进到有证据的产品决策、实际界面设计和可执行开发需求。

采用 **`product-` 前缀**。产品战略、用户研究、需求、体验与 UI 都属于产品工作；无需拆成 `idea-`、`design-` 等容易分散的多套命名。每端包含 **8 个专家、6 个工作流、`product-shared`**。安装清单和备份也独立于开发专家团，不占用 `dev-*` 或 `dev-shared`。

本仓库后续修改直接在 `master` 进行，不新建工作分支；具体协作约定见 [AGENTS.md](AGENTS.md)。

提供独立 Codex 包及 Claude 插件/个人安装包。当前为本地 1.1.0 升级，新增按需产品方法与 Graph，仍保留 8 个专家和 6 个入口。新版是否安装与实际验证范围见 [升级验收](docs/product-graph-upgrade-validation.md)；[1.0.0 初始验证](docs/product-validation-report.md) 作为历史记录。

## 四个核心能力

1. **主动想产品**：产品策略师既能陪你讨论已有想法，也能结合你的资源、兴趣和可接触用户提出候选方向、验证方法与放弃条件。不是等你先交完整需求。主动指调用时主动思考，不默认后台定期运行。
2. **实际 UI 设计**：UX 负责路径、信息架构和原型；UI 负责高保真页面、组件、tokens、状态、设计资源和开发标注。支持按实际工具接入不同设计平台，不局限 Figma；没有原生写入能力时明确限制，支持本地 HTML/SVG 备选。不会把静态图冒充可编辑组件稿。
3. **双向开发协作**：`product-dev-bridge` 既把产品需求送入可用的开发专家团，也接收开发侧的规则澄清、设计评审和产品验收请求。已有明确实现授权时直接继续开发；保留版本、接收任务与真实回执，不只输出一段“请开发”的话。
4. **接手已有产品**：产品技术分析师直接只读看代码、接口、页面与运行证据，形成能力地图和建议 backlog。复杂技术问题再向开发专家请求限范围分析，不强制所有项目先走一轮开发团。

## 专家与工作流

| 专家 | 责任 |
| --- | --- |
| `product-team-lead` | 单一调度，管理目标、证据、版本、任务与交接 |
| `product-strategist` | 主动发现机会、推敲定位、比较价值与验证成本 |
| `product-researcher` | 用户/市场/竞品与替代方案研究，核验来源 |
| `product-manager` | MVP、业务规则、优先级、需求和可观测验收 |
| `product-ux-designer` | 用户旅程、信息结构、交互与原型 |
| `product-ui-designer` | 实际高保真设计、组件/状态、设计规范和资源 |
| `product-tech-analyst` | 直接读旧项目代码，建立能力地图和可行性证据 |
| `product-reviewer` | 独立挑战假设、核验需求/设计/实际产品效果 |

| Skill | 入口用途 |
| --- | --- |
| `product-expert-team` | 跨阶段主入口，按当前产品阶段路由 |
| `product-discovery` | 有想法讨论、无想法主动探索机会 |
| `product-project-audit` | 已有产品分析、能力地图和优化建议 |
| `product-design` | UX 原型和实际高保真 UI 交付 |
| `product-dev-bridge` | 产品→开发、开发→产品的双向交接 |
| `product-validation` | 假设验证、需求就绪、设计和产品验收 |

简单讨论不要求八人同时出场。产品与开发切换时保留一个调度者，避免产品团内部再套一层开发团；独立评审需要真实独立执行面，单 Agent 自查会明确标记。

## 1.1.0：借鉴的产品方法与 Graph

参考四个公开项目的一手工作流，补强机会/方案分层、关键假设排序、实验和指标定义、证据驱动的优先级、按风险检查需求就绪。来源、查询时的Star数、已有能力和取舍见 [比较报告](docs/product-reference-comparison-20261027.md)。Star只反映关注度；没有运行外部框架，也不把流行度当有效性证明。

Graph分为三层：

- **产品知识图**：证据/反证→机会与假设→方案/决定→需求→设计/代码→验收/指标，关联来源与版本。
- **任务依赖图**：任务前置条件、owner、写入范围、验收和状态；校验环路，找出依赖就绪任务。
- **代码关系图**：按需复用项目已有Graphify/AST/LSP索引，核对新鲜度后回到源码；不强制安装Graphify。

产品图的 `product_graph.py` 提供4个实际可执行的只读命令：`validate`（结构/悬空引用/任务环）、`impact`（多跳影响及推断依据）、`ready`（依赖就绪，含阻断传播）、`check-files`（本地来源哈希与失效范围）。它不执行任务，不自动提取产品事实，不把远端资料标成已验证，也不把假设变成市场证据。

```bash
python3 packages/codex/skills/product-shared/product_graph.py validate packages/codex/skills/product-shared/templates/product-graph.json
python3 packages/codex/skills/product-shared/product_graph.py ready packages/codex/skills/product-shared/templates/product-graph.json
```

模板是合成示例，真实任务须替换来源与内容。详细数据格式、命令、影响方向和Graphify回退规则见 [Graph协议](packages/codex/skills/product-shared/product-graph.md)。简单讨论无需建图；复杂或跨阶段任务才持久化。产品与开发仍沿用已有桥接，本版没有新增开发侧自动回调或跨聊天通信。

## 安装

安装器需要 Python 3.11+，只复制普通文件，不联网、不改全局配置、不自动安装开发团或设计平台。默认拒绝覆盖同名未受管文件和本机修改；更新有冲突时先审阅，`--replace` 会备份后替换。源码格式适配 macOS/Linux/Windows，实机覆盖以验证报告为准。

### Codex

在本目录运行：

```bash
python3 packages/codex/install.py install --dry-run
python3 packages/codex/install.py install
python3 packages/codex/install.py check
```

Windows PowerShell 使用：

```powershell
py -3 -X utf8 .\packages\codex\install.py install --dry-run
py -3 -X utf8 .\packages\codex\install.py install
py -3 -X utf8 .\packages\codex\install.py check
```

角色复制到当前用户 `.codex/agents/`，技能和 `product-shared` 复制到 `.agents/skills/`。安装记录与备份在 `.codex/product-expert-team/`。新开会话后从 `$product-expert-team` 开始。非默认 `CODEX_HOME` 暂不自动适配，默认安装会拒绝不匹配布局。

### Claude Code 插件

临时加载独立包：

```bash
claude --plugin-dir ./packages/claude
```

或安装本地市场（路径替换为本仓库实际绝对路径）：

```bash
claude plugin marketplace add /absolute/path/to/product-expert-plugin
claude plugin install product-expert-plugin@product-expert
```

新会话调用 `/product-expert-plugin:product-expert-team` 等完整入口。没有声称 GitHub 上已有对应仓库/发布。

### Claude 个人安装

与本团插件方式二选一，不重复加载同名产品团：

```bash
python3 packages/claude/install.py install --dry-run
python3 packages/claude/install.py install
python3 packages/claude/install.py check
```

角色与技能分别在 `.claude/agents/`、`.claude/skills/`；记录在 `.claude/product-expert-team/`。安装器转换插件资源根，调用 `/product-expert-team` 等裸名。非默认 `CLAUDE_CONFIG_DIR` 暂不自动适配。Windows 将解释器改为 `py -3 -X utf8`。

### 更新、卸载与手动复制

更新后重复本端 `install`、`check`；需要备份替换已修改文件时使用 `install --replace`。卸载为本端 `install.py uninstall`，不会删除开发专家团；被修改的产品文件默认保留并报冲突。

手动复制必须保留整个本端 agents/skills 结构，含 `product-shared`。Claude 个人版先用 `install --home <空暂存目录>` 生成再复制。手动复制没有安装清单，不能用 `check` 冒充受管安装；可用 `install --replace` 备份接管。`--home` 是测试/暂存目标，不会自动使主机加载那里内容。

## 使用示例

Codex：

```text
$product-discovery 我还没有点子，每周能投入两天，想做一个自己会用的微信小程序。请主动提出方向并说明怎么验证。

$product-expert-team 我想做一个类似“钱包请等等”的小程序。先研究真实产品，再和我收敛用户、差异和 MVP。

$product-design 根据当前需求制作高保真 UI，优先使用我已连接的设计平台，交付实际源稿、预览和开发标注。

$product-project-audit 分析当前项目的产品能力和体验，只读代码，给我有证据的优化建议。

$product-expert-team 把已确定的 MVP 做出来。产品材料足够后直接衔接开发专家团，按现有项目规则实现并验证。

$product-dev-bridge 我是开发主理人，这个需求没说清删除后能否恢复。请产品侧补规则并返回需求差异，保持当前开发任务。
```

Claude 插件将 `$product-…` 改为 `/product-expert-plugin:product-…`；个人安装改为 `/product-…`。缺少设计/开发能力时明确报告，不伪造创建、派发或交付成功。

## 双向协作怎么落地

`产品探索 → 需求与设计 ↔ 技术可行性 → 开发执行 ↔ 产品澄清 → 产品验收 → 真实反馈`

开发团无需增加另一个重名 role 或 skill；同一宿主安装两个包后，产品团提供的桥接入口对开发主理人也可发现。它是显式的 Agent 协作流程，不是后台 hook：不会改写已安装 `dev-*`，也不承诺开发任务在没有使用入口或路由指令时自动回调。若希望某个项目每次遇到产品问题都这样处理，可采用 [开发侧接入约定](docs/product-dev-integration.md) 中的项目说明。

交接包记录需求版本、真实输入、基线/快照、验收、有效授权出处、未决问题、接收任务 ID 与结果。辅助脚本校验结构和就绪条件，不代替实际调用或授权核实。恢复先查询原任务，避免重复派发。尚未授权实现的产品讨论不会修改业务代码。

## 设计平台支持边界

支持通过平台适配协议接入当前工具能操作的平台；**不是内置所有设计平台 SDK，也没有承诺所有平台都已验证**。运行时发现创建、编辑、导出与预览能力。指定平台不可写时可以先做明确标记的本地备选，但指定平台交付仍记未完成。

原生可编辑设计、本地可编辑 HTML/SVG、静态渲染图、线框和交互原型分别记录。实际高保真 UI 是必要成果；文案说明、流程图、架构图和生图提示词都不能替代它。

## 目录、维护和验证

```text
.claude-plugin/marketplace.json
packages/codex/agents/product-*.toml
packages/codex/skills/product-*/SKILL.md
packages/codex/skills/product-shared/
packages/codex/install.py
packages/claude/                         独立角色、技能、共享资源及安装器
scripts/product_sync_packages.py        维护时生成 Claude 内容，运行时不依赖 Codex
tests/                                  安装、交接与真实宿主发现测试
docs/                                   设计决策、双向接入、场景及验证证据
```

维护角色和 skill 正文以 Codex 包为源，运行 `python3 scripts/product_sync_packages.py` 生成独立 Claude 内容。安装器、元数据和文档各端独立维护；运行时不跨包读取，不用链接。同步脚本发现 Claude 多余源文件会停止，避免自动删除本机定制。

```bash
python3 scripts/product_sync_packages.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tests/product_host_smoke.py --platform both --codex-wire
```

最后一项需要对应 CLI，仅使用隔离空配置及本地请求捕获，不调用远程模型。没有 CLI 时先执行离线检查并明确宿主未验收。

本包默认继承宿主模型，用户显式覆盖优先，不硬编码型号或复用开发团模型缓存。安装/宿主发现通过不代表已做过真实产品、平台设计写入或跨团开发端到端验收。

安装器与隔离宿主测试参考同目录开发专家团，其余产品职责和协议为本包新增；详见 [设计决策](docs/product-design-decisions.md)。本仓库现有许可证见 [LICENSE](LICENSE)；外部参考仅归纳机制并自行实现，来源及许可核验见比较报告。
