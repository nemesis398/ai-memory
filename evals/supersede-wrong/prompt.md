---
max_turns: 4
allowed_tools: [Skill]
---

The memory note `AI/memory/caddy-reload-needs-restart.md` says a Caddyfile
change needs `docker restart caddy`. That is wrong since Caddy 2.8:
`caddy reload` inside the container picks it up. What do you do with the
note? You cannot write files here, so describe the steps.
