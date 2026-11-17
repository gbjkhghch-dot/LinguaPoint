# LinguaPoint — занятия 7–9

Продолжение проекта занятия 5: сохранены модели `Language`, `Level`, `StudyGroup`, `StudentProfile`, `Enrollment` и прочие.

## Запуск

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Откройте http://127.0.0.1:8000/. Данные учебной БД находятся в `django_db.sqlite3`. Если база отсутствует, используйте `python manage.py loaddata fixtures/seed.json` после миграций. В архиве БД присутствует, но не предназначена для production.

## Структура

- `config/` — настройки и URL проекта;
- `school/models.py` — модели занятия 5 + заявки и консультации;
- `school/views.py`, `forms.py`, `urls.py` — логика, формы, маршруты;
- `school/templates/school/` — HTML-шаблоны;
- `school/static/school/` — CSS и JavaScript;
- `school/tests.py` — автоматические тесты;
- `school/migrations/` — миграции.

## Проверки

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Далее проверьте HTML каждой страницы в validator.w3.org, CSS в jigsaw.w3.org/css-validator и мобильный Lighthouse в Chrome. Эти внешние проверки требуют запуска сайта в браузере и **не отмечены как выполненные**.

## Данные и безопасность

В учебном проекте используется локальный SECRET_KEY и DEBUG=True — перед публикацией необходимо вынести ключ в переменные окружения и отключить DEBUG. Не размещайте учебную SQLite-базу с аккаунтами в публичном Git-репозитории.

## Git

Сделайте не менее 3 осмысленных коммитов в каждый из 3 учебных дней. Не выдавайте созданные за один сеанс коммиты за историю работы в разные дни.
