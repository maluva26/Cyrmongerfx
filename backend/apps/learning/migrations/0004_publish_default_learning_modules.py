from django.db import migrations


def publish_default_modules(apps, schema_editor):
    from apps.learning.starter_modules import STARTER_MODULES

    db = schema_editor.connection.alias
    Lesson = apps.get_model("learning", "Lesson")
    QuizQuestion = apps.get_model("learning", "QuizQuestion")
    QuizOption = apps.get_model("learning", "QuizOption")

    for module in STARTER_MODULES:
        lesson, created = Lesson.objects.using(db).get_or_create(
            template_key=module["key"],
            defaults={
                "title": module["title"],
                "category": module["category"],
                "body": module["body"],
                "illustration_refs": [module["image_url"]],
                "order_index": module["order_index"],
                "status": "PUBLISHED",
            },
        )
        if not created and lesson.status != "PUBLISHED":
            Lesson.objects.using(db).filter(pk=lesson.pk).update(status="PUBLISHED")

        if QuizQuestion.objects.using(db).filter(lesson_id=lesson.pk).exists():
            continue

        for index, (prompt, correct_answer, incorrect_answers, explanation) in enumerate(module["questions"]):
            question = QuizQuestion.objects.using(db).create(
                lesson_id=lesson.pk,
                prompt=prompt,
                explanation=explanation,
                order_index=index,
            )
            QuizOption.objects.using(db).bulk_create(
                [
                    QuizOption(question_id=question.pk, text=correct_answer, is_correct=True),
                    *[QuizOption(question_id=question.pk, text=answer, is_correct=False) for answer in incorrect_answers],
                ]
            )


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0003_lessonresource"),
    ]

    operations = [
        migrations.RunPython(publish_default_modules, migrations.RunPython.noop),
    ]
