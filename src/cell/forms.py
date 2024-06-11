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
        exclude = [
            'user',
            'skills',
            'is_active',
        ]

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
        fields = [
            'title',
            'company',
            'job_type',
            'workplace_type',
            'location',
            'sallary_type',
            'sallary_currency',
            'sallary',
            'fee_currency',
            'fee',
            'experience_duration',
            'start_date_type',
            'start_date',
            'apply_by',
            'description',
            'requirements',
            'required_documents',
            'questionaires',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'apply_by': forms.DateInput(attrs={'type': 'date'}),
        }


class RecruiterChangeRecruitmentPostForm(RecruitmentPostForm):
    class Meta(RecruitmentPostForm.Meta):
        readonly_widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}, choices=RecruitmentPostForm.Meta.model.job_type_choices),
            'workplace_type': forms.Select(attrs={'class': 'form-control'}, choices=RecruitmentPostForm.Meta.model.workplace_type_choices),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'sallary_type': forms.Select(attrs={'class': 'form-control'}, choices=RecruitmentPostForm.Meta.model.sallary_type_choices),
            'sallary_currency': forms.Select(attrs={'class': 'form-control'}, choices=RecruitmentPostForm.Meta.model.currency_choices),
            'sallary': forms.TextInput(attrs={'class': 'form-control'}),
            'fee_currency': forms.Select(attrs={'class': 'form-control'}, choices=RecruitmentPostForm.Meta.model.currency_choices),
            'fee': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date_type': forms.Select(attrs={'class': 'form-control'}, choices=RecruitmentPostForm.Meta.model.start_date_type_choices),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.readonly_widgets:
            self.fields[field].widget = self.Meta.readonly_widgets[field]
            self.fields[field].disabled = True


class TPCChangeRecruitmentPostForm(RecruitmentPostForm):
    class Meta(RecruitmentPostForm.Meta):
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'apply_by': forms.DateInput(attrs={'type': 'date'}),
        }


class RecruitmentPostUpdateForm(forms.ModelForm):
    class Meta:
        model = RecruitmentPostUpdate
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
        exclude = ['user', 'recruitment_post', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            if isinstance(visible.field.widget, forms.Textarea):
                visible.field.widget.attrs['style'] = 'height: 8rem'
