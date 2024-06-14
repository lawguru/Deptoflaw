from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import permission_required
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
from django.db.models import Q
import json

# Create your views here.


def index(request):
    home_heading, created = Setting.objects.get_or_create(key='home_heading')

    random_quote = Quote.objects.order_by('?').first()

    if home_heading.value == None:
        home_heading.value = 'Training & Placement Cell'
        home_heading.save()

    home_subheading, created = Setting.objects.get_or_create(
        key='home_subheading')
    if home_subheading.value == None:
        home_subheading.value = 'Assam University, Department of\nComputer Science and Engineering'
        home_subheading.save()

    home_description, created = Setting.objects.get_or_create(
        key='home_description')
    if home_description.value == None:
        home_description.value = 'Training & Placement Cell (TPC) handles all aspects of campus placements for the graduating students of the Department. TPC of Assam University\'s Department of Computer Science and Engineering (CSE) is well equipped with excellent infrastructure to support each and every stage of the placement processes. TPC staff members and student team assist in arranging Pre-Placement Talks, Written Tests, Group Discussions, and Interviews etc. as per the requirements of the Organizations and Recruiters.'
        home_description.save()

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

    data = {
        'home_heading': home_heading.value,
        'home_subheading': home_subheading.value.splitlines(),
        'home_description': home_description.value,
        'quote': random_quote,
        'message_from_hod': message_from_hod.value,
        'message_from_tpc_head': message_from_tpc_head.value,
        'hod': StaffProfile.objects.get(is_hod=True) if StaffProfile.objects.filter(is_hod=True).exists() else None,
        'tpc_head': StaffProfile.objects.get(is_tpc_head=True) if StaffProfile.objects.filter(is_tpc_head=True).exists() else None,
        'coordinators': User.objects.filter(groups__name='coordinators') if User.objects.filter(groups__name='coordinators').exists() else None,
    }
    return render(request, 'index.html', data)


def contact(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {'form': form, 'success': 'Your message has been sent successfully!'})
        else:
            return render(request, 'contact.html', {'form': form, 'error': 'Could not send your message. Please try again.'})
    return render(request, 'contact.html', {'form': ContactUsForm})


def notices(request):
    notices = Notice.objects.all()
    return render(request, 'notices.html', {'notices': notices})


@permission_required('cell.add_notice')
def add_notice(request):
    if request.method == 'POSt':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'add_notice.html', {'form': NoticeForm, 'success': 'Notice added successfully!'})
        else:
            return render(request, 'add_notice.html', {'form': NoticeForm, 'error': 'Could not add notice. Please try again.'})
    return render(request, 'add_notice.html', {'form': NoticeForm, })


@method_decorator(login_required, name="dispatch")
class ListRecruitmentPost(TemplateView):
    template_name = 'recruitment_posts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = RecruitmentPost.objects.filter(user=kwargs['user'])
        return context


@method_decorator(login_required, name="dispatch")
class AddRecruitmentPost(AddUserKeyObject):
    model = RecruitmentPost
    form = AddRecruitmentPostForm
    template_name = 'add_recruitment_post.html'
    redirect_url_name = 'recruitment_posts'

    def check_permission(self, request, *args, **kwargs):
        if User.objects.get(pk=kwargs['user']).role != 'recruiter':
            return False
        return super().check_permission(request, kwargs['user'], *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not User.objects.filter(pk=kwargs['user']).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, *args, **kwargs):
            raise PermissionDenied()
        if self.template_name and self.form:
            user = User.objects.get(pk=kwargs['user'])
            return render(request, self.template_name, {'form': self.form(initial={'company': user.recruiter_profile.company_name})})
        return redirect(self.get_redirect_url(request, *args, **kwargs))


