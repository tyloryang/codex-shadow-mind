#!/usr/bin/env python3
"""Install and manage Codex Shadow Mind custom auditors."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

VERSION = "0.1.0"
CONFIG_START = "# >>> codex-shadow-mind:config >>>"
CONFIG_END = "# <<< codex-shadow-mind:config <<<"
AGENTS_START = "<!-- >>> codex-shadow-mind:agents >>>"
AGENTS_END = "<!-- <<< codex-shadow-mind:agents <<< -->"
AUDITOR_NAMES = ("code_auditor", "goal_auditor")


def codex_home() -> Path:
    value = os.environ.get("CODEX_HOME")
    return Path(value).expanduser() if value else Path.home() / ".codex"


def source_root() -> Path:
    return Path(__file__).resolve().parent


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def remove_block(text: str, start: str, end: str) -> str:
    pattern = re.compile(rf"(?:^|\n){re.escape(start)}\n.*?\n{re.escape(end)}(?:\n|$)", re.S)
    result = pattern.sub("\n", text, count=1)
    return result.strip("\n") + ("\n" if result.strip("\n") else "")


def upsert_block(text: str, start: str, end: str, body: str) -> str:
    clean = remove_block(text, start, end)
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    return f"{clean.rstrip()}\n\n{block}" if clean.strip() else block


def config_block() -> str:
    return '''[agents.code_auditor]
description = "Independent auditor for code health and project structure"
config_file = "agents/code_auditor.toml"

[agents.goal_auditor]
description = "Independent acceptance auditor for user-goal consistency"
config_file = "agents/goal_auditor.toml"'''


def assert_no_agent_conflict(config_text: str) -> None:
    unmanaged = remove_block(config_text, CONFIG_START, CONFIG_END)
    for name in AUDITOR_NAMES:
        if re.search(rf"(?m)^\s*\[agents\.{re.escape(name)}\]\s*$", unmanaged):
            raise RuntimeError(
                f"config.toml already defines [agents.{name}] outside the managed block; "
                "rename or remove that entry before installing"
            )


def distribution_root() -> Path:
    root = source_root()
    if not (root / "templates" / "AGENTS.shadow.md").exists():
        raise RuntimeError(f"installation templates are missing under {root}")
    return root


def install_payload(home: Path) -> None:
    source = distribution_root()
    target = home / "shadow-mind"
    target.mkdir(parents=True, exist_ok=True)
    (home / "agents").mkdir(parents=True, exist_ok=True)
    if source != target.resolve():
        shutil.copy2(source / "shadowctl.py", target / "shadowctl.py")
        shutil.copytree(source / "templates", target / "templates", dirs_exist_ok=True)
    for name in AUDITOR_NAMES:
        shutil.copy2(source / "templates" / "agents" / f"{name}.toml", home / "agents" / f"{name}.toml")
    state = target / "config.json"
    if not state.exists():
        shutil.copy2(source / "templates" / "config.json", state)


def set_enabled(home: Path, enabled: bool) -> None:
    state_path = home / "shadow-mind" / "config.json"
    state = json.loads(read_text(state_path) or "{}")
    state["enabled"] = enabled
    atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")

    agents_path = home / "AGENTS.md"
    existing = read_text(agents_path)
    if enabled:
        instructions = read_text(home / "shadow-mind" / "templates" / "AGENTS.shadow.md")
        existing = upsert_block(existing, AGENTS_START, AGENTS_END, instructions)
    else:
        existing = remove_block(existing, AGENTS_START, AGENTS_END)
    if existing:
        atomic_write(agents_path, existing)
    elif agents_path.exists():
        agents_path.unlink()


def install(home: Path) -> None:
    home.mkdir(parents=True, exist_ok=True)
    config_path = home / "config.toml"
    existing = read_text(config_path)
    assert_no_agent_conflict(existing)
    install_payload(home)
    atomic_write(config_path, upsert_block(existing, CONFIG_START, CONFIG_END, config_block()))
    set_enabled(home, True)


def enable(home: Path) -> None:
    if not (home / "shadow-mind" / "templates").exists():
        install(home)
        return
    set_enabled(home, True)


def disable(home: Path) -> None:
    if (home / "shadow-mind" / "config.json").exists():
        set_enabled(home, False)


def uninstall(home: Path, purge: bool = False) -> list[str]:
    preserved: list[str] = []
    config_path = home / "config.toml"
    if config_path.exists():
        atomic_write(config_path, remove_block(read_text(config_path), CONFIG_START, CONFIG_END))
    agents_path = home / "AGENTS.md"
    if agents_path.exists():
        content = remove_block(read_text(agents_path), AGENTS_START, AGENTS_END)
        if content:
            atomic_write(agents_path, content)
        else:
            agents_path.unlink()

    installed = home / "shadow-mind"
    for name in AUDITOR_NAMES:
        destination = home / "agents" / f"{name}.toml"
        template = installed / "templates" / "agents" / f"{name}.toml"
        if not destination.exists():
            continue
        if purge or (template.exists() and destination.read_bytes() == template.read_bytes()):
            destination.unlink()
        else:
            preserved.append(str(destination))
    if installed.exists():
        shutil.rmtree(installed)
    return preserved


def status(home: Path) -> dict[str, object]:
    state_path = home / "shadow-mind" / "config.json"
    state = json.loads(read_text(state_path) or "{}")
    config = read_text(home / "config.toml")
    agents = read_text(home / "AGENTS.md")
    return {
        "installed": CONFIG_START in config and all((home / "agents" / f"{name}.toml").exists() for name in AUDITOR_NAMES),
        "enabled": bool(state.get("enabled")) and AGENTS_START in agents,
        "codex_home": str(home),
        "version": VERSION,
        "auditors": {name: (home / "agents" / f"{name}.toml").exists() for name in AUDITOR_NAMES},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, help="override CODEX_HOME for this command")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("install", help="install or synchronize the auditors")
    commands.add_parser("sync", help="synchronize installed files with this checkout")
    commands.add_parser("enable", help="enable audit delegation guidance")
    commands.add_parser("disable", help="disable audit delegation guidance without removing files")
    commands.add_parser("status", help="show installation status").add_argument("--json", action="store_true")
    remove = commands.add_parser("uninstall", help="remove managed configuration and installed files")
    remove.add_argument("--purge", action="store_true", help="also remove locally modified auditor TOML files")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    home = args.codex_home.expanduser() if args.codex_home else codex_home()
    try:
        if args.command in {"install", "sync"}:
            install(home)
            print(f"Codex Shadow Mind installed and enabled in {home}")
        elif args.command == "enable":
            enable(home)
            print("Codex Shadow Mind enabled")
        elif args.command == "disable":
            disable(home)
            print("Codex Shadow Mind disabled")
        elif args.command == "uninstall":
            preserved = uninstall(home, purge=args.purge)
            print("Codex Shadow Mind uninstalled")
            for path in preserved:
                print(f"Preserved modified auditor: {path}")
        elif args.command == "status":
            result = status(home)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"Installed: {result['installed']}")
                print(f"Enabled: {result['enabled']}")
                print(f"CODEX_HOME: {result['codex_home']}")
                for name, present in result["auditors"].items():
                    print(f"  - {name}: {'ready' if present else 'missing'}")
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
