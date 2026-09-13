# R15 credential, API, MCP, and one-time bootstrap guide

## Governing rule

Reuse working credentials before creating anything. Never print secrets, paste them into issue bodies, commit them, or include them in deployment receipts. MCP is optional transport: the GitHub and Prove2Me APIs/CLIs are authoritative, and R15 must remain executable when no MCP server is configured.

## Capability matrix

| Capability | Existing GitHub auth | Prove2Me API key | GitLab SSH/deploy key | GitLab API token | MCP required? |
|---|---:|---:|---:|---:|---:|
| Read/write canonical GitHub repo | yes | no | no | no | no |
| Configure GitHub Actions repo secret/variable | yes, with repository admin/settings permission | no | no | no | no |
| Search Prove2Me missions/theorems | no | yes | no | no | no |
| Draft/upload Prove2Me proposal/items | no | yes | no | no | no |
| Submit Lean proof/disproof / poll verification | no | yes | no | no | no |
| Human self-audit + submit public Prove2Me mission | browser human session | account | no | no | no; human action by design |
| Push canonical SHA to GitLab mirror | no | no | yes | optional alternative | no |
| Read public GitLab issues/MRs for unified intake | no | no | no for public data, subject to rate limits | optional | no |
| Write/manage GitLab issues/settings via API | no | no | no | yes | no |

## Non-secret preflight

Run from the executor shell:

```bash
python3 "$R15_HANDOFF_DIR/LOCAL_CAPABILITY_PREFLIGHT.py"
```

The script reports presence/absence and safe metadata only. It never prints token/key contents.

## GitHub setup if missing

1. Install GitHub CLI from the official GitHub CLI package for the host OS.
2. Authenticate interactively:

```bash
gh auth login
```

Choose GitHub.com and the preferred Git protocol. Browser authentication is preferred to pasting a PAT into shell history.
3. Confirm:

```bash
gh auth status
gh repo view navier-stokes-commons/navier-stokes-commons.github.io
```

4. Confirm Git write access using the actual checkout remote, without making a commit:

```bash
git ls-remote origin refs/heads/main
```

5. GitHub Actions should use the repository-scoped built-in `GITHUB_TOKEN` for same-repository API actions. Do not create a PAT merely for ordinary workflow operations.

### Installing the GitLab mirror secret in GitHub Actions

After creating the dedicated GitLab mirror key below:

```bash
gh secret set NSC_GITLAB_MIRROR_SSH_KEY \
  --repo navier-stokes-commons/navier-stokes-commons.github.io \
  < ~/.ssh/nsc_gitlab_mirror

gh variable set NSC_GITLAB_MIRROR_ENABLED \
  --repo navier-stokes-commons/navier-stokes-commons.github.io \
  --body true
```

Then verify only the secret/variable names, never their values:

```bash
gh secret list --repo navier-stokes-commons/navier-stokes-commons.github.io
gh variable list --repo navier-stokes-commons/navier-stokes-commons.github.io
```

## Prove2Me setup if missing

Canonical API base: `https://prove2.me/api/v1`.

### 1. Reuse existing workspace first

```bash
if [ -d "$HOME/prove2me_workspace/.git" ]; then
  git -C "$HOME/prove2me_workspace" pull --tags origin main
else
  git clone https://github.com/prove2me/prove2me_workspace.git "$HOME/prove2me_workspace"
fi
```

The R15 interoperability pin is workspace commit `8d697eeda2f65d396209a9b4f888602de1f55fbf`, skill version `0.10.3`; the executor must compare against the current live Prove2Me-reported version before mutating anything and reconcile if the API moved.

### 2. Reuse saved API credentials first

If `$HOME/prove2me_workspace/credentials.json` already contains a working API key, use it. The key begins with `p2m_` and is time-limited. Keep the file mode private:

```bash
chmod 600 "$HOME/prove2me_workspace/credentials.json"
```

Never commit or copy it into NSC.

### 3. If no API key exists

Log in at `https://prove2.me`, open the account menu, choose **API key**, generate/copy a key, and store it locally rather than in this chat or a Codex prompt. A minimal local representation accepted by R15 tooling is:

```json
{"api_key":"p2m_..."}
```

at `$HOME/prove2me_workspace/credentials.json`, mode `0600`.

### 4. Exchange API key for a one-hour access token

```bash
curl -sS -X POST https://prove2.me/api/v1/agent/refresh \
  -H 'Content-Type: application/json' \
  --data-binary @- <<'JSON'
{"api_key":"REDACTED_LOCAL_VALUE"}
JSON
```

Do not literally type the key in a shared log. R15 scripts perform this exchange from local secret state without echoing it.

The returned platform `version` must be compared to the current workspace `SKILL.md`; if different, pull current workspace documentation before continuing.

### 5. Human mission-publication boundary

An agent/API can prepare a mission proposal and its items. For a public mission, you must perform the Prove2Me **Self-audit** and **Submit** step in your authenticated human web session after checking the read-backs/statements. Public moderator review follows. R15 must not attempt to bypass this with hidden browser automation or credential replay.

## GitLab persistent mirror setup if missing

A personal GitLab API token is NOT required for ordinary Git mirroring. Prefer a dedicated project deploy key.

### 1. Generate a dedicated keypair locally

```bash
umask 077
ssh-keygen -t ed25519 \
  -f "$HOME/.ssh/nsc_gitlab_mirror" \
  -C "nsc-gitlab-mirror" \
  -N ''
```

### 2. Add only the PUBLIC key to GitLab

Project: `champia-labs-group/navier-stokes-commons-public`

UI:

`Settings -> Repository -> Deploy keys -> Add new key`

- Title: `NSC GitHub mirror`
- Key: contents of `~/.ssh/nsc_gitlab_mirror.pub`
- Grant write permission: enabled
- Scope: this project only

If `main` is protected, ensure the deploy key is authorized to push to the protected branch under the project rules.

### 3. Test locally

```bash
GIT_SSH_COMMAND="ssh -i $HOME/.ssh/nsc_gitlab_mirror -o IdentitiesOnly=yes" \
  git ls-remote git@gitlab.com:champia-labs-group/navier-stokes-commons-public.git refs/heads/main
```

### 4. Store the PRIVATE key in GitHub Actions

Use `gh secret set` as shown above. Do not place the private key in GitLab, source, handoff files, shell transcripts, or issues.

### Optional GitLab API credential

Only create one if R15 encounters a concrete GitLab API write operation that SSH cannot perform. Prefer a project-scoped credential where your plan supports it; otherwise use the narrowest feasible PAT scope and shortest lifetime. It is not a prerequisite for the mirror architecture itself.

## MCP

R15 does not require MCP. If the local Codex harness already exposes GitHub and/or Prove2Me through MCP, use those tools when they implement the needed operation faithfully. Otherwise use `gh`, Git/SSH, and the documented Prove2Me HTTPS API.

Do not invent an MCP configuration merely to satisfy a checklist. The Prove2Me public contract is its `start.md`, `SKILL.md`, and HTTPS API. If an MCP server is custom/local, preserve it but do not make the public product depend on it.

## Terminal credential blockers

R15 may stop only after all independent work is complete, with one of:

- `GITHUB_AUTH_REQUIRED`
- `PROVE2ME_API_KEY_REQUIRED`
- `PROVE2ME_HUMAN_SELF_AUDIT_SUBMIT_REQUIRED`
- `GITLAB_MIRROR_DEPLOY_KEY_UI_REQUIRED`
- `GITLAB_API_AUTH_REQUIRED` (only if a concrete required API write remains)

Each blocker must include the exact smallest user action and exact continuation command.
