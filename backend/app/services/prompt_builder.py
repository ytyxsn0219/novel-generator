from typing import Optional


def build_settings_prompt(theme: str) -> str:
    return (
        f"用户想写一部网文，主题是：{theme}\n"
        "请输出一份结构化小说设定，包含以下字段（JSON 格式）：\n"
        "- world_view: 世界观描述\n"
        "- characters: 主要角色列表，每个角色包含 name, personality, goal, relationships\n"
        "- outline: 主线大纲的分阶段关键节点\n"
        "- style: 文笔风格和基调\n"
        "只输出合法 JSON，不要多余解释。"
    )


def build_chapter_prompt(
    settings: dict,
    prev_summary: str,
    current_number: int,
    locked_before_summary: Optional[str] = None,
    locked_after_constraint: Optional[str] = None,
) -> str:
    parts = [
        "根据以下小说设定写一章网文（约2000-3000字）：",
        f"设定：{settings}",
    ]
    if locked_before_summary:
        parts.append(f"前面锁定章节的结尾摘要（必须承接）：{locked_before_summary}")
    if prev_summary:
        parts.append(f"上一章摘要：{prev_summary}")
    parts.append(f"这是第 {current_number} 章。请生成标题和正文。只输出 JSON 格式：{{'title': '章节标题', 'content': '正文内容'}}")
    if locked_after_constraint:
        parts.append(f"后面锁定章节的开头约束（必须引向）：{locked_after_constraint}")
    return "\n".join(parts)


def build_feedback_scope_prompt(settings: dict, chapter_summary: Optional[str], feedback: str) -> str:
    return (
        "用户针对小说提出了修改意见。请判断这个意见的波及范围。\n"
        f"小说设定：{settings}\n"
        f"针对章节摘要：{chapter_summary or '无（全局意见）'}\n"
        f"用户意见：{feedback}\n"
        "请只输出一个单词：chapter（只改本章）、future（从本章开始改后续走向）、global（需要修改全局设定）。"
    )
