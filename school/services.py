"""Сценарии предметной области (реализация вне views). Для конкурентной записи рекомендуется PostgreSQL."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from .models import (EntranceTest, TestResult, TestAnswer, ScoreBand, StudentLevel,
                     StudyGroup, Enrollment, StudentProfile)

@transaction.atomic
def submit_test(test_id, student, answer_by_question):
    """answer_by_question: {question_id: 'A'|'B'|'C'|'D'}. Только сервер определяет уровень."""
    test = EntranceTest.objects.select_for_update().get(pk=test_id, is_active=True)
    questions = list(test.questions.order_by('position'))
    if not questions or set(answer_by_question) != {q.id for q in questions}:
        raise ValidationError('Необходимо ответить на все вопросы теста')
    max_points = sum(q.points for q in questions)
    bands = list(ScoreBand.objects.filter(test=test).select_related('level').order_by('min_points'))
    # Полная шкала без пробелов, соответствующая языку и максимуму теста.
    if len(bands) != 5 or bands[0].min_points != 0 or bands[-1].max_points != max_points:
        raise ValidationError('Шкала теста заполнена неверно')
    for i, band in enumerate(bands):
        if band.level.language_id != test.language_id or (i and bands[i-1].max_points + 1 != band.min_points):
            raise ValidationError('Шкала теста содержит разрывы/чужой язык')
    score = 0
    for q in questions:
        option=answer_by_question[q.id]
        if option not in 'ABCD':raise ValidationError('Недопустимый вариант ответа')
        if option==q.correct_option:score+=q.points
    level=next(b.level for b in bands if b.min_points <= score <= b.max_points)
    result=TestResult.objects.create(test=test,student=student,score=score,level=level)
    TestAnswer.objects.bulk_create([TestAnswer(result=result,question=q,selected_option=answer_by_question[q.id]) for q in questions])
    if student is not None:
        if student.role != 'student':raise ValidationError('Тест может сохранять профиль только ученика')
        StudentLevel.objects.update_or_create(student=student,language=test.language,defaults={'level':level})
    return result

@transaction.atomic
def enroll_student(group_id, student_id):
    """Блокировка группы и подсчет зачислений должны выполняться внутри одной транзакции PostgreSQL."""
    group=StudyGroup.objects.select_for_update().get(pk=group_id)
    student=StudentProfile.objects.get(pk=student_id,role='student')
    own_level=StudentLevel.objects.filter(student=student,language=group.language).first()
    if not own_level or own_level.level_id != group.level_id:
        raise ValidationError('Уровень ученика не подходит для группы')
    if Enrollment.objects.filter(student=student,group=group).exists():
        raise ValidationError('Ученик уже зачислен')
    count=Enrollment.objects.filter(group=group).count()
    if count>=group.capacity:raise ValidationError('Свободных мест нет')
    record=Enrollment.objects.create(student=student,group=group)
    if count+1>=4 and group.status=='forming':
        group.status='started';group.save(update_fields=['status'])
    return record
