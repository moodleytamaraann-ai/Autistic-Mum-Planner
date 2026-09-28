---
name: Weekly management report
description: Monday-morning management report covering the previous week.
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
  expression: "10 7 * * 1"        # 07:10 Mondays
  timezone: Africa/Johannesburg
budget:
  type: limit
  max_list_cost: {amount: "2000", currency: USD}
initial_events:
  - type: user.define_outcome
    description: >-
      Produce last week's (Monday to Sunday) management report as
      /mnt/session/outputs/weekly-report-<week-ending YYYY-MM-DD>.docx, with the figures also
      exported to a matching .xlsx. Do not perform any action that authority.md reserves for approval.
    max_iterations: 3
    rubric:
      type: text
      content: |
        # Weekly report rubric (starter: tune after the first month)
        1. Both files exist in /mnt/session/outputs/ and cover exactly the previous Monday to Sunday.
        2. Sections, in order: exception summary; pipeline (listings, leads, viewings, transactions by stage); agent-level workload and task completion; stalled items; open information requests; awaiting approval; recommended priorities for this week.
        3. Every figure in the .docx matches the same figure in the .xlsx.
        4. Each figure's calculation is reproducible from agency-records, and the .xlsx has a sheet listing the record paths used.
        5. The report compares activity with the previous week only where last week's data exists; otherwise it says "no baseline".
        6. Recommendations are labelled [RECOMMENDATION] and each names an owner.
        7. No legal interpretation or advice appears anywhere in the report.
---
