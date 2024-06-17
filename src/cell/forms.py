from django import forms
from resume.models import Skill
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
            'skills',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            if isinstance(visible.field.widget, forms.Textarea):
                visible.field.widget.attrs['style'] = 'height: 8rem'
        for field in self.Meta.readonly_widgets:
            self.fields[field].widget = self.Meta.readonly_widgets[field]
            self.fields[field].disabled = True


class AddRecruitmentPostForm(RecruitmentPostForm):
    class Meta(RecruitmentPostForm.Meta):
        exclude = [
            'skills',
            'posted_on',
            'edited_on',
            'pending_application_instructions',
            'rejected_application_instructions',
            'selected_application_instructions',
            'shortlisted_application_instructions',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'apply_by': forms.DateInput(attrs={'type': 'date'}),
        }
        readonly_widgets = {
            'user': forms.HiddenInput(),
        }


class RecruiterChangeRecruitmentPostForm(RecruitmentPostForm):
    class Meta(RecruitmentPostForm.Meta):
        readonly_widgets = {
            'user': forms.HiddenInput(),
            'title': forms.TextInput(),
            'company': forms.TextInput(),
            'job_type': forms.Select(choices=RecruitmentPostForm.Meta.model.job_type_choices),
            'workplace_type': forms.Select(choices=RecruitmentPostForm.Meta.model.workplace_type_choices),
            'location': forms.TextInput(),
            'sallary_type': forms.Select(choices=RecruitmentPostForm.Meta.model.salary_type_choices),
            'minimum_salary': forms.TextInput(),
            'sallary': forms.TextInput(),
            'fee': forms.TextInput(),
            'experience_duration': forms.NumberInput(),
            'start_date_type': forms.Select(choices=RecruitmentPostForm.Meta.model.start_date_type_choices),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TPCChangeRecruitmentPostForm(RecruitmentPostForm):
    class Meta(RecruitmentPostForm.Meta):
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'apply_by': forms.DateInput(attrs={'type': 'date'}),
        }
        readonly_widgets = {
            'user': forms.HiddenInput(),
        }


class SkillForm(forms.Form):
    name = forms.CharField(max_length=150, label='Skill', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skill', 'id': 'id-skill-name', 'list': 'skill-data-list', 'autocomplete': 'off'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


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
