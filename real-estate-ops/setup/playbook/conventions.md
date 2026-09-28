# Record conventions (agency-records)

## Layout

One JSON file per record. Never put several records in one file: several sessions can run at
the same time, and separate files keep them from overwriting each other.

| Folder | Record | ID prefix |
|---|---|---|
| people/ | Staff: principals, managers, qualified agents, candidate agents, admin | P- |
| properties/ | Listings, sale or rental | L- |
| leads/ | Buyer, tenant and seller leads | LD- |
| viewings/ | Viewings and appointments | V- |
| transactions/ | Sales and rentals from offer to finalisation | T- |
| documents/ | Document tracking: metadata only | D- |
| tasks/ | The agency task queue | TK- |
| checklists/ | Checklist instances attached to a record | C- |
| requests/open/, requests/closed/ | Information the Operations Manager needs from people | R- |
| approvals/pending/, approvals/decided/ | Actions awaiting or given a manager's decision | A- |
| activity/YYYY/MM/DD/ | Append-only log: one new file per event, never edited | (timestamp) |

IDs are the prefix plus a four-digit sequence (P-0001). Find the highest existing number with
code before creating a new ID.

## Fields every record carries

`id`, `status`, `owner` (a P- id), `related` (a list of ids), `created_at`, `updated_at`
(ISO 8601, Africa/Johannesburg), `source` ("RECORD" plus the originating path, or
"STATED" plus who and when), `notes`.

## Task fields

`title`, `owner`, `due` (date), `priority` (urgent, high, normal, low),
`status` (open, in_progress, blocked, done, cancelled), `blocked_by`, `next_action`,
`follow_up` (date).

## Activity log entry

`at`, `actor` (a P- id, or "ops-manager"), `action`, `record`, `before`, `after`,
`approved_by` (when approval was required), `session` (if known).

## Personal information: keep it minimal

Store only what operations need: names, roles, contact details used for work, and statuses
and dates. Never store ID numbers, bank details, account numbers, or the contents or copies
of documents. `documents/` records whether a document was requested, received or expired,
when, and who holds it, and nothing more.
