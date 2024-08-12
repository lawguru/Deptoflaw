from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from views import AddUserKeyObject, ChangeUserKeyObject, DeleteUserKeyObject
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.http import JsonResponse
from django.views import View
from django.views.generic.base import TemplateView
from user.models import User
from .forms import *
from .models import *


# Create your views here.

@method_decorator(login_required, name="dispatch")
class EducationInfo(TemplateView):
    template_name = 'education_info.html'

    def get(self, request, user):
        if not User.objects.filter(pk=user).exists():
            raise ObjectDoesNotExist()
        elif User.objects.get(pk=user) != request.user and not request.user.is_superuser:
            raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])

        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['othereducations'] = [(other_education, OtherEducationForm(
            instance=other_education)) for other_education in OtherEducation.objects.filter(user=user).values()]
        context['certifications'] = [(certification, CertificationForm(
            instance=certification)) for certification in Certification.objects.filter(user=user).values()]
        context['skills'] = Skill.objects.filter(users__pk=user.pk).values()
        context['languages'] = Language.objects.filter(users__pk=user.pk).values()

        if Skill.objects.get_add_permission(user, self.request.user):
            context['skill_form'] = SkillForm()
        
        if Language.objects.get_add_permission(user, self.request.user):
            context['language_form'] = LanguageForm()
        
        if OtherEducation.objects.get_create_permission(user, self.request.user):
            context['other_education_form'] = OtherEducationForm(
                initial={'user': user.pk})
        
        if Certification.objects.get_create_permission(user, self.request.user):
            context['certification_form'] = CertificationForm(
                initial={'user': user.pk})

        if Skill.objects.get_remove_permission(user, self.request.user):
            context['remove_skill_permission'] = True

        if Language.objects.get_remove_permission(user, self.request.user):
            context['remove_language_permission'] = True

        return context


@method_decorator(login_required, name="dispatch")
class ExperienceInfo(TemplateView):
    template_name = 'experience_info.html'

    def get(self, request, user):
        if not User.objects.filter(pk=user).exists():
            raise ObjectDoesNotExist()
        elif User.objects.get(pk=user) != request.user and not request.user.is_superuser:
            raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])

        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['work_experiences'] = [(work_experiences, WorkExperienceForm(
            instance=work_experiences)) for work_experiences in WorkExperience.objects.filter(user=user).values()]
        context['projects'] = [(project, ProjectForm(instance=project))
                               for project in Project.objects.filter(user=user).values()]
        
        if WorkExperience.objects.get_create_permission(user, self.request.user):
            context['work_experience_form'] = WorkExperienceForm(
                initial={'user': user.pk})
        
        if Project.objects.get_create_permission(user, self.request.user):
            context['project_form'] = ProjectForm(initial={'user': user.pk})

        return context


@method_decorator(login_required, name="dispatch")
class IPInfo(TemplateView):
    template_name = 'ip_info.html'

    def get(self, request, user):
        if not User.objects.filter(pk=user).exists():
            raise ObjectDoesNotExist()
        elif User.objects.get(pk=user) != request.user and not request.user.is_superuser:
            raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])

        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['patents'] = [(patent, PatentForm(instance=patent))
                              for patent in Patent.objects.filter(user=user).values()]
        context['publications'] = [(publication, PublicationForm(
            instance=publication)) for publication in Publication.objects.filter(user=user).values()]
        
        if Patent.objects.get_create_permission(user, self.request.user):
            context['patent_form'] = PatentForm(initial={'user': user.pk})
        
        if Publication.objects.get_create_permission(user, self.request.user):
            context['publication_form'] = PublicationForm(
                initial={'user': user.pk})

        return context


