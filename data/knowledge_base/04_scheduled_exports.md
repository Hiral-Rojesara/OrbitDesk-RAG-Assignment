---
document_id: KB-004
title: Scheduled Exports
updated: 2026-07-15
status: current
tags: [exports, schedule, delivery, email, storage, troubleshooting]
---

# Scheduled Exports

OrbitDesk can render a dashboard as PDF or CSV on a recurring or one-time schedule[cite: 6]. Analysts, Admins and Owners can create schedules[cite: 6]. Viewers cannot create or edit schedules[cite: 6].

## Schedule States

- **Active:** Eligible to run at the next scheduled time[cite: 6].
- **Paused:** Will not run until resumed[cite: 6].
- **Needs attention:** A required dashboard, connection or destination is unavailable[cite: 6].
- **Running:** Rendering or delivery is in progress[cite: 6].

## Run Sequence

At the scheduled time, OrbitDesk performs these steps[cite: 6]:

1. Confirms that the schedule is active[cite: 6].
2. Confirms that the dashboard still exists and the schedule owner still has access[cite: 6].
3. Waits for required data-source refreshes for up to 15 minutes[cite: 6].
4. Renders the requested format[cite: 6].
5. Delivers the file to the configured email or storage destination[cite: 6].

## Troubleshooting a Missed Export

Check the following in order[cite: 6]:

1. Confirm the schedule state and next-run time[cite: 6].
2. If the workspace timezone recently changed, follow `KB-003` and resave the schedule[cite: 6].
3. Open **Schedule > Run history** and note the latest run status and error code[cite: 6].
4. Confirm that the dashboard exists and that the schedule owner can still open it[cite: 6].
5. Confirm that all required connections are active[cite: 6].
6. Confirm that the destination is verified and enabled[cite: 6].

## Common Error Codes

- `source_refresh_timeout`: A required connection did not finish refreshing within 15 minutes[cite: 6]. The export is not retried automatically[cite: 6].
- `destination_unverified`: Delivery is blocked until the destination is verified[cite: 6].
- `owner_access_revoked`: The schedule owner no longer has access to the dashboard[cite: 6].
- `render_failed`: Rendering failed after the data checks completed[cite: 6].

Use **Run now** after correcting the cause[cite: 6]. A manual run does not alter the recurring schedule's next-run time[cite: 6].

Escalate after two consecutive `render_failed` events for the same dashboard[cite: 6]. Include the schedule ID, dashboard ID, run IDs and timestamps[cite: 6]. Never include exported customer data in an escalation note[cite: 6].
