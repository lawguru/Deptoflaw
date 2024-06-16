from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, reverse
from views import ChangeObject, ChangeUserKeyObject
from user.models import Email
from .models import *
from .forms import *
from django.views.generic import ListView
from django.views.generic.base import TemplateView

# Create your views here.

class StudentSignUp(TemplateView):
    template_name = 'student_sign_up.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StudentSignUpForm()
        return context

    def post(self, request):
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            email = Email.objects.create(email=form.cleaned_data['email'])
            student = StudentProfile.objects.create(registration_number=form.cleaned_data['registration_number'], course=form.cleaned_data['course'], number=int(
                form.cleaned_data['number']), id_number=int(form.cleaned_data['id_number']), primary_email=email)
            student.user.first_name = form.cleaned_data['first_name']
            student.user.last_name = form.cleaned_data['last_name']
            student.user.set_password(form.cleaned_data['password'])
            student.user.save()
            email.save()
            return redirect(reverse('student_sign_in')+f'?next={reverse("build_profile", args=[student.user.pk])}')
        return render(request, self.template_name, {'form': form})


class StudentSignIn(TemplateView):
    template_name = 'student_sign_in.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StudentSigninForm()
        return context

    def post(self, request):
        form = StudentSigninForm(request.POST)
        if form.is_valid():
            registration_number = form.cleaned_data['registration_number']
            password = form.cleaned_data['password']
            if StudentProfile.objects.filter(registration_number=int(registration_number)).exists():
                student = StudentProfile.objects.get(
                    registration_number=int(registration_number))
                user = authenticate(
                    username=student.user.pk, password=password)
                if user is not None:
                    login(request, user)
                    next = request.GET.get('next')
                    if next:
                        return redirect(next)
                    return redirect('build_profile', user.pk)
                return render(request, self.template_name, {'form': form, 'error': 'Wrong Password'})
            return render(request, self.template_name, {'form': form, 'error': 'Invalid Registration Number'})
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name="dispatch")
class StudentProfileDetail(TemplateView):
    template_name = 'student_profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = StudentProfile.objects.get(
            pk=self.kwargs['pk'])
        return context

    def get(self, request, pk):
        if not StudentProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        student_profile = StudentProfile.objects.get(pk=pk)
        if student_profile.user != request.user and not request.user.is_superuser and not request.user.is_coordinator:
            raise PermissionDenied()
        if student_profile.user == request.user and not student_profile.user.is_approved:
            return redirect('build_profile', student_profile.user.pk)
        return super().get(request, pk)


@method_decorator(login_required, name="dispatch")
class AcademicInfo(TemplateView):
    template_name = 'academic_info.html'

    def check_write_permission(self, **kwargs):
        return True if self.request.user.is_superuser or self.request.user == StudentProfile.objects.get(pk=self.kwargs['pk']).user else False

    def get(self, request, pk):
        if not StudentProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        elif StudentProfile.objects.get(pk=pk).user != request.user and not request.user.is_superuser:
            raise PermissionDenied()
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        profile = StudentProfile.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['user'] = profile.user
        context['profile'] = profile
        context['semester_report_cards'] = [(semester_report_card, SemesterReportCardForm(instance=semester_report_card)) for semester_report_card in SemesterReportCard.objects.filter(
            student_profile=profile)[0:profile.semester]]
        if self.check_write_permission(**kwargs):
            context['write_permission'] = True
            context['semester_report_card_empty_form'] = SemesterReportCardForm()
            context['change_profile_form'] = StudentProfileForm(
                instance=profile)
        return context


@method_decorator(login_required, name="dispatch")
class ChangeStudentProfile(ChangeUserKeyObject):
    model = StudentProfile
    form = StudentProfileForm
    redirect_url_name = 'student_profile'

    def get_redirect_url_args(self, request, pk):
        return [pk]

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeSemesterReportCard(ChangeObject):
    model = SemesterReportCard
    form = SemesterReportCardForm
    redirect_url_name = 'academic_info'
    redirect_url_params = '#semester-report-cards'

    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk).student_profile.user != request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get_redirect_url(self, request, pk, *args, **kwargs):
        profile = self.model.objects.get(pk=pk).student_profile.pk
        return reverse(self.redirect_url_name, args=[profile]) + self.redirect_url_params

    def get(self, request, pk):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class SemesterReportCardTemplateListView(TemplateView):
    template_name = 'semester_report_card_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empty_form'] = SemesterReportCardTemplateForm()
        context['semester_report_card_templates'] = [
            (semester_report_card_template,
                SemesterReportCardTemplateForm(
                    instance=semester_report_card_template),
                {
                    'course': semester_report_card_template.course,
                    'semester': semester_report_card_template.semester,
                    'subjects': [
                        {
                            'name': semester_report_card_template.subjects[i],
                            'code': semester_report_card_template.subject_codes[i],
                            'credits': semester_report_card_template.subject_credits[i],
                            'passing_grade_points': semester_report_card_template.subject_passing_grade_points[i]
                        } for i in range(len(semester_report_card_template.subjects))
                    ]
                }
             ) for semester_report_card_template in SemesterReportCardTemplate.objects.all()
        ]
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.is_coordinator:
            raise PermissionDenied()
        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class ChangeSemesterReportCardTemplate(ChangeObject):
    model = SemesterReportCardTemplate
    form = SemesterReportCardTemplateForm
    redirect_url_name = 'semester_report_card_template'

    def check_permission(self, request, pk, *args, **kwargs):
        if not request.user.is_superuser and not request.user.is_coordinator:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get(self, request, pk):
        raise BadRequest()
