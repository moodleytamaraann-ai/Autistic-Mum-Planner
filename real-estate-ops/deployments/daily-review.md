---
name: Daily operations review
description: Weekday-morning exception report from agency-records.
agent: ../agents/ops-manager.md
environment_id: ../environments/cloud.yaml
resources:
  - path: ../memory_stores/agency-records.yaml
    access: read_write
    instructions: System of record. Read-only this run except the activity log, approvals/pending/ and requests/open/.
  - path: ../memory_stores/agency-playbook.yaml
    access: read_only
schedule:
  type: cron
  expression: "50 6 * * 1-5"      # 06:50 weekdays
  timezone: Africa/Johannesburg
budget:                            # hard cap per run: USD cents. Starter value; tune after the first week's runs.
  type: limit
  max_list_cost: {amount: "1000", currency: USD}
initial_events:
  - type: user.define_outcome
    description: >-
      Produce today's operations review as /mnt/session/outputs/daily-review-<YYYY-MM-DD>.md
      from agency-records, following the reporting rules in your instructions.
      Do not perform any action that authority.md reserves for approval.
    max_iterations: 3
    rubric:
      type: text
      content: |
        # Daily review rubric (starter: tune after the first two weeks)
        1. The file exists at /mnt/session/outputs/daily-review-<today's date>.md.
        2. It opens with the exception summary (🔴 / 🟠 / 🟡 / 🟢 counts) and a "Management attention required: N" line.
        3. N equals the number of 🔴 plus 🟠 items listed in the body.
        4. Every count is followed by the script or command that produced it, and that script reads only agency-records.
        5. Every 🔴 and 🟠 item names an owner, a deadline and a next action (trigger → required item → owner → deadline → follow-up).
        6. Every fact carries a [RECORD: path] label that points to an existing file.
        7. The section "Information needed from management" lists every item in requests/open/.
        8. Any action that needs approval appears under "Awaiting approval" and was written to approvals/pending/, not carried out.
        9. If agency-records holds no operational data yet, the report says so plainly and lists the intake steps instead of reporting zero counts as "on track".
---
