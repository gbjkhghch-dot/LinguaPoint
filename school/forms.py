import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CourseApplication, Consultation, StudentProfile

def validate_phone(value):
    if not 10 <= len(re.sub(r'\D','',value)) <= 15: raise forms.ValidationError('Укажите телефон: от 10 до 15 цифр.')

class ApplicationForm(forms.ModelForm):
    class Meta:
        model=CourseApplication
        fields=['name','phone','email','level','consent']
        labels={'name':'Ваше имя','phone':'Телефон','email':'Электронная почта','level':'Уровень','consent':'Согласен на обработку персональных данных'}
        widgets={'name':forms.TextInput(attrs={'minlength':2,'maxlength':60}), 'phone':forms.TextInput(attrs={'type':'tel','placeholder':'+7 999 123-45-67'}), 'email':forms.EmailInput()}
    def clean_name(self):
        v=self.cleaned_data['name'].strip()
        if len(v)<2 or not re.fullmatch(r'[А-Яа-яЁёA-Za-z\s-]+',v):raise forms.ValidationError('Имя: 2–60 символов, только буквы и дефис.')
        return v
    def clean_phone(self):
        v=self.cleaned_data['phone'];validate_phone(v);return v
    def clean_consent(self):
        v=self.cleaned_data['consent']
        if not v:raise forms.ValidationError('Необходимо согласие на обработку данных.')
        return v

class ConsultationForm(forms.ModelForm):
    class Meta:
        model=Consultation
        fields=['name','phone','email']
        labels={'name':'Имя','phone':'Телефон','email':'Электронная почта'}
    def clean_phone(self):
        v=self.cleaned_data['phone'];validate_phone(v);return v

class RegisterForm(UserCreationForm):
    email=forms.EmailField(required=True)
    first_name=forms.CharField(label='Имя',min_length=2,max_length=60)
    class Meta:
        model=User
        fields=['username','first_name','email','password1','password2']
    def save(self,commit=True):
        u=super().save(commit=False);u.email=self.cleaned_data['email'];u.first_name=self.cleaned_data['first_name']
        if commit:
            u.save();StudentProfile.objects.get_or_create(user=u,defaults={'full_name':u.first_name})
        return u

class ProfileForm(forms.ModelForm):
    class Meta:
        model=StudentProfile
        fields=['full_name']
        labels={'full_name':'ФИО'}
