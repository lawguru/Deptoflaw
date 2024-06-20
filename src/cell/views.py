from django.db.models import Count
from django.shortcuts import render, redirect, reverse
from staff.models import StaffProfile
from settings.models import Setting
from user.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from views import AddUserKeyObject, ChangeUserKeyObject, AddObject, DeleteUserKeyObject
from django.views.generic.base import View, TemplateView
from django.views.generic.list import ListView
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from student.models import StudentProfile
from .forms import *
from .models import Notice, Quote
import json
from itertools import chain

# Create your views here.


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Quote.objects.exists():
            random_quote = Quote.objects.order_by('?').first()
            context['quote'] = random_quote

        message_from_hod, created = Setting.objects.get_or_create(
            key='message_from_hod')
        if message_from_hod.value == None:
            message_from_hod.value = 'Welcome to the Department of Computer Science and Engineering at Assam University. The Department of Computer Science and Engineering is one of the premier departments in the University. The Department offers B.Tech, M.Tech and Ph.D. programs in Computer Science and Engineering. The Department has a team of highly qualified, experienced and dedicated faculty members. The Department has state-of-the-art laboratories and infrastructure. The Department has a very active Training and Placement Cell (TPC) which takes care of the training and placement of the students. The Department has a very active student community which organizes various technical and cultural events throughout the year.'
            message_from_hod.save()

        message_from_tpc_head, created = Setting.objects.get_or_create(
            key='message_from_tpc_head')
        if message_from_tpc_head.value == None:
            message_from_tpc_head.value = 'Welcome to the Training and Placement Cell (TPC) of the Department of Computer Science'
            message_from_tpc_head.save()
        
        current_academic_half, created = Setting.objects.get_or_create(
            key='current_academic_half')
        if current_academic_half.value == None:
            current_academic_half.value = 'odd'
            current_academic_half.save()

        context['message_from_hod'] = message_from_hod.value
        context['message_from_tpc_head'] = message_from_tpc_head.value
        context['hod'] = StaffProfile.objects.get(
            is_hod=True) if StaffProfile.objects.filter(is_hod=True).exists() else None
        context['tpc_head'] = StaffProfile.objects.get(
            is_tpc_head=True) if StaffProfile.objects.filter(is_tpc_head=True).exists() else None
        context['coordinators'] = User.objects.filter(
            groups__name='coordinators') if User.objects.filter(groups__name='coordinators').exists() else None
        return context


class Contact(View):
    def get(self, request):
        return render(request, 'contact.html', {'form': ContactUsForm})

    def post(self, request):
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {'form': form, 'success': 'Your message has been sent successfully!'})
        return render(request, 'contact.html', {'form': form, 'error': 'Could not send your message. Please try again.'})


