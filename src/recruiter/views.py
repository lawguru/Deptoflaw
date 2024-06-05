from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, reverse
from views import ChangeUserKeyObject
from user.models import Email
from .models import RecruiterProfile
from .forms import *
from django.views.generic import ListView
from django.views.generic.base import TemplateView, RedirectView

# Create your views here.

@method_decorator(login_required, name="dispatch")
class RecruiterListView(ListView):
    model = RecruiterProfile
    template_name = 'recruiters.html'
    context_object_name = 'recruiters'
    ordering = ['id_number']
    paginate_by = 10

    headers = {
        'ID': 'id_number',
        'Name': 'user__full_name',
        'Phone Number': 'user__primary_phone_number',
        'Email': 'user__primary_email',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recruiters_list = []
        for recruiter in context['recruiters']:
            recruiters_list.append({})
            for key, value in self.headers.items():
                if '__' not in value:
                    recruiters_list[-1][value] = getattr(recruiter, value)
                else:
                    property_splits = value.split('__')
                    recruiters_list[-1][value] = getattr(
                        recruiter, property_splits[0])
                    for split in property_splits[1:]:
                        recruiters_list[-1][value] = getattr(
                            recruiters_list[-1][value], split)

        context['headers_property'] = [
            value for key, value in self.headers.items()]
        context['headers_label'] = [key for key, value in self.headers.items()]
        context['recruiters'] = recruiters_list
        return context


class RecruiterSignUp(TemplateView):
    template_name = 'recruiter_sign_up.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RecruiterSignUpForm()
        return context

    def post(self, request):
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            email = Email.objects.create(email=form.cleaned_data['email'])
            recruiter = RecruiterProfile.objects.create(company_name=form.cleaned_data['company_name'], designation=form.cleaned_data['designation'], primary_email=email)
            recruiter.user.first_name = form.cleaned_data['first_name']
            recruiter.user.last_name = form.cleaned_data['last_name']
            recruiter.user.set_password(form.cleaned_data['password'])
            recruiter.user.save()
            email.save()
            return redirect('recruiter_sign_in')
        return render(request, self.template_name, {'form': form})


class RecruiterSignIn(TemplateView):
    template_name = 'recruiter_sign_in.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RecruiterSigninForm()
        return context

    def post(self, request):
        form = RecruiterSigninForm(request.POST)
        if form.is_valid():
            primary_email = form.cleaned_data['primary_email']
            password = form.cleaned_data['password']
            if RecruiterProfile.objects.filter(user__primary_email__email=primary_email).exists():
                recruiter = RecruiterProfile.objects.get(
                    user__primary_email__email=primary_email)
                user = authenticate(username=recruiter.user.pk, password=password)
                if user is not None:
                    login(request, user)
                return redirect('build_profile')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name="dispatch")
class RecruiterProfileDetail(TemplateView):
    template_name = 'recruiter_profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recruiter'] = RecruiterProfile.objects.get(
            pk=self.kwargs['pk'])
        return context
    
    def get(self, request, pk):
        if not RecruiterProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        recruiter_profile = RecruiterProfile.objects.get(pk=pk)
        if recruiter_profile.user != request.user and not request.user.is_superuser and not request.user.is_coordinator():
            raise PermissionDenied()
        if recruiter_profile.user == request.user and not recruiter_profile.user.is_approved:
            return redirect('build_profile')
        return super().get(request, pk)


@method_decorator(login_required, name="dispatch")
class UpdateRecruiterInfo(TemplateView):
    template_name = 'update_recruiter_info.html'

    def get(self, request, pk):
        if not RecruiterProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        elif RecruiterProfile.objects.get(pk=pk).user != request.user and not request.user.is_superuser:
            raise PermissionDenied()
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        profile = RecruiterProfile.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['user'] = profile.user
        context['profile'] = profile
        return context


@method_decorator(login_required, name="dispatch")
class ChangeRecruiterProfile(ChangeUserKeyObject):
    model = RecruiterProfile
    form = RecruiterProfileForm
    template_name = 'recruiter_profile.html'
    redirect_url_name = 'recruiter_profile'

    def get_redirect_url_args(self, request, pk):
        return [pk]