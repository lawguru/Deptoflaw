from django.db.models import Count
from django.shortcuts import render, redirect, reverse
from staff.models import StaffProfile
from settings.models import Setting
from user.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from views import AddUserKeyObject, ChangeUserKeyObject, AddObject, DeleteUserKeyObject
from django.views.generic.base import View, TemplateView
from django.views.generic.list import ListView
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from student.models import StudentProfile
from .forms import *
from .models import Notice, Quote
import json
import csv
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
        context['hod'] = User.objects.filter(staff_profile__is_hod=True)
        context['tpc_head'] = User.objects.filter(
            staff_profile__is_tpc_head=True).exclude(staff_profile__is_hod=True)
        context['developers'] = User.objects.filter(is_developer=True).exclude(Q(staff_profile__is_hod=True) | Q(
            staff_profile__is_tpc_head=True))
        context['superusers'] = User.objects.filter(is_superuser=True).exclude(Q(staff_profile__is_hod=True) | Q(
            staff_profile__is_tpc_head=True) | Q(is_developer=True))
        context['coordinators'] = User.objects.filter(is_coordinator=True).exclude(Q(staff_profile__is_hod=True) | Q(
            staff_profile__is_tpc_head=True) | Q(is_developer=True) | Q(is_superuser=True))
        context['team'] = list(chain(context['hod'], context['tpc_head'],
                               context['developers'], context['superusers'], context['coordinators']))
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
            context['add_post_form'] = AddRecruitmentPostForm(
                initial={'user': user})

        if Notice.objects.get_create_permission(user):
            context['add_notice_form'] = NoticeForm()

        if Quote.objects.get_create_permission(user, user):
            context['add_quote_form'] = QuoteForm(initial={'user': user})
            context['quotes_count'] = Quote.objects.count()

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
        messages = Message.objects.all()

        context.update({
            'unapproved_user_count': unapproved_users.count(),
            'unapproved_student_count': unapproved_users.filter(role='student').count(),
            'unapproved_staff_count': unapproved_users.filter(role='staff').count(),
            'unapproved_recruiter_count': unapproved_users.filter(role='recruiter').count(),
            'student_count': students.count(),
            'current_student_count': students.filter(is_current=True).count(),
            'alumni_count': students.filter(passed_out=True).count(),
            'messages_count': messages.count(),
            'handled_messages_count': messages.filter(handled=True).count(),
            'unhandled_messages_count': messages.filter(handled=False).count(),
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
        user_notices = Notice.objects.filter(user=self.request.user)
        all_notices = Notice.objects.all()

        return {
            'post_count': RecruitmentPost.objects.count(),
            'active_post_count': active_posts.count(),
            'user_notice_count': len(user_notices),
            'total_notice_count': len(all_notices),
        }


class ListNotice(ListView):
    model = Notice
    template_name = 'notices.html'
    paginate_by = 50

    sorting_options = [
        ('date', 'Date'),
        ('user', 'Posted by'),
        ('title', 'Title'),
    ]
    post_sorting_options = [
        ('recruitment_post__user', 'Recruitment Posted by'),
    ]
    user_options = [
        ('', 'Any'),
        ('me', 'Me'),
    ]
    type_options = [
        ('', 'Any'),
        ('notice', 'Notice'),
        ('post-update', 'Recruitment Post Update'),
    ]
    recruitment_post_options = [
        ('', 'Any'),
    ]
    poster_recruitment_post_options = [
        ('by-me', 'By me'),
    ]
    studnet_recruitment_post_options = [
        ('applied-by-me', 'Applied by me'),
    ]

    def get_queryset(self):
        query = Q()

        type_filter = self.request.GET.get('type-filter')
        if type_filter == 'notice':
            query &= Q(kind='N')
        elif type_filter == 'post-update':
            query &= Q(kind='U')

        query = self.apply_user_filter(query)
        query = self.apply_recruitment_post_filter(query)

        queryset = super().get_queryset()
        queryset = queryset.filter(query)

        sorting = self.request.GET.get('sorting', 'date')
        if sorting:
            if sorting == 'date':
                queryset = queryset.order_by('date')
            elif sorting == 'user':
                queryset = queryset.order_by('user')
            elif sorting == 'title':
                queryset = queryset.order_by('title')
            elif type_filter == 'post-update' and sorting == 'recruitment_post__user':
                queryset = queryset.order_by('recruitment_post__user')

        ordering = self.request.GET.get('ordering')
        if ordering:
            if ordering == 'desc':
                queryset = queryset.reverse()

        return queryset

    def apply_user_filter(self, query):
        user_filter = self.request.GET.get('user-filter')
        if user_filter == 'me':
            query &= Q(user=self.request.user)
        return query

    def apply_recruitment_post_filter(self, query):
        recruitment_post_filter = self.request.GET.get(
            'recruitment-post-filter')
        if recruitment_post_filter == 'by-me':
            query &= Q(
                recruitmentpostupdate__recruitment_post__user=self.request.user)
        elif recruitment_post_filter == 'applied-by-me':
            query &= Q(
                recruitmentpostupdate__recruitment_post__applications__user=self.request.user)
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'].object_list = [(RecruitmentPostUpdate.objects.get(notice_ptr_id=notice.id) if notice.kind == 'U' else notice, RecruitmentPostUpdateForm(instance=notice) if notice.kind == 'U' else NoticeForm(instance=notice))
                                           for notice in context['page_obj'].object_list]
        context['sorting_options'] = self.sorting_options

        context['type_options'] = self.type_options

        context['type_filter'] = self.request.GET.get('type-filter', '')
        context['user_filter'] = self.request.GET.get('user-filter', '')

        if self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_coordinator or self.request.user.role == 'recruiter' or self.request.user.role == 'staff'):
            context['user_options'] = self.user_options

        if context['type_filter'] == 'post-update':
            context['recruitment_post_options'] = self.recruitment_post_options
            if self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_coordinator or self.request.user.role == 'recruiter'):
                context['recruitment_post_options'] += self.poster_recruitment_post_options
            if self.request.user.is_authenticated and self.request.user.role == 'student':
                context['recruitment_post_options'] += self.studnet_recruitment_post_options
            context['sorting_options'] += self.post_sorting_options
            context['recruitment_post_filter'] = self.request.GET.get(
                'recruitment-post-filter', '')
        context['sorting'] = self.request.GET.get('sorting', 'date')
        context['ordering'] = self.request.GET.get('ordering', 'asc')
        return context


