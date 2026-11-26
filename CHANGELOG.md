# Changelog

All notable changes to this plugin are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versions
follow [Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-11-26

### Changed

- The note example writes `domain` and `tags` one item per line, the form
  Obsidian writes and the mimir style check asks for. Both forms still parse.

## [0.2.0] - 2026-11-23

### Added

- `vault.area`, the folder in the vault that holds the memory, session and
  archive folders. It defaults to `AI`, so a config without it works as
  before. `""` or `.` puts them at the vault root. An absolute path, `..` or
  a backslash is an error that names the key.

### Changed

- The Values block names the area, and the skill text reads its paths from it.
- Archiving a note uses `obsidian move` only when the vault root has a
  `.obsidian/` folder. Without one, the skill moves the note into
  `AREA/archive/` with `mv -n` and checks the target, because bare wikilinks
  resolve by filename.

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
