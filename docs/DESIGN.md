# Design

## Goal

Codex Shadow Mind gives Codex two persistent, independent review roles:

1. `code_auditor` protects code health and project structure after a coherent
   implementation milestone.
2. `goal_auditor` verifies the user's MUST requirements immediately before the
   main agent claims completion.

## Codex mapping

Pi Shadow Mind and Codex have different extension models. This project maps the
portable behavior rather than pretending the runtimes are identical.

| Pi concept | Codex implementation |
|---|---|
| Persistent cognitive role | Named custom agent in `config.toml` |
| Shadow prompt | Read-only agent configuration under `agents/` |
| Report to the main agent | Normal subagent result returned to the parent task |
| Activation policy | Durable delegation protocol in `AGENTS.md` |
| Completion review | Required `goal_auditor` delegation before completion |

There is no probabilistic scheduler in this repository. Codex decides when to
delegate according to the installed instructions. The milestone audit is
bounded and the final acceptance audit is deterministic for material coding
tasks.

## Managed files

The installer writes only the following managed state under `CODEX_HOME`:

```text
config.toml                         # one marked registration block
AGENTS.md                           # one marked delegation block
agents/code_auditor.toml
agents/goal_auditor.toml
shadow-mind/
  shadowctl.py
  config.json
  templates/
```

Existing `config.toml` and `AGENTS.md` content is preserved. Installation stops
if either auditor name is already registered outside the managed block.
Uninstall removes an auditor TOML only when it still matches the installed
template; locally edited files are preserved unless `--purge` is explicit.

## Trust boundary

Both default auditors use `sandbox_mode = "read-only"`. They may inspect the
task and repository but cannot modify files. The main agent remains responsible
for implementation, verification, and deciding how to address audit findings.