@method_decorator(login_required, name="dispatch")
class OtherInfos(TemplateView):
    template_name = 'other_info.html'

    def get(self, request, user):
        if not User.objects.filter(pk=user).exists():
            raise ObjectDoesNotExist()
        elif User.objects.get(pk=user) != request.user and not request.user.is_superuser:
            raise PermissionDenied()
        return super().get(request, user)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['user'])

        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['achievements'] = [(achievement, AchievementForm(
            instance=achievement)) for achievement in Achievement.objects.filter(user=user).values()]
        context['presentations'] = [(presentation, PresentationForm(
            instance=presentation)) for presentation in Presentation.objects.filter(user=user).values()]
        context['other_infos'] = [(other_info, OtherInfoForm(
            instance=other_info)) for other_info in OtherInfo.objects.filter(user=user).values()]
        
        if Achievement.objects.get_create_permission(user, self.request.user):
            context['achievement_form'] = AchievementForm(
                initial={'user': user.pk})
        
        if Presentation.objects.get_create_permission(user, self.request.user):
            context['presentation_form'] = PresentationForm(
                initial={'user': user.pk})
            
        if OtherInfo.objects.get_create_permission(user, self.request.user):
            context['other_info_form'] = OtherInfoForm(
                initial={'user': user.pk})
        
        return context


# Other Education

@method_decorator(login_required, name="dispatch")
class AddOtherEducation(AddUserKeyObject):
    model = OtherEducation
    form = OtherEducationForm
    redirect_url_name = 'other_educations'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeOtherEducation(ChangeUserKeyObject):
    model = OtherEducation
    form = OtherEducationForm
    redirect_url_name = 'other_educations'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteOtherEducation(DeleteUserKeyObject):
    model = OtherEducation
    redirect_url_name = 'other_educations'


# Certification

@method_decorator(login_required, name="dispatch")
class AddCertification(AddUserKeyObject):
    model = Certification
    form = CertificationForm
    redirect_url_name = 'certifications'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeCertification(ChangeUserKeyObject):
    model = Certification
    form = CertificationForm
    redirect_url_name = 'certifications'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteCertification(DeleteUserKeyObject):
    model = Certification
    redirect_url_name = 'certifications'


# Skill

@method_decorator(login_required, name="dispatch")
class AddSkill(View):
    model = Skill
    form = SkillForm
    redirect_url_name = 'skills'

    def post(self, request, user, *args, **kwargs):
        if not User.objects.filter(pk=user).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=user)
        if not self.model.objects.get_add_permission(user, self.request.user):
            raise PermissionDenied()
        form = self.form(request.POST)
        if form.is_valid():
            skills = form.cleaned_data['name'].split(',')
            for skill in skills:
                skill = skill.strip()
                if not skill:
                    continue
                if self.model.objects.filter(name__iexact=skill).exists():
                    obj = self.model.objects.get(name__iexact=skill)
                    obj.users.add(user)
                    obj.save()
                else:
                    obj = self.model.objects.create(name=skill)
                    obj.users.add(user)
                    obj.save()
        else:
            raise BadRequest()
        return redirect(reverse(self.redirect_url_name, args=[user.pk]))


@method_decorator(login_required, name="dispatch")
class DeleteSkill(View):
    model = Skill
    redirect_url_name = 'skills'

    def post(self, request, user, pk, *args, **kwargs):
        if not User.objects.filter(pk=user).exists() or not self.model.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=user)
        if not self.model.objects.get_remove_permission(user, self.request.user):
            raise PermissionDenied()
        obj = self.model.objects.get(pk=pk)
        if not obj.users.filter(pk=user.pk).exists():
            raise BadRequest()
        obj.users.remove(user)
        obj.save()
        return redirect(reverse(self.redirect_url_name, args=[user.pk]))


# Language

@method_decorator(login_required, name="dispatch")
class AddLanguage(View):
    model = Language
    form = LanguageForm
    redirect_url_name = 'languages'

    def post(self, request, user, *args, **kwargs):
        if not User.objects.filter(pk=user).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=user)
        if not self.model.objects.get_add_permission(user, self.request.user):
            raise PermissionDenied()
        form = self.form(request.POST)
        if form.is_valid():
            languages = form.cleaned_data['name'].split(',')
            for language in languages:
                language = language.strip()
                if not language:
                    continue
                if self.model.objects.filter(name__iexact=language).exists():
                    obj = self.model.objects.get(name__iexact=language)
                    obj.users.add(user)
                    obj.save()
                else:
                    obj = self.model.objects.create(name=language)
                    obj.users.add(user)
                    obj.save()
        else:
            raise BadRequest()
        return redirect(reverse(self.redirect_url_name, args=[user.pk]))


