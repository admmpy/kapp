"""Daily Mission endpoint — generates a focused 30-45 min learning plan."""
from datetime import datetime, timezone
from flask import Blueprint, jsonify
from sqlalchemy import func
from database import db
from models_v2 import VocabularyItem, ExerciseSRS, UserProgress, Lesson, Unit, Course
from routes.helpers import get_current_user_id

daily_mission_bp = Blueprint("daily_mission", __name__)


@daily_mission_bp.route("/daily-mission", methods=["GET"])
def get_daily_mission():
    """Return today's mission: SRS reviews due + next incomplete lesson + lyric lesson."""
    user_id = get_current_user_id()
    now = datetime.now(timezone.utc)

    # --- Vocab SRS due count (VocabularyItem has no user_id — shared global deck) ---
    vocab_due = (
        db.session.query(func.count(VocabularyItem.id))
        .filter(VocabularyItem.next_review_date <= now)
        .scalar()
        or 0
    )

    # --- Exercise SRS due count ---
    exercise_due = (
        db.session.query(func.count(ExerciseSRS.id))
        .filter(
            ExerciseSRS.user_id == user_id,
            ExerciseSRS.next_review_date <= now,
        )
        .scalar()
        or 0
    )

    total_srs_due = vocab_due + exercise_due

    # --- Next incomplete lesson (non-lyric) ---
    completed_lesson_ids = (
        db.session.query(UserProgress.lesson_id)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.is_completed == True,  # noqa: E712
        )
        .subquery()
    )

    next_lesson = (
        db.session.query(Lesson)
        .join(Unit)
        .join(Course)
        .filter(
            Lesson.id.not_in(completed_lesson_ids),
            ~Lesson.title.ilike("%lyric%"),
            ~Unit.title.ilike("%lyric%"),
        )
        .order_by(Course.id, Unit.id, Lesson.id)
        .first()
    )

    # --- Next lyric lesson ---
    next_lyric = (
        db.session.query(Lesson)
        .join(Unit)
        .filter(
            Lesson.id.not_in(completed_lesson_ids),
            Unit.title.ilike("%lyric%"),
        )
        .order_by(Unit.id, Lesson.id)
        .first()
    )

    tasks = []

    if total_srs_due > 0:
        tasks.append(
            {
                "type": "srs_review",
                "label": "SRS Review",
                "description": f"{total_srs_due} card{'s' if total_srs_due != 1 else ''} due today",
                "estimated_minutes": max(5, min(15, total_srs_due // 2)),
                "icon": "🔁",
                "action": "review",
            }
        )

    if next_lesson:
        tasks.append(
            {
                "type": "lesson",
                "label": "Next Lesson",
                "description": next_lesson.title,
                "lesson_id": next_lesson.id,
                "estimated_minutes": getattr(next_lesson, "estimated_minutes", 10) or 10,
                "icon": "📖",
                "action": "lesson",
            }
        )

    if next_lyric:
        tasks.append(
            {
                "type": "lyric_lesson",
                "label": "Lyric Lesson",
                "description": next_lyric.title,
                "lesson_id": next_lyric.id,
                "estimated_minutes": getattr(next_lyric, "estimated_minutes", 15) or 15,
                "icon": "🎵",
                "action": "lesson",
            }
        )

    if not tasks:
        tasks.append(
            {
                "type": "free",
                "label": "Explore",
                "description": "All caught up! Browse lessons or start a conversation.",
                "estimated_minutes": 10,
                "icon": "✨",
                "action": "home",
            }
        )

    total_minutes = sum(t["estimated_minutes"] for t in tasks)

    return jsonify(
        {
            "tasks": tasks,
            "total_estimated_minutes": total_minutes,
            "srs_due": total_srs_due,
            "generated_at": now.isoformat(),
        }
    )