class ListRecruitmentPost(ListView):
    model = RecruitmentPost
    template_name = 'recruitment_posts.html'
    paginate_by = 50

    job_type_choices = RecruitmentPost.job_type_choices
    workplace_type_choices = RecruitmentPost.workplace_type_choices
    start_date_type_choices = RecruitmentPost.start_date_type_choices
    applications_status_choices = RecruitmentApplication.status_choices
    post_choices = [
        ('', 'Any Post'),
    ]
    recruiter_post_choices = [
        ('by-me', 'By me'),
    ]
    student_post_choices = [
        ('applied-by-me', 'Applied by me'),
    ]

    def get_queryset(self):
        query = Q()

        query = self.apply_company_filter(query)
        query = self.apply_location_filter(query)
        query = self.apply_job_type_filters(query)
        query = self.apply_workplace_type_filters(query)
        query = self.apply_salary_filter(query)
        query = self.apply_experience_filter(query)
        query = self.apply_start_date_filter(query)
        query = self.apply_skill_filter(query)
        query = self.apply_post_filter(query)
        query = self.apply_applications_status_filters(query)
        query = self.apply_active_filter(query)

        queryset = super().get_queryset().filter(query).distinct()

        sorting = self.request.GET.get('sorting')
        if sorting:
            queryset = queryset.order_by(sorting)

        ordering = self.request.GET.get('ordering')
        if ordering == 'desc':
            queryset = queryset.reverse()
        return queryset

    def apply_skill_filter(self, query):
        skill_filter = self.request.GET.getlist('skill-filter')
        if skill_filter:
            query &= Q(skills__name__in=skill_filter)
        return query

    def apply_company_filter(self, query):
        company_filter = self.request.GET.get('company-filter')
        if company_filter:
            query &= Q(company__icontains=company_filter)
        return query

    def apply_location_filter(self, query):
        location_filter = self.request.GET.get('location-filter')
        if location_filter:
            query &= Q(location__icontains=location_filter)
        return query

    def apply_job_type_filters(self, query):
        job_type_filters = self.request.GET.getlist('job-type-filters')
        job_type_filters = [job_type for job_type in job_type_filters if job_type in [
            job_type[0] for job_type in self.job_type_choices]]
        if job_type_filters:
            query &= Q(job_type__in=job_type_filters)
        return query

    def apply_workplace_type_filters(self, query):
        workplace_type_filters = self.request.GET.getlist(
            'workplace-type-filters')
        workplace_type_filters = [workplace_type for workplace_type in workplace_type_filters if workplace_type in [
            workplace_type[0] for workplace_type in self.workplace_type_choices]]
        if workplace_type_filters:
            query &= Q(
                workplace_type__in=workplace_type_filters)
        return query

    def apply_salary_filter(self, query):
        expected_salary = self.request.GET.get('expected-salary', 0)
        if expected_salary and expected_salary.replace('.', '', 1).isdigit():
            query &= Q(minimum_salary__gte=expected_salary)
        return query

    def apply_experience_filter(self, query):
        experience_filter_lower_limit = self.request.GET.get(
            'experience-filter-lower-limit')
        experience_filter_upper_limit = self.request.GET.get(
            'experience-filter-upper-limit')
        if experience_filter_lower_limit and experience_filter_lower_limit.isdigit():
            query &= Q(
                experience_duration__gte=experience_filter_lower_limit)
        if experience_filter_upper_limit and experience_filter_upper_limit.isdigit():
            query &= Q(
                experience_duration__lte=experience_filter_upper_limit)
        return query

    def apply_start_date_filter(self, query):
        start_date_type_filter = self.request.GET.get('start-date-type-filter')
        if start_date_type_filter and start_date_type_filter in [start_date_type[0] for start_date_type in self.start_date_type_choices]:
            query &= Q(start_date_type=start_date_type_filter)
            if start_date_type_filter == 'S':
                start_date_filter_lower_limit = self.request.GET.get(
                    'start-date-filter-lower-limit')
                start_date_filter_upper_limit = self.request.GET.get(
                    'start-date-filter-upper-limit')
                try:
                    if start_date_filter_lower_limit and datetime.strptime(start_date_filter_lower_limit, '%Y-%m-%d'):
                        query &= Q(
                            start_date__gte=start_date_filter_lower_limit)
                    if start_date_filter_upper_limit and datetime.strptime(start_date_filter_upper_limit, '%Y-%m-%d'):
                        query &= Q(
                            start_date__lte=start_date_filter_upper_limit)
                except ValueError:
                    pass
        return query

    def apply_post_filter(self, query):
        if not self.request.user.is_authenticated:
            return query
        post_filter = self.request.GET.get('post-filter', '')
        if post_filter == 'by-me':
            query &= Q(user=self.request.user)
        elif post_filter == 'applied-by-me':
            query &= Q(applications__user=self.request.user)
            query = self.apply_applied_status_filter(query)
        return query

    def apply_applied_status_filter(self, query):
        applied_status_filters = self.request.GET.getlist(
            'applied-status-filters')
        applied_status_filters = [status for status in applied_status_filters if status in [
            status[0] for status in self.applications_status_choices]]

        if len(applied_status_filters):
            applications = RecruitmentApplication.objects.filter(
                user=self.request.user, status__in=applied_status_filters)
            query &= Q(applications__in=applications)

        return query

    def apply_applications_status_filters(self, query):
        applications_status_filters = self.request.GET.getlist(
            'applications-status-filters', [])
        applications_status_filters = [status for status in applications_status_filters if status in [
            status[0] for status in self.applications_status_choices]]

        if applications_status_filters:
            query &= Q(
                applications__status__in=applications_status_filters)

        return query

    def apply_active_filter(self, query):
        is_active_filter = self.request.GET.get('is-active-filter', 'true')
        if is_active_filter is not None:
            if is_active_filter.lower() != 'false':
                query &= Q(apply_by__gte=datetime.today().date())
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_filter'] = self.request.GET.get('company-filter', '')
        context['location_filter'] = self.request.GET.get(
            'location-filter', '')
        context['job_type_filters'] = self.request.GET.getlist(
            'job-type-filters', [])
        context['job_type_choices'] = self.job_type_choices
        context['workplace_type_filters'] = self.request.GET.getlist(
            'workplace-type-filters', [])
        context['workplace_type_choices'] = self.workplace_type_choices
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
        context['start_date_type_choices'] = self.start_date_type_choices
        context['skill_filter'] = self.request.GET.getlist('skill-filter')
        context['is_active_filter'] = self.request.GET.get(
            'is-active-filter', 'true')

        context['post_filter'] = self.request.GET.get('post-filter', '')
        context['post_choices'] = self.post_choices.copy()
        if self.request.user.is_authenticated and self.request.user.role == 'student':
            context['post_choices'] += self.student_post_choices
            context['applied_status_filters'] = self.request.GET.getlist(
                'applied-status-filters', [])
            context['applied_status_choices'] = self.applications_status_choices

        if self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_coordinator or self.request.user.role == 'recruiter'):
            context['post_choices'] += self.recruiter_post_choices
            if self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_coordinator or (self.request.user.role == 'recruiter' and context['post_filter'] == 'by-me')):
                context['applications_status_filters'] = self.request.GET.getlist(
                    'applications-status-filters', [])
                context['applications_status_choices'] = self.applications_status_choices

        context['sorting_options'] = [
            ('apply_by', 'Apply By date'),
            ('start_date', 'Start date'),
            ('experience_duration', 'Experience duration'),
        ]
        context['sorting'] = self.request.GET.get('sorting', 'apply_by')
        context['ordering'] = self.request.GET.get('ordering', 'asc')

        return context