@method_decorator(login_required, name="dispatch")
class DeleteLanguage(View):
    model = Language
    redirect_url_name = 'languages'

    def post(self, request, user, pk, *args, **kwargs):
        if not User.objects.filter(pk=user).exists() or not self.model.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=user)
        if not self.model.objects.get_remove_permission(user, self.request.user):
            raise PermissionDenied()
        obj = self.model.objects.get(pk=pk)
        if not obj.users.filter(pk=user.pk).exists():
            raise BadRequest()
        obj.users.remove(user)
        obj.save()
        return redirect(reverse(self.redirect_url_name, args=[user.pk]))


# Work Experience

@method_decorator(login_required, name="dispatch")
class AddWorkExperience(AddUserKeyObject):
    model = WorkExperience
    form = WorkExperienceForm
    redirect_url_name = 'work_experiences'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeWorkExperience(ChangeUserKeyObject):
    model = WorkExperience
    form = WorkExperienceForm
    redirect_url_name = 'work_experiences'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteWorkExperience(DeleteUserKeyObject):
    model = WorkExperience
    redirect_url_name = 'work_experiences'


# Project

@method_decorator(login_required, name="dispatch")
class AddProject(AddUserKeyObject):
    model = Project
    form = ProjectForm
    redirect_url_name = 'projects'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeProject(ChangeUserKeyObject):
    model = Project
    form = ProjectForm
    redirect_url_name = 'projects'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteProject(DeleteUserKeyObject):
    model = Project
    redirect_url_name = 'projects'


# Patent

@method_decorator(login_required, name="dispatch")
class AddPatent(AddUserKeyObject):
    model = Patent
    form = PatentForm
    redirect_url_name = 'patents'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangePatent(ChangeUserKeyObject):
    model = Patent
    form = PatentForm
    redirect_url_name = 'patents'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeletePatent(DeleteUserKeyObject):
    model = Patent
    redirect_url_name = 'patents'


# Publication

@method_decorator(login_required, name="dispatch")
class AddPublication(AddUserKeyObject):
    model = Publication
    form = PublicationForm
    redirect_url_name = 'publications'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangePublication(ChangeUserKeyObject):
    model = Publication
    form = PublicationForm
    redirect_url_name = 'publications'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeletePublication(DeleteUserKeyObject):
    model = Publication
    redirect_url_name = 'publications'


# Achievement

@method_decorator(login_required, name="dispatch")
class AddAchievement(AddUserKeyObject):
    model = Achievement
    form = AchievementForm
    redirect_url_name = 'achievements'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeAchievement(ChangeUserKeyObject):
    model = Achievement
    form = AchievementForm
    redirect_url_name = 'achievements'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteAchievement(DeleteUserKeyObject):
    model = Achievement
    redirect_url_name = 'achievements'


# Presentation

@method_decorator(login_required, name="dispatch")
class AddPresentation(AddUserKeyObject):
    model = Presentation
    form = PresentationForm
    redirect_url_name = 'presentations'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangePresentation(ChangeUserKeyObject):
    model = Presentation
    form = PresentationForm
    redirect_url_name = 'presentations'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeletePresentation(DeleteUserKeyObject):
    model = Presentation
    redirect_url_name = 'presentations'


# Other Info

@method_decorator(login_required, name="dispatch")
class AddOtherInfo(AddUserKeyObject):
    model = OtherInfo
    form = OtherInfoForm
    redirect_url_name = 'other_infos'

    def get(self, request, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeOtherInfo(ChangeUserKeyObject):
    model = OtherInfo
    form = OtherInfoForm
    redirect_url_name = 'other_infos'

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteOtherInfo(DeleteUserKeyObject):
    model = OtherInfo
    redirect_url_name = 'other_infos'


class SkillAutocomplete(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        user = request.GET.get('u')
        post = request.GET.get('p')
        if user:
            li = [obj.name for obj in Skill.objects.exclude(
                users__id=user).filter(name__icontains=query)]
        elif post:
            li = [obj.name for obj in Skill.objects.exclude(
                jobs__id=post).filter(name__icontains=query)]
        else:
            li = [obj.name for obj in Skill.objects.filter(
                name__icontains=query)]
        return JsonResponse(li, safe=False)


class LanguageAutocomplete(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        user = request.GET.get('u')
        li = [obj.name for obj in Language.objects.exclude(
            users__id=user).filter(name__icontains=query)]
        return JsonResponse(li, safe=False)
