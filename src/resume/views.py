from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from views import AddUserKeyObject, ChangeUserKeyObject, DeleteUserKeyObject
from django.views.generic.base import TemplateView
from user.models import User
from .forms import *

# Create your views here.


# Education

@method_decorator(login_required, name="dispatch")
class UpdateEducationInfo(TemplateView):
    template_name = 'update_education_info.html'

    def get(self, request, user):
        if not user.isdigit():
            return redirect('update_education_info', self.request.user.id)
        else:
            user=int(user)
            if not User.objects.filter(pk=user).exists():
                raise ObjectDoesNotExist()
            elif User.objects.get(pk=user) != self.request.user and not request.user.is_superuser:
                raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])
    
        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['othereducations'] = OtherEducation.objects.filter(user=user)
        context['certifications'] = Certification.objects.filter(user=user)
        context['skills'] = Skill.objects.filter(user=user)
        context['languages'] = Language.objects.filter(user=user)
        context['skill_form'] = SkillForm({'user': user.pk})
        context['language_form'] = LanguageForm({'user': user.pk})
        return context

# Other Education

@method_decorator(login_required, name="dispatch")
class AddOtherEducation(AddUserKeyObject):
    model = OtherEducation
    form = OtherEducationForm
    template_name = 'other_education.html'
    redirect_url_name = 'other_educations'

@method_decorator(login_required, name="dispatch")
class ChangeOtherEducation(ChangeUserKeyObject):
    model = OtherEducation
    form = OtherEducationForm
    template_name = 'other_education.html'
    redirect_url_name = 'other_educations'

@method_decorator(login_required, name="dispatch")
class DeleteOtherEducation(DeleteUserKeyObject):
    model = OtherEducation
    redirect_url_name = 'other_educations'

# Certification

@method_decorator(login_required, name="dispatch")
class AddCertification(AddUserKeyObject):
    model = Certification
    form = CertificationForm
    template_name = 'certification.html'
    redirect_url_name = 'certifications'

@method_decorator(login_required, name="dispatch")
class ChangeCertification(ChangeUserKeyObject):
    model = Certification
    form = CertificationForm
    template_name = 'certification.html'
    redirect_url_name = 'certifications'

@method_decorator(login_required, name="dispatch")
class DeleteCertification(DeleteUserKeyObject):
    model = Certification
    redirect_url_name = 'certifications'

# Skill

@method_decorator(login_required, name="dispatch")
class AddSkill(AddUserKeyObject):
    model = Skill
    form = SkillForm
    redirect_url_name = 'skills'

    def form_unvalid(self, request, form, *args, **kwargs):
        if self.model.objects.filter(name__iexact=form.cleaned_data['name'], **kwargs).exists():
            self.model.objects.filter(name__iexact=form.cleaned_data['name'], **kwargs).update(
                name=form.cleaned_data['name'], proficiency=form.cleaned_data['proficiency'])

@method_decorator(login_required, name="dispatch")
class DeleteSkill(DeleteUserKeyObject):
    model = Skill
    redirect_url_name = 'skills'

# Language

@method_decorator(login_required, name="dispatch")
class AddLanguage(AddUserKeyObject):
    model = Language
    form = LanguageForm
    redirect_url_name = 'languages'

    def form_unvalid(self, request, form, *args, **kwargs):
        if self.model.objects.filter(name__iexact=form.cleaned_data['name'], **kwargs).exists():
            self.model.objects.filter(name__iexact=form.cleaned_data['name'], **kwargs).update(
                name=form.cleaned_data['name'], proficiency=form.cleaned_data['proficiency'])

@method_decorator(login_required, name="dispatch")
class DeleteLanguage(DeleteUserKeyObject):
    model = Language
    redirect_url_name = 'languages'


# Experience

@method_decorator(login_required, name="dispatch")
class UpdateExperienceInfo(TemplateView):
    template_name = 'update_experience_info.html'

    def get(self, request, user):
        if not user.isdigit():
            return redirect('update_experience_info', self.request.user.id)
        else:
            user=int(user)
            if not User.objects.filter(pk=user).exists():
                raise ObjectDoesNotExist()
            elif User.objects.get(pk=user) != self.request.user and not request.user.is_superuser:
                raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])
    
        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['work_experiences'] = WorkExperience.objects.filter(user=user)
        context['projects'] = Project.objects.filter(user=user)
        return context

# Work Experience

@method_decorator(login_required, name="dispatch")
class AddWorkExperience(AddUserKeyObject):
    model = WorkExperience
    form = WorkExperienceForm
    template_name = 'work_experience.html'
    redirect_url_name = 'work_experiences'

@method_decorator(login_required, name="dispatch")
class ChangeWorkExperience(ChangeUserKeyObject):
    model = WorkExperience
    form = WorkExperienceForm
    template_name = 'work_experience.html'
    redirect_url_name = 'work_experiences'

@method_decorator(login_required, name="dispatch")
class DeleteWorkExperience(DeleteUserKeyObject):
    model = WorkExperience
    redirect_url_name = 'work_experiences'

