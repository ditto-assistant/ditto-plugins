# YouTube Music UI observations

Read this only when the chosen service is YouTube Music and the available
execution path is its browser/native UI. Current observed controls take
precedence; these are service-specific lessons, not requirements for other
music services.

- Explicitly replace search text with the supported fill/set-value operation.
  Clicking and typing after a selection shortcut can append to the old query.
  Verify the submitted query and recording before saving.
- Re-read the UI after actions. Search/navigation can initially expose the
  previous page; use the control tool's documented state mechanism to observe
  the requested query or playlist.
- The first Save to playlist action can open a chooser; later saves may target
  the most recently used playlist immediately. Inspect each destination toast
  and use Change when it identifies the wrong playlist.
- The creation dialog can default to Public. Explicitly select Private unless
  the user requests different visibility.
- Inspect Up next after requested queue replacement. Autoplay recommendations
  may appear beyond the curated tracks. If the user asked for only that set,
  disable autoplay as needed, verify their removal and disclose the change.
- On macOS, duplicate Chrome PWA bundle IDs can require selecting the observed
  full app path. Never copy another person's app path or stale control indices.
