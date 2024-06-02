from django.shortcuts import render, redirect, reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from views import AddObject, ChangeObject, AddUserKeyObject, ChangeUserKeyObject, DeleteUserKeyObject
from student.models import StudentProfile
from .forms import UserForm, PhoneNumberForm, EmailForm, AddressForm, LinkForm
from .models import User, PhoneNumber, Email, Address, Link

# Create your views here.


@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = User
    template_name = 'users.html'
    context_object_name = 'users'
    ordering = ['id']
    paginate_by = 10

    def get_queryset(self):
        filters = self.request.GET.get('filters', '{"role": [ "staff", "student" ]}')
        orderby = self.request.GET.get('orderby', 'id')
        new_context = self.model.objects.filter(
            state=filter_val,
        ).order_by(orderby)
        return new_context

    def get_context_data(self, **kwargs):
        context = super(MyView, self).get_context_data(**kwargs)
        context['filters'] = self.request.GET.get('filter', 'give-default-value')
        context['orderby'] = self.request.GET.get('orderby', 'id')
        return context


class SignIn(TemplateView):
    template_name = 'sign_in.html'


@method_decorator(login_required, name="dispatch")
class BuildProfile(TemplateView):
    template_name = 'build_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'student_profile'):
            context['profile'] = self.request.user.student_profile
        elif hasattr(self.request.user, 'staff_profile'):
            context['profile'] = self.request.user.staff_profile
        elif hasattr(self.request.user, 'recruiter_profile'):
            context['profile'] = self.request.user.recruiter_profile
        else:
            raise PermissionDenied()
        return context


@method_decorator(login_required, name="dispatch")
class UpdatePersonalContactInfo(TemplateView):
    template_name = 'update_personal_contact_info.html'

    def get(self, request, pk):
        if not pk.isdigit():
            return redirect('update_personal_contact_info', self.request.user.id)
        else:
            pk = int(pk)
            if not User.objects.filter(pk=pk).exists():
                raise ObjectDoesNotExist()
            elif User.objects.get(pk=pk) != self.request.user and not request.user.is_superuser:
                raise PermissionDenied()
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])

        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['phone_numbers'] = PhoneNumber.objects.filter(user=user)
        context['emails'] = Email.objects.filter(user=user)
        context['addresses'] = Address.objects.filter(user=user)
        context['links'] = Link.objects.filter(user=user)
        context['phone_number_form'] = PhoneNumberForm({'user': user.pk})
        context['email_form'] = EmailForm({'user': user.pk})
        context['link_form'] = LinkForm({'user': user.pk})
        return context


@method_decorator(login_required, name="dispatch")
class ChangeUser(ChangeObject):
    model = User
    form = UserForm
    template_name = 'user.html'
    redirect_url_name = 'update_personal_contact_info'
    redirect_url_params = '#personal-info'

    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk) != self.request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get_redirect_url(self, request, pk, *args, **kwargs):
        return reverse(self.redirect_url_name, args=[pk]) + self.redirect_url_params

    def get(self, request, pk):
        return super().get(request, pk, id=request.user.id)

    def post(self, request, pk):
        return super().post(request, pk, id=request.user.id)


@method_decorator(login_required, name="dispatch")
class AddPhoneNumber(AddUserKeyObject):
    model = PhoneNumber
    form = PhoneNumberForm
    redirect_url_name = 'phone_numbers'

    def get(self, request, user):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class SetPrimaryPhoneNumber(ChangeObject):
    model = PhoneNumber
    redirect_url_name = 'phone_numbers'

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if self.model.objects.filter(pk=pk, user=request.user).exists():
            obj = self.model.objects.get(pk=pk, user=request.user)
            obj.is_primary = True
            obj.save()
        return redirect(self.get_redirect_url(request, pk, user=obj.user))


@method_decorator(login_required, name="dispatch")
class DeletePhoneNumber(DeleteUserKeyObject):
    model = PhoneNumber
    redirect_url_name = 'phone_numbers'

    def post(self, request, pk):
        return super().post(request, pk, is_primary=False)


@method_decorator(login_required, name="dispatch")
class AddEmail(AddUserKeyObject):
    model = Email
    form = EmailForm
    redirect_url_name = 'emails'

    def get(self, request, user):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class SetPrimaryEmail(ChangeObject):
    model = Email
    redirect_url_name = 'emails'

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if self.model.objects.filter(pk=pk, user=request.user).exists():
            obj = self.model.objects.get(pk=pk, user=request.user)
            obj.is_primary = True
            obj.save()
        return redirect(self.get_redirect_url(request, pk, user=obj.user))


@method_decorator(login_required, name="dispatch")
class DeleteEmail(DeleteUserKeyObject):
    model = Email
    redirect_url_name = 'emails'

    def post(self, request, pk):
        return super().post(request, pk, is_primary=False)


@method_decorator(login_required, name="dispatch")
class AddAddress(AddUserKeyObject):
    model = Address
    form = AddressForm
    template_name = 'address.html'
    redirect_url_name = 'addresses'


@method_decorator(login_required, name="dispatch")
class SetPrimaryAddress(ChangeUserKeyObject):
    model = Address
    redirect_url_name = 'addresses'

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if self.model.objects.filter(pk=pk, user=request.user).exists():
            obj = self.model.objects.get(pk=pk, user=request.user)
            obj.is_primary = True
            obj.save()
        return redirect(self.get_redirect_url(request, pk, user=obj.user))


@method_decorator(login_required, name="dispatch")
class ChangeAddress(ChangeUserKeyObject):
    model = Address
    form = AddressForm
    template_name = 'address.html'
    redirect_url_name = 'addresses'


@method_decorator(login_required, name="dispatch")
class DeleteAddress(DeleteUserKeyObject):
    model = Address
    redirect_url_name = 'addresses'

    def post(self, request, pk):
        return super().post(request, pk, is_primary=False)


@method_decorator(login_required, name="dispatch")
class AddLink(AddUserKeyObject):
    model = Link
    form = LinkForm
    redirect_url_name = 'links'

    def get(self, request, user):
        raise BadRequest()

@method_decorator(login_required, name="dispatch")
class DeleteLink(DeleteUserKeyObject):
    model = Link
    redirect_url_name = 'links'