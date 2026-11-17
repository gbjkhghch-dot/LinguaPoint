from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('school','0002_alter_studygroup_students'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Consultation',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=60)),('phone',models.CharField(max_length=24)),('email',models.EmailField(max_length=254)),('created_at',models.DateTimeField(auto_now_add=True))]),
        migrations.CreateModel(name='CourseApplication',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=60)),('phone',models.CharField(max_length=24)),('email',models.EmailField(max_length=120)),('level',models.CharField(choices=[('A1','A1'),('A2','A2'),('B1','B1'),('B2','B2'),('C1','C1'),('unknown','Пока не знаю')],max_length=12)),('consent',models.BooleanField(default=False)),('created_at',models.DateTimeField(auto_now_add=True)),('group',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='applications',to='school.studygroup')),('user',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL))])]
