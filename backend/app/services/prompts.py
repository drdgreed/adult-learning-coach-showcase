from __future__ import annotations

"""
Coaching analysis prompt templates.

This is the most important file in the entire application.
The prompt defines HOW Claude analyzes teaching — it IS the product logic.

Loader pattern:
    This file contains the prompt ARCHITECTURE — function signatures,
    interpolation logic, version constants, the dispatch dict, and the
    formatting helpers. The prompt TEXT itself is loaded from
    prompts_content.py, which is git-ignored. A sanitized placeholder
    lives at prompts_content.example.py; copy it to prompts_content.py
    to run the app with your own prompts.

Versioning policy:
    Every prompt change ships as a new versioned function (`_v2`, `_v3`, ...).
    The previous version stays in this file, untouched, so reports generated
    against it remain reproducible and the Mac app keeps running until the
    consumer (analysis.py) explicitly switches imports. Every prompt also
    emits its own version into the output JSON via "prompt_version", so any
    downstream artifact (DB row, PDF, report archive) is self-describing
    about which prompt produced it.

Currently active in production (Mac app): v1 (build_analysis_prompt).
Currently in evaluation: v2 (build_analysis_prompt_v2).

Synthesized from three sources (2026-04-01):
1. Local prompts.py (JSON output, 4-dimension framework)
2. GitHub prompts.py (Chaos-6/adult-learning-coach, plain-text output,
   operational definitions, strict formatting)
3. Coaching-Prompt_v4.md (most sophisticated rubric: operational definitions,
   transparency requirements, VERIFIED/ESTIMATED labels, 9-section output)

Key design decisions:
1. System prompt sets the role, persona, and constraints
2. Operational definitions ensure reproducible, consistent counts
3. Analysis instructions define 4 dimensions with specific metrics
4. Output format is structured JSON — eliminates markdown parsing fragility
5. Sampling strategy ensures balanced evidence across the full session
6. 2:1 strength-to-improvement ratio keeps feedback motivational
7. Confidence labeling + shown calculations provide metric transparency
8. Every JSON field maps directly to a PDF section — no missing sections

Comparison prompts (multi-video analysis):
- Each comparison type has its own prompt builder function
- All three share COMPARISON_SYSTEM_PROMPT for the coach persona
- Input: evaluation report summaries (NOT raw transcripts) to stay in token budget
- Three types: personal_performance, class_delivery, program_evaluation
"""


from app.services.prompts_content import (
    ANALYSIS_PROMPT_TEMPLATE,
    ANALYSIS_PROMPT_V2_TEMPLATE,
    CLASS_DELIVERY_TEMPLATE,
    COMPARISON_SYSTEM_PROMPT,
    PERSONAL_PERFORMANCE_TEMPLATE,
    PROGRAM_EVALUATION_TEMPLATE,
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_V2,
)


# Version registry. Update on every prompt revision. Each builder also emits
# its own version into its output JSON so reports are self-describing.
PROMPT_VERSION_V1 = "1.0"   # Original JSON-output prompt — Apr 2026
PROMPT_VERSION_V2 = "2.0"   # Andragogy expansion + efficiency consolidation — May 2026


def build_analysis_prompt(
    transcript: str,
    instructor_name: str = "the instructor",
    class_name: str | None = None,
) -> str:
    """Build the full analysis prompt for Claude.

    This is the core "algorithm" of the product. It instructs Claude to:
    1. Apply strict operational definitions for consistent counting
    2. Divide the transcript into 3 segments for balanced sampling
    3. Analyze 4 dimensions with specific metrics
    4. Extract evidence with timestamps across all segments
    5. Calculate metrics with shown formulas and confidence labels
    6. Generate a structured JSON coaching report

    The output is structured JSON — every key maps directly to a section
    in the PDF report. No markdown parsing, no missing sections.

    Args:
        transcript: The full timestamped transcript text.
        instructor_name: Name of the instructor (for personalization).
        class_name: Name/identifier of the class being taught.

    Returns:
        The complete prompt string to send to Claude.
    """
    class_line = f" — {class_name}" if class_name else ""
    return ANALYSIS_PROMPT_TEMPLATE.format(
        instructor_name=instructor_name,
        class_line=class_line,
        transcript=transcript,
    )


# =============================================================================
# Single-Session Analysis Prompt — v2
# =============================================================================
#
# v2 changes vs v1:
#   1. Hoisted "Adult Learning Principles" canonical block near top of prompt,
#      with all SIX Knowles assumptions spelled out (v1 covered only five —
#      missing "readiness from role transitions").
#   2. Vygotsky's Zone of Proximal Development explicit in Dimension 3
#      (scaffolding theory grounding).
#   3. Kolb's experiential learning cycle as a lens for evaluating analogies
#      and examples in Dimension 3.
#   4. Mezirow's three-level critical reflection (content / process / premise)
#      structures the three coaching_reflections questions.
#   5. Universal Field Rules section consolidates "Plain prose only", "Full
#      paragraph", "Verbatim quote" instructions — appeared 15+ times in v1.
#   6. Per-dimension principle restatements replaced with single canonical
#      reference (eliminates 7+ near-duplicate restatements).
#   7. next_steps items now include an explicit deadline phrase
#      ("before the next session") and identify which adult learning
#      principle the action serves.
#   8. prompt_version field emitted into the output JSON for forensics.
#
# Contract with the PDF generator: UNCHANGED. All locked JSON keys preserved
# (instructor_name, session_date, session_topic, executive_summary, metrics,
# strengths, growth_opportunities, top_5_improvements, timestamped_moments,
# coaching_reflections, next_steps). coaching_reflections remains a list of
# three strings; next_steps remains a dict of keep_doing/start_doing/adjust.
# action_plan intentionally NOT emitted (it would be dead code — PDF only
# falls back to action_plan when next_steps is empty).


