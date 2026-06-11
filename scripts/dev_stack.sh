#!/usr/bin/env bash
set -euo pipefail

command="${1:-help}"

case "${command}" in
  check|doctor)
    python3 .gstack/scripts/gstack_doctor.py check
    ;;
  help|--help|-h)
    cat <<'EOF'
KK Dev Skeleton default dev stack entry.

This skeleton does not know your project's app server yet.

Useful commands:
  bash scripts/dev_stack.sh check
  python3 scripts/init_project.py --adapter <project-slug> --create-adapter
  python3 scripts/init_project.py --adapter <project-slug> --detect --plan --report
  python3 scripts/init_project.py --adapter <project-slug> --apply --verify --report

After copying this skeleton into a real project, update:
  adapters/<project-slug>/adapter.md
  adapters/<project-slug>/runtime.json
  scripts/dev_stack.sh
EOF
    ;;
  *)
    echo "Unknown command: ${command}" >&2
    echo "Run: bash scripts/dev_stack.sh help" >&2
    exit 2
    ;;
esac
