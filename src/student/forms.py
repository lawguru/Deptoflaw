from django.contrib.auth import authenticate
from django import forms
from .models import *
from user.models import Email
import datetime


class StudentSignUpForm(forms.Form):
    year = datetime.datetime.now().year
    registration_number = forms.CharField(min_length=11, max_length=11, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'value': year * 10000, 'min': 20000000001, 'max': 99999999999, 'placeholder': 'Registration Number'}), help_text='YYYYXXXXXXX')
    course = forms.CharField(max_length=50, widget=forms.Select(
        choices=StudentProfile.course_choices, attrs={'class': 'form-control', 'placeholder': 'Course'}))
    number = forms.CharField(min_length=10, max_length=10, widget=forms.TextInput(attrs={
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

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match')
        if StudentProfile.objects.filter(registration_number=int(cleaned_data.get('registration_number'))).exists():
            self.add_error('registration_number', 'Student with that Registration number already exists')
        if Email.objects.filter(email=cleaned_data.get('email')).exists():
            if Email.objects.get(email=cleaned_data.get('email')).user:
                self.add_error('email', 'Email already in use')
        return cleaned_data


class StudentSigninForm(forms.Form):
    registration_number_or_email = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Registration number or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    def clean(self):
        cleaned_data = super().clean()
        user = None
        if Email.objects.filter(email=cleaned_data.get('registration_number_or_email')).exists():
            email = Email.objects.get(email=cleaned_data.get('registration_number_or_email'))
            if not email.user:
                self.add_error('registration_number_or_email', 'No User with this Email')
            else:
                user = email.user
        elif cleaned_data.get('registration_number_or_email').isdigit():
            if StudentProfile.objects.filter(registration_number=int(cleaned_data.get('registration_number_or_email'))).exists():
                user = StudentProfile.objects.get(
                    registration_number=int(cleaned_data.get('registration_number_or_email'))).user
            else:
                self.add_error('registration_number_or_email', 'No Student with this Registration Number')
        else:
            self.add_error('registration_number_or_email', 'Invalid Registration Number or Email')
        
        if user is not None:
            user = authenticate(username=user.pk, password=cleaned_data.get('password'))
            if user is None:
                self.add_error('password', 'Invalid Password')

        return cleaned_data


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


class SemesterReportCardForm(forms.ModelForm):
    class Meta:
        model = SemesterReportCard
        exclude = ('student_profile', 'backlogs', 'passed',
                   'total_credits', 'earned_credits', 'sgpa')


class SemesterReportCardTemplateForm(forms.ModelForm):
    class Meta:
        model = SemesterReportCardTemplate
        exclude = ('course', 'semester')
