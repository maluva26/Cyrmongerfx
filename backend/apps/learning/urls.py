from django.urls import path

from .views import (
    AdminArchiveLessonView,
    AdminLessonDetailView,
    AdminLessonListView,
    AdminLessonMaterialView,
    AdminPublishLessonView,
    AdminQuestionView,
    AdminStarterModuleView,
    AdminStatusView,
    LessonDetailView,
    LessonListView,
    LessonMaterialDownloadView,
    ProgressView,
    QuizSubmitView,
)

urlpatterns = [
    path("lessons", LessonListView.as_view(), name="lessons"),
    path("lessons/<uuid:lesson_id>", LessonDetailView.as_view(), name="lesson-detail"),
    path("lessons/<uuid:lesson_id>/materials/<uuid:resource_id>/download", LessonMaterialDownloadView.as_view(), name="lesson-material-download"),
    path("lessons/<uuid:lesson_id>/quiz", QuizSubmitView.as_view(), name="quiz-submit"),
    path("progress", ProgressView.as_view(), name="progress"),
    path("admin/lessons", AdminLessonListView.as_view(), name="admin-lessons"),
    path("admin/lesson-templates", AdminStarterModuleView.as_view(), name="admin-lesson-templates"),
    path("admin/lessons/<uuid:lesson_id>", AdminLessonDetailView.as_view(), name="admin-lesson-detail"),
    path("admin/lessons/<uuid:lesson_id>/materials", AdminLessonMaterialView.as_view(), name="admin-lesson-materials"),
    path("admin/lessons/<uuid:lesson_id>/publish", AdminPublishLessonView.as_view(), name="admin-lesson-publish"),
    path("admin/lessons/<uuid:lesson_id>/archive", AdminArchiveLessonView.as_view(), name="admin-lesson-archive"),
    path("admin/lessons/<uuid:lesson_id>/questions", AdminQuestionView.as_view(), name="admin-question"),
    path("admin/status", AdminStatusView.as_view(), name="admin-status"),
]
