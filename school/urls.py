from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
urlpatterns=[
path('',views.home,name='home'),path('courses/',views.catalog,name='catalog'),path('courses/language/<str:language>/',views.catalog,name='language_catalog'),path('courses/<int:pk>/',views.course,name='course'),path('courses/<int:pk>/apply/',views.apply,name='apply'),path('application/<int:pk>/success/',views.application_success,name='application_success'),path('teachers/',views.teachers,name='teachers'),path('search/',views.search,name='search'),path('register/',views.register,name='register'),path('login/',views.login_view,name='login'),path('logout/',LogoutView.as_view(),name='logout'),path('account/',views.account,name='account'),path('api/courses/',views.courses_api,name='courses_api')]
