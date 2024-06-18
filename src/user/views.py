import json
from django.shortcuts import render, redirect, reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from views import AddObject, ChangeObject, AddUserKeyObject, ChangeUserKeyObject, DeleteUserKeyObject
from student.models import StudentProfile
from staff.models import StaffProfile
from resume.models import Skill
from .forms import UserForm, PhoneNumberForm, EmailForm, AddressForm, LinkForm
from .models import User, PhoneNumber, Email, Address, Link
from django.db.models import Count
from django.contrib.auth import logout

# Create your views here.


@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = User
    template_name = 'users.html'
    context_object_name = 'users'
    ordering = ['id']
    paginate_by = 50

    def get_queryset(self):
        queryset = self.model.objects.all()

        queryset = self.apply_approval_filter(queryset)
        queryset = self.apply_role_filter(queryset)
        queryset = self.apply_skill_filters(queryset)

        role_filter = self.request.GET.get('role-filter')
        if role_filter == 'student':
            queryset = self.apply_student_filters(queryset)
        elif role_filter == 'staff':
            queryset = self.apply_staff_filters(queryset)
        elif role_filter == 'recruiter':
            queryset = self.apply_recruiter_filters(queryset)

        queryset = self.apply_sorting(queryset)
        queryset = self.apply_ordering(queryset)

        return queryset

    def apply_approval_filter(self, queryset):
        is_approved_filter = self.request.GET.get('is-approved-filter')
        if is_approved_filter == 'False' and (self.request.user.is_superuser or self.request.user.is_coordinator):
            return queryset.filter(is_approved=False)
        return queryset.filter(is_approved=True)

    def apply_role_filter(self, queryset):
        role_filter = self.request.GET.get('role-filter')
        if role_filter:
            return queryset.filter(role=role_filter)
        return queryset

    def apply_skill_filters(self, queryset):
        skill_filters = self.request.GET.get('skill-filters')
        if skill_filters:
            for and_filter in json.loads(skill_filters):
                queryset = queryset.filter(skills__in=and_filter).distinct()
        return queryset

    def apply_student_filters(self, queryset):
        queryset = self.apply_course_filters(queryset)
        queryset = self.apply_year_filters(queryset)
        queryset = self.apply_cgpa_filter(queryset)
        queryset = self.apply_backlogs_filter(queryset)
        queryset = self.apply_registration_year_filters(queryset)
        queryset = self.apply_enrollment_status_filter(queryset)
        return queryset

    def apply_course_filters(self, queryset):
        course_filters = self.request.GET.getlist('course-filters')
        if course_filters:
            return queryset.filter(student_profile__course__in=course_filters)
        return queryset

    def apply_year_filters(self, queryset):
        year_lower_limit = self.request.GET.get('year-lower-limit')
        year_upper_limit = self.request.GET.get('year-upper-limit')
        if year_lower_limit or year_upper_limit:
            students = StudentProfile.objects
            if year_lower_limit:
                students = students.filter(year__gte=year_lower_limit)
            if year_upper_limit:
                students = students.filter(year__lte=year_upper_limit)
            return queryset.filter(student_profile__in=students)
        return queryset

    def apply_cgpa_filter(self, queryset):
        cgpa_lower_limit = self.request.GET.get('cgpa-lower-limit')
        if cgpa_lower_limit:
            return queryset.filter(student_profile__cgpa__gte=cgpa_lower_limit)
        return queryset

    def apply_backlogs_filter(self, queryset):
        backlogs_upper_limit = self.request.GET.get('backlogs-upper-limit')
        if backlogs_upper_limit:
            return queryset.filter(student_profile__backlog_count__lte=backlogs_upper_limit)
        return queryset

    def apply_registration_year_filters(self, queryset):
        registration_year_upper_limit = self.request.GET.get('registration-year-upper-limit')
        registration_year_lower_limit = self.request.GET.get('registration-year-lower-limit', 2000)
        if registration_year_upper_limit or registration_year_lower_limit:
            students = StudentProfile.objects
            if registration_year_lower_limit:
                students = students.filter(registration_year__gte=registration_year_lower_limit)
            if registration_year_upper_limit:
                students = students.filter(registration_year__lte=registration_year_upper_limit)
            return queryset.filter(student_profile__in=students)
        return queryset

    def apply_enrollment_status_filter(self, queryset):
        enrollment_status = self.request.GET.get('enrollment-status')
        if enrollment_status:
            students = StudentProfile.objects.all()
            if enrollment_status == 'current':
                students = StudentProfile.objects.filter(is_current=True)
            elif enrollment_status == 'passed_out':
                students = self.apply_pass_out_year_filters(StudentProfile.objects.filter(passed_out=True))
            elif enrollment_status == 'dropped_out':
                students = self.apply_drop_out_year_filters(StudentProfile.objects.filter(dropped_out=True))
            return queryset.filter(student_profile__in=students)
        return queryset

    def apply_pass_out_year_filters(self, students):
        pass_out_year_lower_limit = self.request.GET.get('pass-out-year-lower-limit')
        pass_out_year_upper_limit = self.request.GET.get('pass-out-year-upper-limit')
        if pass_out_year_lower_limit:
            students = students.filter(pass_out_year__gte=pass_out_year_lower_limit)
        if pass_out_year_upper_limit:
            students = students.filter(pass_out_year__lte=pass_out_year_upper_limit)
        return students

    def apply_drop_out_year_filters(self, students):
        drop_out_year_lower_limit = self.request.GET.get('drop-out-year-lower-limit')
        drop_out_year_upper_limit = self.request.GET.get('drop-out-year-upper-limit')
        if drop_out_year_lower_limit:
            students = students.filter(drop_out_year__gte=drop_out_year_lower_limit)
        if drop_out_year_upper_limit:
            students = students.filter(drop_out_year__lte=drop_out_year_upper_limit)
        return students

    def apply_staff_filters(self, queryset):
        queryset = self.apply_designation_filters(queryset)
        queryset = self.apply_qualification_filters(queryset)
        return queryset

    def apply_designation_filters(self, queryset):
        designation_filters = self.request.GET.getlist('designation-filters')
        if designation_filters:
            return queryset.filter(staff_profile__designation__in=designation_filters)
        return queryset

    def apply_qualification_filters(self, queryset):
        qualification_filters = self.request.GET.getlist('qualification-filters')
        if qualification_filters:
            return queryset.filter(staff_profile__qualification__in=qualification_filters)
        return queryset

    def apply_recruiter_filters(self, queryset):
        company_filter = self.request.GET.get('company-filter')
        if company_filter:
            queryset = queryset.filter(recruiter_profile__company_name__icontains=company_filter)
        designation_filter = self.request.GET.get('designation-filter')
        if designation_filter:
            queryset = queryset.filter(recruiter_profile__designation__icontains=designation_filter)
        return queryset

    def apply_sorting(self, queryset):
        sorting = self.request.GET.get('sorting')
        role_filter = self.request.GET.get('role-filter')
        if sorting:
            if sorting == 'total_skills':
                queryset = queryset.annotate(skills_count=Count('skills')).order_by('skills_count')
            elif role_filter == 'student':
                return self.apply_student_sorting(queryset, sorting)
            elif role_filter == 'staff':
                return self.apply_staff_sorting(queryset, sorting)
            elif role_filter == 'recruiter':
                return self.apply_recruiter_sorting(queryset, sorting)
        return queryset.order_by('first_name')

    def apply_student_sorting(self, queryset, sorting):
        if sorting == 'course':
            return queryset.order_by('student_profile__course')
        elif sorting == 'year':
            return queryset.order_by('student_profile__year')
        elif sorting == 'registration_year':
            return queryset.order_by('student_profile__registration_year')
        elif sorting == 'cgpa':
            return queryset.order_by('student_profile__cgpa')
        elif sorting == 'backlogs':
            return queryset.order_by('student_profile__backlog_count')
        return queryset

    def apply_staff_sorting(self, queryset, sorting):
        if sorting == 'designation':
            return queryset.order_by('staff_profile__designation')
        elif sorting == 'qualification':
            return queryset.order_by('staff_profile__qualification')
        return queryset

    def apply_recruiter_sorting(self, queryset, sorting):
        if sorting == 'company':
            return queryset.order_by('recruiter_profile__company_name')
        elif sorting == 'designation':
            return queryset.order_by('recruiter_profile__designation')
        return queryset

    def apply_ordering(self, queryset):
        ordering = self.request.GET.get('ordering')
        if ordering == 'desc':
            return queryset.reverse()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills_dict'] = {}
        context['roles'] = User.role_choices
        context['role_filter'] = self.request.GET.get('role-filter', '')
        context['skill_filters'] = self.request.GET.get('skill-filters', '[]')
        context['is_approved_filter'] = True
        is_approved_filter = self.request.GET.get('is-approved-filter')
        if is_approved_filter == 'False' and (self.request.user.is_superuser or self.request.user.is_coordinator):
            context['is_approved_filter'] = False

        if context['role_filter'] == 'student':
            self.add_student_context(context)
        elif context['role_filter'] == 'staff':
            self.add_staff_context(context)
        elif context['role_filter'] == 'recruiter':
            context['company_filter'] = self.request.GET.get('company-filter', '')
            context['designation_filter'] = self.request.GET.get('designation-filter', '')

        context['sorting'] = self.request.GET.get('sorting', 'name')
        context['ordering'] = self.request.GET.get('ordering', 'asc')
        return context

    def add_student_context(self, context):
        context['courses'] = StudentProfile.course_choices
        context['skills'] = Skill.objects.all()
        self.populate_skills_dict(context)
        context['course_filters'] = self.request.GET.getlist('course-filters', [])
        context['year_lower_limit'] = self.request.GET.get('year-lower-limit', '1')
        context['year_upper_limit'] = self.request.GET.get('year-upper-limit', '')
        context['cgpa_lower_limit'] = self.request.GET.get('cgpa-lower-limit', '0')
        context['backlogs_upper_limit'] = self.request.GET.get('backlogs-upper-limit', '')
        context['registration_year_upper_limit'] = self.request.GET.get('registration-year-upper-limit', '')
        context['registration_year_lower_limit'] = self.request.GET.get('registration-year-lower-limit', '2000')
        context['enrollment_status'] = self.request.GET.get('enrollment-status', '')
        if context['enrollment_status'] == 'passed_out':
            self.add_pass_out_year_context(context)
        elif context['enrollment_status'] == 'dropped_out':
            self.add_drop_out_year_context(context)

    def add_staff_context(self, context):
        context['designations'] = StaffProfile.designation_choices
        context['qualifications'] = StaffProfile.qualification_choices
        context['designation_filters'] = self.request.GET.getlist('designation-filters', [])
        context['qualification_filters'] = self.request.GET.getlist('qualification-filters', [])

    def populate_skills_dict(self, context):
        skill_filters = json.loads(context['skill_filters'])
        for and_filter in skill_filters:
            if len(and_filter) > 1:
                if '' in and_filter:
                    and_filter.remove('')
                for skill in and_filter:
                    context['skills_dict'][skill] = Skill.objects.get(pk=skill).name
            elif len(and_filter) == 1:
                context['skills_dict'][and_filter[0]] = Skill.objects.get(pk=and_filter[0]).name

    def add_pass_out_year_context(self, context):
        context['pass_out_year_lower_limit'] = self.request.GET.get('pass-out-year-lower-limit', '0')
        context['pass_out_year_upper_limit'] = self.request.GET.get('pass-out-year-upper-limit', '')

    def add_drop_out_year_context(self, context):
        context['drop_out_year_lower_limit'] = self.request.GET.get('drop-out-year-lower-limit', '0')
        context['drop_out_year_upper_limit'] = self.request.GET.get('drop-out-year-upper-limit', '')


