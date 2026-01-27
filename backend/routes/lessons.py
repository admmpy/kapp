"""
Lesson routes for lesson content and exercises

Endpoints:
- GET /api/lessons/:id - Get lesson with exercises
- POST /api/lessons/:id/start - Mark lesson started
- POST /api/lessons/:id/complete - Mark lesson completed
- POST /api/exercises/:id/submit - Submit exercise answer
"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import db
from models_v2 import Lesson, Exercise, UserProgress
from utils import not_found_response, error_response, validation_error_response
import logging

logger = logging.getLogger(__name__)

lessons_bp = Blueprint('lessons', __name__)


@lessons_bp.route('/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id: int):
    """
    Get lesson with grammar explanation and exercises

    Response:
        {
            "lesson": {
                "id": 1,
                "title": "Hello & Goodbye",
                "description": "...",
                "grammar_explanation": "...",
                "grammar_tip": "...",
                "estimated_minutes": 5,
                "unit_id": 1,
                "exercises": [
                    {
                        "id": 1,
                        "exercise_type": "vocabulary",
                        "question": "...",
                        "instruction": "...",
                        "korean_text": "...",
                        "romanization": "...",
                        "english_text": "...",
                        "options": ["a", "b", "c", "d"],
                        "audio_url": "..."
                    },
                    ...
                ],
                "progress": {
                    "is_started": true,
                    "is_completed": false,
                    "completed_exercises": 3,
                    "total_exercises": 8
                }
            }
        }
    """
    try:
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return not_found_response('Lesson')

        # Get user progress (user_id=1 for now)
        progress = db.session.query(UserProgress).filter(
            UserProgress.lesson_id == lesson_id,
            UserProgress.user_id == 1
        ).first()

        exercises = []
        for ex in lesson.exercises:
            exercise_data = {
                'id': ex.id,
                'exercise_type': ex.exercise_type.value,
                'question': ex.question,
                'instruction': ex.instruction,
                'display_order': ex.display_order
            }

            # Add type-specific fields
            if ex.korean_text:
                exercise_data['korean_text'] = ex.korean_text
            if ex.romanization:
                exercise_data['romanization'] = ex.romanization
            if ex.english_text:
                exercise_data['english_text'] = ex.english_text
            if ex.content_text:
                exercise_data['content_text'] = ex.content_text
            if ex.audio_url:
                exercise_data['audio_url'] = ex.audio_url
            if ex.options:
                try:
                    exercise_data['options'] = json.loads(ex.options)
                except json.JSONDecodeError:
                    exercise_data['options'] = []

            # Don't include correct_answer in the response (for security)
            exercises.append(exercise_data)

        progress_data = None
        if progress:
            progress_data = {
                'is_started': progress.is_started,
                'is_completed': progress.is_completed,
                'completed_exercises': progress.completed_exercises,
                'total_exercises': progress.total_exercises,
                'score': progress.score
            }

        return jsonify({
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'grammar_explanation': lesson.grammar_explanation,
                'grammar_tip': lesson.grammar_tip,
                'estimated_minutes': lesson.estimated_minutes,
                'unit_id': lesson.unit_id,
                'exercise_count': lesson.exercise_count,
                'exercises': exercises,
                'progress': progress_data
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting lesson {lesson_id}: {e}")
        return error_response('Failed to get lesson', 500, str(e))


@lessons_bp.route('/lessons/<int:lesson_id>/start', methods=['POST'])
def start_lesson(lesson_id: int):
    """
    Mark lesson as started

    Response:
        {
            "success": true,
            "progress": {
                "is_started": true,
                "started_at": "2024-01-15T10:30:00Z"
            }
        }
    """
    try:
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return not_found_response('Lesson')

        # Get or create progress record (user_id=1 for now)
        progress = db.session.query(UserProgress).filter(
            UserProgress.lesson_id == lesson_id,
            UserProgress.user_id == 1
        ).first()

        if not progress:
            progress = UserProgress(
                lesson_id=lesson_id,
                user_id=1,
                total_exercises=lesson.exercise_count
            )
            db.session.add(progress)

        if not progress.is_started:
            progress.is_started = True
            progress.started_at = datetime.utcnow()
            progress.total_exercises = lesson.exercise_count

        progress.last_activity_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'progress': {
                'is_started': progress.is_started,
                'started_at': progress.started_at.isoformat() if progress.started_at else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error starting lesson {lesson_id}: {e}")
        db.session.rollback()
        return error_response('Failed to start lesson', 500, str(e))


@lessons_bp.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
def complete_lesson(lesson_id: int):
    """
    Mark lesson as completed

    Request body:
        {
            "score": 85.5,
            "time_spent_seconds": 300
        }

    Response:
        {
            "success": true,
            "progress": {
                "is_completed": true,
                "completed_at": "2024-01-15T10:35:00Z",
                "score": 85.5
            }
        }
    """
    try:
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return not_found_response('Lesson')

        data = request.get_json() or {}
        score = data.get('score')
        time_spent = data.get('time_spent_seconds', 0)

        # Get or create progress record
        progress = db.session.query(UserProgress).filter(
            UserProgress.lesson_id == lesson_id,
            UserProgress.user_id == 1
        ).first()

        if not progress:
            progress = UserProgress(
                lesson_id=lesson_id,
                user_id=1,
                is_started=True,
                started_at=datetime.utcnow(),
                total_exercises=lesson.exercise_count
            )
            db.session.add(progress)

        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        progress.completed_exercises = lesson.exercise_count
        progress.last_activity_at = datetime.utcnow()

        if score is not None:
            progress.score = float(score)
        if time_spent:
            progress.time_spent_seconds = int(time_spent)

        db.session.commit()

        return jsonify({
            'success': True,
            'progress': {
                'is_completed': progress.is_completed,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                'score': progress.score
            }
        }), 200

    except Exception as e:
        logger.error(f"Error completing lesson {lesson_id}: {e}")
        db.session.rollback()
        return error_response('Failed to complete lesson', 500, str(e))


@lessons_bp.route('/exercises/<int:exercise_id>/submit', methods=['POST'])
def submit_exercise(exercise_id: int):
    """
    Submit an answer for an exercise

    Request body:
        {
            "answer": "hello"
        }

    Response:
        {
            "correct": true,
            "correct_answer": "hello",
            "explanation": "..."
        }
    """
    try:
        exercise = db.session.get(Exercise, exercise_id)
        if not exercise:
            return not_found_response('Exercise')

        data = request.get_json()
        if not data or 'answer' not in data:
            return validation_error_response('answer is required')

        user_answer = str(data['answer']).strip().lower()
        correct_answer = exercise.correct_answer.strip().lower()

        is_correct = user_answer == correct_answer

        # Update lesson progress
        progress = db.session.query(UserProgress).filter(
            UserProgress.lesson_id == exercise.lesson_id,
            UserProgress.user_id == 1
        ).first()

        if progress:
            if is_correct and progress.completed_exercises < progress.total_exercises:
                progress.completed_exercises += 1
            progress.last_activity_at = datetime.utcnow()
            db.session.commit()

        return jsonify({
            'correct': is_correct,
            'correct_answer': exercise.correct_answer,
            'explanation': exercise.explanation
        }), 200

    except Exception as e:
        logger.error(f"Error submitting exercise {exercise_id}: {e}")
        db.session.rollback()
        return error_response('Failed to submit exercise', 500, str(e))
