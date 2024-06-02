from django import forms
from .models import Message, Notice

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'sender_designation', 'sender_company', 'sender_phone', 'sender_email', 'message']
        widgets = {
            'sender': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'sender_designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Designation'}),
            'sender_company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company'}),
            'sender_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'sender_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message', 'style': 'height: 8rem;'}),
        }
        labels = {
            'sender': 'Your Name',
            'sender_designation': 'Designation',
            'sender_company': 'Company',
            'sender_phone': 'Phone',
            'sender_email': 'Email',
            'message': 'Your Message',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['sender_designation'].required = False
        self.fields['sender_company'].required = False
        self.fields['sender_phone'].required = False

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'style': 'height: 8rem;'}),
        }
        labels = {
            'title': 'Title',
            'description': 'Description',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''