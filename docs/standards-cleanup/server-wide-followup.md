# Server-Wide Follow-Up: Nginx Backups and server_tokens

Run this once the Models Gone Wild cleanup is finished (step 13B is live). It sits outside the cleanup because both changes touch the nginx setup that every app on the server shares. Decision 26 in the README set it aside on 2026-10-16.

## Background

Both items were checked on the server on 2026-10-16, read only.

- `server_tokens off` is commented out on line 24 of `/etc/nginx/nginx.conf`, so the origin answers with `Server: nginx/1.18.0 (Ubuntu)`. Cloudflare replaces the header, so the public sees `server: cloudflare`, and the firewall only lets Cloudflare reach the origin. The version is hidden from visitors today, but the origin still names it.
- `/etc/nginx/sites-available/` holds 53 backups: 23 of `annielytics.conf` and 30 of `staging.annielytics.conf`. Only the two live files are linked from `sites-enabled/`, so the backups do nothing, but they bury the live files. The count will be higher by the time this runs, since every nginx change in the cleanup makes another one.
- `/etc/nginx/backup/` already exists and holds two old files from May 2025. It sits outside both `sites-available/` and `sites-enabled/`, so nginx never reads it.

## Done on 2026-10-20

- `server_tokens off` is on, at line 24 of `nginx.conf`. The origin now answers with `Server: nginx`, and the public header still reads `cloudflare`. The old file is `/etc/nginx/backup/nginx.conf.bak.20261020-202544`.
- The 83 backups (37 of `annielytics.conf`, 46 of `staging.annielytics.conf`) moved into `/etc/nginx/backup/sites-available-20261020/`. `sites-available/` holds the two live configs and Ubuntu's unlinked `default`, which stays since it is the package's file, not a backup.
- `sudo nginx -t` passed before the reload. The production root and all eight apps still return 200 at the origin, and staging matches its baseline.
- Two rows went into the PCI Network Security Change Log, rows 82 and 83.
- New backups go flat in `/etc/nginx/backup/` as `<file>.bak.<YYYYMMDD-HHMMSS>`. Rule 17 of `~/.claude/rules/security/server-security.md` says so, and the backup commands in `~/.claude/skills/DEPLOY.md`, the `x-script-name-sweep` skill, the archived Canvas move rule, step 0B, and the README's rules now point there.

## Paste-ready prompt

```
Run the server-wide nginx follow-up, following
docs/standards-cleanup/server-wide-followup.md in the Models Gone Wild
repo and ~/.claude/rules/security/server-security.md exactly.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild
Server: ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51

1. Confirm step 13B of the standards cleanup is marked done in
   docs/standards-cleanup/README.md. Stop if it is not.
2. Read only, and change nothing yet: recount the backups in
   /etc/nginx/sites-available/ by file, confirm sites-enabled/ links only
   the two live files, show line 24 of /etc/nginx/nginx.conf, and show the
   origin's Server header (curl -sI http://127.0.0.1/ -H "Host:
   www.annielytics.com"). Then search ~/.claude/ and the DEPLOY.md and
   CLAUDE.md files of every app under ~/Dropbox/Annielytics/Code/Python/
   for instructions that write nginx backups into sites-available/, and
   list them.
3. Give me the plan (what moves where, the nginx.conf change, and which
   docs would change so new backups land in /etc/nginx/backup/ instead)
   and STOP for my go-ahead. Do not touch the server before I answer.
4. On my go-ahead: back up nginx.conf into /etc/nginx/backup/ with a dated
   name, uncomment server_tokens off, move every backup out of
   sites-available/ into a dated subfolder of /etc/nginx/backup/, run
   sudo nginx -t, and reload nginx only if the test passes.
5. Verify: the origin's Server header reads nginx with no version, the
   public header still reads cloudflare, sites-available/ holds only the
   live files, and every app's home page still returns 200 at the origin.
6. Write one row per change into the PCI Network Security Change Log
   sheet yourself, following ~/.claude/CLAUDE.md (read the tab first,
   write below the last filled row, read it back).
7. Update the docs from step 2 on a branch in each repo, commit, push, and
   tell me what changed. Do not merge any app's branch to main without my
   go-ahead.
```
