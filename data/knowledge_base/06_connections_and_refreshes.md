---
document_id: KB-006
title: Connections and Data Refreshes
updated: 2026-07-11
status: current
tags: [connections, sync, refresh, data, troubleshooting]
---

# Connections and Data Refreshes

OrbitDesk dashboards may depend on one or more data connections[cite: 7]. Owners and Admins can create and edit connections[cite: 7]. Analysts can view non-secret settings and start a manual refresh when the connection allows it[cite: 7].

## Connection States

- **Active:** Available for queries and scheduled refreshes[cite: 7].
- **Refreshing:** A refresh is currently running[cite: 7].
- **Reauthorization required:** The external authorization has expired or been revoked[cite: 7].
- **Disabled:** An Owner or Admin has disabled the connection[cite: 7].
- **Error:** The most recent refresh failed[cite: 7].

## Refresh Behaviour

Only one refresh can run for a connection at a time[cite: 7]. A second request returns `refresh_already_running`[cite: 7]. Scheduled exports wait up to 15 minutes for required refreshes[cite: 7]. If a refresh takes longer, the export run ends with `source_refresh_timeout` even if the refresh later succeeds[cite: 7].

## Troubleshooting

The phrase “sync is not working” is not specific enough to diagnose a connection problem[cite: 7]. Ask for:

- Workspace ID[cite: 7]
- Connection name or ID[cite: 7]
- Current connection state[cite: 7]
- Last successful refresh time[cite: 7]
- Latest error code[cite: 7]
- Whether manual and scheduled refreshes are both affected[cite: 7]

Do not ask for database passwords, OAuth tokens or API secrets[cite: 7].

For `reauthorization_required`, an Owner or Admin must reconnect the data source[cite: 7]. For repeated `connector_internal_error` failures, escalate with the connection ID, refresh job IDs and timestamps after two failed attempts[cite: 7].
