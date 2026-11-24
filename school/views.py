import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction, DatabaseError
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET

from .models import Language, StudyGroup, StudentProfile, CourseApplication
from .forms import ApplicationForm, ConsultationForm, RegisterForm, ProfileForm


logger = logging.getLogger(__name__)


def groups_filtered(request):
    q = (
        StudyGroup.objects
        .select_related('language', 'level', 'teacher')
        .annotate(occupied=Count('enrollments'))
    )

    language = request.GET.get('language', '')
    level = request.GET.get('level', '')
    search = request.GET.get('q', '').strip()

    if language:
        q = q.filter(language__code=language)

    if level:
        q = q.filter(level__code=level)

    if search:
        q = q.filter(
            Q(title__icontains=search) |
            Q(language__name__icontains=search) |
            Q(teacher__full_name__icontains=search)
        )

    q = q.order_by('pk')

    return q, {
        'language': language,
        'level': level,
        'q': search
    }


def home(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
            except DatabaseError:
                logger.exception('Ошибка сохранения консультации')
                form.add_error(
                    None,
                    'Не удалось сохранить заявку. Попробуйте позже.'
                )
            else:
                messages.success(
                    request,
                    'Спасибо! Мы свяжемся с вами.'
                )
                return redirect('home')
    else:
        form = ConsultationForm()

    groups = (
        StudyGroup.objects
        .select_related('language', 'level')
        .order_by('start_date', 'pk')[:6]
    )

    return render(request, 'school/home.html', {
        'groups': groups,
        'languages': Language.objects.all(),
        'form': form
    })


def catalog(request, language=None):
    q, filters = groups_filtered(request)

    if language:
        q = q.filter(language__code=language)
        filters['language'] = language

    page = Paginator(q, 20).get_page(
        request.GET.get('page')
    )

    return render(request, 'school/catalog.html', {
        'page_obj': page,
        'languages': Language.objects.all(),
        'filters': filters
    })


def course(request, pk):
    group = get_object_or_404(
        StudyGroup.objects
        .select_related('language', 'level', 'teacher')
        .annotate(occupied=Count('enrollments')),
        pk=pk
    )

    return render(request, 'school/course.html', {
        'group': group
    })


def apply(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    occupied = group.enrollments.count()

    if occupied >= group.capacity:
        logger.info(
            'Попытка записи в заполненную группу: %s',
            pk
        )

        messages.warning(
            request,
            'В группе нет свободных мест.'
        )

        return redirect('course', pk=pk)

    if request.user.is_authenticated:
        already_applied = CourseApplication.objects.filter(
            user=request.user,
            group=group
        ).exists()

        if already_applied:
            logger.warning(
                'Повторная заявка: пользователь %s, группа %s',
                request.user.pk,
                pk
            )

            messages.warning(
                request,
                'Вы уже подали заявку на этот курс.'
            )

            return redirect('course', pk=pk)

    form = ApplicationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                item = form.save(commit=False)
                item.group = group

                if request.user.is_authenticated:
                    item.user = request.user

                item.save()

        except DatabaseError:
            logger.exception(
                'Ошибка сохранения заявки на курс'
            )

            form.add_error(
                None,
                'Не удалось сохранить заявку. Попробуйте позже.'
            )

        else:
            messages.success(
                request,
                f'Заявка {item} успешно отправлена.'
            )

            return redirect(
                'application_success',
                pk=item.pk
            )

    return render(request, 'school/form.html', {
        'form': form,
        'group': group,
        'heading': 'Запись на курс'
    })


def application_success(request, pk):
    item = get_object_or_404(
        CourseApplication,
        pk=pk
    )

    # Для гостевой заявки показываем только
    # общее подтверждение без персональных данных.
    if item.user_id is None:
        return render(request, 'school/success.html', {
            'heading': 'Заявка отправлена'
        })

    # Запрещаем просмотр чужих заявок.
    if not (
        request.user.is_authenticated
        and item.user_id == request.user.pk
    ):
        logger.warning(
            'Попытка доступа к чужой заявке: %s',
            pk
        )

        raise PermissionDenied(
            'У вас нет прав для просмотра этой заявки.'
        )

    return render(request, 'school/success.html', {
        'heading': 'Заявка отправлена',
        'application': item
    })


def teachers(request):
    profiles = StudentProfile.objects.filter(
        role='teacher'
    )

    return render(request, 'school/teachers.html', {
        'teachers': profiles
    })


def search(request):
    q, filters = groups_filtered(request)

    page = Paginator(q, 20).get_page(
        request.GET.get('page')
    )

    return render(request, 'school/catalog.html', {
        'page_obj': page,
        'languages': Language.objects.all(),
        'filters': filters,
        'search_page': True
    })


def register(request):
    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()

        except DatabaseError:
            logger.exception(
                'Ошибка создания аккаунта'
            )

            form.add_error(
                None,
                'Не удалось создать аккаунт. Попробуйте позже.'
            )

        else:
            login(
                request,
                user,
                backend='django.contrib.auth.backends.ModelBackend'
            )

            messages.success(
                request,
                'Аккаунт создан.'
            )

            return redirect('account')

    return render(request, 'school/form.html', {
        'form': form,
        'heading': 'Регистрация'
    })


def login_view(request):
    form = AuthenticationForm(
        request,
        data=request.POST or None
    )

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('account')

    return render(request, 'school/form.html', {
        'form': form,
        'heading': 'Вход'
    })


@login_required
def account(request):
    profile, _ = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': (
                request.user.get_full_name()
                or request.user.username
            )
        }
    )

    form = ProfileForm(
        request.POST or None,
        instance=profile
    )

    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()

        except DatabaseError:
            logger.exception(
                'Ошибка сохранения профиля'
            )

            form.add_error(
                None,
                'Не удалось сохранить профиль. Попробуйте позже.'
            )

        else:
            messages.success(
                request,
                'Профиль сохранён.'
            )

            return redirect('account')

    applications = (
        CourseApplication.objects
        .filter(user=request.user)
        .select_related('group')
    )

    return render(request, 'school/account.html', {
        'form': form,
        'applications': applications
    })


@require_GET
def courses_api(request):
    q, _ = groups_filtered(request)

    rows = list(
        q[:20].values(
            'id',
            'title',
            'level__code',
            'language__name',
            'start_date'
        )
    )

    for row in rows:
        row['start_date'] = (
            row['start_date'].isoformat()
        )

    return JsonResponse({
        'results': rows,
        'count': q.count()
    })