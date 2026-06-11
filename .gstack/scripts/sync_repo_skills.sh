#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_HOME="${CODEX_HOME}/skills"
REMOVE_TG_LINKS=false

usage() {
  cat <<'EOF'
用法:
  bash .gstack/scripts/sync_repo_skills.sh [--remove-tg-links]

默认行为:
  - 同步当前仓库的 kk-* skills 到 $CODEX_HOME/skills。
  - 不删除其它项目的 tg-* skills。

可选参数:
  --remove-tg-links
      删除 $CODEX_HOME/skills 下的 tg-* symlink。
      只删除 symlink，不删除普通目录或真实 skill 文件。
      如果你仍然需要旧项目的 tg-* skills，不要使用这个参数。
  -h, --help
      显示帮助。
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --remove-tg-links)
      REMOVE_TG_LINKS=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] 未知参数: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

link_skill() {
  local source_dir="$1"
  local target_name="$2"
  local target_path="${SKILLS_HOME}/${target_name}"

  if [ ! -d "${source_dir}" ]; then
    echo "[ERROR] Skill source not found: ${source_dir}" >&2
    exit 1
  fi

  if [ -e "${target_path}" ] && [ ! -L "${target_path}" ]; then
    echo "[ERROR] Target exists and is not a symlink: ${target_path}" >&2
    echo "        Move it away manually, then rerun this script." >&2
    exit 1
  fi

  ln -sfn "${source_dir}" "${target_path}"
    echo "[OK] ${target_name} -> ${source_dir}"
}

remove_legacy_link() {
  local target_name="$1"
  local target_path="${SKILLS_HOME}/${target_name}"

  if [ -L "${target_path}" ]; then
    rm -f "${target_path}"
    echo "[OK] 已删除旧 symlink: ${target_name}"
  fi
}

remove_tg_symlink() {
  local target_path="$1"
  local target_name
  target_name="$(basename "${target_path}")"

  if [ -L "${target_path}" ]; then
    rm -f "${target_path}"
    echo "[OK] 已删除外部 tg symlink: ${target_name}"
  elif [ -e "${target_path}" ]; then
    echo "[WARN] 发现 tg-* skill 但它不是 symlink，已保留: ${target_path}" >&2
  fi
}

warn_tg_symlinks() {
  local found=false
  local target_path

  for target_path in "${SKILLS_HOME}"/tg-*; do
    [ -e "${target_path}" ] || continue
    found=true
    break
  done

  if [ "${found}" = true ]; then
    echo "[WARN] 在 ${SKILLS_HOME} 中发现 tg-* skills。"
    echo "       它们不属于当前 kk-* 骨架，可能让新 Codex 会话串到旧项目上下文。"
    echo "       如果你已经不需要它们，可以运行:"
    echo "       bash .gstack/scripts/sync_repo_skills.sh --remove-tg-links"
  fi
}

mkdir -p "${SKILLS_HOME}"

remove_legacy_link "task-kickoff"
remove_legacy_link "natural-language-dev"
remove_legacy_link "doc-sync"
remove_legacy_link "doc-lifecycle"
remove_legacy_link "doc-backfill"
remove_legacy_link "data-kickoff"
remove_legacy_link "data-query"
remove_legacy_link "subagent-orchestrator"
remove_legacy_link "codex-mode"

if [ "${REMOVE_TG_LINKS}" = true ]; then
  for target_path in "${SKILLS_HOME}"/tg-*; do
    [ -e "${target_path}" ] || continue
    remove_tg_symlink "${target_path}"
  done
fi

link_skill "${REPO_ROOT}/.gstack/skills/kk-task-kickoff" "kk-task-kickoff"
link_skill "${REPO_ROOT}/.gstack/skills/kk-natural-language-dev" "kk-natural-language-dev"
link_skill "${REPO_ROOT}/.gstack/skills/kk-doc-sync" "kk-doc-sync"
link_skill "${REPO_ROOT}/.gstack/skills/kk-doc-lifecycle" "kk-doc-lifecycle"
link_skill "${REPO_ROOT}/.gstack/skills/kk-doc-backfill" "kk-doc-backfill"
link_skill "${REPO_ROOT}/.gstack/skills/kk-data-kickoff" "kk-data-kickoff"
link_skill "${REPO_ROOT}/.gstack/skills/kk-data-query" "kk-data-query"
link_skill "${REPO_ROOT}/.gstack/skills/kk-subagent-orchestrator" "kk-subagent-orchestrator"
link_skill "${REPO_ROOT}/.gstack/skills/kk-codex-mode" "kk-codex-mode"

if [ "${REMOVE_TG_LINKS}" != true ]; then
  warn_tg_symlinks
fi

echo "[DONE] repo-native skills 已同步到 ${SKILLS_HOME}"
