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

    def get_redirect_url_args(self, request, *args, **kwargs):
        return []

    def check_permission(self, request, *args, **kwargs):
        return True

    def get_redirect_url(self, request, *args, **kwargs):
        return reverse(self.redirect_url_name, args=self.get_redirect_url_args(request, *args, **kwargs)) + self.redirect_url_params


class AddObject(ObjectView):
    form = None
    template_name = None

    def form_unvalid(self, request, form, *args, **kwargs):
        print(form.errors)
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

    def form_unvalid(self, request, form, *args, **kwargs):
        print(form.errors)
        raise BadRequest()

    def get(self, request, pk, *args, **kwargs):
        if not self.model.objects.filter(pk=pk, **kwargs).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, pk, *args, **kwargs):
            raise PermissionDenied()
        obj = self.model.objects.get(pk=pk, **kwargs)
        if self.template_name and self.form:
            return render(request, self.template_name, {'form': self.form(instance=obj)})
        return redirect(self.get_redirect_url(request, *args, pk, **kwargs))

    def post(self, request, pk, *args, **kwargs):
        if not self.model.objects.filter(pk=pk, **kwargs).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, pk, *args, **kwargs):
            raise PermissionDenied()
        redirect_url = self.get_redirect_url(request, pk, *args, **kwargs)
        obj = self.model.objects.get(pk=pk, **kwargs)
        form = self.form(request.POST, instance=obj)
        if form.is_valid():
            form.save()
        else:
            self.form_unvalid(request, form, *args, **kwargs)
        return redirect(redirect_url)


class DeleteObject(ObjectView):
    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()

    def post(self, request, pk, *args, **kwargs):
        if not self.model.objects.filter(pk=pk, **kwargs).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, pk, *args, **kwargs):
            raise PermissionDenied()
        redirect_url = self.get_redirect_url(request, pk, *args, **kwargs)
        self.model.objects.get(pk=pk, **kwargs).delete()
        return redirect(redirect_url)


@method_decorator(login_required, name="dispatch")
class AddUserKeyObject(AddObject):
    def check_permission(self, request, *args, **kwargs):
        if User.objects.get(pk=kwargs['user']) != request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, kwargs['user'], *args, **kwargs)

    def get_redirect_url_args(self, request, *args, **kwargs):
        return [kwargs['user']]

    def get(self, request):
        if not User.objects.filter(pk=request.GET.get('user')).exists():
            raise ObjectDoesNotExist()
        return super().get(request, user=request.GET.get('user'))

    def post(self, request):
        if not User.objects.filter(pk=request.POST.get('user')).exists():
            raise ObjectDoesNotExist()
        return super().post(request, user=request.POST.get('user'))


@method_decorator(login_required, name="dispatch")
class ChangeUserKeyObject(ChangeObject):
    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk).user != request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [self.model.objects.get(pk=pk).user.pk]


@method_decorator(login_required, name="dispatch")
class DeleteUserKeyObject(DeleteObject):
    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk).user != request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [self.model.objects.get(pk=pk).user.pk]
