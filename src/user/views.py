import json
from django.shortcuts import render, redirect, reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.db.models import Q, Prefetch
from views import AddObject, ChangeObject, AddUserKeyObject, ChangeUserKeyObject, DeleteUserKeyObject
from student.models import StudentProfile
from staff.models import StaffProfile
from recruiter.models import RecruiterProfile
from resume.models import Skill
from .forms import UserForm, PhoneNumberForm, EmailForm, AddressForm, LinkForm
from .models import User, PhoneNumber, Email, Address, Link
from django.db.models import Count
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
import csv

# Create your views here.


@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = User
    template_name = 'users.html'
    context_object_name = 'users'
    ordering = ['id']
    paginate_by = 50

    role_choices = User.role_choices
    course_choices = StudentProfile.course_choices
    designation_choices = StaffProfile.qualification_choices
    qualification_choices = StaffProfile.qualification_choices
    sorting_options = [('name', 'Name')]
    student_sorting_options = [
        ('registration_year', 'Registration Year'),
        ('course', 'Course'),
        ('year', 'Year'),
        ('cgpa', 'CGPA'),
        ('backlogs', 'Backlogs'),
        ('total_skills', 'Total Skills')
    ]
    staff_sorting_options = [
        ('designation', 'Designation'),
        ('qualification', 'Qualification')
    ]
    recruiter_sorting_options = [
        ('company', 'Company'),
        ('designation', 'Designation')
    ]

    def get_queryset(self):
        query = Q()

        query = self.apply_approval_filter(query)
        query = self.apply_role_filter(query)
        query = self.apply_skill_filters(query)

        role_filter = self.request.GET.get('role-filter')
        if role_filter == 'student':
            query = self.apply_student_filters(query)
        elif role_filter == 'staff':
            query = self.apply_staff_filters(query)
        elif role_filter == 'recruiter':
            query = self.apply_recruiter_filters(query)

        queryset = super().get_queryset()
        queryset = self.apply_prefetch_related(queryset).filter(query).distinct()

        queryset = self.apply_sorting(queryset)
        queryset = self.apply_ordering(queryset)

        return queryset

    def apply_prefetch_related(self, queryset):
        student_profiles = StudentProfile.objects.annotate(skills_count=Count('user__skills'))
        staff_profiles = StaffProfile.objects.all()
        recruiter_profiles = RecruiterProfile.objects.all()

        queryset = queryset.prefetch_related(
            Prefetch('student_profile', queryset=student_profiles),
            Prefetch('staff_profile', queryset=staff_profiles),
            Prefetch('recruiter_profile', queryset=recruiter_profiles)
        )

        return queryset

    def apply_approval_filter(self, query):
        is_approved_filter = self.request.GET.get('is-approved-filter')
        if is_approved_filter == 'False' and (self.request.user.is_superuser or self.request.user.is_coordinator):
            query &= Q(is_approved=False)
        else:
            query &= Q(is_approved=True)
        return query

    def apply_role_filter(self, query):
        role_filter = self.request.GET.get('role-filter')
        if role_filter in [role[0] for role in self.role_choices]:
            query &= Q(role=role_filter)
        return query

    def apply_skill_filters(self, query):
        skill_filters = self.request.GET.get('skill-filters')
        try:
            if skill_filters:
                for and_filter in json.loads(skill_filters):
                    query &= Q(skills__in=and_filter)
        except:
            pass
        return query

    def apply_student_filters(self, query):
        query = self.apply_course_filters(query)
        query = self.apply_year_filters(query)
        query = self.apply_cgpa_filter(query)
        query = self.apply_backlogs_filter(query)
        query = self.apply_registration_year_filters(query)
        query = self.apply_enrollment_status_filter(query)
        return query

    def apply_course_filters(self, query):
        course_filters = self.request.GET.getlist('course-filters')
        course_filters = [course for course in course_filters if course in [
            course[0] for course in self.course_choices]]
        if course_filters:
            query &= Q(student_profile__course__in=course_filters)
        return query

    def apply_year_filters(self, query):
        year_lower_limit = self.request.GET.get('year-lower-limit')
        year_upper_limit = self.request.GET.get('year-upper-limit')
        if year_lower_limit or year_upper_limit:
            students = StudentProfile.objects.all()
            if year_lower_limit.isdigit():
                students = students.filter(year__gte=year_lower_limit)
            if year_upper_limit.isdigit():
                students = students.filter(year__lte=year_upper_limit)
            query &= Q(student_profile__in=students)
        return query

    def apply_cgpa_filter(self, query):
        cgpa_lower_limit = self.request.GET.get('cgpa-lower-limit')
        if cgpa_lower_limit and cgpa_lower_limit.replace('.', '', 1).isdigit():
            query &= Q(student_profile__cgpa__gte=cgpa_lower_limit)
        return query

    def apply_backlogs_filter(self, query):
        backlogs_upper_limit = self.request.GET.get('backlogs-upper-limit')
        if backlogs_upper_limit and backlogs_upper_limit.isdigit():
            query &= Q(student_profile__backlog_count__lte=backlogs_upper_limit)
        return query

    def apply_registration_year_filters(self, query):
        registration_year_upper_limit = self.request.GET.get(
            'registration-year-upper-limit')
        registration_year_lower_limit = self.request.GET.get(
            'registration-year-lower-limit', '2000')
        students = StudentProfile.objects.all()
        if registration_year_lower_limit.isdigit():
            students = students.filter(
                registration_year__gte=registration_year_lower_limit)
        if registration_year_upper_limit and registration_year_upper_limit.isdigit():
            students = students.filter(
                registration_year__lte=registration_year_upper_limit)
        query &= Q(student_profile__in=students)
        return query

    def apply_enrollment_status_filter(self, query):
        enrollment_status = self.request.GET.get('enrollment-status')
        if enrollment_status:
            students = StudentProfile.objects.all()
            if enrollment_status == 'current':
                students = students.filter(is_current=True)
            elif enrollment_status == 'passed_out':
                students = self.apply_pass_out_year_filters(
                    students.filter(passed_out=True))
            elif enrollment_status == 'dropped_out':
                students = self.apply_drop_out_year_filters(
                    students.filter(dropped_out=True))
            query &= Q(student_profile__in=students)
        return query

    def apply_pass_out_year_filters(self, students):
        pass_out_year_lower_limit = self.request.GET.get(
            'pass-out-year-lower-limit')
        pass_out_year_upper_limit = self.request.GET.get(
            'pass-out-year-upper-limit')
        if pass_out_year_lower_limit and pass_out_year_lower_limit.isdigit():
            students = students.filter(
                pass_out_year__gte=pass_out_year_lower_limit)
        if pass_out_year_upper_limit and pass_out_year_upper_limit.isdigit():
            students = students.filter(
                pass_out_year__lte=pass_out_year_upper_limit)
        return students

    def apply_drop_out_year_filters(self, students):
        drop_out_year_lower_limit = self.request.GET.get(
            'drop-out-year-lower-limit')
        drop_out_year_upper_limit = self.request.GET.get(
            'drop-out-year-upper-limit')
        if drop_out_year_lower_limit and drop_out_year_lower_limit.isdigit():
            students = students.filter(
                drop_out_year__gte=drop_out_year_lower_limit)
        if drop_out_year_upper_limit and drop_out_year_upper_limit.isdigit():
            students = students.filter(
                drop_out_year__lte=drop_out_year_upper_limit)
        return students

    def apply_staff_filters(self, query):
        query = self.apply_designation_filters(query)
        query = self.apply_qualification_filters(query)
        return query

    def apply_designation_filters(self, query):
        designation_filters = self.request.GET.getlist('designation-filters')
        designation_filters = [designation for designation in designation_filters if designation in [
            designation[0] for designation in self.designation_choices]]
        if designation_filters:
            query &= Q(staff_profile__designation__in=designation_filters)
        return query

    def apply_qualification_filters(self, query):
        qualification_filters = self.request.GET.getlist(
            'qualification-filters')
        qualification_filters = [qualification for qualification in qualification_filters if qualification in [
            qualification[0] for qualification in self.qualification_choices]]
        if qualification_filters:
            query &= Q(staff_profile__qualification__in=qualification_filters)
        return query

    def apply_recruiter_filters(self, query):
        company_filter = self.request.GET.get('company-filter')
        if company_filter:
            query &= Q(
                recruiter_profile__company_name__icontains=company_filter)
        designation_filter = self.request.GET.get('designation-filter')
        if designation_filter:
            query &= Q(
                recruiter_profile__designation__icontains=designation_filter)
        return query

    def apply_sorting(self, queryset):
        sorting = self.request.GET.get('sorting')
        role_filter = self.request.GET.get('role-filter')
        if sorting:
            if role_filter == 'student':
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
        elif sorting == 'total_skills':
            return queryset.annotate(skills_count=Count('skills')).order_by('skills_count')
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

        context['sorting_options'] = self.sorting_options
        context['roles'] = self.role_choices

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
            self.add_recruiter_context(context)

        context['sorting'] = self.request.GET.get('sorting', 'name')
        context['ordering'] = self.request.GET.get('ordering', 'asc')
        return context

    def add_student_context(self, context):
        context['sorting_options'] += self.student_sorting_options
        context['courses'] = self.course_choices
        context['skills'] = Skill.objects.all()
        self.populate_skills_dict(context)
        context['course_filters'] = self.request.GET.getlist(
            'course-filters', [])
        context['year_lower_limit'] = self.request.GET.get(
            'year-lower-limit', '1')
        context['year_upper_limit'] = self.request.GET.get(
            'year-upper-limit', '')
        context['cgpa_lower_limit'] = self.request.GET.get(
            'cgpa-lower-limit', '0')
        context['backlogs_upper_limit'] = self.request.GET.get(
            'backlogs-upper-limit', '')
        context['registration_year_upper_limit'] = self.request.GET.get(
            'registration-year-upper-limit', '')
        context['registration_year_lower_limit'] = self.request.GET.get(
            'registration-year-lower-limit', '2000')
        context['enrollment_status'] = self.request.GET.get(
            'enrollment-status', '')
        if context['enrollment_status'] == 'passed_out':
            self.add_pass_out_year_context(context)
        elif context['enrollment_status'] == 'dropped_out':
            self.add_drop_out_year_context(context)

    def add_staff_context(self, context):
        context['sorting_options'] += self.staff_sorting_options
        context['designations'] = StaffProfile.designation_choices
        context['qualifications'] = StaffProfile.qualification_choices
        context['designation_filters'] = self.request.GET.getlist(
            'designation-filters', [])
        context['qualification_filters'] = self.request.GET.getlist(
            'qualification-filters', [])

    def add_recruiter_context(self, context):
        context['sorting_options'] += self.recruiter_sorting_options
        context['company_filter'] = self.request.GET.get('company-filter', '')
        context['designation_filter'] = self.request.GET.get(
            'designation-filter', '')

    def populate_skills_dict(self, context):
        skill_filters = json.loads(context['skill_filters'])
        for and_filter in skill_filters:
            if len(and_filter) > 1:
                if '' in and_filter:
                    and_filter.remove('')
                for skill in and_filter:
                    context['skills_dict'][skill] = Skill.objects.get(
                        pk=skill).name
            elif len(and_filter) == 1:
                context['skills_dict'][and_filter[0]
                                       ] = Skill.objects.get(pk=and_filter[0]).name

    def add_pass_out_year_context(self, context):
        context['pass_out_year_lower_limit'] = self.request.GET.get(
            'pass-out-year-lower-limit', '0')
        context['pass_out_year_upper_limit'] = self.request.GET.get(
            'pass-out-year-upper-limit', '')

    def add_drop_out_year_context(self, context):
        context['drop_out_year_lower_limit'] = self.request.GET.get(
            'drop-out-year-lower-limit', '0')
        context['drop_out_year_upper_limit'] = self.request.GET.get(
            'drop-out-year-upper-limit', '')

    def get(self, request):
        if not request.user.is_superuser and not request.user.is_coordinator and request.user.role != 'staff' :
            raise PermissionDenied()
        return super().get(request)