@method_decorator(login_required, name="dispatch")
class MessageListView(ListView):
    model = Message
    template_name = 'messages.html'
    paginate_by = 50
    status_options = [
        ('', 'Any'),
        ('handled', 'Handled'),
        ('unhandled', 'Unhandled'),
    ]
    sorting_options = [
        ('date', 'Date Received'),
        ('sender', 'Sender\'s Name'),
        ('sender_company', 'Company'),
        ('sender_designation', 'Designation'),
        ('sender_phone', 'Phone'),
        ('sender_email', 'Email'),
    ]
    handled_sorting_option = [
        ('handled_on', 'Date Handled')
    ]

    def get_queryset(self):
        query = Q()

        status_filter = self.request.GET.get('status-filter', '')
        if status_filter == 'handled':
            query &= Q(handled=True)
        elif status_filter == 'unhandled':
            query &= Q(handled=False)

        company_filter = self.request.GET.get('company-filter')
        if company_filter:
            query &= Q(sender_company__icontains=company_filter)

        designation_filter = self.request.GET.get('designation-filter')
        if designation_filter:
            query &= Q(sender_designation__icontains=designation_filter)

        phone_filter = self.request.GET.get('phone-filter')
        if phone_filter:
            query &= Q(sender_phone__icontains=phone_filter)

        email_filter = self.request.GET.get('email-filter')
        if email_filter:
            query &= Q(sender_email__icontains=email_filter)

        name_filter = self.request.GET.get('name-filter')
        if name_filter:
            query &= Q(sender__icontains=name_filter)

        queryset = super().get_queryset().filter(query)

        sorting = self.request.GET.get('sorting', 'date')
        if sorting:
            if sorting == 'sender_company':
                queryset = queryset.order_by('sender_company')
            elif sorting == 'sender_designation':
                queryset = queryset.order_by('sender_designation')
            elif sorting == 'sender_phone':
                queryset = queryset.order_by('sender_phone')
            elif sorting == 'sender_email':
                queryset = queryset.order_by('sender_email')
            elif sorting == 'sender':
                queryset = queryset.order_by('sender')
            else:
                if sorting == 'date' or status_filter == 'unhandled':
                    queryset = queryset.order_by('date')
                else:
                    if sorting == 'handled_on':
                        queryset = queryset.order_by('handled_on')
                    else:
                        queryset = queryset.order_by('date')

        ordering = self.request.GET.get('ordering')
        if ordering == 'desc':
            queryset = queryset.reverse()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_obj'].object_list = [(message, MessageHandledForm(
            instance=message)) for message in context['page_obj'].object_list]

        context['sorting_options'] = self.sorting_options
        context['status_options'] = self.status_options

        context['sorting'] = self.request.GET.get('sorting', 'date')
        context['ordering'] = self.request.GET.get('ordering', 'asc')

        context['status_filter'] = self.request.GET.get(
            'status-filter', '')
        if context['status_filter'] == 'handled':
            context['sorting_options'] = self.handled_sorting_option + \
                context['sorting_options']

        context['company_filter'] = self.request.GET.get('company-filter', '')
        context['designation_filter'] = self.request.GET.get(
            'designation-filter', '')
        context['phone_filter'] = self.request.GET.get('phone-filter', '')
        context['email_filter'] = self.request.GET.get('email-filter', '')
        context['name_filter'] = self.request.GET.get('name-filter', '')

        return context

    def get(self, request):
        if request.user.is_superuser or request.user.is_coordinator:
            return super().get(request)
        raise PermissionDenied()


