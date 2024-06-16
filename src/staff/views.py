from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, reverse
from views import ChangeUserKeyObject
from user.models import Email
from .models import StaffProfile
from .forms import *
from django.views.generic.base import TemplateView

# Create your views here.

class StaffSignUp(TemplateView):
    template_name = 'staff_sign_up.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StaffSignUpForm()
        return context

    def post(self, request):
        form = StaffSignUpForm(request.POST)
        if form.is_valid():
            email = Email.objects.create(email=form.cleaned_data['email'])
            staff = StaffProfile.objects.create(
                id_number=form.cleaned_data['id_number'], qualification=form.cleaned_data['qualification'], designation=form.cleaned_data['designation'], primary_email=email)
            staff.user.first_name = form.cleaned_data['first_name']
            staff.user.last_name = form.cleaned_data['last_name']
            staff.user.set_password(form.cleaned_data['password'])
            staff.user.save()
            email.save()
            return redirect(reverse('staff_sign_in') + f'?next={reverse("build_profile", args=[staff.user.pk])}')
        return render(request, self.template_name, {'form': form})


class StaffSignIn(TemplateView):
    template_name = 'staff_sign_in.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StaffSigninForm()
        return context

    def post(self, request):
        form = StaffSigninForm(request.POST)
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            password = form.cleaned_data['password']
            if StaffProfile.objects.filter(id_number=id_number).exists():
                staff = StaffProfile.objects.get(
                    id_number=id_number)
                user = authenticate(username=staff.user.pk, password=password)
                if user is not None:
                    login(request, user)
                    next = request.GET.get('next')
                    if next:
                        return redirect(next)
                    return redirect('build_profile', user.pk)
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name="dispatch")
class StaffProfileDetail(TemplateView):
    template_name = 'staff_profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = StaffProfile.objects.get(
            pk=self.kwargs['pk'])
        return context

    def get(self, request, pk):
        if not StaffProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        staff_profile = StaffProfile.objects.get(pk=pk)
        if staff_profile.user != request.user and not request.user.is_superuser and not request.user.is_coordinator():
            raise PermissionDenied()
        if staff_profile.user == request.user and not staff_profile.user.is_approved:
            return redirect('build_profile', staff_profile.user.pk)
        return super().get(request, pk)


@method_decorator(login_required, name="dispatch")
class StaffInfo(TemplateView):
    template_name = 'staff_info.html'

    def check_write_permission(self, **kwargs):
        return True if self.request.user.is_superuser or self.request.user == StaffProfile.objects.get(pk=self.kwargs['pk']).user else False

    def get(self, request, pk):
        if not StaffProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        elif StaffProfile.objects.get(pk=pk).user != request.user and not request.user.is_superuser:
            raise PermissionDenied()
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        profile = StaffProfile.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['user'] = profile.user
        context['profile'] = profile
        if self.check_write_permission(**kwargs):
            context['write_permission'] = True
            context['change_profile_form'] = StaffProfileForm(
                instance=profile)
        return context


@method_decorator(login_required, name="dispatch")
class ChangeStaffProfile(ChangeUserKeyObject):
    model = StaffProfile
    form = StaffProfileForm
    template_name = 'staff_profile.html'
    redirect_url_name = 'staff_profile'

    def get_redirect_url_args(self, request, pk):
        return [pk]

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()