@method_decorator(login_required, name="dispatch")
class UserCSVView(UserListView):
    content_type = 'text/csv'

    def get(self, request):
        if not request.user.is_superuser and not request.user.is_coordinator and request.user.role != 'staff' :
            raise PermissionDenied()

        if self.request.GET.get('role-filter') != 'student':
            return redirect(reverse('user_csv') + '?role-filter=student' + ''.join([f'&{key}={value}' for key, value in self.request.GET.items() if key != 'role-filter']))

        queryset = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)

        row = []
        row.append('Name')
        row.append('Email')
        row.append('Phone number')
        row.append('Address')
        row.append('Registration Year')
        row.append('Registration Number')
        row.append('Roll Number')
        row.append('Course')
        row.append('Year')
        row.append('CGPA')
        row.append('Backlogs')
        row.append('Pass Out Year')
        row.append('Skills')
        row.append('Resume URL')

        writer.writerow(row)

        for user in queryset:
            row = []
            row.append(user.full_name)
            row.append(user.primary_email.email if user.primary_email else '')
            row.append(user.primary_phone_number.__str__()
                       if user.primary_phone_number else '')
            row.append(f'{user.primary_address.address}, {user.primary_address.city}, {user.primary_address.state}, {user.primary_address.country}, {user.primary_address.pincode}' if user.primary_address else '')
            row.append(user.student_profile.registration_year)
            row.append(user.student_profile.registration_number)
            row.append(
                f'{user.student_profile.roll}-{user.student_profile.number}')
            row.append(user.student_profile.course)
            row.append(user.student_profile.year)
            row.append(user.student_profile.cgpa)
            row.append(user.student_profile.backlog_count)
            row.append(user.student_profile.pass_out_year)
            row.append(', '.join([skill.name for skill in user.skills.all()]))
            row.append(request.build_absolute_uri(
                reverse('resume', args=[user.id])))

            writer.writerow(row)

        return response