@method_decorator(login_required, name="dispatch")
class QuoteListView(ListView):
    model = Quote
    template_name = 'quotes.html'
    paginate_by = 50

    sorting_options = [
        ('date', 'Date'),
        ('date_edited', 'Date Edited'),
        ('author', 'Author'),
        ('quote', 'Quote'),
        ('source', 'Source'),
    ]
    user_options = [
        ('', 'Anyone'),
        ('me', 'Me'),
    ]
    fictional_options = [
        ('on', 'Fictional'),
        ('off', 'Non-Fictional'),
    ]

    def get_queryset(self):
        query = Q()

        author_filter = self.request.GET.get('author-filter')
        if author_filter:
            query &= Q(author__icontains=author_filter)

        quote_filter = self.request.GET.get('quote-filter')
        if quote_filter:
            query &= Q(quote__icontains=quote_filter)

        source_filter = self.request.GET.get('source-filter')
        if source_filter:
            query &= Q(source__icontains=source_filter)

        user_filter = self.request.GET.get('user-filter', '')
        if user_filter == 'me':
            query &= Q(user=self.request.user)

        fictional_filters = self.request.GET.getlist('fictional-filters')
        fictional_filters = [fictional for fictional in fictional_filters if fictional in [
            fictional[0] for fictional in self.fictional_options]]
        fictional_filters = [True if fictional ==
                             'on' else False for fictional in fictional_filters]
        if fictional_filters:
            query &= Q(fictional__in=fictional_filters)

        queryset = super().get_queryset().filter(query)

        sorting = self.request.GET.get('sorting', 'date')
        if sorting:
            if sorting == 'date_edited':
                queryset = queryset.order_by('date_edited')
            elif sorting == 'author':
                queryset = queryset.order_by('author')
            elif sorting == 'quote':
                queryset = queryset.order_by('quote')
            elif sorting == 'source':
                queryset = queryset.order_by('source')
            else:
                queryset = queryset.order_by('date')

        ordering = self.request.GET.get('ordering', 'asc')
        if ordering == 'desc':
            queryset = queryset.reverse()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_obj'].object_list = [(quote, QuoteForm(
            instance=quote)) for quote in context['page_obj'].object_list]

        context['sorting_options'] = self.sorting_options
        context['user_options'] = self.user_options
        context['fictional_options'] = self.fictional_options

        context['sorting'] = self.request.GET.get('sorting', 'date')
        context['ordering'] = self.request.GET.get('ordering', 'asc')

        context['author_filter'] = self.request.GET.get('author-filter', '')
        context['quote_filter'] = self.request.GET.get('quote-filter', '')
        context['source_filter'] = self.request.GET.get('source-filter', '')
        context['user_filter'] = self.request.GET.get('user-filter', '')
        context['fictional_filters'] = self.request.GET.getlist(
            'fictional-filters', [])

        return context


