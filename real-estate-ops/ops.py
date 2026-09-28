"""Runtime entry points for the Real Estate Operations Manager.

    python ops.py chat                  talk to the Operations Manager (intake, brain-dumps, questions)
    python ops.py run daily|weekly      trigger a scheduled review now, outside its schedule
    python ops.py outputs <session_id>  download the reports a session wrote

IDs are read from environment variables if set (OPS_AGENT_ID, OPS_ENV_ID, OPS_RECORDS_ID,
OPS_PLAYBOOK_ID, OPS_DAILY_ID, OPS_WEEKLY_ID); otherwise from claude-lock.json.
"""

import json
import os
import sys
import time
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent
CONSOLE = "https://platform.claude.com/workspaces/default/sessions/{}"  # swap 'default' for your workspace slug

LOCK_KEYS = {
    "OPS_AGENT_ID": "./agents/ops-manager.md",
    "OPS_ENV_ID": "./environments/cloud.yaml",
    "OPS_RECORDS_ID": "./memory_stores/agency-records.yaml",
    "OPS_PLAYBOOK_ID": "./memory_stores/agency-playbook.yaml",
    "OPS_DAILY_ID": "./deployments/daily-review.md",
    "OPS_WEEKLY_ID": "./deployments/weekly-report.md",
}


def resource_id(env_var: str) -> str:
    if os.getenv(env_var):
        return os.environ[env_var]
    lock = json.loads((ROOT / "claude-lock.json").read_text())
    entry = lock["resources"].get(LOCK_KEYS[env_var])
    if entry is None:
        sys.exit(f"{LOCK_KEYS[env_var]} has not been applied yet. Run `ant apply` for it first.")
    return entry["id"]


def print_turn(client: anthropic.Anthropic, session_id: str, events: list) -> None:
    """Send events and print the agent's reply until the turn finishes.

    Approval prompts only appear if a tool is later set to always_ask (e.g. an email MCP).
    """
    with client.beta.sessions.events.stream(session_id=session_id) as stream:
        client.beta.sessions.events.send(session_id=session_id, events=events)
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
            elif event.type in ("agent.tool_use", "agent.mcp_tool_use") and event.evaluated_permission == "ask":
                print(f"\n\n[approval needed] {event.name}\n{json.dumps(event.input, indent=2)}")
                allow = input("Allow? [y/N] ").strip().lower() == "y"
                decision = {"type": "user.tool_confirmation", "tool_use_id": event.id, "result": "allow" if allow else "deny"}
                if not allow:
                    decision["deny_message"] = input("Reason (sent to the agent): ").strip() or "Denied by manager."
                client.beta.sessions.events.send(session_id=session_id, events=[decision])
            elif event.type == "session.error":
                print(f"\n[session error] {event.error}", file=sys.stderr)
            elif event.type == "session.status_terminated":
                print("\n[session terminated]")
                return
            elif event.type == "session.status_idle" and event.stop_reason.type != "requires_action":
                print()
                return


def chat() -> None:
    client = anthropic.Anthropic()
    session = client.beta.sessions.create(
        agent=resource_id("OPS_AGENT_ID"),
        environment_id=resource_id("OPS_ENV_ID"),
        title="Operations Manager: conversation",
        resources=[
            {
                "type": "memory_store",
                "memory_store_id": resource_id("OPS_RECORDS_ID"),
                "access": "read_write",
                "instructions": "System of record. Follow agency-playbook/conventions.md for every write.",
            },
            {"type": "memory_store", "memory_store_id": resource_id("OPS_PLAYBOOK_ID"), "access": "read_only"},
        ],
    )
    print(f"Session {session.id}\nWatch live: {CONSOLE.format(session.id)}\n")
    print("Type your message. A blank line sends it; type 'exit' to finish.\n")
    while True:
        lines = []
        while (line := input("you> " if not lines else "...> ")) != "":
            lines.append(line)
        text = "\n".join(lines).strip()
        if text.lower() in ("exit", "quit"):
            break
        if text:
            print_turn(client, session.id, [{"type": "user.message", "content": [{"type": "text", "text": text}]}])
    print(f"Reports from this session: python ops.py outputs {session.id}")


def run(which: str) -> None:
    client = anthropic.Anthropic()
    deployment = resource_id({"daily": "OPS_DAILY_ID", "weekly": "OPS_WEEKLY_ID"}[which])
    run_ = client.beta.deployments.run(deployment)
    if run_.error:
        sys.exit(f"Run failed: {run_.error.type}: {run_.error.message}")
    print(f"Started session {run_.session_id}\nWatch live: {CONSOLE.format(run_.session_id)}")
    print(f"When it finishes: python ops.py outputs {run_.session_id}")


def outputs(session_id: str) -> None:
    client = anthropic.Anthropic()
    out_dir = ROOT / "outputs" / session_id
    out_dir.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):  # outputs are indexed a few seconds after the session goes idle
        files = list(client.beta.files.list(scope_id=session_id, betas=["managed-agents-2026-04-01"]))
        if files:
            break
        time.sleep(3)
    for f in files:
        client.files.download(f.id).write_to_file(out_dir / f.filename)
        print(f"saved {out_dir / f.filename}")
    if not files:
        print("No output files yet. Is the session still running?")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["chat"]:
        chat()
    elif args[:1] == ["run"] and len(args) == 2 and args[1] in ("daily", "weekly"):
        run(args[1])
    elif args[:1] == ["outputs"] and len(args) == 2:
        outputs(args[1])
    else:
        sys.exit(__doc__)
