"""
Demo seed — synthetic data for the portfolio hero screenshot ONLY.

Creates one instructor (the UUID the frontend Dashboard hardcodes) with a
six-session improvement arc, so the dashboard renders real trend charts,
recurring strengths, and growth areas. No real recordings or people.

Run from backend/ with the venv active:
    python seed_demo.py
Idempotent: if the demo instructor already exists, it does nothing.
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal, init_db
from app.models import (
    Comparison,
    ComparisonEvaluation,
    Evaluation,
    Organization,
    User,
    Video,
)

# The frontend hardcodes this instructor id (Dashboard.tsx).
INSTRUCTOR_ID = uuid.UUID("3707ea11-ce8a-46dc-a4ae-93a5b895c0bb")
ORG_ID = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000001")


def _dt(month: int, day: int) -> datetime:
    return datetime(2026, month, day, 15, 0, 0, tzinfo=timezone.utc)


# Six sessions, chronological. The arc: pace settles toward the 120-160 target,
# filler words fall, pauses/questions rise, tangent time drops.
SESSIONS = [
    {
        "file": "intro-to-databases-wk1.mp4", "date": _dt(1, 12),
        "metrics": {"wpm": 176, "pauses_per_10min": 2.4, "filler_words_per_min": 5.1,
                    "questions_per_5min": 0.9, "tangent_percentage": 17.5},
        "strengths": ["Experience-Based Analogies", "Confident Vocal Variety"],
        "growth": ["Filler Word Reduction", "Tighten Tangents", "Slow Speaking Pace"],
    },
    {
        "file": "relational-modeling-wk2.mp4", "date": _dt(2, 9),
        "metrics": {"wpm": 170, "pauses_per_10min": 3.0, "filler_words_per_min": 4.3,
                    "questions_per_5min": 1.2, "tangent_percentage": 14.0},
        "strengths": ["Experience-Based Analogies"],
        "growth": ["Filler Word Reduction", "Tighten Tangents", "Slow Speaking Pace"],
    },
    {
        "file": "sql-joins-deep-dive-wk3.mp4", "date": _dt(3, 8),
        "metrics": {"wpm": 162, "pauses_per_10min": 3.6, "filler_words_per_min": 3.6,
                    "questions_per_5min": 1.6, "tangent_percentage": 11.5},
        "strengths": ["Experience-Based Analogies", "Clear Structural Signposting"],
        "growth": ["Filler Word Reduction", "Tighten Tangents"],
    },
    {
        "file": "indexing-and-performance-wk4.mp4", "date": _dt(4, 5),
        "metrics": {"wpm": 158, "pauses_per_10min": 4.2, "filler_words_per_min": 2.9,
                    "questions_per_5min": 1.9, "tangent_percentage": 9.5},
        "strengths": ["Experience-Based Analogies", "Clear Structural Signposting",
                      "Inclusive Questioning"],
        "growth": ["Filler Word Reduction", "Add Wait Time After Questions"],
    },
    {
        "file": "transactions-and-acid-wk5.mp4", "date": _dt(5, 3),
        "metrics": {"wpm": 152, "pauses_per_10min": 4.8, "filler_words_per_min": 2.4,
                    "questions_per_5min": 2.2, "tangent_percentage": 8.0},
        "strengths": ["Experience-Based Analogies", "Clear Structural Signposting",
                      "Inclusive Questioning", "Confident Vocal Variety"],
        "growth": ["Add Wait Time After Questions"],
    },
    {
        "file": "query-optimization-capstone-wk6.mp4", "date": _dt(5, 31),
        "metrics": {"wpm": 149, "pauses_per_10min": 5.1, "filler_words_per_min": 2.0,
                    "questions_per_5min": 2.5, "tangent_percentage": 6.8},
        "strengths": ["Experience-Based Analogies", "Clear Structural Signposting",
                      "Inclusive Questioning"],
        "growth": ["Add Wait Time After Questions"],
    },
]

# Short evidence text per theme, so each item is a realistic {title, text, timestamp}.
THEME_TEXT = {
    "Experience-Based Analogies": "Grounded an abstract concept in a concrete, real-world scenario adult learners recognized.",
    "Confident Vocal Variety": "Used pitch and emphasis to mark transitions and keep attention.",
    "Clear Structural Signposting": "Previewed the agenda and signaled section boundaries explicitly.",
    "Inclusive Questioning": "Invited participation from quieter learners by name and with open prompts.",
    "Filler Word Reduction": "Frequent 'um' / 'like' fillers diluted otherwise clear explanations.",
    "Tighten Tangents": "A side-story ran long and pushed core material to the end of the session.",
    "Slow Speaking Pace": "Pace exceeded the 120-160 WPM target during dense material.",
    "Add Wait Time After Questions": "Questions were answered too quickly to let learners think.",
}


def _items(titles, base_ts):
    out = []
    for i, t in enumerate(titles):
        mm = 8 + i * 7
        out.append({
            "title": t,
            "text": THEME_TEXT.get(t, ""),
            "timestamp": f"00:{mm:02d}:{(i * 13) % 60:02d}",
        })
    return out


async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.id == INSTRUCTOR_ID))
        if existing.scalar_one_or_none():
            print("Demo instructor already present — nothing to seed.")
            return

        db.add(Organization(
            id=ORG_ID, name="Northwind Technical Institute",
            subscription_tier="professional", max_evaluations_per_month=200, max_users=40,
            billing_email="ops@northwind.example.edu",
        ))
        db.add(User(
            id=INSTRUCTOR_ID, email="jordan.rivera@northwind.example.edu",
            password_hash="x", display_name="Jordan Rivera",
            role="instructor", organization_id=ORG_ID,
        ))

        eval_ids = []
        for s in SESSIONS:
            video_id = uuid.uuid4()
            eval_id = uuid.uuid4()
            eval_ids.append(eval_id)
            db.add(Video(
                id=video_id, instructor_id=INSTRUCTOR_ID, filename=s["file"],
                s3_key=f"local/{s['file']}", file_size_bytes=820_000_000,
                duration_seconds=3300, format="mp4", upload_status="completed",
                uploaded_at=s["date"],
            ))
            db.add(Evaluation(
                id=eval_id, video_id=video_id, instructor_id=INSTRUCTOR_ID,
                status="completed", processing_started_at=s["date"],
                processing_completed_at=s["date"], created_at=s["date"],
                metrics=s["metrics"],
                strengths=_items(s["strengths"], s["date"]),
                growth_opportunities=_items(s["growth"], s["date"]),
                coaching_data={"summary": f"Coaching analysis for {s['file']}."},
            ))

        # One completed cross-session comparison over the last three sessions.
        comp_id = uuid.uuid4()
        db.add(Comparison(
            id=comp_id, title="Jordan Rivera — Spring Term Progress",
            comparison_type="personal_performance", status="completed",
            organization_id=ORG_ID, created_by_id=INSTRUCTOR_ID,
            created_at=_dt(6, 1), processing_started_at=_dt(6, 1),
            processing_completed_at=_dt(6, 1),
            metrics={"wpm": {"avg": 153, "trend": "improving"},
                     "filler_words_per_min": {"avg": 2.4, "trend": "improving"}},
            strengths=_items(["Experience-Based Analogies", "Clear Structural Signposting"], _dt(6, 1)),
            growth_opportunities=_items(["Add Wait Time After Questions"], _dt(6, 1)),
        ))
        for order, eid in enumerate(eval_ids[-3:]):
            db.add(ComparisonEvaluation(
                id=uuid.uuid4(), comparison_id=comp_id, evaluation_id=eid,
                display_order=order, label=f"Session {order + 4}",
            ))

        await db.commit()
        print(f"Seeded instructor {INSTRUCTOR_ID} with {len(SESSIONS)} evaluations + 1 comparison.")


if __name__ == "__main__":
    asyncio.run(main())
