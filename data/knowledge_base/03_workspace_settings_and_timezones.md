---
document_id: KB-003
title: Workspace Settings and Timezones
updated: 2026-07-08
status: current
tags: [workspace, settings, timezone, locale, schedules]
---

# Workspace Settings and Timezones

Owners and Admins can change workspace settings from **Settings > Workspace**[cite: 5]. The workspace timezone controls how dates are displayed and how new recurring schedules interpret local time[cite: 5].

## Changing the Timezone

Changing the workspace timezone does not immediately rewrite existing recurring export schedules[cite: 5]. Existing schedules retain the timezone stored when they were last saved and display a `Timezone update pending` notice[cite: 5].

To apply the new workspace timezone to an existing recurring schedule:

1. Open the schedule[cite: 5].
2. Review the displayed next-run time[cite: 5].
3. Select **Save schedule**, even if no other field changes[cite: 5].
4. Confirm that the `Timezone update pending` notice disappears[cite: 5].

Resaving changes future run times only[cite: 5]. It does not create a replacement run for an export that was already missed[cite: 5].

## Other Time-related Behaviour

- New recurring schedules use the current workspace timezone[cite: 5].
- One-time exports store an absolute timestamp and do not move when the workspace timezone changes[cite: 5].
- Audit-log events are stored in UTC and displayed in the viewer's selected locale[cite: 5].
- Daylight-saving changes are applied using the timezone stored on the schedule[cite: 5].

If the schedule still does not run after being resaved, continue with the checks in `KB-004 Scheduled Exports`[cite: 5].
