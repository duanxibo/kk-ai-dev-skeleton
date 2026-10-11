"""Read-only next-action guidance; a suggested reply never grants authorization."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class NextAction:
    status: str
    recommended_next_step: str
    suggested_user_input: str
    reply_required: bool
    reason: str


STEPS = {
    'requirement-brief': '整理当前需求的目标、使用者和成功标准。',
    'plan-ceo-review': '检查当前需求的价值和范围，先做最小可验收版本。',
    'requirement-freeze': '固定当前需求的范围和验收标准。',
    'plan-eng-review': '检查实现方案、风险和测试计划。',
    'domain-spec-readiness': '同步当前任务需要的产品和工程说明。',
    'implement': '完成当前任务范围内的实现和测试。',
    'qa': '运行当前任务的验收测试，核对实际结果。',
}


def next_action_for(task: dict | None, *, intent: str = '', helper_status: str = 'ok',
                    needs_confirmation: bool = False) -> NextAction:
    # An explicit pause or a failed helper must never be followed by a generic continue.
    if intent == 'pause_current_task':
        return NextAction('paused', '保留当前进度，等你决定是否恢复。',
                          '先停一下，请说明上次停在哪里、还有哪些未完成，暂时不要恢复执行。',
                          False, '你已要求暂停，提醒不会恢复任务。')
    if helper_status == 'failed' or intent in {'error_recovery', 'ci_failure_explain', 'undo_request'}:
        return NextAction('inspect-first', '先查清错误或受影响的范围，再给出恢复建议。',
                          '出错了，帮我看下一步怎么办。先说明失败原因和影响范围，只检查并给出建议。',
                          False, '需要先诊断，不能把报错或撤销请求当成通用续跑授权。')
    if needs_confirmation or intent in {'confirmation_brief', 'scope_change', 'mode_control'}:
        return NextAction('clarify-scope', '说明需要你决定的具体问题、可选方案和影响。',
                          '现在需要我确认什么？请列出具体问题、选项和各自影响，先说明，不执行。',
                          True, '具体范围或决定尚需明确，不能用一句“同意”代替授权。')
    if intent in {'first_use_guide', 'recommendation', 'feature_request', 'complex_task_starter',
                  'controlled_starter', 'formal_kickoff_preview', 'task_kickoff', 'requirement_brief',
                  'requirement_readiness', 'page_change_brief', 'ui_optimization_kickoff'}:
        return NextAction('define-goal', '补齐这次需求的使用者、预期结果和不做范围。',
                          '我想让【谁】能够【做什么】；成功时能看到【结果】。本轮范围仅为【范围】。请先整理最小方案和验收方式。',
                          True, '先把用户目标说清楚，避免把新需求混进当前任务。')
    if not task:
        return NextAction('no-active-task', '先描述要做的目标，或明确要恢复哪项任务。',
                          '我想让【谁】能够【做什么】；成功时能看到【结果】。请先整理最小方案和验收方式。',
                          True, '当前没有明确任务，不能从历史记录猜测你要继续什么。')
    mode = str(task.get('mode', ''))
    if mode in {'manual', '手动控制'}:
        return NextAction('manual-review', '先说明当前方案和影响，等待明确的执行范围。',
                          '先别改代码。请说明当前建议、影响范围和验收方式，暂时不要修改文件。',
                          True, '当前采用手动控制，提醒不能改变协作模式。')
    if task.get('blocked'):
        return NextAction('blocked', '先定位当前任务卡住的原因，分清工程问题和需要你决定的事项。',
                          '当前进度怎么样？请说明当前卡在哪里；能在已授权范围内解决的由你处理，需要我决定的请列出具体问题和选项。',
                          False, '卡住原因需要核对，提醒不会代替业务决定或高风险授权。')
    if task.get('acceptance_status') in {'historical-record', 'needs-verification'} or (
        task.get('current_step_key') == 'complete' and task.get('acceptance_status') != 'verified'
    ):
        return NextAction('needs-verification', '先重新验证对应任务，确认结果后再给完成说明。',
                          '继续做。请先检查当前任务的验收记录，补齐缺失项并重新验证；验证通过后再收口。',
                          False, '已有完成标记缺少当前有效验收，暂不推荐开启新任务。')
    if task.get('current_step_key') == 'complete':
        return NextAction('accept-result', '先按验收步骤检查本轮结果，再决定下一项具体目标。',
                          '我怎么知道它真的好了？请带我按当前记录验收，先不要开启新任务。',
                          True, '本轮已验证完成，下一步建议本身不授权新任务。')
    step = str(task.get('current_step_key', ''))
    return NextAction('continue-current-task', STEPS.get(step, '先核对当前任务记录，再处理尚未完成的阶段。'),
                      '继续做。请在当前已授权范围内完成实现、验证和文档同步；遇到需要我决定的事项再说明。',
                      False, 'Codex 可在当前已授权范围内继续；下面文案只是可选输入，不要求你重复说“继续”。')


def current_next_action(root: Path, **kwargs) -> NextAction:
    from gstack_dashboard import active_boundary, summarize_boundary
    # Dashboard reads the current local pointer/environment; never select a historical task.
    try:
        active = active_boundary()
        if active and not active.resolve().is_relative_to(root.resolve()):
            raise ValueError('active task is outside this repository')
        task = asdict(summarize_boundary(active, active)) if active else None
        return next_action_for(task, **kwargs)
    except (OSError, ValueError, RuntimeError):
        return next_action_for(None, intent=kwargs.get('intent', ''), helper_status='failed')


def render_reminder(action: NextAction) -> str:
    need = '请按下方提示验收结果，或补充所需目标和决定。' if action.reply_required else '暂时不需要你回复；以下文案可选。'
    return '\n'.join(['下一步提醒：' + action.recommended_next_step,
                      '是否需要你回复：' + need, '原因：' + action.reason,
                      '你下一句可以直接复制：', '> ' + action.suggested_user_input])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--format', choices=('user', 'json'), default='user')
    args = parser.parse_args()
    action = current_next_action(Path(__file__).resolve().parents[2])
    print(json.dumps(asdict(action), ensure_ascii=False, indent=2) if args.format == 'json' else render_reminder(action))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
