# Codex Shadow Mind

**Two persistent, read-only audit minds for Codex developers.**

**为 Codex 开发者提供两个持续存在的只读审计认知核心。**

[English](#english) · [中文](#中文)

Inspired by [pi-shadow-mind](https://github.com/liuzhengdongfortest/pi-shadow-mind)
and adapted to Codex's custom-agent and `AGENTS.md` configuration surfaces.

> This is an independent community project. It is not affiliated with OpenAI
> or the Pi project.

---

## English

### Why Codex Shadow Mind?

An implementation agent has two competing responsibilities: move the task
forward and critically review its own work. Codex Shadow Mind separates those
responsibilities into two named, persistent audit roles:

| Auditor | Trigger point | Responsibility |
|---|---|---|
| `code_auditor` | After a coherent implementation milestone | Detect one concrete code-health or project-structure regression introduced by the current change |
| `goal_auditor` | Before the main agent claims completion | Verify the implementation against the user's current MUST requirements and available evidence |

Both auditors run with `sandbox_mode = "read-only"`. They inspect and report;
the main Codex agent remains responsible for implementation, testing, and the
final decision.

### Architecture

```text
User requirements
       │
       ▼
Main Codex agent ─────────────── implements and verifies
       │
       ├─ implementation milestone
       │          │
       │          ▼
       │    code_auditor
       │    “Did this change introduce a concrete structural problem?”
       │
       └─ before completion
                  │
                  ▼
            goal_auditor
            “Does the result satisfy the user's MUST requirements?”
```

The installer registers both roles as Codex custom agents in `config.toml`
and adds a bounded delegation protocol to the global `AGENTS.md`. Audit
results return to the main task through Codex's normal subagent result flow.

### Runtime boundary

Pi and Codex expose different extension models. This project maps the portable
behavior instead of pretending the runtimes are identical.

| Pi Shadow Mind concept | Codex Shadow Mind implementation |
|---|---|
| Persistent cognitive role | Named custom agent under `[agents.*]` |
| Shadow prompt | Dedicated read-only agent TOML |
| Activation policy | Durable delegation protocol in `AGENTS.md` |
| Report to main | Normal subagent result returned to the parent task |
| Completion review | `goal_auditor` review before a completion claim |

This repository does **not** implement a probabilistic background heartbeat,
hidden session interception, or an independent daemon. Codex is explicitly
instructed to delegate bounded audits at meaningful points in a coding task.

### Requirements

- Codex with custom-agent support
- Python 3.10 or later
- Linux, macOS, WSL, or Windows PowerShell

The current release has been validated with Codex CLI 0.147.0 using strict
configuration loading.

### Quick start

#### Linux, macOS, or WSL

```bash
git clone https://github.com/tyloryang/codex-shadow-mind.git
cd codex-shadow-mind
./install.sh
```

#### Windows PowerShell

```powershell
git clone https://github.com/tyloryang/codex-shadow-mind.git
cd codex-shadow-mind
.\install.ps1
```

The default target is `~/.codex`. To install into another profile, set
`CODEX_HOME` or pass an explicit path:

```bash
python3 shadowctl.py --codex-home /path/to/codex-home install
```

Start a **new Codex task** after installation. Existing tasks do not
retroactively reload global agent registrations or `AGENTS.md` guidance.

### What the installer changes

Only the following managed state is added under `CODEX_HOME`:

```text
CODEX_HOME/
├── config.toml                         # marked custom-agent block
├── AGENTS.md                           # marked audit-protocol block
├── agents/
│   ├── code_auditor.toml
│   └── goal_auditor.toml
└── shadow-mind/
    ├── shadowctl.py
    ├── config.json
    └── templates/
```

The installer:

- preserves all existing `config.toml` and `AGENTS.md` content;
- writes removable start/end markers around its own blocks;
- is idempotent and safe to run again;
- stops instead of overwriting an unmanaged agent with the same name;
- installs both agent definitions with read-only sandbox access.

### Manage the installation

#### Linux, macOS, or WSL

```bash
python3 ~/.codex/shadow-mind/shadowctl.py status
python3 ~/.codex/shadow-mind/shadowctl.py disable
python3 ~/.codex/shadow-mind/shadowctl.py enable
python3 ~/.codex/shadow-mind/shadowctl.py sync
python3 ~/.codex/shadow-mind/shadowctl.py uninstall
```

#### Windows PowerShell

```powershell
python "$HOME\.codex\shadow-mind\shadowctl.py" status
python "$HOME\.codex\shadow-mind\shadowctl.py" disable
python "$HOME\.codex\shadow-mind\shadowctl.py" enable
python "$HOME\.codex\shadow-mind\shadowctl.py" sync
python "$HOME\.codex\shadow-mind\shadowctl.py" uninstall
```

Command behavior:

| Command | Effect |
|---|---|
| `status` | Reports installation, enabled state, and auditor readiness |
| `disable` | Removes delegation guidance while keeping agent definitions |
| `enable` | Restores delegation guidance |
| `sync` | Reapplies the currently installed templates and managed blocks |
| `uninstall` | Removes managed blocks and unchanged installed files |
| `uninstall --purge` | Also removes locally modified auditor TOML files |

### Developer workflow

After installation, a material coding task follows this review loop:

1. The main agent implements and tests a coherent unit of work.
2. `code_auditor` inspects only the changed scope and nearby context.
3. It reports at most one high-confidence, evidence-backed issue.
4. Before completion, `goal_auditor` reconstructs the user's current MUST
   requirements and checks implementation and verification evidence.
5. The main agent resolves confirmed gaps, reruns relevant checks, and reports
   the final result.

The protocol deliberately skips trivial edits and prevents repeated reviews
when no new evidence exists. Audits complement normal tests; they do not
replace them.

### Customize the auditors

The source prompts live here:

```text
templates/agents/code_auditor.toml
templates/agents/goal_auditor.toml
```

Recommended customization workflow:

1. Edit the templates in your checkout.
2. Run `install.sh`, `install.ps1`, or `shadowctl.py install` again.
3. Start a new Codex task.

You can also edit `CODEX_HOME/agents/*.toml` directly for a quick local
experiment. Direct edits are preserved by a normal uninstall, but a later
`install` or `sync` intentionally reapplies the templates and may replace
those edits.

Keep audit roles narrow. A useful auditor should have:

- one stable responsibility;
- the minimum tool and sandbox permissions it needs;
- explicit evidence requirements;
- a strict output budget;
- a clear rule for remaining silent when no actionable issue exists.

### Project layout

```text
codex-shadow-mind/
├── README.md
├── LICENSE
├── NOTICE.md
├── install.sh
├── install.ps1
├── uninstall.sh
├── uninstall.ps1
├── shadowctl.py
├── docs/
│   └── DESIGN.md
├── templates/
│   ├── AGENTS.shadow.md
│   ├── config.json
│   ├── agents/
│   │   ├── code_auditor.toml
│   │   └── goal_auditor.toml
│   └── shadows/
│       ├── code-auditor.md
│       └── goal-auditor.md
└── tests/
    └── test_shadowctl.py
```

### Development and verification

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile shadowctl.py
```

The automated tests cover:

- idempotent installation;
- valid generated TOML;
- enable/disable behavior;
- configuration-conflict detection;
- synchronization from the installed controller;
- conservative uninstall behavior;
- machine-readable status output.

For an isolated installation test:

```bash
python3 shadowctl.py --codex-home ./tmp-codex-home install
python3 shadowctl.py --codex-home ./tmp-codex-home status --json
```

### Safety and rollback

- Auditors are read-only by default.
- Existing Codex files are updated atomically.
- Unmanaged configuration is preserved.
- Same-name unmanaged agents cause an explicit installation error.
- Modified auditor TOML files survive a normal uninstall.

To remove the integration:

```bash
python3 ~/.codex/shadow-mind/shadowctl.py uninstall
```

Use `--purge` only when locally modified auditor definitions should also be
deleted.

### Known limitations

- Activation is instruction-driven, not a probabilistic background scheduler.
- The current task must end before newly installed global guidance is loaded.
- Audit quality depends on the parent task providing relevant requirements,
  changed scope, and verification evidence.
- A read-only auditor can identify a problem but cannot fix it directly.
- This project does not replace tests, code review, CI, or security scanning.

### References

- [Codex documentation](https://developers.openai.com/codex/)
- [Codex subagents](https://developers.openai.com/codex/subagents/)
- [Pi Shadow Mind](https://github.com/liuzhengdongfortest/pi-shadow-mind)
- [Design notes](docs/DESIGN.md)

Released under the [MIT License](LICENSE).

---

## 中文

### 为什么需要 Codex Shadow Mind？

一个实现型 Agent 往往同时承担两项互相竞争的职责：持续推进任务，以及批判性地审查
自己的工作。Codex Shadow Mind 将这两项职责拆分为两个具名、持续存在的独立审计角色：

| 审计者 | 触发时机 | 职责 |
|---|---|---|
| `code_auditor` | 完成一个内聚的实现里程碑后 | 发现本次修改新引入的一个明确代码健康或项目结构问题 |
| `goal_auditor` | 主 Agent 宣布完成前 | 根据用户当前的 MUST 需求和已有证据独立验收实现 |

两个审计者都使用 `sandbox_mode = "read-only"`。它们只负责检查和报告；实现、测试以及
最终决策仍由 Codex 主 Agent 负责。

### 架构

```text
用户需求
   │
   ▼
Codex 主 Agent ─────────────── 实现并验证
   │
   ├─ 完成实现里程碑
   │        │
   │        ▼
   │   code_auditor
   │   “本次修改是否引入了明确的结构问题？”
   │
   └─ 宣布完成前
            │
            ▼
       goal_auditor
       “最终结果是否满足用户的 MUST 需求？”
```

安装器会在 `config.toml` 中将两个角色注册为 Codex custom agents，并在全局
`AGENTS.md` 中加入有边界的委派协议。审计结果通过 Codex 正常的子 Agent 结果流返回
主任务。

### 运行时边界

Pi 与 Codex 提供的扩展模型不同。本项目映射可迁移的行为，不会假装两种运行时完全一致。

| Pi Shadow Mind 概念 | Codex Shadow Mind 实现 |
|---|---|
| 持续存在的认知职责 | `[agents.*]` 下的具名 custom agent |
| Shadow 提示词 | 独立的只读 Agent TOML |
| 激活策略 | `AGENTS.md` 中的持久委派协议 |
| 向主 Agent 报告 | 返回父任务的正常子 Agent 结果 |
| 完成度审计 | 宣布完成前调用 `goal_auditor` |

本项目**不实现**随机后台 heartbeat、隐藏的会话拦截或独立守护进程。它通过明确指令，
让 Codex 在编码任务的关键节点委派有边界的审计。

### 环境要求

- 支持 custom agents 的 Codex
- Python 3.10 或更高版本
- Linux、macOS、WSL 或 Windows PowerShell

当前版本已在 Codex CLI 0.147.0 上通过严格配置加载验证。

### 快速安装

#### Linux、macOS 或 WSL

```bash
git clone https://github.com/tyloryang/codex-shadow-mind.git
cd codex-shadow-mind
./install.sh
```

#### Windows PowerShell

```powershell
git clone https://github.com/tyloryang/codex-shadow-mind.git
cd codex-shadow-mind
.\install.ps1
```

默认安装目标为 `~/.codex`。如需安装到其他配置目录，可以设置 `CODEX_HOME` 或传入
明确路径：

```bash
python3 shadowctl.py --codex-home /path/to/codex-home install
```

安装后请启动一个**新的 Codex 任务**。已经打开的任务不会追溯加载新的全局 Agent 注册
或 `AGENTS.md` 指令。

### 安装器会修改什么

安装器只会在 `CODEX_HOME` 下添加以下受管理状态：

```text
CODEX_HOME/
├── config.toml                         # 带标记的 custom-agent 配置块
├── AGENTS.md                           # 带标记的审计协议配置块
├── agents/
│   ├── code_auditor.toml
│   └── goal_auditor.toml
└── shadow-mind/
    ├── shadowctl.py
    ├── config.json
    └── templates/
```

安装器具备以下行为：

- 保留 `config.toml` 与 `AGENTS.md` 中的全部现有内容；
- 使用可移除的开始/结束标记包围自己的配置；
- 支持幂等重复执行；
- 遇到同名的非受管 Agent 时停止，而不是覆盖；
- 将两个 Agent 都安装为只读沙箱模式。

### 管理安装

#### Linux、macOS 或 WSL

```bash
python3 ~/.codex/shadow-mind/shadowctl.py status
python3 ~/.codex/shadow-mind/shadowctl.py disable
python3 ~/.codex/shadow-mind/shadowctl.py enable
python3 ~/.codex/shadow-mind/shadowctl.py sync
python3 ~/.codex/shadow-mind/shadowctl.py uninstall
```

#### Windows PowerShell

```powershell
python "$HOME\.codex\shadow-mind\shadowctl.py" status
python "$HOME\.codex\shadow-mind\shadowctl.py" disable
python "$HOME\.codex\shadow-mind\shadowctl.py" enable
python "$HOME\.codex\shadow-mind\shadowctl.py" sync
python "$HOME\.codex\shadow-mind\shadowctl.py" uninstall
```

命令行为：

| 命令 | 效果 |
|---|---|
| `status` | 报告安装状态、启用状态和审计者就绪情况 |
| `disable` | 移除委派指令，但保留 Agent 定义 |
| `enable` | 恢复委派指令 |
| `sync` | 重新应用当前已安装的模板和受管理配置块 |
| `uninstall` | 移除受管理配置块和未修改的安装文件 |
| `uninstall --purge` | 同时删除在本地修改过的审计 Agent TOML |

### 开发者工作流

安装后，一个实质性的编码任务会遵循以下审计循环：

1. 主 Agent 实现并测试一个内聚的工作单元。
2. `code_auditor` 只检查本次修改范围及理解它所需的邻近上下文。
3. 它最多报告一个高置信度、具有直接证据的问题。
4. 宣布完成前，`goal_auditor` 重建用户当前的 MUST 需求，并核对实现与验证证据。
5. 主 Agent 处理已确认的缺口，重新运行相关检查，然后报告最终结果。

协议会主动跳过微小修改，并避免在没有新证据时重复审计。审计用于补充正常测试，而不是
替代测试。

### 定制审计者

源提示词位于：

```text
templates/agents/code_auditor.toml
templates/agents/goal_auditor.toml
```

推荐的定制流程：

1. 修改本地仓库中的模板。
2. 再次运行 `install.sh`、`install.ps1` 或 `shadowctl.py install`。
3. 启动一个新的 Codex 任务。

你也可以直接修改 `CODEX_HOME/agents/*.toml` 进行快速本地实验。普通卸载会保留这些
直接修改，但后续执行 `install` 或 `sync` 时会重新应用模板，可能覆盖这些修改。

一个有效的审计者应当保持职责狭窄，并具备：

- 一个长期稳定的职责；
- 完成职责所需的最小工具与沙箱权限；
- 明确的证据要求；
- 严格的输出预算；
- 在没有可执行问题时保持沉默的清晰规则。

### 项目结构

```text
codex-shadow-mind/
├── README.md
├── LICENSE
├── NOTICE.md
├── install.sh
├── install.ps1
├── uninstall.sh
├── uninstall.ps1
├── shadowctl.py
├── docs/
│   └── DESIGN.md
├── templates/
│   ├── AGENTS.shadow.md
│   ├── config.json
│   ├── agents/
│   │   ├── code_auditor.toml
│   │   └── goal_auditor.toml
│   └── shadows/
│       ├── code-auditor.md
│       └── goal-auditor.md
└── tests/
    └── test_shadowctl.py
```

### 开发与验证

运行测试：

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile shadowctl.py
```

自动化测试覆盖：

- 幂等安装；
- 生成 TOML 的有效性；
- 启用/停用行为；
- 配置冲突检测；
- 从已安装控制器执行同步；
- 保守卸载行为；
- 机器可读的状态输出。

如需执行隔离安装测试：

```bash
python3 shadowctl.py --codex-home ./tmp-codex-home install
python3 shadowctl.py --codex-home ./tmp-codex-home status --json
```

### 安全与回滚

- 两个审计者默认均为只读。
- 对现有 Codex 文件的更新采用原子写入。
- 非受管配置会被保留。
- 遇到同名非受管 Agent 时会明确报错。
- 普通卸载会保留修改过的审计 Agent TOML。

移除集成：

```bash
python3 ~/.codex/shadow-mind/shadowctl.py uninstall
```

只有在确定也要删除本地修改过的审计者定义时，才使用 `--purge`。

### 已知边界

- 激活由指令驱动，不是随机后台调度器。
- 当前任务结束后，新安装的全局指令才会被加载。
- 审计质量取决于父任务是否提供了相关需求、修改范围和验证证据。
- 只读审计者可以发现问题，但不能直接修复问题。
- 本项目不能替代测试、代码评审、CI 或安全扫描。

### 参考资料

- [Codex 文档](https://developers.openai.com/codex/)
- [Codex 子 Agent](https://developers.openai.com/codex/subagents/)
- [Pi Shadow Mind](https://github.com/liuzhengdongfortest/pi-shadow-mind)
- [设计说明](docs/DESIGN.md)

本项目采用 [MIT License](LICENSE) 发布。
