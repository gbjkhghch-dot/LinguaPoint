"""Занятие 5, вариант 12. Концептуальные сущности + поддержка ФТ технического задания."""
from django.conf import settings
from django.db import models
from django.db.models import Q, F

LEVELS = [('A1','A1'),('A2','A2'),('B1','B1'),('B2','B2'),('C1','C1')]

class Language(models.Model):
    name = models.CharField('Название', max_length=80, unique=True)
    code = models.CharField('ISO-код', max_length=8, unique=True)
    class Meta:
        verbose_name = 'Язык'; verbose_name_plural = 'Языки'; ordering = ['name']
    def __str__(self): return self.name

class Level(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='levels', verbose_name='Язык')
    code = models.CharField('Уровень CEFR', max_length=2, choices=LEVELS)
    rank = models.PositiveSmallIntegerField('Порядок', default=1)
    class Meta:
        verbose_name = 'Уровень владения'; verbose_name_plural = 'Уровни владения'; ordering = ['language_id','rank']
        constraints = [models.UniqueConstraint(fields=['language','code'], name='uniq_language_level'), models.UniqueConstraint(fields=['language','rank'], name='uniq_language_rank'),models.CheckConstraint(check=Q(rank__gte=1)&Q(rank__lte=5), name='level_rank_range')]
    def __str__(self): return f'{self.language}: {self.code}'

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile', verbose_name='Пользователь')
    full_name = models.CharField('ФИО', max_length=150)
    role = models.CharField('Роль', max_length=12, choices=[('student','Ученик'),('teacher','Преподаватель'),('methodist','Методист'),('admin','Администратор')], default='student')
    class Meta:
        verbose_name = 'Профиль'; verbose_name_plural = 'Профили'; ordering = ['full_name']
    def __str__(self): return self.full_name

class StudentLevel(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='current_levels', verbose_name='Ученик')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='student_levels', verbose_name='Язык')
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='student_levels', verbose_name='Определённый уровень')
    assigned_at = models.DateTimeField('Дата определения', auto_now=True)
    class Meta:
        verbose_name = 'Уровень ученика'; verbose_name_plural = 'Уровни учеников'; ordering = ['student_id','language_id']
        constraints = [models.UniqueConstraint(fields=['student','language'], name='uniq_student_language')]
    def __str__(self): return f'{self.student} — {self.level}'

class EntranceTest(models.Model):
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='tests', verbose_name='Язык')
    title = models.CharField('Название теста', max_length=150)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    class Meta:
        verbose_name = 'Входной тест'; verbose_name_plural = 'Входные тесты'; ordering = ['title']
        constraints = [models.UniqueConstraint(fields=['language','title'],name='uniq_test_title_language')]
    def __str__(self): return self.title

class TestQuestion(models.Model):
    test = models.ForeignKey(EntranceTest, on_delete=models.CASCADE, related_name='questions', verbose_name='Тест')
    text = models.TextField('Вопрос')
    option_a = models.CharField('A', max_length=250); option_b = models.CharField('B', max_length=250)
    option_c = models.CharField('C', max_length=250); option_d = models.CharField('D', max_length=250)
    correct_option = models.CharField('Ключ', max_length=1, choices=[(x,x) for x in 'ABCD'])
    points = models.PositiveSmallIntegerField('Баллы', default=1)
    position = models.PositiveSmallIntegerField('Порядок', default=1)
    class Meta:
        verbose_name = 'Вопрос теста'; verbose_name_plural = 'Вопросы тестов'; ordering = ['test_id','position']
        constraints = [models.UniqueConstraint(fields=['test','position'],name='uniq_question_position'),models.CheckConstraint(check=Q(points__gte=1),name='question_points_positive')]
    def __str__(self): return f'{self.test}: {self.position}'

class ScoreBand(models.Model):
    test = models.ForeignKey(EntranceTest, on_delete=models.CASCADE, related_name='score_bands', verbose_name='Тест')
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='score_bands', verbose_name='Уровень')
    min_points = models.PositiveIntegerField('От'); max_points = models.PositiveIntegerField('До')
    class Meta:
        verbose_name = 'Шкала баллов'; verbose_name_plural = 'Шкалы баллов'; ordering = ['test_id','min_points']
        constraints = [models.UniqueConstraint(fields=['test','level'],name='uniq_band_level'),models.CheckConstraint(check=Q(max_points__gte=F('min_points')),name='band_valid_range')]
    def __str__(self): return f'{self.test} {self.min_points}–{self.max_points}'

class TestResult(models.Model):
    test = models.ForeignKey(EntranceTest, on_delete=models.PROTECT, related_name='results', verbose_name='Тест')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='test_results', verbose_name='Ученик', null=True, blank=True)
    guest_email = models.EmailField('Email гостя', blank=True)
    score = models.PositiveIntegerField('Баллы')
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='test_results', verbose_name='Результат уровня')
    completed_at = models.DateTimeField('Дата сдачи', auto_now_add=True)
    class Meta:
        verbose_name = 'Результат тестирования'; verbose_name_plural = 'Результаты тестирования'; ordering = ['-completed_at']
    def __str__(self): return f'{self.test} — {self.score} ({self.level.code})'

