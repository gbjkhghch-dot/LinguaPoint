"""Запуск: python manage.py shell < queries.py; предварительно загрузить данные."""
from django.db.models import Count, Avg, Sum
from school.models import StudyGroup, Enrollment, TestResult, Homework

queries = [
    ('1. Фильтрация: группы B1', StudyGroup.objects.filter(level__code='B1')),
    ('2. Сортировка: ближайший старт', StudyGroup.objects.order_by('start_date','title')),
    ('3. Агрегация: число учеников, средний результат, сумма баллов', TestResult.objects.values('test__title').annotate(count=Count('id'),avg=Avg('score'),total=Sum('score'))),
    ('4. 1:N + select_related: зачисления и группы', Enrollment.objects.select_related('group','student').order_by('id')),
    ('5. M:N + prefetch_related: группы и ученики', StudyGroup.objects.prefetch_related('students').order_by('id')),
]
for title, qs in queries:
    print('\n'+title+'\nORM:',repr(qs.query),'\nSQL:',str(qs.query))
    if 'prefetch_related' in title:
        for group in qs[:5]: print(group.title, [p.full_name for p in group.students.all()])
    else:
        print('Результат:',list(qs[:10]))