class SignIn(TemplateView):
    template_name = 'sign_in.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('build_profile', request.user.pk)
        return super().get(request)


@method_decorator(login_required, name="dispatch")
class SignOut(View):
    def get(self, request):
        logout(request)
        next = request.GET.get('next')
        if next:
            return redirect(next)
        return redirect('sign_in')


@method_decorator(login_required, name="dispatch")
class UserPerformAction(View):
    def post(self, request, pk, action):
        if not User.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        user = User.objects.get(pk=pk)

        if action == 'approve':
            if request.user not in user.approve_users:
                raise PermissionDenied()
            user.is_approved = True
            user.save()
        elif action == 'reject':
            if request.user not in user.delete_users:
                raise PermissionDenied()
            user.delete()
        elif action == 'make_superuser':
            if request.user not in user.make_superuser_users:
                raise PermissionDenied()
            user.is_superuser = True
            user.save()
        elif action == 'make_coordinator':
            if request.user not in user.make_coordinator_users:
                raise PermissionDenied()
            user.is_coordinator = True
            user.save()
        elif action == 'remove_coordinator':
            if request.user not in user.remove_coordinator_users:
                raise PermissionDenied()
            user.is_coordinator = False
            user.save()
        elif action == 'make_quoter':
            if request.user not in user.make_quoter_users:
                raise PermissionDenied()
            user.is_quoter = True
            user.save()
        elif action == 'remove_quoter':
            if request.user not in user.remove_quoter_users:
                raise PermissionDenied()
            user.is_quoter = False
            user.save()
        elif action == 'make_cr':
            if request.user not in user.make_cr_users:
                raise PermissionDenied()
            profile = user.student_profile
            profile.is_cr = True
            profile.save()
        elif action == 'remove_cr':
            if request.user not in user.remove_cr_users:
                raise PermissionDenied()
            profile = user.student_profile
            profile.is_cr = False
            profile.save()
        elif action == 'make_hod':
            if request.user not in user.make_hod_users:
                raise PermissionDenied()
            profile = user.staff_profile
            profile.is_hod = True
            profile.save()
        elif action == 'make_tpc_head':
            if request.user not in user.make_tpc_head_users:
                raise PermissionDenied()
            profile = user.staff_profile
            profile.is_tpc_head = True
            profile.save()

        actions = []

        if request.user in user.approve_users:
            actions.append({
                'name': 'Approve',
                'url': reverse('approve_user', args=[pk])
            })
        if request.user in user.delete_users:
            actions.append({
                'name': 'Reject',
                'url': reverse('reject_user', args=[pk])
            })
        if request.user in user.make_superuser_users:
            actions.append({
                'name': 'Make Superuser',
                'url': reverse('make_superuser', args=[pk])
            })
        if request.user in user.make_coordinator_users:
            actions.append({
                'name': 'Make Coordinator',
                'url': reverse('make_coordinator', args=[pk])
            })
        if request.user in user.remove_coordinator_users:
            actions.append({
                'name': 'Remove Coordinator',
                'url': reverse('remove_coordinator', args=[pk])
            })
        if request.user in user.make_quoter_users:
            actions.append({
                'name': 'Make Quoter',
                'url': reverse('make_quoter', args=[pk])
            })
        if request.user in user.remove_quoter_users:
            actions.append({
                'name': 'Remove Quoter',
                'url': reverse('remove_quoter', args=[pk])
            })
        if request.user in user.make_cr_users:
            actions.append({
                'name': 'Make CR',
                'url': reverse('make_cr', args=[pk])
            })
        if request.user in user.remove_cr_users:
            actions.append({
                'name': 'Remove CR',
                'url': reverse('remove_cr', args=[pk])
            })
        if request.user in user.make_hod_users:
            actions.append({
                'name': 'Make HOD',
                'url': reverse('make_hod', args=[pk])
            })
        if request.user in user.make_tpc_head_users:
            actions.append({
                'name': 'Make TPC Head',
                'url': reverse('make_tpc_head', args=[pk])
            })

        return JsonResponse(actions, safe=False)


