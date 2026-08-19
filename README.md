# Codex Shadow Mind

Two persistent, read-only audit minds for Codex: one protects code structure
during implementation, and one independently verifies the user's goal before
completion.

Inspired by [pi-shadow-mind](https://github.com/liuzhengdongfortest/pi-shadow-mind),
adapted to Codex's native custom-agent and `AGENTS.md` surfaces.

## What it installs

```text
Main Codex
  ├─ implementation milestone → code_auditor
  │                              checks code/structure regressions
  └─ before completion         → goal_auditor
                                 checks MUST requirements and evidence
```

Both auditors are read-only and report at most one high-confidence problem per
run. The installer preserves existing Codex configuration and uses removable
managed blocks.

> Important: this is an honest Codex adaptation, not a port of Pi's extension
> runtime. It does not claim probabilistic background heartbeats or hidden
> session interception. Codex performs explicit subagent delegation according
> to durable instructions.

## Install

Linux / macOS / WSL:

```bash
git clone https://github.com/tyloryang/codex-shadow-mind.git
cd codex-shadow-mind
./install.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/tyloryang/codex-shadow-mind.git
cd codex-shadow-mind
.\install.ps1
```

By default the project installs into `~/.codex`. Set `CODEX_HOME`, or pass
`--codex-home PATH`, to target another Codex profile.

Start a new Codex task after installation so the new global instructions and
custom-agent registrations are loaded.

## Manage

Linux / macOS / WSL:

```bash
python3 ~/.codex/shadow-mind/shadowctl.py status
python3 ~/.codex/shadow-mind/shadowctl.py disable
python3 ~/.codex/shadow-mind/shadowctl.py enable
python3 ~/.codex/shadow-mind/shadowctl.py sync
python3 ~/.codex/shadow-mind/shadowctl.py uninstall
```

Windows PowerShell:

```powershell
python "$HOME\.codex\shadow-mind\shadowctl.py" status
python "$HOME\.codex\shadow-mind\shadowctl.py" disable
python "$HOME\.codex\shadow-mind\shadowctl.py" enable
python "$HOME\.codex\shadow-mind\shadowctl.py" uninstall
```

`disable` removes only the delegation instructions. Agent definitions remain
installed and can be re-enabled. `uninstall` preserves auditor TOML files you
edited locally; use `uninstall --purge` only when you want those deleted too.

## Verify

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile shadowctl.py
```

The test suite exercises idempotent installation, valid TOML output,
enable/disable behavior, configuration-conflict detection, and conservative
uninstall behavior.

See [DESIGN.md](docs/DESIGN.md) for the runtime mapping and trust boundaries.

## 中文说明

Codex Shadow Mind 为 Codex 安装两个长期存在的只读审计 Agent：

- `code_auditor`：在一段实质性实现完成后，检查本次改动是否引入明显的代码或项目结构问题。
- `goal_auditor`：在主 Agent 宣布完成前，独立核验用户的 MUST 需求、实现与测试证据是否一致。

它借鉴 Pi Shadow Mind 的“主 Agent 推进、独立认知核心审阅”思想，但使用 Codex 原生的
custom agents 与 `AGENTS.md` 指令实现。它不会假装拥有 Pi 扩展的随机 heartbeat 或后台
会话拦截能力。

安装器只维护带明确标记的配置区块，不覆盖你原有的 `config.toml` 或 `AGENTS.md`。
卸载时，如果你修改过审计 Agent 的 TOML 文件，默认会保留它。
