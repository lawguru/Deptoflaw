from django.contrib.auth import authenticate
from django import forms
from user.models import Email
from .models import StaffProfile


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = '__all__'
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label


class StaffSignUpForm(forms.Form):
    id_number = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'ID Number'}))
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
    qualification = forms.CharField(max_length=50, widget=forms.Select(
        choices=StaffProfile.qualification_choices, attrs={'class': 'form-control', 'placeholder': 'Qualification'}))
    designation = forms.CharField(max_length=50, widget=forms.Select(
        choices=StaffProfile.designation_choices, attrs={'class': 'form-control', 'placeholder': 'Designation'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match')
        if StaffProfile.objects.filter(id_number=cleaned_data.get('id_number')).exists():
            self.add_error('id_number', 'Staff with that ID number already exists')
        if Email.objects.filter(email=cleaned_data.get('email')).exists():
            if Email.objects.get(email=cleaned_data.get('email')).user:
                self.add_error('email', 'Email already in use')
        return cleaned_data


class StaffSigninForm(forms.Form):
    email_or_id = forms.CharField(label='Email or ID number', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email or ID number'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    def clean(self):
        cleaned_data = super().clean()
        user = None
        if Email.objects.filter(email=cleaned_data.get('email_or_id')).exists():
            email = Email.objects.get(email=cleaned_data.get('email_or_id'))
            if not email.user:
                self.add_error('email_or_id', 'No User with this Email')
            else:
                user = email.user
        elif StaffProfile.objects.filter(id_number=cleaned_data.get('email_or_id')).exists():
            user = StaffProfile.objects.get(id_number=cleaned_data.get('email_or_id')).user
        else:
            self.add_error('email_or_id', 'Invalid ID Number or Email')
        
        if user is not None:
            user = authenticate(username=user.pk, password=cleaned_data.get('password'))
            if user is None:
                self.add_error('password', 'Invalid Password')

        return cleaned_data