@method_decorator(login_required, name="dispatch")
class ViewRecruitmentPost(TemplateView):
    template_name = 'recruitment_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = RecruitmentPost.objects.get(pk=kwargs['pk'])
        context['skills'] = context['post'].skills.all()
        context['updates'] = [(update, RecruitmentPostUpdateForm(
            instance=update)) for update in context['post'].updates.all()]
        if context['post'].user == self.request.user or self.request.user.is_superuser or self.request.user.is_coordinator:
            context['update_form'] = RecruitmentPostUpdateForm()
            context['skill_form'] = SkillForm()
        if self.request.user == context['post'].user:
            context['edit_form'] = RecruiterChangeRecruitmentPostForm(
                instance=context['post'])
        if self.request.user.is_superuser or self.request.user.is_coordinator:
            context['edit_form'] = TPCChangeRecruitmentPostForm(
                instance=context['post'])
        if self.request.user.role == 'student':
            if context['post'].applications.filter(user=self.request.user).exists():
                context['application'] = context['post'].applications.get(
                    user=self.request.user)
            if context['post'].is_active:
                context['apply_form'] = RecruitmentApplicationForm()
        return context

    def get(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().get(request, pk=pk)


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

    def check_permission(self, request, pk, *args, **kwargs):
        if request.user.is_superuser or request.user.is_coordinator:
            return True
        return RecruiterChangeRecruitmentPost.check_permission(self, request, pk, *args, **kwargs)


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
        if kwargs['recruitment_post'].user == request.user or request.user.is_superuser or request.user.is_coordinator:
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

    def check_permission(self, request, pk, *args, **kwargs):
        obj = self.model.objects.get(pk=pk)
        if obj.user == request.user or obj.recruitment_post.user == request.user or request.user.is_superuser:
            return True
        return super().check_permission(request, *args, **kwargs)

    def get_redirect_url_params(self, request, pk, *args, **kwargs):
        return f'#update-{pk}'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [self.model.objects.get(pk=pk).recruitment_post.pk]

    def get(self, request, pk):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteRecruitmentPostUpdate(DeleteUserKeyObject):
    model = RecruitmentPostUpdate
    redirect_url_name = 'view_recruitment_post'

    def check_permission(self, request, pk, *args, **kwargs):
        obj = self.model.objects.get(pk=pk)
        if obj.user == request.user or obj.recruitment_post.user == request.user or request.user.is_superuser:
            return True
        return super().check_permission(request, *args, **kwargs)

    def get_redirect_url_params(self, request, pk, *args, **kwargs):
        return '#updates'

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
        if request.user != post.user and not request.user.is_superuser and not request.user.is_coordinator():
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
        if request.user != post.user and not request.user.is_superuser and not request.user.is_coordinator():
            raise PermissionDenied()
        post.skills.remove(self.model.objects.get(pk=skill))
        post.save()
        return redirect(reverse('view_recruitment_post', args=[pk]) + '#skills')


@method_decorator(login_required, name="dispatch")
class AddRecruitmentApplication(AddObject):
    model = RecruitmentApplication
    form = RecruitmentApplicationForm
    redirect_url_name = 'recruitment_application'

    def check_permission(self, request, *args, **kwargs):
        if not kwargs['recruitment_post'].is_active or kwargs['recruitment_post'].applications.filter(user=request.user).exists() or request.user.role != 'student':
            return False

        return super().check_permission(request, *args, **kwargs)

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().post(request, recruitment_post=RecruitmentPost.objects.get(pk=pk), user=request.user)


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
            query = Q()
            for course in course_filters:
                query |= Q(user__student_profile__course=course)
            queryset = queryset.filter(query)

        if year_lower_limit or year_upper_limit:
            students = StudentProfile.objects

        if year_lower_limit:
            students = students.filter(year__gte=year_lower_limit)

        if year_upper_limit:
            students = students.filter(year__lte=year_upper_limit)

        if year_lower_limit or year_upper_limit:
            queryset = queryset.filter(
                user__student_profile__in=students)

        if cgpa_lower_limit:
            queryset = queryset.filter(
                user__student_profile__cgpa__gte=cgpa_lower_limit)

        if backlogs_upper_limit:
            queryset = queryset.filter(
                user__student_profile__backlog_count__lte=backlogs_upper_limit)

        if status_filters:
            query = Q()
            for status in status_filters:
                query |= Q(status=status)
            queryset = queryset.filter(query)

        if sorting:
            if sorting == 'cgpa':
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


class SkillAutocomplete(View):
    def get(self, request, pk, *args, **kwargs):
        query = request.GET.get('q')
        li = [(obj.name, f'{obj.pk}') for obj in Skill.objects.filter(
            jobs__id=pk, name__icontains=query)]
        return JsonResponse(li, safe=False)