class SignIn(TemplateView):
    template_name = 'sign_in.html'


@method_decorator(login_required, name="dispatch")
class SignOut(View):
    def get(self, request):
        logout(request)
        next = request.GET.get('next')
        if next:
            return redirect(next)
        return redirect('sign_in')


@method_decorator(login_required, name="dispatch")
class ApproveUser(View):
    def post(self, request, pk):
        if not User.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=pk)
        if request.user not in user.approve_users:
            raise PermissionDenied()
        user.is_approved = True
        user.save()
        return redirect(reverse('user_list') + f'?is-approved-filter=False')


@method_decorator(login_required, name="dispatch")
class RejectUser(View):
    def post(self, request, pk):
        if not User.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=pk)
        if request.user not in user.delete_users:
            raise PermissionDenied()
        user.delete()
        return redirect(reverse('user_list') + f'?is-approved-filter=True')


@method_decorator(login_required, name="dispatch")
class MakeCoordinator(View):
    def post(self, request, pk):
        if not User.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=pk)
        if request.user not in user.make_coordinator_users:
            raise PermissionDenied()
        user.is_coordinator = True
        user.save()
        return redirect(reverse('user_list'))


@method_decorator(login_required, name="dispatch")
class RemoveCoordinator(View):
    def post(self, request, pk):
        if not User.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=pk)
        if request.user not in user.remove_coordinator_users:
            raise PermissionDenied()
        user.is_coordinator = False
        user.save()
        return redirect(reverse('user_list'))


