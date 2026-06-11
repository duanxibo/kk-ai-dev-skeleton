#!/usr/bin/env python3
"""Explain CI / GitHub check failures in plain language.

This helper is deterministic and read-only. It does not call GitHub, modify
workflow files, execute git actions, connect to production, touch databases, or
read/write real data. It maps a user's CI-failure wording to the repository's
known engineering-smoke check areas and returns a user-safe troubleshooting
summary.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "engineering-smoke.yml"


@dataclass(frozen=True)
class CiCheckRule:
    check_id: str
    user_label: str
    keywords: tuple[str, ...]
    scope: str
    codex_actions: tuple[str, ...]
    likely_follow_up: str


@dataclass(frozen=True)
class CiFailureExplanation:
    raw_request: str
    status: str
    status_reason: str
    detected_check: str
    detected_label: str
    workflow_known: bool
    check_scope: str
    what_codex_will_check: list[str]
    what_user_may_need_to_provide: list[str]
    non_actions: list[str]
    next_user_message: str


CHECK_RULES: tuple[CiCheckRule, ...] = (
    CiCheckRule(
        check_id="natural-language-dev",
        user_label="自然语言开发关键路径检查",
        keywords=(
            "natural-language-dev",
            "natural language",
            "自然语言",
            "nontechnical",
            "py_compile",
            "natural_language_dev_smoke",
        ),
        scope="检查非技术开发入口、自然语言路由、下一步说明和脚本语法。",
        codex_actions=(
            "先复查自然语言开发入口是否还能正确识别用户原话。",
            "再复查关键路径说明是否仍然能用人话输出。",
            "如果是脚本语法或回归失败，Codex 会在自然语言 helper 范围内修复。",
        ),
        likely_follow_up="通常不需要你判断业务口径；除非失败日志显示某个用户场景本身需要重新定义。",
    ),
    CiCheckRule(
        check_id="runtime-artifact-guard",
        user_label="运行产物 / 本地残留检查",
        keywords=(
            "runtime-artifact",
            "runtime artifact",
            "artifact guard",
            "运行产物",
            "本地残留",
            "node_modules",
            "dist",
            "target",
            ".vite",
            "__pycache__",
        ),
        scope="检查是否把 node_modules、dist、target、浏览器日志、缓存等运行产物带进仓库。",
        codex_actions=(
            "先区分失败项是运行产物，还是项目允许携带的配置文件。",
            "再定位对应文件属于临时残留、需要正式化的工具，还是允许入仓的敏感配置。",
            "敏感配置允许随仓库携带；Codex 不会把已允许的敏感配置当成缺陷处理。",
        ),
        likely_follow_up="如果失败项看起来像临时工具，Codex 会判断是清理、正式化，还是补文档和测试。",
    ),
    CiCheckRule(
        check_id="app-backend",
        user_label="app 后端测试",
        keywords=("app-backend", "maven", "mvn", "后端测试", "backend test", "java", "spring"),
        scope="检查 app/backend 后端测试、Java 编译和后端契约相关问题。",
        codex_actions=(
            "先确认失败是不是后端测试、编译或配置问题。",
            "再回到对应 stack domain spec、后端测试和实现路径定位。",
            "如果需要改后端业务实现，Codex 会另建后续任务边界和后端验证范围。",
        ),
        likely_follow_up="如果失败涉及业务口径、接口语义或真实数据，需要用户确认口径或数据范围。",
    ),
    CiCheckRule(
        check_id="restricted-module",
        user_label="受限业务模块检查",
        keywords=("restricted-module", "restricted module", "受限业务模块", "受限业务治理", "frontend:build", "characterization"),
        scope="检查受限业务模块服务、受限业务模块前端构建和 characterization 测试。",
        codex_actions=(
            "先确认失败是否属于受限业务模块服务、前端构建或 characterization 测试。",
            "再检查当前任务是否允许触碰受限业务模块范围。",
            "如果当前任务禁止受限业务模块，Codex 会先说明需要另建任务或等待你确认范围。",
        ),
        likely_follow_up="如果你明确禁止过受限业务模块，Codex 不会擅自修改这个范围。",
    ),
    CiCheckRule(
        check_id="zm-demo",
        user_label="zm-demo 检查",
        keywords=("zm-demo", "zm demo", "demo", "backend smoke", "frontend build"),
        scope="检查 zm-demo 后端 smoke 和前端构建。",
        codex_actions=(
            "先确认失败属于 demo 后端 smoke 还是前端构建。",
            "再判断它是否和当前任务相关，避免把无关 demo 失败混进当前任务。",
            "如果需要修 demo，Codex 会另建对应范围的后续任务边界。",
        ),
        likely_follow_up="如果失败和当前任务无关，Codex 会把它标成独立后续工作，而不是混在本轮改动里。",
    ),
    CiCheckRule(
        check_id="spec-sync-guard",
        user_label="规格同步检查",
        keywords=("spec-sync", "spec_sync", "规格同步", "文档同步", "spec sync"),
        scope="检查实现改动、规格真源、boundary、review 和 QA evidence 是否对齐。",
        codex_actions=(
            "先看失败是缺 requirement、review、boundary、QA，还是规格真源没有同步。",
            "能由本地证据证明的缺口，Codex 会补齐再复测。",
            "如果缺口是业务口径或数据权限，Codex 会只问那个确认点。",
        ),
        likely_follow_up="通常 Codex 可以自行补齐本地 evidence；业务口径不明确时才需要你确认。",
    ),
)


FAILURE_WORDS = (
    "失败",
    "没过",
    "挂了",
    "红了",
    "failed",
    "failure",
    "failing",
    "broken",
)


CI_CONTEXT_WORDS = (
    "github",
    "actions",
    "ci",
    "workflow",
    "pr 检查",
    "pull request",
    "检查",
    "工程检查",
    "engineering-smoke",
)


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def lower_text(*values: str) -> str:
    return " ".join(value for value in values if value).lower()


def text_has(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def workflow_known() -> bool:
    return WORKFLOW_PATH.exists()


def detected_rule(raw: str, job: str, log: str) -> CiCheckRule | None:
    haystack = lower_text(raw, job, log)
    for rule in CHECK_RULES:
        if any(keyword.lower() in haystack for keyword in rule.keywords):
            return rule
    return None


def looks_like_ci_failure(raw: str, job: str, log: str) -> bool:
    haystack = lower_text(raw, job, log)
    return text_has(haystack, FAILURE_WORDS) and (
        text_has(haystack, CI_CONTEXT_WORDS)
        or detected_rule(raw, job, log) is not None
    )


def generic_codex_actions() -> list[str]:
    return [
        "先确认红色检查属于自然语言入口、运行产物、后端测试、受限业务模块检查还是 demo 检查。",
        "再对照仓库里的工程检查分层，定位应该查哪一块。",
        "如果本地没有 GitHub 日志，Codex 会请你提供失败检查名或报错前几行，而不是猜测。",
    ]


def non_actions() -> list[str]:
    return [
        "不会执行代码提交、推送、合并或发起合并请求。",
        "不会连接生产环境、写数据库、操作真实数据或调用外部服务。",
        "不会把项目允许携带的敏感配置当成缺陷清理。",
    ]


def build_explanation(args: argparse.Namespace) -> CiFailureExplanation:
    raw = compact(args.raw)
    job = compact(args.job)
    log = compact(args.log)
    rule = detected_rule(raw, job, log)
    known = workflow_known()
    if rule:
        status = "check-identified"
        reason = f"已从用户描述识别为{rule.user_label}。"
        check_id = rule.check_id
        label = rule.user_label
        scope = rule.scope
        actions = list(rule.codex_actions)
        user_needs = [rule.likely_follow_up]
        next_message = f"我会按{rule.user_label}来排查，不会只看本地协作状态。"
    elif looks_like_ci_failure(raw, job, log):
        status = "needs-ci-detail"
        reason = "已识别为 CI / GitHub 检查失败，但还缺具体失败检查名。"
        check_id = "unknown"
        label = "暂未识别具体检查"
        scope = "需要先知道失败的是哪一个检查，才能判断对应范围。"
        actions = generic_codex_actions()
        user_needs = ["请提供失败检查名，也就是 GitHub 上红色检查的名字，或报错前几行；如果 Codex 本地能看到日志，会自己读取。"]
        next_message = "我会按 CI 失败来处理，但需要先知道红色检查的名字或报错前几行。"
    else:
        status = "not-ci-failure"
        reason = "这句话不像 CI / GitHub 检查失败，更适合走普通错误恢复。"
        check_id = "not-ci"
        label = "不是 CI 检查失败"
        scope = "普通本地错误或协作状态问题。"
        actions = ["先用普通错误恢复入口检查本地协作状态。"]
        user_needs = ["暂时不需要；除非你实际想说的是 GitHub 或 CI 检查失败。"]
        next_message = "这看起来不是 CI 检查失败，我会按普通错误恢复处理。"

    return CiFailureExplanation(
        raw_request=raw,
        status=status,
        status_reason=reason,
        detected_check=check_id,
        detected_label=label,
        workflow_known=known,
        check_scope=scope,
        what_codex_will_check=actions,
        what_user_may_need_to_provide=user_needs,
        non_actions=non_actions(),
        next_user_message=next_message,
    )


def render_json(explanation: CiFailureExplanation) -> str:
    return json.dumps(asdict(explanation), ensure_ascii=False, indent=2)


def render_markdown(explanation: CiFailureExplanation) -> str:
    lines = [
        "# 非技术 CI 失败解释",
        "",
        f"- 状态：{explanation.status}",
        f"- 判断：{explanation.status_reason}",
        f"- 识别检查：{explanation.detected_check}",
        f"- 检查说明：{explanation.detected_label}",
        f"- 已找到工程检查配置：{'是' if explanation.workflow_known else '否'}",
        f"- 检查范围：{explanation.check_scope}",
        "- Codex 下一步：",
        *[f"  - {item}" for item in explanation.what_codex_will_check],
        "- 需要用户提供：",
        *[f"  - {item}" for item in explanation.what_user_may_need_to_provide],
        "- 不会做：",
        *[f"  - {item}" for item in explanation.non_actions],
        f"- 给用户的下一句话：{explanation.next_user_message}",
    ]
    return "\n".join(lines)


def render_user(explanation: CiFailureExplanation) -> str:
    lines = [
        "我会按 CI / GitHub 检查失败来处理。",
        "",
        f"判断：{explanation.status_reason}",
        "",
        "先确认失败的是哪类检查：",
        f"- {explanation.detected_label}",
        f"- {explanation.check_scope}",
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in explanation.what_codex_will_check],
        "",
        "需要你确认：",
        *[f"- {item}" for item in explanation.what_user_may_need_to_provide],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in explanation.non_actions],
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original CI-failure wording.")
    parser.add_argument("--job", default="", help="Optional failed check/job name.")
    parser.add_argument("--log", default="", help="Optional short failure log excerpt.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    explanation = build_explanation(args)
    if args.format == "json":
        print(render_json(explanation))
    elif args.format == "user":
        print(render_user(explanation))
    else:
        print(render_markdown(explanation))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
