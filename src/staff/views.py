from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, reverse
from views import ChangeUserKeyObject
from user.models import Email, User
from .models import StaffProfile
from .forms import *
from django.views.generic.base import TemplateView, View

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
            email, created = Email.objects.get_or_create(
                email=form.cleaned_data['email'])
            if email.user:
                return render(request, self.template_name, {'form': form, 'error': 'Email already in use'})
            user = User.objects.create(role='staff', primary_email=email)
            if StaffProfile.objects.filter(id_number=form.cleaned_data['id_number']).exists():
                user.delete()
                return render(request, self.template_name, {'form': form, 'error': 'Staff with that ID number already exists'})
            staff = StaffProfile.objects.create(user=user,
                                                id_number=form.cleaned_data['id_number'], qualification=form.cleaned_data['qualification'], designation=form.cleaned_data['designation'])
            staff.user.first_name = form.cleaned_data['first_name']
            staff.user.last_name = form.cleaned_data['last_name']
            staff.user.primary_email = email
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
            email_or_id = form.cleaned_data['email_or_id']
            if StaffProfile.objects.filter(id_number=email_or_id).exists():
                user = StaffProfile.objects.get(id_number=email_or_id).user
            elif Email.objects.filter(email=email_or_id).exists():
                user = Email.objects.get(email=email_or_id).user

            if user is not None:
                login(request, user)
                next = request.GET.get('next')
                if next:
                    return redirect(next)
                return redirect('build_profile', user.pk)
            
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name="dispatch")
class MakeHOD(View):
    def post(self, request, pk):
        if not StaffProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        staff = StaffProfile.objects.get(pk=pk)
        if request.user not in staff.make_hod_users:
            raise PermissionDenied()
        staff.is_hod = True
        staff.save()
        return redirect('staff_list')


@method_decorator(login_required, name="dispatch")
class MakeTPCHead(View):
    def post(self, request, pk):
        if not StaffProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        staff = StaffProfile.objects.get(pk=pk)
        if request.user not in staff.make_tpc_head_users:
            raise PermissionDenied()
        staff.is_tpc_head = True
        staff.save()
        return redirect('staff_list')


@method_decorator(login_required, name="dispatch")
class StaffInfo(TemplateView):
    template_name = 'staff_info.html'

    def get(self, request, pk):
        if not StaffProfile.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        staff = StaffProfile.objects.get(pk=pk)
        if request.user not in staff.view_users:
            raise PermissionDenied()
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        profile = StaffProfile.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['user'] = profile.user
        context['profile'] = profile
        if self.request.user in profile.edit_users:
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
