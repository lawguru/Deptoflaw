from django import forms
from .models import *
import datetime


class StudentSignUpForm(forms.Form):
    year = datetime.datetime.now().year
    registration_number = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'value': year * 10000, 'min': 2000000001, 'max': 99999999999, 'placeholder': 'Registration Number'}), help_text='YYYYXXXXXXX')
    course = forms.CharField(max_length=50, widget=forms.Select(
        choices=StudentProfile.course_choices, attrs={'class': 'form-control', 'placeholder': 'Course'}))
    number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
                             'class': 'form-control', 'type': 'number', 'placeholder': 'Roll Number'}), label='Roll Number', help_text='10 digit number in Roll number')
    id_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'value': 000,
                                'min': 1, 'max': 999, 'placeholder': 'Library ID Number'}), label='Library ID Number', help_text='Last 3 digits of ID YYCSEBTCXXX')
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class StudentSigninForm(forms.Form):
    registration_number = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Registration number'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        exclude = ('user', 'id_card', 'registration_year',
                   'backlog_count', 'pass_out_year', 'passed_semesters', 'cgpa')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            if visible.field.label == 'ID Number':
                visible.field.initial = f'{visible.field.initial:03d}'


class SemesterReportCardForm(forms.ModelForm):
    class Meta:
        model = SemesterReportCard
        exclude = ('student_profile', 'backlogs', 'passed',
                   'total_credits', 'earned_credits', 'sgpa')

class SemesterReportCardTemplateForm(forms.ModelForm):
    class Meta:
        model = SemesterReportCardTemplate
        exclude = ('course', 'semester')