# Project

@method_decorator(login_required, name="dispatch")
class AddProject(AddUserKeyObject):
    model = Project
    form = ProjectForm
    template_name = 'project.html'
    redirect_url_name = 'projects'

@method_decorator(login_required, name="dispatch")
class ChangeProject(ChangeUserKeyObject):
    model = Project
    form = ProjectForm
    template_name = 'project.html'
    redirect_url_name = 'projects'

@method_decorator(login_required, name="dispatch")
class DeleteProject(DeleteUserKeyObject):
    model = Project
    redirect_url_name = 'projects'


# IP

@method_decorator(login_required, name="dispatch")
class UpdateIPInfo(TemplateView):
    template_name = 'update_ip_info.html'

    def get(self, request, user):
        if not user.isdigit():
            return redirect('update_ip_info', self.request.user.id)
        else:
            user=int(user)
            if not User.objects.filter(pk=user).exists():
                raise ObjectDoesNotExist()
            elif User.objects.get(pk=user) != self.request.user and not request.user.is_superuser:
                raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])
    
        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['patents'] = Patent.objects.filter(user=user)
        context['publications'] = Publication.objects.filter(user=user)
        return context

# Patent

@method_decorator(login_required, name="dispatch")
class AddPatent(AddUserKeyObject):
    model = Patent
    form = PatentForm
    template_name = 'patent.html'
    redirect_url_name = 'patents'

@method_decorator(login_required, name="dispatch")
class ChangePatent(ChangeUserKeyObject):
    model = Patent
    form = PatentForm
    template_name = 'patent.html'
    redirect_url_name = 'patents'

@method_decorator(login_required, name="dispatch")
class DeletePatent(DeleteUserKeyObject):
    model = Patent
    redirect_url_name = 'patents'

# Publication

@method_decorator(login_required, name="dispatch")
class AddPublication(AddUserKeyObject):
    model = Publication
    form = PublicationForm
    template_name = 'publication.html'
    redirect_url_name = 'publications'

@method_decorator(login_required, name="dispatch")
class ChangePublication(ChangeUserKeyObject):
    model = Publication
    form = PublicationForm
    template_name = 'publication.html'
    redirect_url_name = 'publications'

@method_decorator(login_required, name="dispatch")
class DeletePublication(DeleteUserKeyObject):
    model = Publication
    redirect_url_name = 'publications'


# Other

@method_decorator(login_required, name="dispatch")
class UpdateOtherInfo(TemplateView):
    template_name = 'update_other_info.html'

    def get(self, request, user):
        if not user.isdigit():
            return redirect('update_other_info', self.request.user.id)
        else:
            user=int(user)
            if not User.objects.filter(pk=user).exists():
                raise ObjectDoesNotExist()
            elif User.objects.get(pk=user) != self.request.user and not request.user.is_superuser:
                raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])
    
        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['achievements'] = Achievement.objects.filter(user=user)
        context['presentations'] = Presentation.objects.filter(user=user)
        context['other_infos'] = OtherInfo.objects.filter(user=user)
        return context

# Achievement

@method_decorator(login_required, name="dispatch")
class AddAchievement(AddUserKeyObject):
    model = Achievement
    form = AchievementForm
    template_name = 'achievement.html'
    redirect_url_name = 'achievements'

@method_decorator(login_required, name="dispatch")
class ChangeAchievement(ChangeUserKeyObject):
    model = Achievement
    form = AchievementForm
    template_name = 'achievement.html'
    redirect_url_name = 'achievements'

@method_decorator(login_required, name="dispatch")
class DeleteAchievement(DeleteUserKeyObject):
    model = Achievement
    redirect_url_name = 'achievements'

# Presentation

@method_decorator(login_required, name="dispatch")
class AddPresentation(AddUserKeyObject):
    model = Presentation
    form = PresentationForm
    template_name = 'presentation.html'
    redirect_url_name = 'presentations'

@method_decorator(login_required, name="dispatch")
class ChangePresentation(ChangeUserKeyObject):
    model = Presentation
    form = PresentationForm
    template_name = 'presentation.html'
    redirect_url_name = 'presentations'

@method_decorator(login_required, name="dispatch")
class DeletePresentation(DeleteUserKeyObject):
    model = Presentation
    redirect_url_name = 'presentations'

# Other Info

@method_decorator(login_required, name="dispatch")
class AddOtherInfo(AddUserKeyObject):
    model = OtherInfo
    form = OtherInfoForm
    template_name = 'other_info.html'
    redirect_url_name = 'other_infos'

@method_decorator(login_required, name="dispatch")
class ChangeOtherInfo(ChangeUserKeyObject):
    model = OtherInfo
    form = OtherInfoForm
    template_name = 'other_info.html'
    redirect_url_name = 'other_infos'

@method_decorator(login_required, name="dispatch")
class DeleteOtherInfo(DeleteUserKeyObject):
    model = OtherInfo
    redirect_url_name = 'other_infos'
