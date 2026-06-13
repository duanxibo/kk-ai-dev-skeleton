# Internal Marketplace Install And Upgrade

This guide describes how to turn the repo-local plugin source into an internal Codex marketplace.

For rollout planning, use:

- `plugins/PARTNER_INSTALL.md`
- `plugins/MARKETPLACE_ROLLOUT.md`
- `plugins/ADMIN_INSTALL_CHECKLIST.md`
- `plugins/PILOT_FEEDBACK.md`

Normal business users should not start here. They should ask Codex in natural language:

```text
请把当前项目接入 KK Dev Skeleton。
```

The commands below are for an administrator, release owner, or Codex agent acting with explicit approval to install or update the internal marketplace. Do not present these commands as the normal business-user onboarding path.

## Published Git Marketplace

The published Git marketplace source is:

```text
https://github.com/duanxibo/kk-ai-dev-skeleton.git
```

Partner-facing installation text lives in `plugins/PARTNER_INSTALL.md`.

For Git marketplace installation:

```bash
codex plugin marketplace add https://github.com/duanxibo/kk-ai-dev-skeleton.git --ref main
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```

After installation, start a new Codex thread before testing the installed skill.

## Source Layout

```text
.agents/plugins/marketplace.json
plugins/kk-dev-skeleton-adoption/
```

The marketplace root is the repository root. The marketplace entry uses:

```text
./plugins/kk-dev-skeleton-adoption
```

## Install Flow

Use this only after the team approves installing the repo-local marketplace in a Codex environment.

1. Validate the plugin source.

Ask Codex to run the locally installed `plugin-creator` validator against:

```text
plugins/kk-dev-skeleton-adoption
```

2. Validate the skill source.

Ask Codex to run the locally installed `skill-creator` validator against:

```text
plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption
```

3. Read the marketplace name.

Ask Codex to run the locally installed `plugin-creator` marketplace-name reader with:

```text
--marketplace-path .agents/plugins/marketplace.json
```

4. Add the repo root as a non-default local marketplace, or use the published Git marketplace.

```bash
codex plugin marketplace add <repo-root>
```

```bash
codex plugin marketplace add https://github.com/duanxibo/kk-ai-dev-skeleton.git --ref main
```

5. Install the plugin from that marketplace.

```bash
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```

6. Start a new Codex thread before testing the installed skill.

## Upgrade Flow

1. Update plugin source files under `plugins/kk-dev-skeleton-adoption/`.
2. Run plugin and skill validation.
3. If Codex needs to pick up local plugin changes, update the plugin cachebuster through the plugin-creator helper.

Ask Codex to run the locally installed `plugin-creator` cachebuster helper against:

```text
plugins/kk-dev-skeleton-adoption
```

4. Reinstall the plugin from the internal marketplace.

```bash
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```

5. Start a new Codex thread for validation.

## Safety Rules

- Do not install or update this marketplace without explicit approval.
- Do not use this marketplace flow for ordinary project onboarding.
- Do not connect real data, production systems, databases, or git workflow actions through the plugin.
- The plugin only routes Codex into the target repository's natural-language adoption flow and V1 helper.
- The target repository's `AGENTS.md`, adapter, active boundary, guard checks, and QA evidence remain authoritative.