@method_decorator(login_required, name="dispatch")
class Dashboard(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if RecruitmentPost.objects.get_create_permission(user, user):
            context['add_post_form'] = AddRecruitmentPostForm(initial={'user': user})

        if Notice.objects.get_create_permission(user):
            context['add_notice_form'] = NoticeForm()

        if user.role == 'student':
            self.add_student_context(context, user)

        if user.is_superuser or user.is_coordinator or user.role == 'recruiter':
            self.add_recruiter_context(context, user)

        if user.is_superuser or user.is_coordinator:
            self.add_admin_context(context)

        context.update(self.add_general_context())

        return context

    def add_student_context(self, context, user):
        user_applications = RecruitmentApplication.objects.filter(user=user)
        context.update({
            'user_application_count': user_applications.count(),
            'pending_user_application_count': user_applications.filter(status='P').count(),
            'selected_user_application_count': user_applications.filter(status='S').count(),
            'rejected_user_application_count': user_applications.filter(status='R').count(),
            'shortlisted_user_application_count': user_applications.filter(status='I').count(),
        })

    def add_recruiter_context(self, context, user):
        user_posts = RecruitmentPost.objects.filter(user=user)
        active_user_posts = user_posts.filter(
            apply_by__gte=datetime.today().date())
        user_applicants = RecruitmentApplication.objects.filter(
            recruitment_post__in=user_posts)
        active_user_applicants = user_applicants.filter(
            recruitment_post__in=active_user_posts)

        context.update({
            'user_post_count': user_posts.count(),
            'user_active_post_count': active_user_posts.count(),
            'user_applicant_count': user_applicants.count(),
            'pending_user_applicant_count': user_applicants.filter(status='P').count(),
            'selected_user_applicant_count': user_applicants.filter(status='S').count(),
            'rejected_user_applicant_count': user_applicants.filter(status='R').count(),
            'shortlisted_user_applicant_count': user_applicants.filter(status='I').count(),
            'user_active_applicant_count': active_user_applicants.count(),
            'pending_user_active_applicant_count': active_user_applicants.filter(status='P').count(),
            'selected_user_active_applicant_count': active_user_applicants.filter(status='S').count(),
            'rejected_user_active_applicant_count': active_user_applicants.filter(status='R').count(),
            'shortlisted_user_active_applicant_count': active_user_applicants.filter(status='I').count(),
        })

    def add_admin_context(self, context):
        unapproved_users = User.objects.filter(is_approved=False)
        students = StudentProfile.objects.filter(user__is_approved=True)
        applicants = RecruitmentApplication.objects.all()
        active_applicants = RecruitmentApplication.objects.filter(
            recruitment_post__in=RecruitmentPost.objects.filter(
                apply_by__gte=datetime.today().date())
        )

        context.update({
            'unapproved_user_count': unapproved_users.count(),
            'unapproved_student_count': unapproved_users.filter(role='student').count(),
            'unapproved_staff_count': unapproved_users.filter(role='staff').count(),
            'unapproved_recruiter_count': unapproved_users.filter(role='recruiter').count(),
            'student_count': students.count(),
            'current_student_count': students.filter(is_current=True).count(),
            'alumni_count': students.filter(passed_out=True).count(),
            'applicant_count': applicants.count(),
            'pending_applicant_count': applicants.filter(status='P').count(),
            'selected_applicant_count': applicants.filter(status='S').count(),
            'rejected_applicant_count': applicants.filter(status='R').count(),
            'shortlisted_applicant_count': applicants.filter(status='I').count(),
            'active_applicant_count': active_applicants.count(),
            'pending_active_applicant_count': active_applicants.filter(status='P').count(),
            'selected_active_applicant_count': active_applicants.filter(status='S').count(),
            'rejected_active_applicant_count': active_applicants.filter(status='R').count(),
            'shortlisted_active_applicant_count': active_applicants.filter(status='I').count(),
        })

    def add_general_context(self):
        active_posts = RecruitmentPost.objects.filter(
            apply_by__gte=datetime.today().date())
        user_notices = list(chain(
            Notice.objects.filter(user=self.request.user),
            RecruitmentPostUpdate.objects.filter(user=self.request.user)
        ))
        all_notices = list(chain(
            Notice.objects.all(),
            RecruitmentPostUpdate.objects.all()
        ))

        return {
            'post_count': RecruitmentPost.objects.count(),
            'active_post_count': active_posts.count(),
            'user_notice_count': len(user_notices),
            'total_notice_count': len(all_notices),
        }


class ListNotice(ListView):
    model = Notice
    template_name = 'notices.html'
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset2 = RecruitmentPostUpdate.objects.all()
        queryset2 = self.apply_recruitment_post_filters(queryset2)
        queryset2 = self.apply_recruitment_post_filter(queryset2)

        queryset = self.apply_user_filter(queryset)
        queryset2 = self.apply_user_filter(queryset2)

        sorting = self.request.GET.get('sorting')
        if sorting:
            if sorting == 'date':
                queryset = queryset.order_by('date')
                queryset2 = queryset2.order_by('date')
            elif sorting == 'user':
                queryset = queryset.order_by('user')
                queryset2 = queryset2.order_by('user')
            elif sorting == 'title':
                queryset = queryset.order_by('title')
                queryset2 = queryset2.order_by('title')
            elif type_filter == 'post-update' and sorting == 'recruitment_post_user':
                queryset = queryset.order_by('recruitment_post__user')
                queryset2 = queryset2.order_by('recruitment_post__user')

        ordering = self.request.GET.get('ordering')
        if ordering:
            if ordering == 'desc':
                queryset = queryset.reverse()
                queryset2 = queryset2.reverse()

        type_filter = self.request.GET.get('type-filter')
        if type_filter == 'notice':
            return queryset
        if type_filter == 'post-update':
            return queryset2
        
        queryset = [(notice, NoticeForm(instance=notice)) for notice in queryset]
        queryset2 = [(update, None) for update in queryset2]

        return list(chain(queryset, queryset2))

    def apply_user_filter(self, queryset):
        user_filter = self.request.GET.get('user-filter')
        if user_filter == 'me':
            return queryset.filter(user=self.request.user)
        return queryset

    def apply_recruitment_post_filters(self, queryset):
        recruitment_post_filters = self.request.GET.getlist(
            'recruitment-post-filters')
        if recruitment_post_filters:
            return queryset.filter(recruitment_post__id__in=recruitment_post_filters)
        return queryset

    def apply_recruitment_post_filter(self, queryset):
        recruitment_post_filter = self.request.GET.get(
            'recruitment-post-filter')
        if recruitment_post_filter == 'by-me':
            return queryset.filter(recruitment_post__user=self.request.user)
        elif recruitment_post_filter == 'applied-by-me':
            return queryset.filter(recruitment_post__applications__user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_filter'] = self.request.GET.get('user-filter') or ''
        context['type_filter'] = self.request.GET.get('type-filter') or ''
        if context['type_filter'] == 'post-update':
            context['recruitment_post_filters'] = self.request.GET.getlist(
                'recruitment-post-filters') or []
            context['recruitment_post_filter'] = self.request.GET.get(
                'recruitment-post-filter') or ''
        context['sorting'] = self.request.GET.get('sorting') or 'date'
        context['ordering'] = self.request.GET.get('ordering') or 'asc'
        return context


class ListRecruitmentPost(ListView):
    model = RecruitmentPost
    template_name = 'recruitment_posts.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.apply_company_filter(queryset)
        queryset = self.apply_location_filter(queryset)
        queryset = self.apply_job_type_filters(queryset)
        queryset = self.apply_workplace_type_filters(queryset)
        queryset = self.apply_salary_filter(queryset)
        queryset = self.apply_experience_filter(queryset)
        queryset = self.apply_start_date_filter(queryset)
        queryset = self.apply_skill_filter(queryset)
        queryset = self.apply_active_filter(queryset)
        queryset = self.apply_applications_filter(queryset)
        queryset = self.apply_post_filter(queryset)

        sorting = self.request.GET.get('sorting')
        if sorting:
            queryset = queryset.order_by(sorting)

        ordering = self.request.GET.get('ordering')
        if ordering == 'desc':
            queryset = queryset.reverse()
        return queryset

    def apply_skill_filter(self, queryset):
        skill_filter = self.request.GET.getlist('skill-filter')
        if skill_filter:
            queryset = queryset.filter(skills__name__in=skill_filter)
        return queryset

    def apply_company_filter(self, queryset):
        company_filter = self.request.GET.get('company-filter')
        if company_filter:
            queryset = queryset.filter(company__icontains=company_filter)
        return queryset

    def apply_location_filter(self, queryset):
        location_filter = self.request.GET.get('location-filter')
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)
        return queryset

    def apply_job_type_filters(self, queryset):
        job_type_filters = self.request.GET.getlist('job-type-filters')
        if job_type_filters:
            queryset = queryset.filter(job_type__in=job_type_filters)
        return queryset

    def apply_workplace_type_filters(self, queryset):
        workplace_type_filters = self.request.GET.getlist(
            'workplace-type-filters')
        if workplace_type_filters:
            queryset = queryset.filter(
                workplace_type__in=workplace_type_filters)
        return queryset

    def apply_salary_filter(self, queryset):
        expected_salary = self.request.GET.get('expected-salary', 0)
        if expected_salary:
            queryset = queryset.filter(minimum_salary__gte=expected_salary)
        return queryset

    def apply_experience_filter(self, queryset):
        experience_filter_lower_limit = self.request.GET.get(
            'experience-filter-lower-limit')
        experience_filter_upper_limit = self.request.GET.get(
            'experience-filter-upper-limit')
        if experience_filter_lower_limit:
            queryset = queryset.filter(
                experience_duration__gte=experience_filter_lower_limit)
        if experience_filter_upper_limit:
            queryset = queryset.filter(
                experience_duration__lte=experience_filter_upper_limit)
        return queryset

    def apply_start_date_filter(self, queryset):
        start_date_type_filter = self.request.GET.get('start-date-type-filter')
        if start_date_type_filter:
            queryset = queryset.filter(start_date_type=start_date_type_filter)
            if start_date_type_filter == 'S':
                start_date_filter_lower_limit = self.request.GET.get(
                    'start-date-filter-lower-limit')
                start_date_filter_upper_limit = self.request.GET.get(
                    'start-date-filter-upper-limit')
                if start_date_filter_lower_limit:
                    queryset = queryset.filter(
                        start_date__gte=start_date_filter_lower_limit)
                if start_date_filter_upper_limit:
                    queryset = queryset.filter(
                        start_date__lte=start_date_filter_upper_limit)
        return queryset

    def apply_post_filter(self, queryset):
        post_filter = self.request.GET.get('post-filter')
        if post_filter == 'by-me':
            queryset = queryset.filter(user=self.request.user)
        elif post_filter == 'applied-by-me':
            queryset = queryset.filter(
                applications__user=self.request.user).distinct()
        return queryset

    def apply_active_filter(self, queryset):
        is_active_filter = self.request.GET.get('is-active-filter')
        if is_active_filter is not None:
            if is_active_filter.lower() != 'false':
                queryset = queryset.filter(
                    apply_by__gte=datetime.today().date())
        return queryset

    def apply_applications_filter(self, queryset):
        if self.request.user.is_authenticated and self.request.user.role == 'recruiter' and not self.request.GET.get('post-filter') == 'applied-by-me':
            return queryset
        elif self.request.user.is_authenticated and not self.request.user.is_superuser and not self.request.user.is_coordinator:
            return queryset

        applications_filter_lower_limit = self.request.GET.get(
            'applications-filter-lower-limit', 0)
        queryset = queryset.annotate(application_count=Count('applications')).filter(
            application_count__gte=applications_filter_lower_limit)

        applications_status_filters = self.request.GET.getlist(
            'applications-status-filters')
        if applications_status_filters:
            queryset = queryset.filter(
                applications__status__in=applications_status_filters).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_filter'] = self.request.GET.get('company-filter', '')
        context['location_filter'] = self.request.GET.get(
            'location-filter', '')
        context['job_type_filters'] = self.request.GET.getlist(
            'job-type-filters', [])
        context['job_type_choices'] = RecruitmentPost.job_type_choices
        context['workplace_type_filters'] = self.request.GET.getlist(
            'workplace-type-filters', [])
        context['workplace_type_choices'] = RecruitmentPost.workplace_type_choices
        context['expected_salary'] = self.request.GET.get(
            'expected-salary', 0)
        context['experience_filter_lower_limit'] = self.request.GET.get(
            'experience-filter-lower-limit', 0)
        context['experience_filter_upper_limit'] = self.request.GET.get(
            'experience-filter-upper-limit', '')
        context['start_date_type_filter'] = self.request.GET.get(
            'start-date-type-filter', '')
        if context['start_date_type_filter'] == 'S':
            context['start_date_filter_lower_limit'] = self.request.GET.get(
                'start-date-filter-lower-limit', '')
            context['start_date_filter_upper_limit'] = self.request.GET.get(
                'start-date-filter-upper-limit', '')
        context['start_date_type_choices'] = RecruitmentPost.start_date_type_choices
        context['skill_filter'] = self.request.GET.getlist('skill-filter')
        context['is_active_filter'] = self.request.GET.get(
            'is-active-filter', 'any')
        if (self.request.user.is_authenticated and self.request.user.role == 'recruiter' and self.request.GET.get('post-filter') == 'applied-by-me') or (self.request.user.is_authenticated and self.request.user.is_superuser and self.request.user.is_coordinator):
            context['applications_filter_lower_limit'] = self.request.GET.get(
                'applications-filter-lower-limit', 0)
            context['applications_status_filters'] = self.request.GET.getlist(
                'applications-status-filters', [])
        context['post_filter'] = self.request.GET.get('post-filter', '')
        if self.request.user.is_authenticated and self.request.user.role == 'student':
            context['applied_posts'] = RecruitmentPost.objects.filter(
                applications__user=self.request.user).distinct()

        context['sorting_options'] = [
            ('apply_by', 'Apply By date'),
            ('start_date', 'Start date'),
            ('experience_duration', 'Experience duration'),
        ]
        context['sorting'] = self.request.GET.get('sorting', 'apply_by')
        context['ordering'] = self.request.GET.get('ordering', 'asc')

        return context


@method_decorator(login_required, name="dispatch")
class ViewRecruitmentPost(TemplateView):
    template_name = 'recruitment_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = RecruitmentPost.objects.get(pk=kwargs['pk'])
        context['post'] = post
        context['updates'] = [(update, RecruitmentPostUpdateForm(
            instance=update)) for update in post.updates.all()]

        if RecruitmentPostUpdate.objects.get_create_permission(post, self.request.user):
            context['update_form'] = RecruitmentPostUpdateForm()

        if self.request.user in post.add_skill_users:
            context['skill_form'] = SkillForm()

        if self.request.user in post.select_application_users or \
                self.request.user in post.reject_application_users or \
                self.request.user in post.shortlist_application_users:
            context['pending_applications_count'] = post.applications.filter(
                status='P').count()

        if self.request.user in post.pending_application_users:
            context['rejected_applications_count'] = post.applications.filter(
                status='R').count()
            context['selected_applications_count'] = post.applications.filter(
                status='S').count()
            context['interview_applications_count'] = post.applications.filter(
                status='I').count()

        if self.request.user in post.edit_users:
            context['edit_form'] = RecruiterChangeRecruitmentPostForm(
                instance=post)
            if self.request.user.is_superuser or self.request.user.is_coordinator:
                context['edit_form'] = TPCChangeRecruitmentPostForm(
                    instance=post)


        if RecruitmentApplication.objects.get_create_permission(post, self.request.user):
            context['apply_form'] = RecruitmentApplicationForm()

        if post.applications.filter(user=self.request.user).exists():
            context['application'] = post.applications.get(
                user=self.request.user)
        return context

    def get(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().get(request, pk=pk)


@method_decorator(login_required, name="dispatch")
class RecruitmentApplications(ListView):
    model = RecruitmentApplication
    paginate_by = 100
    template_name = 'recruitment_applications.html'

    def get_queryset(self):
        queryset = self.model.objects.filter(
            recruitment_post=self.kwargs['pk'])
        skill_filters = self.request.GET.get('skill-filters')
        course_filters = self.request.GET.getlist('course-filters')
        year_lower_limit = self.request.GET.get('year-lower-limit')
        year_upper_limit = self.request.GET.get('year-upper-limit')
        cgpa_lower_limit = self.request.GET.get('cgpa-lower-limit')
        backlogs_upper_limit = self.request.GET.get('backlogs-upper-limit')
        status_filters = self.request.GET.getlist('status-filters')
        sorting = self.request.GET.get('sorting')
        ordering = self.request.GET.get('ordering')

        if skill_filters:
            for and_filter in json.loads(skill_filters):
                queryset = queryset.filter(
                    user__skills__in=and_filter).distinct()

        if course_filters:
            queryset = queryset.filter(
                student_profile__course__in=course_filters)

        if year_lower_limit or year_upper_limit:
            students = StudentProfile.objects

            if year_lower_limit:
                students = students.filter(year__gte=year_lower_limit)

            if year_upper_limit:
                students = students.filter(year__lte=year_upper_limit)

            queryset = queryset.filter(
                user__student_profile__in=students)

        if cgpa_lower_limit:
            queryset = queryset.filter(
                user__student_profile__cgpa__gte=cgpa_lower_limit)

        if backlogs_upper_limit:
            queryset = queryset.filter(
                user__student_profile__backlog_count__lte=backlogs_upper_limit)

        if status_filters:
            queryset = queryset.filter(status__in=status_filters)

        if sorting:
            if sorting == 'name':
                queryset = queryset.order_by(f'user__first_name')
            elif sorting == 'course':
                queryset = queryset.order_by(f'user__student_profile__course')
            elif sorting == 'year':
                queryset = queryset.order_by(f'user__student_profile__year')
            elif sorting == 'cgpa':
                queryset = queryset.order_by(f'user__student_profile__cgpa')
            elif sorting == 'backlogs':
                queryset = queryset.order_by(
                    f'user__student_profile__backlog_count')
            elif sorting == 'total_skills':
                queryset = queryset.annotate(skills_count=models.Count(
                    'user__skills')).order_by('skills_count')
            elif sorting == 'skill_matches':
                queryset = queryset.order_by(f'skill_matches')
            elif sorting == 'other_skills_count':
                queryset = queryset.order_by(f'other_skills_count')
        else:
            queryset = queryset.order_by(f'applied_on')

        if ordering:
            if ordering == 'desc':
                return queryset.reverse()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = RecruitmentPost.objects.get(pk=self.kwargs['pk'])
        skill_filters = self.request.GET.get('skill-filters')
        course_filters = self.request.GET.getlist('course-filters')
        year_lower_limit = self.request.GET.get('year-lower-limit')
        year_upper_limit = self.request.GET.get('year-upper-limit')
        cgpa_lower_limit = self.request.GET.get('cgpa-lower-limit')
        backlogs_upper_limit = self.request.GET.get('backlogs-upper-limit')
        status_filters = self.request.GET.getlist('status-filters')
        sorting = self.request.GET.get('sorting')
        ordering = self.request.GET.get('ordering')

        context['skills_dict'] = {}
        context['skill_filters'] = '[]'
        context['year_lower_limit'] = '1'
        context['year_upper_limit'] = ''
        context['cgpa_lower_limit'] = '0'
        context['backlogs_upper_limit'] = ''
        context['status_filters'] = []
        context['sorting'] = 'applied_on'
        context['ordering'] = 'asc'
        context['course_filters'] = '[]'

        if skill_filters:
            context['skill_filters'] = skill_filters
            for and_filter in json.loads(skill_filters):
                if len(and_filter) > 1:
                    if '' in and_filter:
                        and_filter.remove('')
                    for skill in and_filter:
                        context['skills_dict'][skill] = Skill.objects.get(
                            pk=skill).name
                elif len(and_filter) == 1:
                    context['skills_dict'][and_filter[0]
                                           ] = Skill.objects.get(pk=and_filter[0]).name
        if course_filters:
            context['course_filters'] = course_filters
        if year_lower_limit:
            context['year_lower_limit'] = year_lower_limit
        if year_upper_limit:
            context['year_upper_limit'] = year_upper_limit
        if cgpa_lower_limit:
            context['cgpa_lower_limit'] = cgpa_lower_limit
        if backlogs_upper_limit:
            context['backlogs_upper_limit'] = backlogs_upper_limit
        if status_filters:
            context['status_filters'] = status_filters
        if sorting:
            context['sorting'] = sorting
        if ordering:
            context['ordering'] = ordering
        return context


@method_decorator(login_required, name="dispatch")
class AddNotice(View):
    def post(self, request):
        if not Notice.objects.get_create_permission(request.user):
            raise PermissionDenied()
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = Notice.objects.create(
                title=form.cleaned_data['title'], description=form.cleaned_data['description'], user=request.user)
            return redirect(reverse('notices') + f'#notice-{notice.id}')
        else:
            raise BadRequest()


@method_decorator(login_required, name="dispatch")
class ChangeNotice(View):
    def post(self, request, pk):
        if not Notice.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        notice = Notice.objects.get(pk=pk)
        if request.user not in notice.edit_users:
            raise PermissionDenied()
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice.title = form.cleaned_data['title']
            notice.description = form.cleaned_data['description']
            notice.save()
            return redirect(reverse('notices') + f'#notice-{notice.id}')
        else:
            raise BadRequest()


@method_decorator(login_required, name="dispatch")
class AddRecruitmentPost(AddUserKeyObject):
    model = RecruitmentPost
    form = AddRecruitmentPostForm
    redirect_url_name = 'recruitment_posts'

    def get_redirect_url_args(self, request, *args, **kwargs):
        return []

    def get_redirect_url_params(self, request, *args, **kwargs):
        return f'?user-filter={kwargs["user"]}'


@method_decorator(login_required, name="dispatch")
class RecruiterChangeRecruitmentPost(ChangeUserKeyObject):
    model = RecruitmentPost
    form = RecruiterChangeRecruitmentPostForm
    redirect_url_name = 'view_recruitment_post'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [pk]

    def get(self, request, pk):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class TPCChangeRecruitmentPost(RecruiterChangeRecruitmentPost):
    form = TPCChangeRecruitmentPostForm


@method_decorator(login_required, name="dispatch")
class ChangeRecruitmentPost(TPCChangeRecruitmentPost):
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_superuser or request.user.is_coordinator:
            self.form = TPCChangeRecruitmentPost.form
            return TPCChangeRecruitmentPost.post(self, request, pk, *args, **kwargs)
        self.form = RecruiterChangeRecruitmentPost.form
        return RecruiterChangeRecruitmentPost.post(self, request, pk, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class AddRecruitmentPostUpdate(AddObject):
    model = RecruitmentPostUpdate
    form = RecruitmentPostUpdateForm
    redirect_url_name = 'view_recruitment_post'

    def check_permission(self, request, *args, **kwargs):
        if self.model.objects.get_create_permission(kwargs['recruitment_post'], request.user):
            return True
        return super().check_permission(request, *args, **kwargs)

    def get_redirect_url_params(self, request, *args, **kwargs):
        return f'#updates-last'

    def get_redirect_url_args(self, request, *args, **kwargs):
        return [kwargs['recruitment_post'].pk]

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().post(request, recruitment_post=RecruitmentPost.objects.get(pk=pk), user=request.user)


@method_decorator(login_required, name="dispatch")
class ChangeRecruitmentPostUpdate(ChangeUserKeyObject):
    model = RecruitmentPostUpdate
    form = RecruitmentPostUpdateForm
    redirect_url_name = 'view_recruitment_post'

    def get_redirect_url_params(self, request, pk, *args, **kwargs):
        return f'#update-{pk}'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [self.model.objects.get(pk=pk).recruitment_post.pk]

    def get(self, request, pk):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class AddRecruitmentSkill(View):
    model = Skill
    form = SkillForm
    redirect_url_name = 'view_recruitment_post'

    def post(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        post = RecruitmentPost.objects.get(pk=pk)
        if request.user not in post.add_skill_users:
            raise PermissionDenied()
        form = self.form(request.POST)
        if form.is_valid():
            if self.model.objects.filter(name__iexact=form.cleaned_data['name']).exists():
                skill = self.model.objects.get(
                    name__iexact=form.cleaned_data['name'])
            else:
                skill = self.model.objects.create(
                    name=form.cleaned_data['name'])
            post.skills.add(skill)
            post.save()
        else:
            print(form.errors)
            raise BadRequest()
        return redirect(reverse('view_recruitment_post', args=[pk]) + '#skills')


@method_decorator(login_required, name="dispatch")
class DeleteRecruitmentSkill(View):
    model = Skill
    redirect_url_name = 'view_recruitment_post'

    def post(self, request, pk, skill):
        if not RecruitmentPost.objects.filter(pk=pk).exists() or not self.model.objects.filter(pk=skill).exists():
            raise ObjectDoesNotExist()
        post = RecruitmentPost.objects.get(pk=pk)
        if request.user not in post.remove_skill_users:
            raise PermissionDenied()
        post.skills.remove(self.model.objects.get(pk=skill))
        post.save()
        return redirect(reverse('view_recruitment_post', args=[pk]) + '#skills')


@method_decorator(login_required, name="dispatch")
class AddRecruitmentApplication(AddObject):
    model = RecruitmentApplication
    form = RecruitmentApplicationForm
    redirect_url_name = 'view_recruitment_post'

    def check_permission(self, request, *args, **kwargs):
        if not self.model.objects.get_create_permission(kwargs['recruitment_post'], request.user):
            return False

        return super().check_permission(request, *args, **kwargs)

    def get_redirect_url_args(self, request, *args, **kwargs):
        return [kwargs['recruitment_post'].pk]

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().post(request, recruitment_post=RecruitmentPost.objects.get(pk=pk), user=request.user)


@method_decorator(login_required, name="dispatch")
class SelectRecruitmentApplication(View):
    def post(self, request, pk):
        if not RecruitmentApplication.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        application = RecruitmentApplication.objects.get(pk=pk)
        if request.user not in application.select_users:
            raise PermissionDenied()
        application.status = 'S'
        application.save()
        return redirect(reverse('recruitment_applications', args=[pk]))


@method_decorator(login_required, name="dispatch")
class RejectRecruitmentApplication(View):
    def post(self, request, pk):
        if not RecruitmentApplication.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        application = RecruitmentApplication.objects.get(pk=pk)
        if request.user not in application.reject_users:
            raise PermissionDenied()
        application.status = 'R'
        application.save()
        return redirect(reverse('recruitment_applications', args=[pk]))


@method_decorator(login_required, name="dispatch")
class ShortlistRecruitmentApplication(View):
    def post(self, request, pk):
        if not RecruitmentApplication.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        application = RecruitmentApplication.objects.get(pk=pk)
        if request.user not in application.shortlist_users:
            raise PermissionDenied()
        application.status = 'I'
        application.save()
        return redirect(reverse('recruitment_applications', args=[pk]))


@method_decorator(login_required, name="dispatch")
class PendingRecruitmentApplication(View):
    def post(self, request, pk):
        if not RecruitmentApplication.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        application = RecruitmentApplication.objects.get(pk=pk)
        if request.user not in application.pending_users:
            raise PermissionDenied()
        application.status = 'P'
        application.save()
        return redirect(reverse('recruitment_applications', args=[pk]))


class SkillAutocomplete(View):
    def get(self, request, pk, *args, **kwargs):
        query = request.GET.get('q')
        li = [(obj.name, f'{obj.pk}') for obj in Skill.objects.filter(
            jobs__id=pk, name__icontains=query)]
        return JsonResponse(li, safe=False)
