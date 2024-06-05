from django import forms
from .models import *


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'sender_designation', 'sender_company',
                  'sender_phone', 'sender_email', 'message']
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            if isinstance(visible.field.widget, forms.Textarea):
                visible.field.widget.attrs['style'] = 'height: 8rem'


class RecruitmentPostForm(forms.ModelForm):
    class Meta:
        model = RecruitmentPost
        fields = '__all__'
        exclude = ['user', 'is_active', 'pending_application_instructions', 'rejected_application_instructions',
                   'selected_application_instructions', 'interview_application_instructions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            if isinstance(visible.field.widget, forms.Textarea):
                visible.field.widget.attrs['style'] = 'height: 8rem'


class AddRecruitmentPostForm(RecruitmentPostForm):
    class Meta(RecruitmentPostForm.Meta):
        exclude = ['user', 'is_active']


class ChangeRecruitmentPostForm(RecruitmentPostForm):
    class Meta(RecruitmentPostForm.Meta):
        fields = ['sallary_currency', 'sallary', 'fee_currency', 'fee', 'description', 'pending_application_instructions',
                  'rejected_application_instructions', 'selected_application_instructions', 'shortlisted_application_instructions']
        exclude = []


class RecruitmentPostUpdateForm(forms.ModelForm):
    class Meta:
        model = RecruitmentPostUpdate
        fields = '__all__'
        exclude = ['user', 'recruitment_post']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            if isinstance(visible.field.widget, forms.Textarea):
                visible.field.widget.attrs['style'] = 'height: 8rem'


class RecruitmentApplicationForm(forms.ModelForm):
    class Meta:
        model = RecruitmentApplication
        fields = '__all__'
        exclude = ['user', 'recruitment_post', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            if isinstance(visible.field.widget, forms.Textarea):
                visible.field.widget.attrs['style'] = 'height: 8rem'
