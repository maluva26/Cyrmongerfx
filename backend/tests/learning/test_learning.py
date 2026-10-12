import pytest
from rest_framework import status

from apps.learning.models import Lesson


@pytest.fixture
def published_lesson(db, admin):
    return Lesson.objects.create(title="Test", category="test", body="# Test", status=Lesson.Status.PUBLISHED, created_by=admin)


class TestLearning:
    def test_lesson_list(self, trader_client, published_lesson):
        r = trader_client.get("/api/v1/lessons")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.json()) >= 1

    def test_quiz_submit(self, trader_client, published_lesson):
        q = published_lesson.questions.create(prompt="Q", explanation="E", order_index=0)
        correct = q.options.create(text="A", is_correct=True)
        q.options.create(text="B", is_correct=False)
        r = trader_client.post(f"/api/v1/lessons/{published_lesson.lesson_id}/quiz", {"answers": {str(q.question_id): str(correct.option_id)}}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["score"] == 100

    def test_quiz_wrong_answer_scores_zero(self, trader_client, published_lesson):
        q = published_lesson.questions.create(prompt="Q2", explanation="E", order_index=0)
        q.options.create(text="A", is_correct=True)
        wrong = q.options.create(text="B", is_correct=False)
        r = trader_client.post(f"/api/v1/lessons/{published_lesson.lesson_id}/quiz", {"answers": {str(q.question_id): str(wrong.option_id)}}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["score"] == 0

    def test_progress(self, trader_client):
        r = trader_client.get("/api/v1/progress")
        assert r.status_code == status.HTTP_200_OK
        assert "lessons_total" in r.json()

    def test_admin_create(self, admin_client):
        r = admin_client.post("/api/v1/admin/lessons", {"title": "Admin Lesson", "category": "test", "body": "body"}, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_trader_cannot_admin(self, trader_client):
        r = trader_client.get("/api/v1/admin/lessons")
        assert r.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    def _add_question(self, lesson, prompt="Q", correct_text="A"):
        question = lesson.questions.create(prompt=prompt, explanation="E", order_index=0)
        correct = question.options.create(text=correct_text, is_correct=True)
        question.options.create(text="wrong", is_correct=False)
        return question, correct

    def test_draft_lesson_is_not_listed(self, trader_client, admin):
        Lesson.objects.create(title="Draft", category="test", body="b", status=Lesson.Status.DRAFT, created_by=admin)
        r = trader_client.get("/api/v1/lessons")
        assert r.status_code == status.HTTP_200_OK
        assert all(item["title"] != "Draft" for item in r.json())

    def test_lesson_detail_includes_questions(self, trader_client, published_lesson):
        self._add_question(published_lesson)
        r = trader_client.get(f"/api/v1/lessons/{published_lesson.lesson_id}")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.json()["questions"]) == 1
        assert len(r.json()["questions"][0]["options"]) == 2

    def test_quiz_requires_an_answer_for_every_question(self, trader_client, published_lesson):
        self._add_question(published_lesson)
        r = trader_client.post(f"/api/v1/lessons/{published_lesson.lesson_id}/quiz", {"answers": {}}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_QUIZ_ANSWERS"

    def test_quiz_rejects_option_from_another_question(self, trader_client, published_lesson):
        question, _ = self._add_question(published_lesson)
        other_question, other_option = self._add_question(published_lesson, prompt="Q2")
        answers = {str(question.question_id): str(other_option.option_id), str(other_question.question_id): str(other_option.option_id)}
        r = trader_client.post(f"/api/v1/lessons/{published_lesson.lesson_id}/quiz", {"answers": answers}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_QUIZ_ANSWERS"

    def test_progress_reflects_a_passed_quiz(self, trader_client, published_lesson):
        question, correct = self._add_question(published_lesson)
        submit = trader_client.post(f"/api/v1/lessons/{published_lesson.lesson_id}/quiz", {"answers": {str(question.question_id): str(correct.option_id)}}, format="json")
        assert submit.status_code == status.HTTP_200_OK

        r = trader_client.get("/api/v1/progress")
        assert r.status_code == status.HTTP_200_OK
        body = r.json()
        assert body["lessons_total"] == 1
        assert body["lessons_completed"] == 1
        assert body["completion_percent"] == 100

    def test_admin_publish_requires_questions(self, admin_client, admin):
        lesson = Lesson.objects.create(title="Empty", category="test", body="b", created_by=admin)
        r = admin_client.post(f"/api/v1/admin/lessons/{lesson.lesson_id}/publish", {}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "LESSON_HAS_NO_QUESTIONS"

    def test_admin_can_add_question_then_publish(self, admin_client, admin):
        lesson = Lesson.objects.create(title="To publish", category="test", body="b", created_by=admin)
        payload = {"prompt": "P", "explanation": "E", "order_index": 0, "options": [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}]}
        created = admin_client.post(f"/api/v1/admin/lessons/{lesson.lesson_id}/questions", payload, format="json")
        assert created.status_code == status.HTTP_201_CREATED

        published = admin_client.post(f"/api/v1/admin/lessons/{lesson.lesson_id}/publish", {}, format="json")
        assert published.status_code == status.HTTP_200_OK
        lesson.refresh_from_db()
        assert lesson.status == Lesson.Status.PUBLISHED

    def test_admin_question_requires_exactly_one_correct_option(self, admin_client, admin):
        lesson = Lesson.objects.create(title="Bad", category="test", body="b", created_by=admin)
        payload = {"prompt": "P", "explanation": "E", "order_index": 0, "options": [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": True}]}
        r = admin_client.post(f"/api/v1/admin/lessons/{lesson.lesson_id}/questions", payload, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_status_endpoint(self, admin_client):
        r = admin_client.get("/api/v1/admin/status")
        assert r.status_code == status.HTTP_200_OK
        assert "lessons" in r.json()
