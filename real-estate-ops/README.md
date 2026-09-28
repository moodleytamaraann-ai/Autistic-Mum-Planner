# Real Estate Operations Manager

A Claude Managed Agent that runs a real estate company's operational system of record, directs
and chases work, and reports exceptions to management. It does no legal work.

## What's here

| Path | What it is |
|---|---|
| `agents/ops-manager.md` | The agent: model, tools and operating instructions |
| `environments/cloud.yaml` | The sandbox it runs in |
| `memory_stores/agency-records.yaml` | The system of record, which the agent builds and maintains |
| `memory_stores/agency-playbook.yaml` | Management's rules, which the agent can read but not change |
| `setup/playbook/*.md` | Playbook contents: authority, record conventions, service levels |
| `deployments/daily-review.md`, `weekly-report.md` | Scheduled runs (06:50 weekdays, 07:10 Mondays, SAST) |
| `ops.py` | Chat with the agent, trigger a run now, download reports |

## Setup (once)

You need the `ant` CLI (1.30.0 or later) and Python 3.10+. Run every command from this folder.

```sh
pip install -r requirements.txt
ant auth login                       # or: export ANTHROPIC_API_KEY=...

# 1. Agent, environment and both memory stores. The schedules come later, in step 4.
ant apply --dry-run -v agents/ops-manager.md environments/cloud.yaml \
  memory_stores/agency-records.yaml memory_stores/agency-playbook.yaml
ant apply agents/ops-manager.md environments/cloud.yaml \
  memory_stores/agency-records.yaml memory_stores/agency-playbook.yaml

# 2. Load the playbook rules
python setup/seed_playbook.py

# 3. Intake: the agent sets up the records and asks you for what it needs
python ops.py chat
```

Commit `claude-lock.json`. It holds the resource IDs, and without it the next `ant apply`
creates duplicates.

**4. Turn on the schedules once the records hold real data** (gate: at least one intake
completed):

```sh
ant apply deployments/daily-review.md deployments/weekly-report.md
python ops.py run daily              # test now instead of waiting for 06:50
python ops.py outputs <session_id>
```

## Changing the rules

Edit `setup/playbook/*.md`, then run `python setup/seed_playbook.py --update`. Earlier
versions are kept in the memory store's version history.
