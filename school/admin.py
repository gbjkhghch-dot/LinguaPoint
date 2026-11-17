
from django.contrib import admin
from django.apps import apps

admin.site.site_header = "Языковая школа"
admin.site.site_title = "Администрирование"
admin.site.index_title = "Управление базой данных"

for model in apps.get_app_config('school').get_models():
    admin.site.register(model)
