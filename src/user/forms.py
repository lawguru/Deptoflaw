from django import forms
from .models import User, PhoneNumber, Email, Address, Link


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'required': True}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about Yourself', 'style': 'height: 16rem;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class ResetPasswordSpecifyForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['email'].widget.attrs['required'] = True

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if not Email.objects.filter(email=email).exists():
            self.add_error('email', 'Email does not exist.')
        else:
            email = Email.objects.get(email=email)
            if not email.user:
                self.add_error('email', 'No user associated with this email.')
        return cleaned_data
            


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['password'].widget.attrs['required'] = True
        self.fields['confirm_password'].widget.attrs['required'] = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ['user', 'country_code', 'phone_number']
        widgets = {
            'user': forms.HiddenInput(),
            'country_code': forms.TextInput(attrs={'class': 'form-control h-100 rounded-start rounded-end-0 border border-0 z-1', 'placeholder': 'Country Code'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control h-100', 'placeholder': 'Phone Number'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        if user:
            self.fields['user'].initial = user
        self.fields['user'].widget.attrs['readonly'] = True


class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['user', 'email']
        widgets = {
            'user': forms.HiddenInput(),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        if user:
            self.fields['user'].initial = user
        self.fields['user'].widget.attrs['readonly'] = True


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['user', 'address', 'city', 'state',
                  'country', 'pincode']
        widgets = {
            'user': forms.HiddenInput(),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'House number, Building, Locality, Street, Landmark', 'style': 'height: 8rem;'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN/ZIP Code'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        if user:
            self.fields['user'].initial = user
        self.fields['user'].widget.attrs['readonly'] = True


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['user', 'url', 'title']
        widgets = {
            'user': forms.HiddenInput(),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        if user:
            self.fields['user'].initial = user
        self.fields['user'].widget.attrs['readonly'] = True
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