def build_analysis_prompt_v2(
    transcript: str,
    instructor_name: str = "the instructor",
    class_name: str | None = None,
) -> str:
    """Build the v2 analysis prompt for Claude.

    Output contract is identical to v1 from the PDF generator's perspective —
    every locked top-level key and nested field name from v1 is preserved.
    The differences live in (a) the prompt's internal organization (less
    redundancy, single canonical principle block) and (b) the depth of
    andragogical grounding (all six Knowles assumptions, plus ZPD, Kolb, and
    Mezirow as supporting frameworks).

    Args:
        transcript: The full timestamped transcript text.
        instructor_name: Name of the instructor (for personalization).
        class_name: Name/identifier of the class being taught.

    Returns:
        The complete prompt string to send to Claude.
    """
    class_line = f" — {class_name}" if class_name else ""
    return ANALYSIS_PROMPT_V2_TEMPLATE.format(
        PROMPT_VERSION_V2=PROMPT_VERSION_V2,
        instructor_name=instructor_name,
        class_line=class_line,
        transcript=transcript,
    )


# =============================================================================
# Comparison Prompts — Multi-video cross-session analysis
# =============================================================================


def build_personal_performance_prompt(evaluations_data: list[dict]) -> str:
    """Build a prompt for comparing one instructor's sessions over time.

    This comparison type answers: "How has this instructor evolved?"

    Args:
        evaluations_data: List of dicts, each with:
            - label: str (e.g., "Session 1")
            - date: str (session date)
            - instructor_name: str
            - report_markdown: str (individual coaching report)
            - metrics: dict (extracted metrics from individual eval)

    Returns:
        The complete prompt string for Claude.
    """
    instructor_name = evaluations_data[0].get("instructor_name", "the instructor")
    session_count = len(evaluations_data)

    session_blocks = []
    for i, ev in enumerate(evaluations_data):
        block = _format_session_block(ev, i, include_instructor=False)
        session_blocks.append(block)

    sessions_text = "\n---\n".join(session_blocks)

    return PERSONAL_PERFORMANCE_TEMPLATE.format(
        session_count=session_count,
        instructor_name=instructor_name,
        sessions_text=sessions_text,
    )


def build_class_delivery_prompt(
    evaluations_data: list[dict],
    class_tag: str = "the class",
) -> str:
    """Build a prompt for comparing different instructors teaching the same class.

    This comparison type answers: "How do different instructors deliver the same material?"

    Args:
        evaluations_data: List of dicts (same structure as personal_performance).
        class_tag: Name/identifier of the class being compared.

    Returns:
        The complete prompt string for Claude.
    """
    instructor_count = len(evaluations_data)

    session_blocks = []
    for i, ev in enumerate(evaluations_data):
        block = _format_session_block(ev, i, include_instructor=True)
        session_blocks.append(block)

    sessions_text = "\n---\n".join(session_blocks)

    return CLASS_DELIVERY_TEMPLATE.format(
        instructor_count=instructor_count,
        class_tag=class_tag,
        sessions_text=sessions_text,
    )


def build_program_evaluation_prompt(evaluations_data: list[dict]) -> str:
    """Build a prompt for evaluating overall program delivery quality.

    This comparison type answers: "Is this program consistent and effective?"

    Args:
        evaluations_data: List of dicts (same structure as personal_performance).

    Returns:
        The complete prompt string for Claude.
    """
    session_count = len(evaluations_data)

    session_blocks = []
    for i, ev in enumerate(evaluations_data):
        block = _format_session_block(ev, i, include_instructor=True)
        session_blocks.append(block)

    sessions_text = "\n---\n".join(session_blocks)

    return PROGRAM_EVALUATION_TEMPLATE.format(
        session_count=session_count,
        sessions_text=sessions_text,
    )


# =============================================================================
# Helpers
# =============================================================================


def _format_session_block(ev: dict, index: int, include_instructor: bool = True) -> str:
    """Format a single evaluation dict into a text block for comparison prompts.

    Centralizes the session-block formatting that was previously duplicated
    across the three comparison prompt builders.
    """
    name = ev.get("instructor_name", f"Instructor {index + 1}")
    label = ev.get("label", f"Session {index + 1}")
    date = ev.get("date", "Not specified")
    metrics_text = _format_metrics(ev.get("metrics", {}))
    report = ev.get("report_markdown", "No report available.")

    header = f"SESSION: {label}"
    instructor_line = f"Instructor: {name}\n" if include_instructor else ""

    return f"""{header}
{instructor_line}Date: {date}
Key Metrics: {metrics_text}

Individual Coaching Report:
{report}
"""


def _format_metrics(metrics: dict) -> str:
    """Format a metrics dict as a readable one-line summary.

    Used inside comparison prompts to give Claude a quick numeric overview
    of each session before the full report.
    """
    if not metrics:
        return "No metrics available"

    parts = []
    label_map = {
        "wpm": "WPM",
        "pauses_per_10min": "Pauses/10min",
        "filler_words_per_min": "Fillers/min",
        "questions_per_5min": "Questions/5min",
        "understanding_checks_per_hour": "Checks/hr",
        "tangent_percentage": "Tangent%",
        "curse_of_knowledge_count": "CoK instances",
    }
    for key, label in label_map.items():
        if key in metrics:
            value = metrics[key]
            parts.append(f"{label}: {value}")

    return " | ".join(parts) if parts else "No standard metrics"


# Map comparison type strings to their prompt builders
COMPARISON_PROMPT_BUILDERS = {
    "personal_performance": build_personal_performance_prompt,
    "class_delivery": build_class_delivery_prompt,
    "program_evaluation": build_program_evaluation_prompt,
}
