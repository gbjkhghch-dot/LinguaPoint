# Занятие 5 — Языковая школа, вариант 12

Содержимое: `school/models.py`, `services.py`, миграции, SQLite демонстрационная база `evidence/school_demo.sqlite3`, фикстура `fixtures/seed.json`, `queries.py`, ER-диаграммы (PNG, DBML, DOT) и пояснительная записка DOCX.

## Подтверждено пользователем на Windows (13.11.2026)

- `python manage.py makemigrations`: создана миграция `school/migrations/0002_alter_studygroup_students.py`.
- `python manage.py migrate`: миграции 0001 и 0002 успешно применены.
- `showmigrations school`: обе отмечены `[X]`.
- База, открытая в DB Browser, называется `django_db.sqlite3`; на скриншотах видны 23 таблицы, 44 записи `school_testresult`.
- ORM и SQL пяти запросов выполнены в PowerShell; подтверждения в папке `Скриншоты_проверок_из_чата` на уровень выше.

## Примечание о восстановленном комплекте

Этот архив сформирован из исходников, ранее подготовленных в чате, и пользовательских снимков экрана, но не из актуальной папки на компьютере пользователя. Исправление `LEVELS` в `0001_initial.py` включено. Файл `0002_alter_studygroup_students.py` **воссоздан по названию и текущей модели**, а не скопирован из пользовательского компьютера. Для сдачи лучше заменить его реальным файлом `school/migrations/0002_alter_studygroup_students.py` из своего проекта.

**Реальная локальная база** `django_db.sqlite3` с компьютера пользователя в чате не прикреплялась. Файл `evidence/school_demo.sqlite3` — демонстрационная база, не локальная база пользователя. Чтобы сдать точное состояние после `migrate` и `loaddata`, добавьте свой локальный `django_db.sqlite3` в архив вручную.

## Запуск

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/seed.json
python manage.py shell -c "exec(open('queries.py', encoding='utf-8').read())"
```

Если база уже заполнена, не загружайте фикстуру повторно без резервной копии.
