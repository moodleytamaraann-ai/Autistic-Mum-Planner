"""Copy setup/playbook/*.md into the agency-playbook memory store.

Run once after `ant apply`, and again after management edits a playbook file.
Existing files are left alone unless --update is passed. Every update is kept as a
memory version, so earlier rules stay auditable.
"""

import json
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK_DIR = ROOT / "setup" / "playbook"


def store_id() -> str:
    lock = json.loads((ROOT / "claude-lock.json").read_text())
    return lock["resources"]["./memory_stores/agency-playbook.yaml"]["id"]


def main(update: bool) -> None:
    client = anthropic.Anthropic()
    sid = store_id()
    existing = {
        m.path: m
        for m in client.beta.memory_stores.memories.list(sid, path_prefix="/")
        if m.type == "memory"
    }
    for src in sorted(PLAYBOOK_DIR.glob("*.md")):
        path = f"/{src.name}"
        content = src.read_text()
        if path not in existing:
            client.beta.memory_stores.memories.create(sid, path=path, content=content)
            print(f"created  {path}")
        elif update:
            current = existing[path]
            client.beta.memory_stores.memories.update(
                current.id,
                memory_store_id=sid,
                content=content,
                precondition={"type": "content_sha256", "content_sha256": current.content_sha256},
            )
            print(f"updated  {path}")
        else:
            print(f"exists   {path}  (pass --update to overwrite)")


if __name__ == "__main__":
    main(update="--update" in sys.argv)
