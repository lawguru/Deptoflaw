from django.contrib.auth import authenticate
from django import forms
from .models import RecruiterProfile
from user.models import Email


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = '__all__'
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label


class RecruiterSignUpForm(forms.Form):
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
    company_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Company Name'}))
    designation = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Designation'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match')
        if Email.objects.filter(email=cleaned_data.get('email')).exists():
            if Email.objects.get(email=cleaned_data.get('email')).user:
                self.add_error('email', 'Email already in use')
        return cleaned_data


class RecruiterSigninForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    def clean(self):
        cleaned_data = super().clean()
        user = None
        if Email.objects.filter(email=cleaned_data.get('email')).exists():
            email = Email.objects.get(email=cleaned_data.get('email'))
            if email.user:
                user = email.user
        else:
            self.add_error('email', 'No User with this Email')
        
        if user is not None:
            user = authenticate(username=user.pk, password=cleaned_data.get('password'))
            if user is None:
                self.add_error('password', 'Invalid Password')
        
        return cleaned_data