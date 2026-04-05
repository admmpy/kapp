"""Tests for LLM listening practice generation and answer checking routes."""

import json

import routes.llm as llm_routes


class _FakeLLMClient:
    def __init__(self, response_text: str):
        self._response_text = response_text

    def chat(self, **kwargs):
        return self._response_text


class _FakeTTSService:
    def generate_audio(self, text, lang="ko", slow=False):  # pragma: no cover - simple fake
        return "fake-audio.mp3"

    def get_audio_url(self, filename):  # pragma: no cover - simple fake
        return f"/api/audio/{filename}"


def _enable_llm(app):
    app.config["LLM_ENABLED"] = True


def _mock_deps(monkeypatch, response_text: str):
    monkeypatch.setattr(llm_routes, "get_llm_client", lambda: _FakeLLMClient(response_text))

    import tts_service

    monkeypatch.setattr(tts_service, "get_tts_service", lambda cache_dir: _FakeTTSService())


def test_listening_practice_requires_topic(client, app):
    _enable_llm(app)
    response = client.post("/api/llm/listening-practice", json={"topic": ""})
    assert response.status_code == 400
    assert response.get_json()["error"] == "topic is required"


def test_listening_practice_generates_answer_key_and_hides_correct_answer(client, app, monkeypatch):
    _enable_llm(app)
    llm_routes._listening_answer_store.clear()

    llm_payload = {
        "korean_text": "저는 커피를 주문해요.",
        "romanization": "jeoneun keopireul jumunhaeyo.",
        "english_translation": "I order coffee.",
        "question": "What is the speaker doing?",
        "options": [
            "Ordering coffee",
            "Asking for directions",
            "Paying for groceries",
            "Calling a friend",
        ],
        "correct_answer": "Ordering coffee",
        "explanation": "The sentence directly says the speaker is ordering coffee.",
    }
    _mock_deps(monkeypatch, json.dumps(llm_payload))

    response = client.post(
        "/api/llm/listening-practice",
        json={"topic": "ordering coffee", "level": 2},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["question"] == llm_payload["question"]
    assert len(body["options"]) == 4
    assert "answer_key" in body and isinstance(body["answer_key"], str)
    assert "correct_answer" not in body


def test_listening_practice_rejects_invalid_option_count(client, app, monkeypatch):
    _enable_llm(app)
    llm_routes._listening_answer_store.clear()

    llm_payload = {
        "korean_text": "저는 커피를 주문해요.",
        "question": "What is the speaker doing?",
        "options": ["Ordering coffee", "Asking for directions"],
        "correct_answer": "Ordering coffee",
    }
    _mock_deps(monkeypatch, json.dumps(llm_payload))

    response = client.post(
        "/api/llm/listening-practice",
        json={"topic": "ordering coffee", "level": 2},
    )
    assert response.status_code == 500
    assert "invalid options" in response.get_json()["error"]


def test_listening_practice_rejects_mismatched_correct_answer(client, app, monkeypatch):
    _enable_llm(app)
    llm_routes._listening_answer_store.clear()

    llm_payload = {
        "korean_text": "저는 커피를 주문해요.",
        "question": "What is the speaker doing?",
        "options": [
            "Ordering coffee",
            "Asking for directions",
            "Paying for groceries",
            "Calling a friend",
        ],
        "correct_answer": "Cooking dinner",
    }
    _mock_deps(monkeypatch, json.dumps(llm_payload))

    response = client.post(
        "/api/llm/listening-practice",
        json={"topic": "ordering coffee", "level": 2},
    )
    assert response.status_code == 500
    assert "mismatched correct_answer" in response.get_json()["error"]


def test_listening_practice_check_answer_one_time_key(client, app, monkeypatch):
    _enable_llm(app)
    llm_routes._listening_answer_store.clear()

    llm_payload = {
        "korean_text": "저는 커피를 주문해요.",
        "question": "What is the speaker doing?",
        "options": [
            "Ordering coffee",
            "Asking for directions",
            "Paying for groceries",
            "Calling a friend",
        ],
        "correct_answer": "Ordering coffee",
    }
    _mock_deps(monkeypatch, json.dumps(llm_payload))

    generate_response = client.post(
        "/api/llm/listening-practice",
        json={"topic": "ordering coffee", "level": 2},
    )
    answer_key = generate_response.get_json()["answer_key"]

    check_response = client.post(
        "/api/llm/listening-practice/check",
        json={"answer_key": answer_key, "selected_answer": "Ordering coffee"},
    )
    assert check_response.status_code == 200
    assert check_response.get_json()["correct"] is True

    reused_response = client.post(
        "/api/llm/listening-practice/check",
        json={"answer_key": answer_key, "selected_answer": "Ordering coffee"},
    )
    assert reused_response.status_code == 400
    assert "invalid or expired" in reused_response.get_json()["error"]
