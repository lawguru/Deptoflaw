from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.views import View
from user.models import User

class ObjectView(View):
    model = None
    redirect_url_name = None
    redirect_url_params = ''
    redirect_url_args = []

    def check_permission(self, request, *args, **kwargs):
        return True

    def get_redirect_url(self, request, *args, **kwargs):
        return reverse(self.redirect_url_name, args=self.redirect_url_args) + self.redirect_url_params

class AddObject(ObjectView):
    form = None
    template_name = None

    def form_unvalid(self, request, form, *args, **kwargs):
        raise BadRequest()

    def get(self, request, *args, **kwargs):
        if not self.check_permission(request, *args, **kwargs):
            raise PermissionDenied()
        if self.template_name and self.form:
            return render(request, self.template_name, {'form': self.form()})
        return redirect(self.get_redirect_url(request, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        if not self.check_permission(request, *args, **kwargs):
            raise PermissionDenied()
        form = self.form(request.POST)
        if form.is_valid():
            for key in kwargs:
                if key not in form.cleaned_data:
                    form.cleaned_data[key] = kwargs[key]
            self.model.objects.create(**form.cleaned_data)
        else:
            self.form_unvalid(request, form, *args, **kwargs)
        return redirect(self.get_redirect_url(request, *args, **kwargs))

class ChangeObject(ObjectView):
    form = None
    template_name = None

    def check_permission(self, request, pk, *args, **kwargs):
        return True

    def get_redirect_url(self, request, pk, *args, **kwargs):
        return reverse(self.redirect_url_name, args=self.redirect_url_args) + self.redirect_url_params

    def form_unvalid(self, request, form, *args, **kwargs):
        raise BadRequest()

    def get(self, request, pk, *args, **kwargs):
        if self.model.objects.filter(pk=pk, **kwargs).exists():
            obj = self.model.objects.get(pk=pk, **kwargs)
            if self.template_name and self.form:
                return render(request, self.template_name, {'form': self.form(instance=obj)})
            return redirect(self.get_redirect_url(request, *args, **kwargs))
        if not self.check_permission(request, pk, *args, **kwargs):
            raise PermissionDenied()
        raise ObjectDoesNotExist()

    def post(self, request, pk, *args, **kwargs):
        if self.model.objects.filter(pk=pk, **kwargs).exists():
            redirect_url = self.get_redirect_url(request, pk, *args, **kwargs)
            obj = self.model.objects.get(pk=pk, **kwargs)
            form = self.form(request.POST, instance=obj)
            if form.is_valid():
                form.save()
            else:
                self.form_unvalid(request, form, *args, **kwargs)
            return redirect(redirect_url)
        if not self.check_permission(request, pk, *args, **kwargs):
            raise PermissionDenied()
        raise ObjectDoesNotExist()

class DeleteObject(ObjectView):
    def check_permission(self, request, pk, *args, **kwargs):
        return True

    def get_redirect_url(self, request, pk, *args, **kwargs):
        return reverse(self.redirect_url_name, args=self.redirect_url_args) + self.redirect_url_params

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()

    def post(self, request, pk, *args, **kwargs):
        if self.model.objects.filter(pk=pk, **kwargs).exists():
            redirect_url = self.get_redirect_url(request, pk, *args, **kwargs)
            self.model.objects.get(pk=pk, **kwargs).delete()
            return redirect(redirect_url)
        if not self.check_permission(request, pk, *args, **kwargs):
            raise PermissionDenied()
        raise ObjectDoesNotExist()

@method_decorator(login_required, name="dispatch")
class AddUserKeyObject(AddObject):
    def check_permission(self, request, *args, **kwargs):
        if kwargs['user'] != self.request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, kwargs['user'], *args, **kwargs)

    def get_redirect_url(self, request, *args, **kwargs):
        return reverse(self.redirect_url_name, args=[kwargs['user'].pk]) + self.redirect_url_params

    def get(self, request, user):
        user = int(user) if user.isdigit() else request.user.pk
        if not User.objects.filter(pk=user).exists():
            raise ObjectDoesNotExist()
        return super().get(request, user=User.objects.get(pk=user))
    
    def post(self, request, user):
        user = int(user) if user.isdigit() else request.user.pk
        return super().post(request, user=User.objects.get(pk=user))

@method_decorator(login_required, name="dispatch")
class ChangeUserKeyObject(ChangeObject):
    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk).user != self.request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get_redirect_url(self, request, pk, *args, **kwargs):
        user = self.model.objects.get(pk=pk).user.pk
        return reverse(self.redirect_url_name, args=[user]) + self.redirect_url_params

@method_decorator(login_required, name="dispatch")
class DeleteUserKeyObject(DeleteObject):
    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk).user != self.request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get_redirect_url(self, request, pk, *args, **kwargs):
        user = self.model.objects.get(pk=pk).user.pk
        return reverse(self.redirect_url_name, args=[user]) + self.redirect_url_params