@method_decorator(login_required, name="dispatch")
class BuildProfile(TemplateView):
    template_name = 'build_profile.html'

    def get(self, request, pk):
        if not User.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=pk)
        if request.user not in user.edit_users:
            raise PermissionDenied()
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])

        context = super().get_context_data(**kwargs)
        context['user'] = user
        if hasattr(user, 'student_profile'):
            context['profile'] = user.student_profile
        elif hasattr(user, 'staff_profile'):
            context['profile'] = user.staff_profile
        elif hasattr(user, 'recruiter_profile'):
            context['profile'] = user.recruiter_profile
        else:
            raise PermissionDenied()
        return context


@method_decorator(login_required, name="dispatch")
class SelfUser(View):
    def get(self, request):
        return redirect(to=f'{request.user.pk}/')


@method_decorator(login_required, name="dispatch")
class PersonalContactInfo(TemplateView):
    template_name = 'personal_contact_info.html'

    def get(self, request, pk):
        if not User.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=pk)
        if request.user not in user.view_users:
            raise PermissionDenied()
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])

        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['phone_numbers'] = PhoneNumber.objects.filter(user=user)
        context['emails'] = Email.objects.filter(user=user)
        context['addresses'] = [(address, AddressForm(instance=address))
                                for address in Address.objects.filter(user=user)]
        context['links'] = Link.objects.filter(user=user)

        if PhoneNumber.objects.get_create_permission(user, self.request.user):
            context['phone_number_form'] = PhoneNumberForm(initial={'user': user.pk})
        
        if Email.objects.get_create_permission(user, self.request.user):
            context['email_form'] = EmailForm(initial={'user': user.pk})

        if Address.objects.get_create_permission(user, self.request.user):
            context['address_form'] = AddressForm(initial={'user': user.pk})
        
        if Link.objects.get_create_permission(user, self.request.user):
            context['link_form'] = LinkForm(initial={'user': user.pk})
        
        if self.request.user in user.edit_users:
            context['change_user_form'] = UserForm(instance=user)

        return context


