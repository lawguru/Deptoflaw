from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, reverse
from views import ChangeObject, ChangeUserKeyObject
from user.models import Email
from .models import StudentProfile, SemesterReportCard
from .forms import *
from django.views.generic import ListView
from django.views.generic.base import TemplateView

# Create your views here.

@method_decorator(login_required, name="dispatch")
class StudentListView(ListView):
    model = StudentProfile
    template_name = 'students.html'
    context_object_name = 'students'
    ordering = ['registration_number']
    paginate_by = 10

    headers = {
        'ID': 'id_card',
        'Registration Number': 'registration_number',
        'Name': 'user__full_name',
        'Phone Number': 'user__primary_phone_number',
        'Email': 'user__primary_email',
        'Course': 'course',
        'Roll': 'roll',
        'Number': 'number',
        'Semester': 'semester',
        'Year': 'year',
        'Backlogs': 'backlog_count',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        students_list = []
        for student in context['students']:
            students_list.append({})
            for key, value in self.headers.items():
                if '__' not in value:
                    students_list[-1][value] = getattr(student, value)
                else:
                    property_splits = value.split('__')
                    students_list[-1][value] = getattr(
                        student, property_splits[0])
                    for split in property_splits[1:]:
                        students_list[-1][value] = getattr(
                            students_list[-1][value], split)

        context['headers_property'] = [
            value for key, value in self.headers.items()]
        context['headers_label'] = [key for key, value in self.headers.items()]
        context['students'] = students_list
        return context


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
            return redirect('student_sign_in')
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
                user = authenticate(username=student.user.pk, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('build_profile')
                else:
                    return render(request, self.template_name, {'form': form, 'error': 'Wrong Password'})
            else:
                return render(request, self.template_name, {'form': form, 'error': 'Invalid Registration Number'})
        else:
            raise BadRequest()
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
        if student_profile.user != request.user and not request.user.is_superuser and not request.user.is_coordinator():
            raise PermissionDenied()
        if student_profile.user == request.user and not student_profile.user.is_approved:
            return redirect('build_profile')
        return super().get(request, pk)


@method_decorator(login_required, name="dispatch")
class UpdateAcademicInfo(TemplateView):
    template_name = 'update_academic_info.html'

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
        context['semester_report_cards'] = SemesterReportCard.objects.filter(
            student_profile=profile)[0:profile.semester]
        return context


@method_decorator(login_required, name="dispatch")
class ChangeStudentProfile(ChangeUserKeyObject):
    model = StudentProfile
    form = StudentProfileForm
    template_name = 'student_profile.html'
    redirect_url_name = 'student_profile'

    def get_redirect_url_args(self, request, pk):
        return [pk]


@method_decorator(login_required, name="dispatch")
class ChangeSemesterReportCard(ChangeObject):
    model = SemesterReportCard
    form = SemesterReportCardForm
    template_name = 'semester_report_card.html'
    redirect_url_name = 'update_academic_info'
    redirect_url_params = '#semester-report-cards'

    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk).student_profile.user != request.user and not request.user.is_superuser():
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get_redirect_url(self, request, pk, *args, **kwargs):
        profile = self.model.objects.get(pk=pk).student_profile.pk
        return reverse(self.redirect_url_name, args=[profile]) + self.redirect_url_params

    def get(self, request, profile, sem):
        if not self.model.objects.filter(student_profile=profile).exists():
            raise ObjectDoesNotExist()
        obj = [obj for obj in self.model.objects.filter(
            student_profile=profile)][sem-1]
        return super().get(request, obj.pk)

    def post(self, request, profile, sem):
        if not self.model.objects.filter(student_profile=profile).exists():
            raise ObjectDoesNotExist()
        obj = [obj for obj in self.model.objects.filter(
            student_profile=profile)][sem-1]
        return super().post(request, obj.pk)
