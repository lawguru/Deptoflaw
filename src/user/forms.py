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


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ['user', 'country_code', 'phone_number']
        widgets = {
            'country_code': forms.TextInput(attrs={'class': 'form-control h-100 rounded-start rounded-end-0 border border-0 z-1', 'placeholder': 'Country Code'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control h-100', 'placeholder': 'Phone Number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['user', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['user', 'address', 'city', 'state',
                  'country', 'pincode']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'House number, Building, Locality, Street, Landmark', 'style': 'height: 8rem;'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN/ZIP Code'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label