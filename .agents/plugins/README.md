# KK Dev Skeleton Internal Marketplace

This directory contains a repo-local marketplace source for internal Codex plugin distribution.

Marketplace file:

- `.agents/plugins/marketplace.json`

Included plugin:

- `kk-dev-skeleton-adoption`

The marketplace root is the repository root. The marketplace entry points to:

```text
./plugins/kk-dev-skeleton-adoption
```

This file is not installed automatically. Installing or publishing this marketplace is an explicit admin / release action, not a business-user onboarding step.

Published Git marketplace:

- `https://github.com/duanxibo/kk-ai-dev-skeleton.git`

Rollout and install references:

- `plugins/PARTNER_INSTALL.md`
- `plugins/MARKETPLACE_INSTALL.md`
- `plugins/MARKETPLACE_ROLLOUT.md`
- `plugins/ADMIN_INSTALL_CHECKLIST.md`
- `plugins/PILOT_FEEDBACK.md`
