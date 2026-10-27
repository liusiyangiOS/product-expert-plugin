# 产品 Graph：关系、依赖与变更影响

Graph 是本包的按需工作方法。复杂任务维护可查询、带来源与版本的关系；简单问答或局部需求可记录 `GRAPH=not_needed` 并说明理由，无需先建图。

## 三种图分别使用

| 图 | 回答的问题 | 载体 |
| --- | --- | --- |
| 产品知识关系图 | 这个需求服务谁、依据什么、关联哪些方案/设计/验收/指标；证据失效影响哪些结论？ | 本包 product-graph.json 的 sources/nodes/edges |
| 任务依赖图 | 哪些工作已具备前置条件、哪些被阻断、谁负责什么文件？ | 同一文件的 tasks，必须是有向无环依赖 |
| 代码关系图 | 用户路径经过哪些路由、接口和模块，变更影响哪里？ | 已有 Graphify/LSP/AST 等索引，关键关系回到源码 |

产品图不是用户证据，代码图不是已上线证明；任务 DAG 不是自动调度引擎。下面的脚本只读校验和遍历人工/Agent 维护的图，不自动从代码或文档提取产品事实，不创建专家，不执行图中的指令。

## 什么时候建与读

1. 主理人确认实际项目根、问题和范围。跨阶段、多方案、多模块或需要复用证据时，先检查当前任务记录中的产品图和项目已有代码索引；不扫描整个用户主目录。
2. 无产品图且持久追溯有收益时，将 [模板](templates/product-graph.json) 复制到当前任务文档目录，逐项替换成实际来源、版本和关系。模板是合成例子，不可原样作为业务证据；无可靠证据的内容用 hypothesis/inferred 标记。
3. 在上下文中只传问题相关节点、路径、证据和盲区，避免每次加载整份图。精确查询/源码足够时直接使用，不为了 Graph 扩大任务。
4. 修改或消费图前先校验；本地来源执行 check-files，再回到关键文档/源码核验。URL 和远端设计文件需用相应工具核验版本/实际内容，不能因本地哈希没变就称全图新鲜。

## 数据约定

`schema_version=1`，顶层 `sources / nodes / edges / tasks` 均为数组，允许没有任务。ID 稳定，重命名显示标题不重建 ID。

- sources：`id / kind(file|url) / ref / version`。file 的 ref 是相对项目根的安全路径，version 是 `sha256:<64位十六进制>`；url 的 version 是读取时的版本/时间定位，脚本不联网。只登记必要、已获授权的文件，不登记凭据或无关个人数据。
- nodes：`id / type / label / sources / status`。type 为 outcome、opportunity、solution、hypothesis、evidence、experiment、decision、requirement、design、acceptance、metric 或 code。status 如 proposed/validated/rejected/unverified 由任务使用者解释，不是脚本验证过的真实性结论。
- edges：`from / to / relation / basis / sources`。basis 为 observed、inferred 或 hypothesis；observed 必须引用至少一个已有 source，但有引用仍需人工核对内容是否真正支持关系。
- tasks：`id / depends_on / owner / write_scope / status / acceptance / evidence`。status 为 pending/running/done/blocked/skipped。done 必须附实际验收记录；skipped 只允许 optional=true 且有 skip_reason。任务、来源、节点 ID 各自唯一，不允许悬空依赖和任务环。

### 关系方向

除 depends_on 外，from→to 表示上游变化可能影响下游：证据 supports/challenges 假设，机会 motivates 方案或需求，需求 realized_by 设计/代码，需求/设计/代码 verified_by 验收或实验，目标/实验 measured_by 指标。`A depends_on B` 表示 A 依赖 B，影响传播时从 B 走向 A。产品关系可以有环，但不会允许任务依赖环。

图可表达反证和已否定方案。impact 返回的是可能受影响项及路径依据；经过 inferred/hypothesis 的路径仍是不确定推断，不自动升级为事实，也不因缺边判断没有关联。

## 工具与命令

从本端已安装 product-shared 解析 `product_graph.py` 的绝对路径；Python 3.11+，跨平台路径作为完整参数传入。

```text
python3 <本端脚本绝对路径> validate <产品图路径>
python3 <本端脚本绝对路径> ready <产品图路径>
python3 <本端脚本绝对路径> impact <产品图路径> <节点ID>
python3 <本端脚本绝对路径> check-files <产品图路径> --root <项目根目录>
```

validate 只检查结构；ready 只计算依赖满足的 pending 任务，任一上游仍为 blocked 时不会放行，即使中间任务被标为 done。不证明授权、验收真实性或可并行。主理人仍核对共享文件/设计画板/服务冲突与实际并发槽位。

check-files 只检查显式登记的本地文件，报告 changed/missing/unsafe/remote_unverified 和关联影响范围，只为计算哈希读取文件，不输出文件内容，不自动访问 URL。路径越界、外部链接与凭据路径不能作为可验证来源。退出码 0 表示该命令检查通过，1 表示输入/图格式错误，check-files 的 2 表示存在失效、不安全或未核验来源。URL 未核验也会返回 2，需要补充真实核验记录；不能把这个退出码当成软件运行失败或偷偷删除 URL 来变绿。

## 图谱新鲜度与恢复

来源变更后，由主理人运行影响查询，标记相关节点/需求/设计/验收待复核，再核验内容、更新来源哈希和版本。不要仅重算哈希就宣称结论仍然成立，也不要用旧测试证明新需求。只重验受影响部分，不机械全量重做。

同一产品图只有一个写入负责人，其余专家返回带证据的增量。主理人先合入增量、校验，再派发下游。恢复时核对图、任务账本、实际源文件和已有接收任务；不把 running 自动改为 done，不重放外部写入。

交接摘要包含 `GRAPH=used|fallback|not_needed|stale_or_unknown`、图路径/版本/覆盖范围、查询问题、关键路径和来源、推断/盲区、受影响的需求与待重验项。产品→开发时放入现有 artifacts 及上下文即可，不升级 bridge schema，也不修改开发团的路由。

## 可选 Graphify / 代码索引

product-tech-analyst 遇到跨模块或多跳代码关系时，优先检查项目 `graphify-out/graph.json` 或已有索引。核对覆盖范围、manifest、HEAD 和相关未提交内容；时间戳新不等于源码匹配。Graphify 的 JSON 与本包 schema 不兼容，不直接传给 product_graph.py；将核验过的代码位置和关系作为来源/摘要关联到产品图。

有工具时先检查本机 `graphify --help` 并读对应 skill，使用实际支持的 query/path/affected；例如查询“这个用户流程依赖哪些模块”后回到关键符号核验。无图、过期或查询失败则回退 rg/AST/LSP，并记 fallback/stale_or_unknown，不能硬猜。

确有重复查询收益且已授权时才构建或更新项目索引；纯代码分析优先本地 AST，按真实 CLI 支持使用 code-only，不为了查代码额外调用语义模型。构建前排除凭据、依赖、构建产物与无关文件。不会自动安装 Graphify、上传私有源码、启动数据库/MCP、安装全局 hook 或启用后台监听。