class TestAnswer(models.Model):
    result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='answers', verbose_name='Результат')
    question = models.ForeignKey(TestQuestion, on_delete=models.PROTECT, related_name='answers', verbose_name='Вопрос')
    selected_option = models.CharField('Ответ', max_length=1, choices=[(x,x) for x in 'ABCD'])
    class Meta:
        verbose_name = 'Ответ на тест'; verbose_name_plural = 'Ответы на тест'; ordering = ['result_id','question_id']
        constraints = [models.UniqueConstraint(fields=['result','question'],name='uniq_result_question')]
    def __str__(self): return f'{self.result_id} / {self.question_id}'

class StudyGroup(models.Model):
    title = models.CharField('Название группы', max_length=150)
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='groups', verbose_name='Язык')
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='groups', verbose_name='Уровень')
    teacher = models.ForeignKey(StudentProfile, on_delete=models.PROTECT, related_name='taught_groups', verbose_name='Преподаватель')
    capacity = models.PositiveSmallIntegerField('Лимит мест', default=8)
    status = models.CharField('Статус', max_length=10, choices=[('forming','Комплектуется'),('started','Запущена')], default='forming')
    start_date = models.DateField('Дата старта')
    students = models.ManyToManyField(StudentProfile, through='Enrollment', related_name='study_groups', verbose_name='Ученики')
    class Meta:
        verbose_name = 'Учебная группа'; verbose_name_plural = 'Учебные группы'; ordering = ['start_date','title']
        constraints = [models.UniqueConstraint(fields=['title','start_date'],name='uniq_group_start'),models.CheckConstraint(check=Q(capacity__gte=4),name='group_capacity_min4')]
    def __str__(self): return self.title

class GroupSchedule(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='schedule', verbose_name='Группа')
    weekday = models.PositiveSmallIntegerField('День недели (1–7)')
    start_time = models.TimeField('Начало'); end_time = models.TimeField('Окончание')
    meeting_url = models.URLField('Ссылка на занятие', blank=True)
    class Meta:
        verbose_name = 'Расписание группы'; verbose_name_plural = 'Расписания групп'; ordering = ['group_id','weekday','start_time']
        constraints = [models.UniqueConstraint(fields=['group','weekday','start_time'],name='uniq_schedule_slot'),models.CheckConstraint(check=Q(weekday__gte=1)&Q(weekday__lte=7),name='weekday_range'),models.CheckConstraint(check=Q(end_time__gt=F('start_time')),name='schedule_time_order')]
    def __str__(self): return f'{self.group} / {self.weekday}'

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Ученик')
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Группа')
    enrolled_at = models.DateTimeField('Дата зачисления', auto_now_add=True)
    class Meta:
        verbose_name = 'Зачисление'; verbose_name_plural = 'Зачисления'; ordering = ['-enrolled_at']
        constraints = [models.UniqueConstraint(fields=['student','group'],name='uniq_enrollment')]
    def __str__(self): return f'{self.student} → {self.group}'

class Homework(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='homeworks', verbose_name='Группа')
    title = models.CharField('Тема', max_length=150)
    description = models.TextField('Описание')
    deadline = models.DateTimeField('Срок сдачи')
    class Meta:
        verbose_name = 'Домашнее задание'; verbose_name_plural = 'Домашние задания'; ordering = ['deadline']
    def __str__(self): return self.title

class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions', verbose_name='Домашнее задание')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions', verbose_name='Ученик')
    text = models.TextField('Решение')
    submitted_at = models.DateTimeField('Дата сдачи', auto_now_add=True)
    grade = models.PositiveSmallIntegerField('Оценка', null=True, blank=True)
    teacher_comment = models.TextField('Комментарий', blank=True)
    class Meta:
        verbose_name = 'Сданная работа'; verbose_name_plural = 'Сданные работы'; ordering = ['-submitted_at']
        constraints = [models.UniqueConstraint(fields=['homework','student'],name='uniq_homework_submission'),models.CheckConstraint(check=Q(grade__isnull=True)|(Q(grade__gte=1)&Q(grade__lte=5)),name='submission_grade_range')]
    def __str__(self): return f'{self.homework} / {self.student}'


class CourseApplication(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.PROTECT, related_name='applications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=60)
    phone = models.CharField(max_length=24)
    email = models.EmailField(max_length=120)
    level = models.CharField(max_length=12, choices=LEVELS + [('unknown','Пока не знаю')])
    consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'LP-{self.pk:04d}' if self.pk else self.email

class Consultation(models.Model):
    name = models.CharField(max_length=60)
    phone = models.CharField(max_length=24)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
