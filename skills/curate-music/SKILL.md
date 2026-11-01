---
name: curate-music
description: Curate personalized music playlists for any music service using the user's Ditto memories and library, with service-aware playlist creation, queue and playback when available.
---

# Curate music

Build an original listening sequence from the user's genre, mood, duration and
discovery preferences. Use their requested music service; do not silently move
them to a different service. This workflow applies to Spotify, Apple Music,
YouTube Music, Tidal, Deezer, Amazon Music, SoundCloud and other services through
the capabilities actually available in the current host.

Use the bundled `ditto-memory` skill for memory connection and permissions.
A Ditto memory connection does not itself provide a music-service connection.
Only save a playlist, alter a queue or start playback when requested. Selecting
tracks alone does not authorize changing the current listening session.

## Choose the service and execution path

If the user has not named a service, use their verified preference or the
intended connected account. Ask which service only when the destination matters
and cannot be determined. Verify the account and available capabilities before
writing, and keep the musical choices independent of the execution adapter.

Use this fallback order:

1. Prefer an available purpose-built connector for the selected service.
   Inspect its current schemas and supported search, library, playlist, queue
   and playback operations; do not invent endpoints or assume that one operation
   implies another.
2. If the connector is absent or cannot complete a requested operation, use
   supported browser use or computer use on that service's website or app.
   Read the control tool's current documentation, discover the existing tab/app,
   verify the account, and derive controls from fresh observed state.
3. Use web search as the last fallback when service connectors and browser/
   computer controls are unavailable or insufficient. Search for recordings,
   official artist/catalog pages and service links. Return an ordered playlist
   plan with verified links and explain which actions could not be executed.
   Search results do not prove that a playlist was saved or music is playing.

Fallbacks may be combined for the missing operation; retain successful work and
verify it before retrying elsewhere. Do not abandon the user's chosen service
just because another one has a connector. Do not put private memory excerpts
or conversation details in public search queries or playlist metadata.

## Learn the listener

Search Ditto for musical preferences, favorite artists, listening history and
reactions to recommendations. Fetch relevant full memories before attributing
a preference. Check authorship: subscribed content, another person's production
brief and a friend's recommendation are not the listener's taste without evidence
of the listener's own reaction.

When authorized library access exists, inspect actual saved tracks and several
relevant playlists on the chosen service. Keep saved songs distinct from
recommendations, search results and autoplay suggestions. Playlist titles alone
are weak evidence. If memories or library access are sparse, say so briefly and
use the verified context plus the current request. The latest brief controls
genre and mood; unrelated library preferences should not displace it.

## Curate the sequence

Choose specific recordings, balancing familiar anchors with discoveries. Shape
an arc with an inviting opener, purposeful transitions, contrasting intensity
and an intentional ending. Adjust length to the brief; ten to fourteen tracks
can be a useful starting point when no duration is given.

Verify title, artist, recording/version and availability on the intended service
using the strongest available execution path above. Official recordings, remixes,
live takes, fan uploads and similarly named songs are distinct choices. If
service/region availability cannot be checked, mark it unverified rather than
claiming a universal catalog match. Do not substitute a whole album or someone
else's genre mix for an original selection.

## Save and verify

For a requested new playlist, select private or library-only visibility when the
service supports it, unless the user requests sharing. If the service cannot
keep it private, explain that before creating a public playlist. Use a musical
title and description without private memory or conversation details.

Add tracks in the intended order. Verify the actual destination, contents,
count, order and visibility; do not confuse suggested tracks with saved ones.
Reconcile an uncertain save by reading the playlist before retrying to avoid
duplicates. Refresh UI state after actions and explicitly replace search text.
For YouTube Music UI-specific pitfalls, read
[the service reference](references/youtube-music.md) only when using that UI.

## Queue and playback

Honor append, play-next or replacement intent. A request to queue music does not
by itself authorize clearing the current queue. When replacement is requested,
verify the new queue and absence of the previous tracks; pressing Play can append
instead on some services. Preserve shuffle/autoplay unless the listening request
requires a change. For an ordered set, turn shuffle off only when playback is
requested. If the user wants only the curated set, disable added autoplay
recommendations when necessary, verify their removal, and disclose a persistent
setting change.

Verify playback from the requested starting track through the actual title and
artist plus a playing-state signal and progressing elapsed time, or equivalent
service receipt. Opening a playlist or seeing a Play button is not proof of
playback. Refresh state if the user changes the app during execution.

Finish with the playlist link if created, otherwise the ordered selections and
verified service links, plus count/duration and a short selection rationale.
State what was actually saved, queued or played and what remains unavailable.
Stop when the requested state is verified; do not keep adding songs or restarting
the opener. Never bundle credentials, account-specific IDs or one listener's
taste into this skill.
