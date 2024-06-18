from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, reverse
from views import ChangeUserKeyObject
from user.models import Email, User
from .models import RecruiterProfile
from .forms import *
from django.views.generic.base import TemplateView, RedirectView

# Create your views here.


class RecruiterSignUp(TemplateView):
    template_name = 'recruiter_sign_up.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RecruiterSignUpForm()
        return context

    def post(self, request):
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            email, created = Email.objects.get_or_create(
                email=form.cleaned_data['email'])
            if email.user:
                return render(request, self.template_name, {'form': form, 'error': 'Email already in use'})
            user = User.objects.create(role='recruiter', primary_email=email)
            recruiter = RecruiterProfile.objects.create(user=user,
                                                        company_name=form.cleaned_data['company_name'], designation=form.cleaned_data['designation'])
            recruiter.user.first_name = form.cleaned_data['first_name']
            recruiter.user.last_name = form.cleaned_data['last_name']
            recruiter.user.primary_email = email
            recruiter.user.set_password(form.cleaned_data['password'])
            recruiter.user.save()
            email.save()
            return redirect(reverse('recruiter_sign_in') + f'?next={reverse("build_profile", args=[recruiter.user.pk])}')
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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if not Email.objects.filter(email=email).exists():
                return render(request, self.template_name, {'form': form, 'error': 'Email does not exist'})
            email = Email.objects.get(email=email)
            if email.user:
                user = authenticate(
                    username=email.user.pk, password=password)
                if user is not None:
                    login(request, user)
                    next = request.GET.get('next')
                    if next:
                        return redirect(next)
                    return redirect('build_profile', user.pk)
                return render(request, self.template_name, {'form': form, 'error': 'Invalid password'})
            return render(request, self.template_name, {'form': form, 'error': 'No user with this email'})
        return render(request, self.template_name, {'form': form, 'error': 'Invalid form data'})


@method_decorator(login_required, name="dispatch")
class RecruiterInfo(TemplateView):
    template_name = 'recruiter_info.html'

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
        
        if self.request.user in profile.edit_users:
            context['change_profile_form'] = RecruiterProfileForm(
                instance=profile)
        return context


@method_decorator(login_required, name="dispatch")
class ChangeRecruiterProfile(ChangeUserKeyObject):
    model = RecruiterProfile
    form = RecruiterProfileForm
    template_name = 'recruiter_profile.html'
    redirect_url_name = 'recruiter_profile'

    def get_redirect_url_args(self, request, pk):
        return [pk]

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()