@method_decorator(login_required, name="dispatch")
class MessageSetHandled(View):
    form = MessageHandledForm

    def post(self, request, pk):
        if not Message.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        message = Message.objects.get(pk=pk)
        if request.user not in message.handle_users:
            raise PermissionDenied()
        form = self.form(request.POST, instance=message)
        if form.is_valid():
            message.handled = True
            message.handled_on = datetime.now()
            message.handled_by = request.user
            message.handled_notes = form.cleaned_data['handled_notes']
            message.save()
        return redirect(reverse('messages')+f'?status-filter=handled&sorting=handled_on&ordering=desc')


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

    course_choices = StudentProfile.course_choices
    status_choices = RecruitmentApplication.status_choices
    sorting_options = [
        ('applied_on', 'Applied On'),
        ('name', 'Name'),
        ('total_skills', 'Total Skills'),
        ('skill_matches', 'Skill Matches'),
        ('other_skills_count', 'Other Skills Count'),
        ('course', 'Course'),
        ('year', 'Year'),
        ('cgpa', 'CGPA'),
        ('backlogs', 'Backlogs'),
    ]

    def get_queryset(self):
        skill_filters = self.request.GET.get('skill-filters')
        course_filters = self.request.GET.getlist('course-filters', [])
        year_lower_limit = self.request.GET.get('year-lower-limit', 0)
        year_upper_limit = self.request.GET.get('year-upper-limit')
        cgpa_lower_limit = self.request.GET.get('cgpa-lower-limit', 0)
        backlogs_upper_limit = self.request.GET.get('backlogs-upper-limit')
        status_filters = self.request.GET.getlist('status-filters', [])
        sorting = self.request.GET.get('sorting', 'applied_on')
        ordering = self.request.GET.get('ordering', 'asc')

        query = Q(recruitment_post=self.kwargs['pk'])

        if skill_filters:
            try:
                for and_filter in json.loads(skill_filters):
                    query &= Q(user__skills__in=and_filter)
            except:
                pass

        course_filters = [course for course in course_filters if course in [
            course[0] for course in self.course_choices]]
        if course_filters:
            query &= Q(
                student_profile__course__in=course_filters)

        if year_lower_limit or year_upper_limit:
            students = StudentProfile.objects

            if year_lower_limit and year_lower_limit.isdigit():
                students = students.filter(year__gte=year_lower_limit)

            if year_upper_limit and year_upper_limit.isdigit():
                students = students.filter(year__lte=year_upper_limit)

            query &= Q(user__student_profile__in=students)

        if cgpa_lower_limit and cgpa_lower_limit.replace('.', '', 1).isdigit():
            query &= Q(
                user__student_profile__cgpa__gte=cgpa_lower_limit)

        if backlogs_upper_limit and backlogs_upper_limit.isdigit():
            query &= Q(
                user__student_profile__backlog_count__lte=backlogs_upper_limit)

        status_filters = [status for status in status_filters if status in [
            status[0] for status in self.status_choices]]
        if status_filters:
            query &= Q(status__in=status_filters)

        queryset = super().get_queryset().filter(query)

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
        context['sorting_options'] = self.sorting_options

        skill_filters = self.request.GET.get('skill-filters', [])
        course_filters = self.request.GET.getlist('course-filters', [])
        year_lower_limit = self.request.GET.get('year-lower-limit', 0)
        year_upper_limit = self.request.GET.get('year-upper-limit')
        cgpa_lower_limit = self.request.GET.get('cgpa-lower-limit', 0)
        backlogs_upper_limit = self.request.GET.get('backlogs-upper-limit')
        status_filters = self.request.GET.getlist('status-filters', [])
        sorting = self.request.GET.get('sorting', 'applied_on')
        ordering = self.request.GET.get('ordering', 'asc')

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

    def get(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        if request.user not in RecruitmentPost.objects.get(pk=pk).view_application_users:
            raise PermissionDenied()
        return super().get(request, pk=pk)


@method_decorator(login_required, name="dispatch")
class RecruitmentApplicationsCSV(RecruitmentApplications):
    content_type = 'text/csv'

    def get(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        if request.user not in RecruitmentPost.objects.get(pk=pk).view_application_users:
            raise PermissionDenied()

        queryset = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications.csv"'

        writer = csv.writer(response)

        row = []
        row.append('Name')
        row.append('Application Status')
        row.append('Applied On')
        row.append('Cover Letter')
        row.append('Answers')
        row.append('Bio')
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

        for application in queryset:
            row = []
            row.append(application.user.full_name)
            row.append(application.get_status_display())
            row.append(application.applied_on)
            row.append(application.cover_letter)
            row.append(application.answers)
            row.append(application.user.bio)
            row.append(
                application.user.primary_email.email if application.user.primary_email else '')
            row.append(application.user.primary_phone_number.__str__()
                       if application.user.primary_phone_number else '')
            row.append(f'{application.user.primary_address.address}, {application.user.primary_address.city}, {application.user.primary_address.state}, {application.user.primary_address.country}, {application.user.primary_address.pincode}' if application.user.primary_address else '')
            row.append(application.user.student_profile.registration_year)
            row.append(application.user.student_profile.registration_number)
            row.append(
                f'{application.user.student_profile.roll}-{application.user.student_profile.number}')
            row.append(application.user.student_profile.course)
            row.append(application.user.student_profile.year)
            row.append(application.user.student_profile.cgpa)
            row.append(application.user.student_profile.backlog_count)
            row.append(application.user.student_profile.pass_out_year)
            row.append(
                ', '.join([skill.name for skill in application.user.skills.all()]))
            row.append(request.build_absolute_uri(
                reverse('resume', args=[application.user.id])))
            writer.writerow(row)

        return response


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
class AddQuote(AddUserKeyObject):
    model = Quote
    form = QuoteForm
    redirect_url_name = 'quotes'

    def get_redirect_url_args(self, request, *args, **kwargs):
        return []

    def get_redirect_url_params(self, request, *args, **kwargs):
        return f'?sorting=date&ordering=desc'


@method_decorator(login_required, name="dispatch")
class ChangeQuote(ChangeUserKeyObject):
    model = Quote
    form = QuoteForm
    redirect_url_name = 'quotes'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return []

    def get_redirect_url_params(self, request, *args, **kwargs):
        return f'?sorting=date_edited&ordering=desc'


@method_decorator(login_required, name="dispatch")
class DeleteQuote(DeleteUserKeyObject):
    model = Quote
    redirect_url_name = 'quotes'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return []

    def get_redirect_url_params(self, request, *args, **kwargs):
        return ''


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
class ApplicationPerformAction(View):
    def post(self, request, pk, action):
        if not RecruitmentApplication.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        application = RecruitmentApplication.objects.get(pk=pk)

        if action == 'S':
            if request.user not in application.select_users:
                raise PermissionDenied()
            application.status = 'S'
        elif action == 'R':
            if request.user not in application.reject_users:
                raise PermissionDenied()
            application.status = 'R'
        elif action == 'I':
            if request.user not in application.shortlist_users:
                raise PermissionDenied()
            application.status = 'I'
        elif action == 'P':
            if request.user not in application.pending_users:
                raise PermissionDenied()
            application.status = 'P'

        application.save()

        actions = []
        if request.user in application.select_users:
            actions.append(
                {
                    'name': 'Select',
                    'url': reverse('select_recruitment_application', args=[pk])
                }
            )
        if request.user in application.reject_users:
            actions.append(
                {
                    'name': 'Reject',
                    'url': reverse('reject_recruitment_application', args=[pk])
                }
            )
        if request.user in application.shortlist_users:
            actions.append(
                {
                    'name': 'Shortlist',
                    'url': reverse('shortlist_recruitment_application', args=[pk])
                }
            )
        if request.user in application.pending_users:
            actions.append(
                {
                    'name': 'Set as Pending',
                    'url': reverse('pending_recruitment_application', args=[pk])
                }
            )

        return JsonResponse({'actions': actions, 'status': application.status, 'status_text': application.get_status_display()})


@method_decorator(login_required, name="dispatch")
class SelectRecruitmentApplication(ApplicationPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'S')


@method_decorator(login_required, name="dispatch")
class RejectRecruitmentApplication(ApplicationPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'R')


@method_decorator(login_required, name="dispatch")
class ShortlistRecruitmentApplication(ApplicationPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'I')


@method_decorator(login_required, name="dispatch")
class PendingRecruitmentApplication(ApplicationPerformAction):
    def post(self, request, pk):
        return super().post(request, pk, 'P')


class SkillAutocomplete(View):
    def get(self, request, pk, *args, **kwargs):
        query = request.GET.get('q')
        li = [(obj.name, f'{obj.pk}') for obj in Skill.objects.filter(
            jobs__id=pk, name__icontains=query)]
        return JsonResponse(li, safe=False)
