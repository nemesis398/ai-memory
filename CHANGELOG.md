# Changelog

All notable changes to this plugin are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versions
follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-22

### Added

- The `ai-memory` skill: the four tests a memory has to pass, the better
  homes to try first, the note format, and how to supersede, archive and
  review a note.
- Three hooks: the pinned lines at session start, the notes a prompt points
  at, and the notes whose symptom a failed tool call shows.
- `scripts/lint.py` for the memory notes and `scripts/sweep.py` for the
  weekly report of candidates and archive proposals.
- The values from `AI_MEMORY_CONFIG`, else
  `${XDG_CONFIG_HOME:-~/.config}/ai-memory/config.json`, rendered into the
  skill when it loads.