@method_decorator(login_required, name="dispatch")
class ApproveUser(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'approve')


@method_decorator(login_required, name="dispatch")
class RejectUser(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'reject')


@method_decorator(login_required, name="dispatch")
class MakeSuperUser(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'make_superuser')


@method_decorator(login_required, name="dispatch")
class MakeCoordinator(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'make_coordinator')


@method_decorator(login_required, name="dispatch")
class RemoveCoordinator(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'remove_coordinator')


@method_decorator(login_required, name="dispatch")
class MakeQuoter(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'make_quoter')


@method_decorator(login_required, name="dispatch")
class RemoveQuoter(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'remove_quoter')


@method_decorator(login_required, name="dispatch")
class MakeClassRep(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'make_cr')


@method_decorator(login_required, name="dispatch")
class RemoveClassRep(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'remove_cr')


@method_decorator(login_required, name="dispatch")
class MakeHOD(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'make_hod')


@method_decorator(login_required, name="dispatch")
class MakeTPCHead(UserPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'make_tpc_head')


@method_decorator(login_required, name="dispatch")
class Resume(TemplateView):
    template_name = 'resume.html'

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
        return context


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
            context['phone_number_form'] = PhoneNumberForm(
                initial={'user': user.pk})

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

    def get(self, request):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeletePhoneNumber(DeleteUserKeyObject):
    model = PhoneNumber
    redirect_url_name = 'phone_numbers'


class VerifyEmail(View):
    def get(self, request, pk, code):
        if not Email.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        email = Email.objects.get(pk=pk)
        if email.is_verified:
            return render(request, 'email_verified.html', {'email': email.email})
        if code == 'request' and email.send_verification_email(request):
            return render(request, 'email_verification_sent.html', {'email': email.email})
        if email.verify_code == code:
            email.is_verified = True
            email.save()
            return render(request, 'email_verified.html', {'email': email.email})
        return render(request, 'email_verification_failed.html', {'email': email.email})


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


class SkillAutocomplete(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        li = [(obj.name, f'{obj.pk}')
              for obj in Skill.objects.filter(name__icontains=query)]
        return JsonResponse(li, safe=False)