@method_decorator(login_required, name="dispatch")
class ChangeUser(ChangeObject):
    model = User
    form = UserForm
    redirect_url_name = 'personal_contact_info'
    redirect_url_params = '#personal-info'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [pk]

    def check_permission(self, request, pk, *args, **kwargs):
        if self.model.objects.get(pk=pk) != request.user and not request.user.is_superuser:
            return False
        return super().check_permission(request, pk, *args, **kwargs)

    def get(self, request, pk, *args, **kwargs):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class SetPrimaryPhoneNumber(ChangeUser):
    model = User
    redirect_url_name = 'phone_numbers'

    def get(self, request, pk, phone_number):
        raise BadRequest()

    def post(self, request, pk, phone_number):
        if not self.model.objects.filter(pk=pk).exists() or not PhoneNumber.objects.filter(pk=phone_number).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, pk):
            raise PermissionDenied()
        obj = self.model.objects.get(pk=pk)
        obj.primary_phone_number = PhoneNumber.objects.get(pk=phone_number)
        obj.save()
        return redirect(self.get_redirect_url(request, pk))


@method_decorator(login_required, name="dispatch")
class SetPrimaryEmail(ChangeUser):
    redirect_url_name = 'emails'

    def get(self, request, user, pk, email):
        raise BadRequest()

    def post(self, request, pk, email):
        if not self.model.objects.filter(pk=pk).exists() or not Email.objects.filter(pk=email).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, pk):
            raise PermissionDenied()
        obj = self.model.objects.get(pk=pk)
        obj.primary_email = Email.objects.get(pk=email)
        obj.save()
        return redirect(self.get_redirect_url(request, pk))


@method_decorator(login_required, name="dispatch")
class SetPrimaryAddress(ChangeUser):
    redirect_url_name = 'addresses'

    def get(self, request, user, pk, address):
        raise BadRequest()

    def post(self, request, pk, address):
        if not self.model.objects.filter(pk=pk).exists() or not Address.objects.filter(pk=address).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, pk):
            raise PermissionDenied()
        obj = self.model.objects.get(pk=pk)
        obj.primary_address = Address.objects.get(pk=address)
        obj.save()
        return redirect(self.get_redirect_url(request, pk))


@method_decorator(login_required, name="dispatch")
class AddPhoneNumber(AddUserKeyObject):
    model = PhoneNumber
    form = PhoneNumberForm
    redirect_url_name = 'phone_numbers'

    def get(self, request, user):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeletePhoneNumber(DeleteUserKeyObject):
    model = PhoneNumber
    redirect_url_name = 'phone_numbers'


@method_decorator(login_required, name="dispatch")
class AddEmail(AddUserKeyObject):
    model = Email
    form = EmailForm
    redirect_url_name = 'emails'

    def get(self, request, user):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteEmail(DeleteUserKeyObject):
    model = Email
    redirect_url_name = 'emails'


@method_decorator(login_required, name="dispatch")
class AddAddress(AddUserKeyObject):
    model = Address
    form = AddressForm
    redirect_url_name = 'addresses'

    def get(self, request, user):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeAddress(ChangeUserKeyObject):
    model = Address
    form = AddressForm
    redirect_url_name = 'addresses'

    def get(self, request, user):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteAddress(DeleteUserKeyObject):
    model = Address
    redirect_url_name = 'addresses'


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
